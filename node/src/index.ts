/**
 * Mailhuset — the official Node client for the Mailhuset transactional email API.
 *
 *   import { Mailhuset } from "mailhuset";
 *   const mh = new Mailhuset("mh_live_…");
 *   await mh.emails.send({
 *     from: "you@yourdomain.com",
 *     to: "user@example.com",
 *     subject: "Verify your email",
 *     html: "<p>Welcome</p>",
 *   });
 */

const DEFAULT_BASE_URL = "https://api.mailhuset.com/v1";

export interface MailhusetOptions {
  /** Override the API base URL. Defaults to https://api.mailhuset.com/v1 */
  baseUrl?: string;
  /** Provide a fetch implementation (defaults to the global fetch). */
  fetch?: typeof fetch;
}

/** A file attachment. `content` is base64-encoded. */
export interface Attachment {
  filename: string;
  content: string;
  contentType: string;
}

export interface SendParams {
  /** Sender, e.g. `Acme <you@yourdomain.com>`. The domain must be verified. */
  from: string;
  to: string | string[];
  subject?: string;
  html?: string;
  text?: string;
  cc?: string | string[];
  bcc?: string | string[];
  replyTo?: string | string[];
  /** Extra headers, e.g. `{ "List-Unsubscribe": "<mailto:…>" }`. */
  headers?: Record<string, string>;
  /** Provider tags for your own reporting. */
  tags?: Record<string, string>;
  /** Message stream / configuration set. Defaults to `transactional`. */
  stream?: string;
  /** Render a stored template; `subject`/`html`/`text` override the result. */
  templateAlias?: string;
  templateModel?: Record<string, unknown>;
  /** File attachments (base64). Combined size is capped at ~10 MB. */
  attachments?: Attachment[];
  /** ISO-8601 time to send at (delayed send). Must be within 30 days. */
  sendAt?: string;
  /** A repeat call with the same key returns the original message. */
  idempotencyKey?: string;
}

export interface SendResult {
  id: string;
  status: string;
}

/** One result in a batch send: the accepted message, or a per-item error. */
export interface BatchItemResult {
  id?: string;
  status: string;
  error?: string;
}

export interface Message {
  id: string;
  to: string[];
  subject: string;
  status: string;
  provider: string | null;
  providerMessageId: string | null;
  createdAt: string;
  sentAt: string | null;
}

export interface MessageList {
  items: Message[];
  total: number;
  limit: number;
  offset: number;
}

/** Thrown when the API returns a non-2xx response. */
export class MailhusetError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "MailhusetError";
    this.status = status;
    this.code = code;
  }
}

function toArray(value?: string | string[]): string[] | undefined {
  if (value == null) return undefined;
  return Array.isArray(value) ? value : [value];
}

export class Mailhuset {
  readonly #apiKey: string;
  readonly #baseUrl: string;
  readonly #fetch: typeof fetch;

  constructor(apiKey: string, options: MailhusetOptions = {}) {
    if (!apiKey) throw new Error("Mailhuset: an API key is required");
    this.#apiKey = apiKey;
    this.#baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    const fetchImpl = options.fetch ?? globalThis.fetch;
    if (!fetchImpl) {
      throw new Error(
        "Mailhuset: no global fetch available. Use Node 18+ or pass options.fetch.",
      );
    }
    this.#fetch = fetchImpl;
  }

  async #request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const res = await this.#fetch(`${this.#baseUrl}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${this.#apiKey}`,
        "Content-Type": "application/json",
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });

    const raw = await res.text();
    const data = raw ? (JSON.parse(raw) as Record<string, unknown>) : {};

    if (!res.ok) {
      const message = typeof data.message === "string" ? data.message : res.statusText;
      const code = typeof data.error === "string" ? data.error : undefined;
      throw new MailhusetError(res.status, message, code);
    }
    return data as T;
  }

  #sendBody(params: SendParams): Record<string, unknown> {
    return {
      from: params.from,
      to: toArray(params.to),
      cc: toArray(params.cc),
      bcc: toArray(params.bcc),
      replyTo: toArray(params.replyTo),
      subject: params.subject,
      html: params.html,
      text: params.text,
      headers: params.headers,
      tags: params.tags,
      stream: params.stream,
      templateAlias: params.templateAlias,
      templateModel: params.templateModel,
      attachments: params.attachments,
      sendAt: params.sendAt,
      idempotencyKey: params.idempotencyKey,
    };
  }

  readonly emails = {
    /** Send a transactional email. Returns the queued message id. */
    send: (params: SendParams): Promise<SendResult> =>
      this.#request<SendResult>("POST", "/email", this.#sendBody(params)),

    /** Send up to 500 messages in one call. Returns a result per message. */
    batch: (messages: SendParams[]): Promise<BatchItemResult[]> =>
      this.#request<BatchItemResult[]>("POST", "/email/batch", {
        messages: messages.map((m) => this.#sendBody(m)),
      }),

    /** Fetch one message and its event history. */
    get: (id: string): Promise<Message> =>
      this.#request<Message>("GET", `/email/${encodeURIComponent(id)}`),

    /** List recent messages, newest first. */
    list: (opts: { limit?: number; offset?: number } = {}): Promise<MessageList> => {
      const query = new URLSearchParams();
      if (opts.limit != null) query.set("limit", String(opts.limit));
      if (opts.offset != null) query.set("offset", String(opts.offset));
      const qs = query.toString();
      return this.#request<MessageList>("GET", `/email${qs ? `?${qs}` : ""}`);
    },
  };

  /** Suppression list — recipients that will be skipped on send. */
  readonly suppressions = {
    list: (): Promise<unknown> => this.#request("GET", "/suppressions"),
    add: (address: string, reason?: string): Promise<unknown> =>
      this.#request("POST", "/suppressions", { address, reason }),
    remove: (address: string): Promise<unknown> =>
      this.#request("DELETE", `/suppressions/${encodeURIComponent(address)}`),
  };

  /** Sending domains — add, inspect DNS/DKIM, verify. */
  readonly domains = {
    list: (): Promise<unknown> => this.#request("GET", "/domains"),
    create: (domain: string): Promise<unknown> => this.#request("POST", "/domains", { domain }),
    get: (domain: string): Promise<unknown> =>
      this.#request("GET", `/domains/${encodeURIComponent(domain)}`),
    verify: (domain: string): Promise<unknown> =>
      this.#request("POST", `/domains/${encodeURIComponent(domain)}/verify`),
    remove: (domain: string): Promise<unknown> =>
      this.#request("DELETE", `/domains/${encodeURIComponent(domain)}`),
  };

  /** Stored templates. */
  readonly templates = {
    list: (): Promise<unknown> => this.#request("GET", "/templates"),
    create: (body: Record<string, unknown>): Promise<unknown> =>
      this.#request("POST", "/templates", body),
    get: (id: string): Promise<unknown> =>
      this.#request("GET", `/templates/${encodeURIComponent(id)}`),
    update: (id: string, body: Record<string, unknown>): Promise<unknown> =>
      this.#request("PUT", `/templates/${encodeURIComponent(id)}`, body),
    remove: (id: string): Promise<unknown> =>
      this.#request("DELETE", `/templates/${encodeURIComponent(id)}`),
  };
}

export default Mailhuset;
