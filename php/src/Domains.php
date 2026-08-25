<?php

declare(strict_types=1);

namespace Mailhuset;

/** Sending domains — add, inspect DNS/DKIM, verify. */
final class Domains
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /** @return array<mixed> */
    public function list(): array
    {
        return $this->http->request('GET', '/domains');
    }

    /** @return array<mixed> */
    public function create(string $domain): array
    {
        return $this->http->request('POST', '/domains', ['domain' => $domain]);
    }

    /** @return array<mixed> */
    public function get(string $domain): array
    {
        return $this->http->request('GET', '/domains/' . rawurlencode($domain));
    }

    /** @return array<mixed> */
    public function verify(string $domain): array
    {
        return $this->http->request('POST', '/domains/' . rawurlencode($domain) . '/verify');
    }

    /** @return array<mixed> */
    public function remove(string $domain): array
    {
        return $this->http->request('DELETE', '/domains/' . rawurlencode($domain));
    }
}
