import base64
import hashlib
import json
import random
import re
import time
import urllib
from gettext import gettext as _

import requests

from lfy.api.server import TIME_OUT

try:
    from cryptography.hazmat.backends import openssl
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms,
                                                        modes)
except ModuleNotFoundError as e0:
    print(_("python no lib: cryptography, please try: \n\n pip install cryptography"))

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57",
    "Origin": "https://fanyi.youdao.com",
    "Referer": "https://fanyi.youdao.com/",
})
FIXED_VALUE = None
INTERFACE_SELECT = 1


def translate_text(text, lang_to="", lang_from="auto"):
    """_summary_

    Args:
        text (_type_): _description_
        lang_to (str, optional): _description_. Defaults to "".
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    global INTERFACE_SELECT
    if INTERFACE_SELECT == 1:
        res = translate_interface_1(text, lang_from, lang_to)
        if res is None:
            INTERFACE_SELECT += 1
            return _("youdao interface is error, auto change interface. please try again")
    elif INTERFACE_SELECT == 2:
        res = translate_interface_2(text, lang_from, lang_to)
    return res


def translate_interface_2(text, from_lang="auto", to_lang=""):
    """_summary_

    Args:
        text (_type_): _description_
        from_lang (str, optional): _description_. Defaults to "auto".
        to_lang (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    url = "http://fanyi.youdao.com/translate?&doctype=json&type=%s&i=%s"
    url = url % (from_lang + "2" + to_lang, urllib.parse.quote(text))
    error_msg = _("something error, try other translate engine?")

    request = requests.get(url, timeout=TIME_OUT)
    if request.status_code == 200:
        result = request.json()
        if "errorCode" in result and result["errorCode"] != 0:
            return f"{error_msg}\n\n{result}"
        else:
            s1 = ""
            for line in result["translateResult"]:
                for sentence in line:
                    s1 += sentence["tgt"]
                s1 += '\n'
            return s1
    else:
        return f"{error_msg}\n\n{request.content}"


def translate_interface_1(text, from_lang="auto", to_lang=""):
    """_summary_

    Args:
        text (_type_): _description_
        from_lang (str, optional): _description_. Defaults to "auto".
        to_lang (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    url = "https://dict.youdao.com/webtranslate"
    sk = get_translate_secret_key()
    if sk is None:
        return _("can not get secret key\n\ntry other translate engine?")
    _time = int(time.time() * 1000)
    res = session.post(url, data={
        "i": text,
        "from": from_lang,
        "to": to_lang,
        "domain": "0",
        "dictResult": True,
        "keyid": "webfanyi",
        "sign": sign(sk, _time),
        "client": "fanyideskweb",
        "product": "webfanyi",
        "appVersion": "1.0.0",
        "vendor": "web",
        "pointParam": "client,mysticTime,product",
        "mysticTime": _time,
        "keyfrom": "fanyi.web"
    }).text
    try:
        res = decode_translate(res)
    except Exception as e:
        error_s = _("decrypt translation message failed")
        return f"{error_s}\n\n{e}"
    print(res)
    tmp = ""
    if res['code'] != 0:
        return ""
    trans_res = res.get('translateResult', None)
    if trans_res is not None:
        for line in trans_res:
            # 有道接口数据已提供段落换行符号
            for sentence in line:
                tmp += sentence['tgt']
        tmp += '\n'
    dict_res = res.get('dictResult', None)
    if dict_res is not None and dict_res.get("ec", None) is not None:
        word = dict_res['ec']['word']
        phones = map(lambda x: f"{x[:x.find('p')]}: /{word[x]}/",
                     filter(lambda x: "phone" in x, word.keys()))
        tmp += "  ".join(phones) + '\n'
        for description in word['trs']:
            tmp += description.get("pos", "") + ' ' + \
                description.get('tran', "") + '\n'
        wfs = word.get("wfs", None)
        if wfs is not None:
            for wf in wfs:
                tmp += wf['wf']['name'] + ':' + wf['wf']['value'] + '\n'
    return tmp


def sign(key, _time=None):
    """_summary_

    Args:
        key (_type_): _description_
        _time (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    _time = _time if _time is not None else int(time.time() * 1000)
    hash_md5 = hashlib.md5()
    input_string = f"client=fanyideskweb&mysticTime={_time}&product=webfanyi&key={key}"
    hash_md5.update(input_string.encode('utf-8'))
    return hash_md5.hexdigest()


def get_fixed_value():
    """_summary_

    Returns:
        _type_: _description_
    """
    index_url = "https://fanyi.youdao.com/index.html"
    res = session.get(index_url).text
    js = re.findall(r'src="(js/app\..+?\.js)"', res)
    if len(js) != 1:
        print("get js url error")
        return None
    url = "https://fanyi.youdao.com/" + js[0]
    js = session.get(url).text
    first_sign_key = r'webfanyi-key-getter".+?a\s*=\s*"(\w+)'
    decode_key = r'decodeKey:\s*"(.+?)"'
    decode_iv = r'decodeIv:\s*"(.+?)"'
    first_sign_key = re.findall(first_sign_key, js)
    decode_key = re.findall(decode_key, js)
    decode_iv = re.findall(decode_iv, js)
    if len(first_sign_key) != 1:
        print("get secret key value error:", first_sign_key)
        return None
    if len(decode_key) != 1:
        print("get decode key value error:", decode_key)
        return None
    if len(decode_iv) != 1:
        print("get decode iv value error:", decode_iv)
        return None
    cookie_url = "https://dict.youdao.com/login/acc/query/accountinfo"
    res = session.get(cookie_url)
    session.cookies.set("OUTFOX_SEARCH_USER_ID_NCOO",
                        str(2147483647 * random.random()))
    session.cookies.set("OUTFOX_SEARCH_USER_ID", res.cookies.get_dict()[
                        'OUTFOX_SEARCH_USER_ID'])
    print(session.cookies.get_dict())
    return {
        'secret_key': first_sign_key[0],
        'decode_key': decode_key[0],
        'decode_iv': decode_iv[0]
    }


def get_translate_secret_key():
    """_summary_

    Returns:
        _type_: _description_
    """
    url = "https://dict.youdao.com/webtranslate/key"
    global FIXED_VALUE
    if FIXED_VALUE is None:
        FIXED_VALUE = get_fixed_value()
        if FIXED_VALUE is None:
            print("get fixed value failed")
            return None

    now_time = int(time.time() * 1000)
    params = {
        "keyid": "webfanyi-key-getter",
        "sign": sign(FIXED_VALUE['secret_key'], now_time),
        "client": "fanyideskweb",
        "product": "webfanyi",
        "appVersion": "1.0.0",
        "vendor": "web",
        "pointParam": "client,mysticTime,product",
        "mysticTime": now_time,
        "keyfrom": "fanyi.web"
    }
    res = session.get(url, params=params)
    translate_secret_key: dict = res.json()
    if translate_secret_key['code'] == 0:
        return translate_secret_key['data']['secretKey']
    else:
        print("get translate secret key failed", params)
        return None


def decode_translate(text):
    """_summary_

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    md5 = hashlib.md5()
    key = FIXED_VALUE['decode_key']
    md5.update(key.encode("utf-8"))
    key = md5.digest()
    md5 = hashlib.md5()
    iv = FIXED_VALUE['decode_iv']
    md5.update(iv.encode("utf-8"))
    iv = md5.digest()
    print(key, iv)
    # 创建AES CBC解密器对象并解密数据
    print("text length:", len(text))
    input_bytes = base64.urlsafe_b64decode(text)
    print("bytes length:", len(input_bytes))
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), openssl.backend)
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(input_bytes) + decryptor.finalize()
    # 使用PKCS5填充解密的数据
    padder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = padder.update(decrypted_data) + padder.finalize()
    res = unpadded_data.decode("utf-8")
    res = json.loads(res)
    return res


if __name__ == "__main__":
    s = translate_text("Flow")
    print(s)
