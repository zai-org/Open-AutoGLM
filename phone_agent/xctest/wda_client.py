"""Lightweight HTTP client for WebDriverAgent (WDA)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


class WDAError(RuntimeError):
    """Base error for WDA client failures."""


@dataclass
class WDAHTTPError(WDAError):
    """HTTP error response from WDA."""

    method: str
    url: str
    status_code: int
    body: str

    def __str__(self) -> str:
        body = self.body.strip()
        if len(body) > 500:
            body = body[:500] + "…"
        return f"WDA {self.method} {self.url} -> {self.status_code}: {body}"


class WDAClient:
    """
    Minimal client for calling WebDriverAgent endpoints.

    WDA mixes standard WebDriver session endpoints (e.g. /session/{id}/actions)
    and WDA-specific endpoints (e.g. /wda/activeAppInfo). This client supports
    both patterns and centralizes timeout/error handling.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8100",
        *,
        session_id: str | None = None,
        timeout: float = 10.0,
        verify_tls: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout
        self.verify_tls = verify_tls

        try:
            import requests  # type: ignore
        except ImportError as e:
            raise ImportError(
                "requests library required for iOS/WDA support. Install: pip install requests"
            ) from e

        self._session = requests.Session()

    def with_session(self, session_id: str | None) -> "WDAClient":
        """Return a shallow copy with a different session_id, reusing HTTP session."""
        clone = WDAClient(
            self.base_url,
            session_id=session_id,
            timeout=self.timeout,
            verify_tls=self.verify_tls,
        )
        clone._session = self._session
        return clone

    def _build_url(self, endpoint: str, use_session: bool | None) -> str:
        endpoint = endpoint.lstrip("/")
        if use_session is False:
            return f"{self.base_url}/{endpoint}"

        if self.session_id:
            return f"{self.base_url}/session/{self.session_id}/{endpoint}"

        return f"{self.base_url}/{endpoint}"

    def request(
        self,
        method: Literal["GET", "POST", "DELETE"],
        endpoint: str,
        *,
        use_session: bool | None = None,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        allow_status: tuple[int, ...] = (200, 201),
    ) -> Any:
        url = self._build_url(endpoint, use_session)
        try:
            response = self._session.request(
                method,
                url,
                json=json,
                params=params,
                timeout=timeout or self.timeout,
                verify=self.verify_tls,
            )
        except Exception as e:
            raise WDAError(f"WDA {method} {url} failed: {e}") from e

        if response.status_code not in allow_status:
            raise WDAHTTPError(
                method=method,
                url=url,
                status_code=response.status_code,
                body=response.text,
            )

        if not response.content:
            return None

        try:
            return response.json()
        except Exception:
            return response.text

    def get(
        self,
        endpoint: str,
        *,
        use_session: bool | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        allow_status: tuple[int, ...] = (200,),
    ) -> Any:
        return self.request(
            "GET",
            endpoint,
            use_session=use_session,
            params=params,
            timeout=timeout,
            allow_status=allow_status,
        )

    def post(
        self,
        endpoint: str,
        *,
        use_session: bool | None = None,
        json: Any | None = None,
        timeout: float | None = None,
        allow_status: tuple[int, ...] = (200, 201),
    ) -> Any:
        return self.request(
            "POST",
            endpoint,
            use_session=use_session,
            json=json,
            timeout=timeout,
            allow_status=allow_status,
        )

    def delete(
        self,
        endpoint: str,
        *,
        use_session: bool | None = None,
        timeout: float | None = None,
        allow_status: tuple[int, ...] = (200, 204),
    ) -> Any:
        return self.request(
            "DELETE",
            endpoint,
            use_session=use_session,
            timeout=timeout,
            allow_status=allow_status,
        )

