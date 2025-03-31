import requests


async def ping_url(url: str, timeout: int = 3):
    """
    :param url: url to ping
    :param timeout: optional timeout, default is 3 seconds
    :return: is_ok: bool, status_code: int
    """
    res = requests.get(url, timeout=timeout)
    return res.ok, res.status_code
