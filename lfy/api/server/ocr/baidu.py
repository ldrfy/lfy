"""百度翻译接口
"""
import base64
import time
from gettext import gettext as _

from lfy.api.server import TIME_OUT, Server
from lfy.utils import s2ks
from lfy.utils.settings import Settings


def _get_token(session, ocr_api_key_s):
    """https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjhhu

    Returns:
        _type_: _description_
    """
    sg = Settings()

    expires_in_date = sg.g("ocr-baidu-token-expires-date", t=float)

    if expires_in_date - time.time() > 0:
        access_token = sg.g("ocr-baidu-token")
        if len(access_token) != 0:
            return True, access_token

    api_key, secret_key = s2ks(ocr_api_key_s)
    # API Key | Secret Key
    if api_key is None or api_key == "API Key":
        return False, _("please input API Key in preference") + ": OCR"

    ok, access_token, expires_in_date = \
        _get_token_by_url(session, api_key, secret_key)

    if ok:
        sg.s("ocr-baidu-token", access_token)
        sg.s("ocr-baidu-token-expires-date", expires_in_date)

    return ok, access_token


def _get_token_by_url(session, api_key, secret_key):
    """获取token

    Args:
        api_key (_type_): _description_
        secret_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    ok = False
    expires_in_date = -1

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    url0 = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"
    url = f'{url0}&client_id={api_key}&client_secret={secret_key}'

    request = session.get(url, timeout=TIME_OUT)

    jsons = request.json()
    if "access_token" not in jsons:
        access_token = "错误：" + jsons["error_description"]
    else:
        access_token = jsons["access_token"]
        expires_in_date = time.time() + jsons["expires_in"]
        ok = True

    return ok, str(access_token), expires_in_date


class BaiduServer(Server):
    """百度翻译
    """

    def __init__(self):

        # Development documentation
        # https://ai.baidu.com/ai-doc/OCR/zk3h7xz52
        lang_key_ns = {
            # 中英混合，默认
            "CHN_ENG": 1,
            "ENG": 3,
            "JAP": 4,
            "KOR": 5,
            "GER": 6,
            "FRE": 7,
            "ITA": 8
        }

        super().__init__("baidu", _("baidu"), lang_key_ns)
        self.can_ocr = True

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings().g("server-sk-baidu-ocr")

    def ocr_image(self, img_path, lang_str=None):
        """图文识别

        Args:
            img_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        img_data = None
        with open(img_path, 'rb') as f:
            img_data = f.read()
        if img_data is None:
            return False, ""

        img = base64.b64encode(img_data)

        # open('./images/lt.png', 'rb').read()
        s = ""
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/"

        request_url += "general_basic"

        ok, token = _get_token(self.session, self.get_api_key_s_ocr())
        if not ok:
            return False, token
        params = {"image": img}
        print(lang_str)
        if lang_str is not None:
            params["language_type"] = lang_str

        request_url = request_url + "?access_token=" + token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = self.session.post(request_url,
                                data=params,
                                headers=headers,
                                timeout=TIME_OUT).json()

        if "error_code" in res:
            if 110 == res["error_code"]:
                Settings().s("ocr-baidu-token", "")
            return False, _("something error: {}")\
                .format(f'\n\n{res["error_code"]}: {res["error_msg"]}')

        for word in res["words_result"]:
            s += word["words"] + '\n'

            s_ = word["words"]
            if s_[len(s_) - 1:len(s_)] != "-":
                s += " "

        return ok, s

    def check_ocr(self, api_key_ocr_s):
        """OCR测试

        Args:
            api_key_ocr_s (str): _description_

        Returns:
            _type_: _description_
        """
        api_key, secret_key = s2ks(api_key_ocr_s)
        if api_key is None or api_key == "API Key":
            error_msg = _("please input API Key and Secret Key like:")
            return False, error_msg + " 121343 | fdsdsdg"

        ok, access_token, expires_in_date = \
            _get_token_by_url(self.session, api_key, secret_key)
        if ok:
            ss = Settings()
            ss.s("server-sk-baidu-ocr", api_key_ocr_s)
            ss.s("ocr-baidu-token", access_token)
            ss.s("ocr-baidu-token-expires-date", expires_in_date)
            return True, "success"
        return False, access_token
