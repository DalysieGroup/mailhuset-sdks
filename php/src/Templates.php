<?php

declare(strict_types=1);

namespace Mailhuset;

/** Stored templates. */
final class Templates
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /** @return array<mixed> */
    public function list(): array
    {
        return $this->http->request('GET', '/templates');
    }

    /**
     * @param  array<string,mixed>  $body
     * @return array<mixed>
     */
    public function create(array $body): array
    {
        return $this->http->request('POST', '/templates', $body);
    }

    /** @return array<mixed> */
    public function get(string $id): array
    {
        return $this->http->request('GET', '/templates/' . rawurlencode($id));
    }

    /**
     * @param  array<string,mixed>  $body
     * @return array<mixed>
     */
    public function update(string $id, array $body): array
    {
        return $this->http->request('PUT', '/templates/' . rawurlencode($id), $body);
    }

    /** @return array<mixed> */
    public function remove(string $id): array
    {
        return $this->http->request('DELETE', '/templates/' . rawurlencode($id));
    }
}
