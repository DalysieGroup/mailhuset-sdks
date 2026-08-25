<?php

declare(strict_types=1);

namespace Mailhuset;

/** Suppression list — recipients skipped on send. */
final class Suppressions
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /** @return array<mixed> */
    public function list(): array
    {
        return $this->http->request('GET', '/suppressions');
    }

    /** @return array<mixed> */
    public function add(string $address, ?string $reason = null): array
    {
        $body = ['address' => $address];
        if ($reason !== null) {
            $body['reason'] = $reason;
        }

        return $this->http->request('POST', '/suppressions', $body);
    }

    /** @return array<mixed> */
    public function remove(string $address): array
    {
        return $this->http->request('DELETE', '/suppressions/' . rawurlencode($address));
    }
}
