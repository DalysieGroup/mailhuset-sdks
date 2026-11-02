# Mailhuset — PHP

Official PHP client for the [Mailhuset](https://mailhuset.com) transactional email API.
Requires PHP 8.1+ with the `curl` and `json` extensions. No runtime dependencies.

## Install

```bash
composer require dalysie/mailhuset
```

## Usage

```php
<?php
require 'vendor/autoload.php';

$mh = new \Mailhuset\Mailhuset('mh_live_…');

$result = $mh->emails->send([
    'from'    => 'you@yourdomain.com',
    'to'      => 'user@example.com',
    'subject' => 'Verify your email',
    'html'    => '<p>Welcome</p>',
]);

echo $result['id'], ' ', $result['status'], PHP_EOL;
```

`to`, `cc`, `bcc`, and `replyTo` accept a single address or a list. Optional
fields (`text`, `headers`, `tags`, `stream`, `templateAlias`, `templateModel`,
`attachments`, `sendAt`, `idempotencyKey`, `tracking`) may be omitted.

Turn on open and click tracking for one message with
`'tracking' => ['opens' => true, 'clicks' => true]`. Broadcasts track opens and clicks by default; transactional mail is not tracked
unless you ask. Opens are a rough guide (Apple Mail preloads images), and click
tracking rewrites links, so leave it off for password resets and one-time links.

## Resources

- `$mh->emails->send()`, `->batch()`, `->get()`, `->list()`
- `$mh->suppressions->list()`, `->add()`, `->remove()`
- `$mh->domains->list()`, `->create()`, `->get()`, `->verify()`, `->remove()`
- `$mh->templates->list()`, `->create()`, `->get()`, `->update()`, `->remove()`

## Errors

A non-2xx response throws `\Mailhuset\MailhusetException` with `$status` and an
optional `$errorCode`:

```php
try {
    $mh->emails->send([...]);
} catch (\Mailhuset\MailhusetException $e) {
    error_log("mailhuset {$e->status}: {$e->getMessage()}");
}
```

## Options

```php
$mh = new \Mailhuset\Mailhuset('mh_live_…', [
    'baseUrl' => 'https://api.mailhuset.com/v1',
]);
```
