<?php

declare(strict_types=1);

namespace Mailhuset;

/**
 * Official PHP client for the Mailhuset transactional email API.
 *
 *   $mh = new \Mailhuset\Mailhuset('mh_live_…');
 *   $mh->emails->send([
 *       'from'    => 'you@yourdomain.com',
 *       'to'      => 'user@example.com',
 *       'subject' => 'Verify your email',
 *       'html'    => '<p>Welcome</p>',
 *   ]);
 */
final class Mailhuset
{
    public readonly Emails $emails;
    public readonly Suppressions $suppressions;
    public readonly Domains $domains;
    public readonly Templates $templates;

    /** @param array{baseUrl?:string} $options */
    public function __construct(string $apiKey, array $options = [])
    {
        if ($apiKey === '') {
            throw new \InvalidArgumentException('Mailhuset: an API key is required');
        }
        $baseUrl = rtrim($options['baseUrl'] ?? 'https://api.mailhuset.com/v1', '/');
        $http = new HttpClient($apiKey, $baseUrl);

        $this->emails = new Emails($http);
        $this->suppressions = new Suppressions($http);
        $this->domains = new Domains($http);
        $this->templates = new Templates($http);
    }
}
