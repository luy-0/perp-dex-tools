import logging
import aiohttp
from datetime import datetime
from http.cookies import SimpleCookie

import asyncio
import requests


def get_cookie_with_expiration(
    path: str, api_key: str | None
) -> dict[str, str | float | None] | None:
    """
    Authenticates and retrieves the session cookie, its expiration time and grvt-account-id token.
    :return: The session cookie.
    """
    FN = f"get_cookie_with_expiration {path=}"
    if api_key:
        data = {}
        try:
            data = {"api_key": api_key}
            session = requests.Session()
            return_value = session.post(
                path,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            if return_value.ok:
                cookie = SimpleCookie()
                cookie.load(return_value.headers.get("Set-Cookie", ""))
                cookie_value: str = cookie["gravity"].value
                cookie_expiry: datetime = datetime.strptime(
                    cookie["gravity"]["expires"],
                    "%a, %d %b %Y %H:%M:%S %Z",
                )
                grvt_account_id: str = return_value.headers.get("X-Grvt-Account-Id", "")
                logging.info(
                    f"{FN} OK response {cookie_value=} {cookie_expiry=} {grvt_account_id=}"
                )
                return {
                    "gravity": cookie_value,
                    "expires": cookie_expiry.timestamp(),
                    "X-Grvt-Account-Id": grvt_account_id,
                }
            logging.warning(f"{FN} Invalid return_value {data=} {path=} {return_value=}")
            return None
        except Exception as e:
            logging.error(f"{FN} Error getting cookie: {e}")
            return None
    else:
        return None

if __name__ == "__main__":
    endpoint = "https://edge.grvt.io/auth/api_key/login"
    api_key = "33gRRRzfGs2zhPGi2eGzre4BaAY"
    ret = (get_cookie_with_expiration(endpoint, api_key))
    print(ret)