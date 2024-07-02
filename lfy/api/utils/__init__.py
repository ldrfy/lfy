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
