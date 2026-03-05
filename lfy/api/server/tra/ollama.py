"""Ollama 翻译接口
"""
from gettext import gettext as _

import requests

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils import clear_key

DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "translategemma:4b"
DEFAULT_SYSTEM = "You are a translation engine. Only output the translated text."
DEFAULT_PROMPT = "Translate the following text from {from_lang} to {to_lang}:\n{text}"
DEFAULT_OPTIONS = "temperature=0.2;top_p=0.9;timeout=60"


def _lang_name_from_key(st: ServerTra, key: str) -> str:
    for lang in st.langs:
        if lang.key == key:
            return lang.get_name()
    return key


def _parse_options(options_str: str) -> dict:
    options = {}
    if not options_str:
        return options
    for item in options_str.replace(",", ";").split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue
        k, v = item.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        if v.lower() in ("true", "false"):
            options[k] = v.lower() == "true"
            continue
        try:
            options[k] = int(v)
            continue
        except ValueError:
            pass
        try:
            options[k] = float(v)
            continue
        except ValueError:
            pass
        options[k] = v
    return options


def _parse_conf(st: ServerTra):
    conf_str = st.get_conf() or ""
    if conf_str:
        conf_str = clear_key(conf_str)
    parts = conf_str.split("|") if conf_str else []
    parts += [""] * (5 - len(parts))
    url = parts[0] or DEFAULT_URL
    model = parts[1] or DEFAULT_MODEL
    system_prompt = parts[2] or DEFAULT_SYSTEM
    user_prompt = parts[3] or DEFAULT_PROMPT
    options_str = parts[4] or DEFAULT_OPTIONS
    return url, model, system_prompt, user_prompt, options_str


def _translate(st: ServerTra, text: str, lang_to="en", lang_from="auto"):
    url, model, system_prompt, user_prompt, options_str = _parse_conf(st)
    lang_to_name = _lang_name_from_key(st, lang_to)
    lang_from_name = _lang_name_from_key(st, lang_from)
    prompt = user_prompt.format(
        text=text,
        source=text,
        from_lang=lang_from_name,
        to_lang=lang_to_name,
        server=st.name,
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system_prompt:
        payload["system"] = system_prompt
    options = _parse_options(options_str)
    timeout = TIME_OUT * 20
    if "timeout" in options:
        try:
            timeout = float(options.pop("timeout"))
        except (TypeError, ValueError):
            timeout = TIME_OUT * 20
    if options:
        payload["options"] = options

    resp = st.session.post(
        f"{url.rstrip('/')}/api/generate",
        json=payload,
        timeout=timeout,
    )
    if resp.status_code != 200:
        raise RuntimeError(resp.text.strip() or f"HTTP {resp.status_code}")
    data = resp.json()
    return True, data.get("response", "")


class OllamaServer(ServerTra):
    """Ollama 翻译
    """

    def __init__(self):
        lang_key_ns = {
            "zh": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8,
            "es": 9,
            "pt-pt": 10,
            "pt": 11,
        }
        super().__init__("ollama", _("Ollama"))
        self.set_data(
            lang_key_ns,
            "url|model|system|prompt|options",
            session=requests.Session(),
        )

    def get_conf(self, add=""):
        conf = super().get_conf(add)
        if not conf:
            conf = "|".join(
                [DEFAULT_URL, DEFAULT_MODEL, DEFAULT_SYSTEM, DEFAULT_PROMPT, DEFAULT_OPTIONS]
            )
            self._conf_str = conf
        return conf

    def check_conf(self, conf_str, fun_check=_translate, py_libs=None):
        # 快速校验，避免模型生成导致超时
        self._conf_str = clear_key(conf_str.strip())
        sk_no = not self.get_conf() \
                or (self.sk_placeholder_text.count("|") == 1
                    and self.get_conf().count("|") != 1) \
                or self.get_conf()[0] == "|" \
                or self.get_conf()[-1] == "|"
        if sk_no:
            self._conf_str = None
            return False, _("please input `{sk}` for `{server}` in preference") \
                .format(sk=self.sk_placeholder_text, server=self.name)

        url, model, _sys, _prompt, options_str = _parse_conf(self)
        options = _parse_options(options_str)
        timeout = TIME_OUT * 20
        if "timeout" in options:
            try:
                timeout = float(options.get("timeout"))
            except (TypeError, ValueError):
                timeout = TIME_OUT * 20

        try:
            resp = self.session.get(f"{url.rstrip('/')}/api/tags", timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(resp.text.strip() or f"HTTP {resp.status_code}")
            data = resp.json()
            models = [m.get("name") for m in data.get("models", [])]
            if model and model not in models:
                return False, _("Model not found: {model}").format(model=model)
        except Exception as exc:  # pylint: disable=W0718
            return False, str(exc)

        self.set_conf()
        return True, _("Applied")

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
