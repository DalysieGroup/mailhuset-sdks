# Mailhuset SDKs

Official client libraries for the [Mailhuset](https://mailhuset.com) transactional
email API. All four cover the same surface: `emails` (send / batch / get / list),
`suppressions`, `domains`, and `templates`.

| Language | Package | Install |
| --- | --- | --- |
| Node | [`node/`](node) | `npm install mailhuset` |
| Python | [`python/`](python) | `pip install mailhuset` |
| PHP | [`php/`](php) | `composer require dalysie/mailhuset` |
| Go | [`go/`](go) | `go get github.com/Dalysie-ceo/mailhuset-sdks/go@latest` |

## Publishing

Each package releases from its own git tag:

- `node-v0.2.0` → publishes the Node package to npm (needs the `NPM_TOKEN` repo secret).
- `py-v0.2.0` → publishes the Python package to PyPI (needs the `PYPI_API_TOKEN` repo secret).
- `go/v0.2.0` → makes the Go module resolvable via the Go proxy. No secret or CI
  needed — Go tooling reads the tag directly (the `go/` prefix is required for a
  module in a subdirectory).
- `php-v0.2.0` → the PHP release tag. Packagist reads a package from a repository
  root, so the PHP SDK is published via a subtree-split mirror repo
  (`git subtree split --prefix=php`) registered on Packagist as `dalysie/mailhuset`,
  or by registering that split repo with a Packagist auto-update webhook. One-time
  maintainer setup, like the npm/PyPI tokens above.

The Node/Python workflows skip cleanly when their token is unset, so the repo stays
green until you are ready to publish.
