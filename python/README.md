# mailhuset

Official Python client for [Mailhuset](https://mailhuset.com), with no dependencies
beyond the standard library.

## Install

```bash
pip install mailhuset
```

## Send an email

```python
from mailhuset import Mailhuset

mh = Mailhuset("mh_live_…")

mh.emails.send(
    sender="you@yourdomain.com",
    to="user@example.com",
    subject="Verify your email",
    html="<p>Welcome 👋</p>",
)
```

`send` returns `{"id": ..., "status": ...}`. You can also `mh.emails.get(id)` and
`mh.emails.list(limit=20)`.

A non-2xx response raises `MailhusetError` with `.status` and `.code`. Point it at
another host with `Mailhuset(key, base_url="https://api.mailhuset.com/v1")`.
