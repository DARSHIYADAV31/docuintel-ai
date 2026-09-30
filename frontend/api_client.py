from http_client import HttpClient

UPLOAD_TIMEOUT = 60
ASK_TIMEOUT = 90  # answering can involve a model fallback


class ApiClient(HttpClient):
    def login(self, username: str, password: str) -> None:
        creds = {"username": username, "password": password}
        self.store_tokens(self.request("POST", "/auth/login", json=creds))

    def register(self, username: str, password: str) -> None:
        creds = {"username": username, "password": password}
        self.store_tokens(self.request("POST", "/auth/register", json=creds))

    def dashboard(self) -> dict:
        return self.request("GET", "/dashboard")

    def list_documents(self) -> list[dict]:
        return self.request("GET", "/documents")

    def get_document(self, document_id: int, reveal: bool = False) -> dict:
        params = {"reveal_sensitive": str(reveal).lower()}
        return self.request("GET", f"/documents/{document_id}", params=params)

    def upload(self, name: str, data: bytes, mime: str, handwritten: bool) -> dict:
        return self.request("POST", "/documents", timeout=UPLOAD_TIMEOUT,
                            files={"file": (name, data, mime)},
                            data={"handwritten": str(handwritten).lower()})

    def ask(self, document_id: int, question: str) -> dict:
        return self.request("POST", f"/documents/{document_id}/ask",
                            timeout=ASK_TIMEOUT, json={"question": question})
