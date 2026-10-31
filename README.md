# Mailhuset SDKs

Official client libraries for the [Mailhuset](https://mailhuset.com) transactional
email API. All four cover the same surface: `emails` (send / batch / get / list),
`suppressions`, `domains`, and `templates`.

| Language | Package | Install |
| --- | --- | --- |
| Node | [`node/`](node) | `npm install mailhuset` |
| Python | [`python/`](python) | `pip install mailhuset` |
| PHP | [`php/`](php) | `composer require dalysie/mailhuset` |
| Go | [`go/`](go) | `go get github.com/DalysieGroup/mailhuset-sdks/go@latest` |

## Publishing

Each package releases from its own git tag:

- `node-v0.2.0` → publishes the Node package to npm (needs the `NPM_TOKEN` repo secret).
- `py-v0.2.0` → publishes the Python package to PyPI (needs the `PYPI_API_TOKEN` repo secret).
- `go/v0.2.0` → makes the Go module resolvable via the Go proxy. No secret or CI
  needed — Go tooling reads the tag directly (the `go/` prefix is required for a
  module in a subdirectory).
- **PHP** is published to Packagist as [`dalysie/mailhuset`](https://packagist.org/packages/dalysie/mailhuset).
  Packagist reads a package from a repo root, so the PHP SDK lives on a read-only
  split mirror, [`DalysieGroup/mailhuset-php`](https://github.com/DalysieGroup/mailhuset-php).
  To cut a new PHP release from this monorepo:
  ```bash
  git subtree split --prefix=php -b php-split
  git push https://github.com/DalysieGroup/mailhuset-php.git php-split:main
  git push https://github.com/DalysieGroup/mailhuset-php.git php-split:refs/tags/vX.Y.Z
  git branch -D php-split
  ```
  Then click **Update** on the Packagist package page (or set up its GitHub Hook to
  auto-update on push).

The Node/Python workflows skip cleanly when their token is unset, so the repo stays
green until you are ready to publish.
