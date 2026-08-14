"""Official Python client for the Mailhuset transactional email API.

    from mailhuset import Mailhuset

    mh = Mailhuset("mh_live_…")
    mh.emails.send(
        sender="you@yourdomain.com",
        to="user@example.com",
        subject="Verify your email",
        html="<p>Welcome</p>",
    )

Depends only on the standard library.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence, Union

__version__ = "0.1.0"
__all__ = ["Mailhuset", "MailhusetError"]

DEFAULT_BASE_URL = "https://api.mailhuset.com/v1"

Recipients = Union[str, Sequence[str]]


class MailhusetError(Exception):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status: int, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


def _as_list(value: Optional[Recipients]) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    return list(value)


class _Emails:
    def __init__(self, client: "Mailhuset") -> None:
        self._client = client

    def send(
        self,
        *,
        sender: str,
        to: Recipients,
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        cc: Optional[Recipients] = None,
        bcc: Optional[Recipients] = None,
        reply_to: Optional[Recipients] = None,
        headers: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        stream: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a transactional email. Returns ``{"id": ..., "status": ...}``.

        ``sender`` is the from address; its domain must be verified.
        """
        body = {
            "from": sender,
            "to": _as_list(to),
            "cc": _as_list(cc),
            "bcc": _as_list(bcc),
            "replyTo": _as_list(reply_to),
            "subject": subject,
            "html": html,
            "text": text,
            "headers": headers,
            "tags": tags,
            "stream": stream,
            "idempotencyKey": idempotency_key,
        }
        return self._client._request("POST", "/email", {k: v for k, v in body.items() if v is not None})

    def get(self, message_id: str) -> Dict[str, Any]:
        """Fetch one message and its event history."""
        return self._client._request("GET", f"/email/{message_id}")

    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """List recent messages, newest first."""
        params = []
        if limit is not None:
            params.append(f"limit={limit}")
        if offset is not None:
            params.append(f"offset={offset}")
        query = ("?" + "&".join(params)) if params else ""
        return self._client._request("GET", f"/email{query}")


class Mailhuset:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL) -> None:
        if not api_key:
            raise ValueError("Mailhuset: an API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.emails = _Emails(self)

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> Dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"mailhuset-python/{__version__}",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                payload = json.loads(raw)
            except ValueError:
                payload = {}
            raise MailhusetError(
                exc.code,
                payload.get("message", exc.reason or "request failed"),
                payload.get("error"),
            ) from None
