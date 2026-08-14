# mailhuset

Official Node client for the [Mailhuset](https://mailhuset.com) transactional email API.

## Install

```bash
npm install mailhuset
```

## Send an email

```js
import { Mailhuset } from "mailhuset";

const mh = new Mailhuset(process.env.MAILHUSET_API_KEY);

await mh.emails.send({
  from: "you@yourdomain.com",
  to: "user@example.com",
  subject: "Verify your email",
  html: "<p>Welcome 👋</p>",
});
```

`send` returns `{ id, status }`. You can also:

```js
const message = await mh.emails.get(id);
const { items } = await mh.emails.list({ limit: 20 });
```

Any non-2xx response throws a `MailhusetError` with `.status` and `.code`.

Requires Node 18 or newer (for the global `fetch`). Point it at another host with
`new Mailhuset(key, { baseUrl: "https://api.mailhuset.com/v1" })`.
