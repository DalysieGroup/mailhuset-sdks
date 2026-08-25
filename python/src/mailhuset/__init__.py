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

__version__ = "0.2.0"
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


def _send_body(
    *,
    sender: str,
    to: Recipients,
    subject: Optional[str] = None,
    html: Optional[str] = None,
    text: Optional[str] = None,
    cc: Optional[Recipients] = None,
    bcc: Optional[Recipients] = None,
    reply_to: Optional[Recipients] = None,
    headers: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, str]] = None,
    stream: Optional[str] = None,
    template_alias: Optional[str] = None,
    template_model: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
    send_at: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the JSON body for a send, dropping unset (None) fields."""
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
        "templateAlias": template_alias,
        "templateModel": template_model,
        "attachments": attachments,
        "sendAt": send_at,
        "idempotencyKey": idempotency_key,
    }
    return {k: v for k, v in body.items() if v is not None}


class _Emails:
    def __init__(self, client: "Mailhuset") -> None:
        self._client = client

    def send(
        self,
        *,
        sender: str,
        to: Recipients,
        subject: Optional[str] = None,
        html: Optional[str] = None,
        text: Optional[str] = None,
        cc: Optional[Recipients] = None,
        bcc: Optional[Recipients] = None,
        reply_to: Optional[Recipients] = None,
        headers: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        stream: Optional[str] = None,
        template_alias: Optional[str] = None,
        template_model: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        send_at: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a transactional email. Returns ``{"id": ..., "status": ...}``.

        ``sender`` is the from address; its domain must be verified. ``attachments``
        are dicts of ``{"filename", "content" (base64), "contentType"}``. ``send_at``
        is an ISO-8601 time for delayed send (within 30 days).
        """
        return self._client._request("POST", "/email", _send_body(
            sender=sender, to=to, subject=subject, html=html, text=text, cc=cc, bcc=bcc,
            reply_to=reply_to, headers=headers, tags=tags, stream=stream,
            template_alias=template_alias, template_model=template_model,
            attachments=attachments, send_at=send_at, idempotency_key=idempotency_key,
        ))

    def batch(self, messages: Sequence[Dict[str, Any]]) -> Any:
        """Send up to 500 messages in one call. Each item is the same kwargs dict
        you would pass to ``send`` (using snake_case keys). Returns a result per
        message (``{"id", "status"}`` or ``{"status": "error", "error": ...}``)."""
        return self._client._request(
            "POST", "/email/batch", {"messages": [_send_body(**m) for m in messages]}
        )

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


class _Suppressions:
    def __init__(self, client: "Mailhuset") -> None:
        self._client = client

    def list(self) -> Any:
        return self._client._request("GET", "/suppressions")

    def add(self, address: str, reason: Optional[str] = None) -> Any:
        body = {"address": address}
        if reason is not None:
            body["reason"] = reason
        return self._client._request("POST", "/suppressions", body)

    def remove(self, address: str) -> Any:
        return self._client._request("DELETE", f"/suppressions/{address}")


class _Domains:
    def __init__(self, client: "Mailhuset") -> None:
        self._client = client

    def list(self) -> Any:
        return self._client._request("GET", "/domains")

    def create(self, domain: str) -> Any:
        return self._client._request("POST", "/domains", {"domain": domain})

    def get(self, domain: str) -> Any:
        return self._client._request("GET", f"/domains/{domain}")

    def verify(self, domain: str) -> Any:
        return self._client._request("POST", f"/domains/{domain}/verify")

    def remove(self, domain: str) -> Any:
        return self._client._request("DELETE", f"/domains/{domain}")


class _Templates:
    def __init__(self, client: "Mailhuset") -> None:
        self._client = client

    def list(self) -> Any:
        return self._client._request("GET", "/templates")

    def create(self, **body: Any) -> Any:
        return self._client._request("POST", "/templates", body)

    def get(self, template_id: str) -> Any:
        return self._client._request("GET", f"/templates/{template_id}")

    def update(self, template_id: str, **body: Any) -> Any:
        return self._client._request("PUT", f"/templates/{template_id}", body)

    def remove(self, template_id: str) -> Any:
        return self._client._request("DELETE", f"/templates/{template_id}")


class Mailhuset:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL) -> None:
        if not api_key:
            raise ValueError("Mailhuset: an API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.emails = _Emails(self)
        self.suppressions = _Suppressions(self)
        self.domains = _Domains(self)
        self.templates = _Templates(self)

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> Any:
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
