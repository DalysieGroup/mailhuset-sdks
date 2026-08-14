# Mailhuset SDKs

Official client libraries for the [Mailhuset](https://mailhuset.com) transactional
email API.

| Language | Package | Install |
| --- | --- | --- |
| Node | [`node/`](node) | `npm install mailhuset` |
| Python | [`python/`](python) | `pip install mailhuset` |

## Publishing

Each package publishes from its own git tag:

- `node-v0.1.0` → publishes the Node package (needs the `NPM_TOKEN` repo secret)
- `py-v0.1.0` → publishes the Python package (needs the `PYPI_API_TOKEN` repo secret)

The workflows skip cleanly if the token is not set, so the repo stays green until
you are ready to publish.
