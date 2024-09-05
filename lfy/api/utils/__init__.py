def s2ks(s):
    """_summary_

    Args:
        s (_type_): _description_

    Returns:
        _type_: _description_
    """
    if "|" not in s:
        return None, None

    [app_id, secret_key] = s.split("|")
    a = app_id.strip()
    b = secret_key.strip()
    return a, b


def is_text(cf):
    """cb.get_formats()

    Args:
        cf (GdkContentFormats): Gdk.Clipboard.get_formats

    Returns:
        _type_: _description_
    """
    if cf.contain_mime_type("text/plain") \
        or cf.contain_mime_type("text/html") \
            or cf.contain_mime_type("text/plain;charset=utf-8"):
        return True
    return False
