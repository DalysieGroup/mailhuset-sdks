<?php

declare(strict_types=1);

namespace Mailhuset;

/** Internal HTTP transport (curl). Not part of the public API. */
final class HttpClient
{
    public function __construct(
        private readonly string $apiKey,
        private readonly string $baseUrl,
    ) {
    }

    /**
     * @param  array<string,mixed>|null  $body
     * @return array<mixed>
     */
    public function request(string $method, string $path, ?array $body = null): array
    {
        $ch = curl_init($this->baseUrl . $path);
        $headers = ['Authorization: Bearer ' . $this->apiKey];

        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);

        if ($body !== null) {
            $headers[] = 'Content-Type: application/json';
            curl_setopt(
                $ch,
                CURLOPT_POSTFIELDS,
                json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
            );
        }
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

        $raw = curl_exec($ch);
        if ($raw === false) {
            $err = curl_error($ch);
            curl_close($ch);
            throw new MailhusetException(0, 'Mailhuset: request failed: ' . $err);
        }
        $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        curl_close($ch);

        $data = $raw !== '' ? json_decode((string) $raw, true) : [];
        if (!is_array($data)) {
            $data = [];
        }

        if ($status < 200 || $status >= 300) {
            $message = is_string($data['message'] ?? null) ? $data['message'] : ('HTTP ' . $status);
            $code = is_string($data['error'] ?? null) ? $data['error'] : null;
            throw new MailhusetException($status, $message, $code);
        }

        return $data;
    }
}
