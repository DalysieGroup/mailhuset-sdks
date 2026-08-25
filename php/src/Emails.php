<?php

declare(strict_types=1);

namespace Mailhuset;

/** Send and read email. */
final class Emails
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * Send a transactional email. Returns the queued message (id, status).
     *
     * @param  array<string,mixed>  $params  from (required), to (required, string|list),
     *   subject, html, text, cc, bcc, replyTo, headers, tags, stream, templateAlias,
     *   templateModel, attachments, sendAt, idempotencyKey
     * @return array<mixed>
     */
    public function send(array $params): array
    {
        return $this->http->request('POST', '/email', $this->body($params));
    }

    /**
     * Send up to 500 messages in one call. Returns a result per message.
     *
     * @param  list<array<string,mixed>>  $messages
     * @return array<mixed>
     */
    public function batch(array $messages): array
    {
        return $this->http->request('POST', '/email/batch', [
            'messages' => array_map(fn (array $m): array => $this->body($m), $messages),
        ]);
    }

    /** @return array<mixed> */
    public function get(string $id): array
    {
        return $this->http->request('GET', '/email/' . rawurlencode($id));
    }

    /**
     * @param  array{limit?:int,offset?:int}  $opts
     * @return array<mixed>
     */
    public function list(array $opts = []): array
    {
        $query = [];
        if (isset($opts['limit'])) {
            $query['limit'] = $opts['limit'];
        }
        if (isset($opts['offset'])) {
            $query['offset'] = $opts['offset'];
        }
        $qs = $query !== [] ? '?' . http_build_query($query) : '';

        return $this->http->request('GET', '/email' . $qs);
    }

    /**
     * @param  array<string,mixed>  $p
     * @return array<string,mixed>
     */
    private function body(array $p): array
    {
        $arr = static fn (mixed $v): mixed => $v === null ? null : (is_array($v) ? $v : [$v]);

        $body = [
            'from' => $p['from'] ?? null,
            'to' => $arr($p['to'] ?? null),
            'cc' => $arr($p['cc'] ?? null),
            'bcc' => $arr($p['bcc'] ?? null),
            'replyTo' => $arr($p['replyTo'] ?? null),
            'subject' => $p['subject'] ?? null,
            'html' => $p['html'] ?? null,
            'text' => $p['text'] ?? null,
            'headers' => $p['headers'] ?? null,
            'tags' => $p['tags'] ?? null,
            'stream' => $p['stream'] ?? null,
            'templateAlias' => $p['templateAlias'] ?? null,
            'templateModel' => $p['templateModel'] ?? null,
            'attachments' => $p['attachments'] ?? null,
            'sendAt' => $p['sendAt'] ?? null,
            'idempotencyKey' => $p['idempotencyKey'] ?? null,
        ];

        // Drop nulls so optional fields are omitted (keep falsy values like "").
        return array_filter($body, static fn (mixed $v): bool => $v !== null);
    }
}
