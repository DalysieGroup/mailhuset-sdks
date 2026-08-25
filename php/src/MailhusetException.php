<?php

declare(strict_types=1);

namespace Mailhuset;

/** Thrown when the API returns a non-2xx response (or the request fails). */
final class MailhusetException extends \Exception
{
    public function __construct(
        public readonly int $status,
        string $message,
        public readonly ?string $errorCode = null,
    ) {
        parent::__construct($message, $status);
    }
}
