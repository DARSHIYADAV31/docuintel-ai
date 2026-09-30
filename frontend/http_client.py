import requests

TIMEOUT = 15  # seconds; every call has an explicit limit so the UI never hangs


class ApiError(Exception):
    """A failure the user can be shown as-is."""


def _detail(resp: requests.Response) -> str:
    try:
        detail = resp.json().get("detail")
    except ValueError:
        detail = None
    return detail if isinstance(detail, str) else f"Request failed ({resp.status_code})"


class HttpClient:
    """Adds the bearer token, and transparently refreshes it once on a 401."""

    def __init__(self, base_url: str, tokens: dict):
        self.base_url, self.tokens = base_url.rstrip("/"), tokens

    def store_tokens(self, data: dict) -> None:
        self.tokens["access"] = data["access_token"]
        self.tokens["refresh"] = data["refresh_token"]

    def _send(self, method: str, path: str, timeout: int, **kwargs):
        headers = {"Authorization": f"Bearer {self.tokens['access']}"} \
            if self.tokens.get("access") else {}
        try:
            return requests.request(method, self.base_url + path, headers=headers,
                                    timeout=timeout, **kwargs)
        except requests.Timeout:
            raise ApiError("The server took too long to respond")
        except requests.RequestException:
            raise ApiError("Cannot reach the server")

    def _refresh(self) -> bool:
        try:
            resp = requests.post(self.base_url + "/auth/refresh", timeout=TIMEOUT,
                                 json={"refresh_token": self.tokens["refresh"]})
        except requests.RequestException:
            return False
        if not resp.ok:
            self.tokens.clear()  # session expired: force a fresh login
            return False
        self.store_tokens(resp.json())
        return True

    def request(self, method: str, path: str, timeout: int = TIMEOUT, **kwargs):
        resp = self._send(method, path, timeout, **kwargs)
        if resp.status_code == 401 and self.tokens.get("refresh") and self._refresh():
            resp = self._send(method, path, timeout, **kwargs)
        if not resp.ok:
            raise ApiError(_detail(resp))
        return resp.json()
