// Package mailhuset is the official Go client for the Mailhuset transactional
// email API.
//
//	mh, _ := mailhuset.New("mh_live_…")
//	res, err := mh.Emails.Send(ctx, mailhuset.SendParams{
//		From:    "you@yourdomain.com",
//		To:      []string{"user@example.com"},
//		Subject: "Verify your email",
//		HTML:    "<p>Welcome</p>",
//	})
package mailhuset

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

// DefaultBaseURL is the production API base. Override with WithBaseURL.
const DefaultBaseURL = "https://api.mailhuset.com/v1"

// Client is a Mailhuset API client. Create one with New.
type Client struct {
	apiKey  string
	baseURL string
	http    *http.Client

	Emails       *EmailsService
	Suppressions *SuppressionsService
	Domains      *DomainsService
	Templates    *TemplatesService
}

// Option configures a Client.
type Option func(*Client)

// WithBaseURL overrides the API base URL.
func WithBaseURL(baseURL string) Option {
	return func(c *Client) { c.baseURL = strings.TrimRight(baseURL, "/") }
}

// WithHTTPClient supplies a custom *http.Client (timeouts, transport, etc.).
func WithHTTPClient(h *http.Client) Option {
	return func(c *Client) { c.http = h }
}

// New returns a client authenticated with the given API key.
func New(apiKey string, opts ...Option) (*Client, error) {
	if apiKey == "" {
		return nil, fmt.Errorf("mailhuset: an API key is required")
	}
	c := &Client{apiKey: apiKey, baseURL: DefaultBaseURL, http: http.DefaultClient}
	for _, opt := range opts {
		opt(c)
	}
	c.Emails = &EmailsService{c: c}
	c.Suppressions = &SuppressionsService{c: c}
	c.Domains = &DomainsService{c: c}
	c.Templates = &TemplatesService{c: c}
	return c, nil
}

// Error is returned when the API responds with a non-2xx status.
type Error struct {
	Status  int    // HTTP status code
	Message string // human-readable message
	Code    string // machine-readable error code, when present
}

func (e *Error) Error() string {
	if e.Code != "" {
		return fmt.Sprintf("mailhuset: %s (status %d, code %s)", e.Message, e.Status, e.Code)
	}
	return fmt.Sprintf("mailhuset: %s (status %d)", e.Message, e.Status)
}

func (c *Client) request(ctx context.Context, method, path string, body, out any) error {
	var reader io.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("mailhuset: encoding request: %w", err)
		}
		reader = bytes.NewReader(buf)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, reader)
	if err != nil {
		return fmt.Errorf("mailhuset: building request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	res, err := c.http.Do(req)
	if err != nil {
		return fmt.Errorf("mailhuset: request failed: %w", err)
	}
	defer res.Body.Close()

	raw, err := io.ReadAll(res.Body)
	if err != nil {
		return fmt.Errorf("mailhuset: reading response: %w", err)
	}

	if res.StatusCode < 200 || res.StatusCode >= 300 {
		apiErr := &Error{Status: res.StatusCode, Message: res.Status}
		var parsed struct {
			Message string `json:"message"`
			Error   string `json:"error"`
		}
		if json.Unmarshal(raw, &parsed) == nil {
			if parsed.Message != "" {
				apiErr.Message = parsed.Message
			}
			apiErr.Code = parsed.Error
		}
		return apiErr
	}

	if out != nil && len(raw) > 0 {
		if err := json.Unmarshal(raw, out); err != nil {
			return fmt.Errorf("mailhuset: decoding response: %w", err)
		}
	}
	return nil
}

// Attachment is a file attachment; Content is base64-encoded.
type Attachment struct {
	Filename    string `json:"filename"`
	Content     string `json:"content"`
	ContentType string `json:"contentType"`
}

// SendParams are the fields of an outbound email. From and To are required.
type SendParams struct {
	From           string            `json:"from"`
	To             []string          `json:"to"`
	Subject        string            `json:"subject,omitempty"`
	HTML           string            `json:"html,omitempty"`
	Text           string            `json:"text,omitempty"`
	CC             []string          `json:"cc,omitempty"`
	BCC            []string          `json:"bcc,omitempty"`
	ReplyTo        []string          `json:"replyTo,omitempty"`
	Headers        map[string]string `json:"headers,omitempty"`
	Tags           map[string]string `json:"tags,omitempty"`
	Stream         string            `json:"stream,omitempty"`
	TemplateAlias  string            `json:"templateAlias,omitempty"`
	TemplateModel  map[string]any    `json:"templateModel,omitempty"`
	Attachments    []Attachment      `json:"attachments,omitempty"`
	SendAt         string            `json:"sendAt,omitempty"`
	IdempotencyKey string            `json:"idempotencyKey,omitempty"`
}

// SendResult is the outcome of a single send.
type SendResult struct {
	ID     string `json:"id"`
	Status string `json:"status"`
}

// BatchItemResult is one entry in a batch send: an accepted message or an error.
type BatchItemResult struct {
	ID     string `json:"id,omitempty"`
	Status string `json:"status"`
	Error  string `json:"error,omitempty"`
}

// Message is a message record.
type Message struct {
	ID                string   `json:"id"`
	To                []string `json:"to"`
	Subject           string   `json:"subject"`
	Status            string   `json:"status"`
	Provider          *string  `json:"provider"`
	ProviderMessageID *string  `json:"providerMessageId"`
	CreatedAt         string   `json:"createdAt"`
	SentAt            *string  `json:"sentAt"`
}

// MessageList is a page of messages.
type MessageList struct {
	Items  []Message `json:"items"`
	Total  int       `json:"total"`
	Limit  int       `json:"limit"`
	Offset int       `json:"offset"`
}

// EmailsService sends and reads email.
type EmailsService struct{ c *Client }

// Send sends a transactional email and returns the queued message.
func (s *EmailsService) Send(ctx context.Context, params SendParams) (*SendResult, error) {
	var out SendResult
	if err := s.c.request(ctx, http.MethodPost, "/email", params, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// Batch sends up to 500 messages in one call, returning a result per message.
func (s *EmailsService) Batch(ctx context.Context, messages []SendParams) ([]BatchItemResult, error) {
	var out []BatchItemResult
	body := map[string]any{"messages": messages}
	if err := s.c.request(ctx, http.MethodPost, "/email/batch", body, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// Get fetches one message and its event history.
func (s *EmailsService) Get(ctx context.Context, id string) (*Message, error) {
	var out Message
	if err := s.c.request(ctx, http.MethodGet, "/email/"+url.PathEscape(id), nil, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// List returns recent messages, newest first. Pass 0 for limit/offset to use defaults.
func (s *EmailsService) List(ctx context.Context, limit, offset int) (*MessageList, error) {
	q := url.Values{}
	if limit > 0 {
		q.Set("limit", strconv.Itoa(limit))
	}
	if offset > 0 {
		q.Set("offset", strconv.Itoa(offset))
	}
	path := "/email"
	if enc := q.Encode(); enc != "" {
		path += "?" + enc
	}
	var out MessageList
	if err := s.c.request(ctx, http.MethodGet, path, nil, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// SuppressionsService manages the suppression list.
type SuppressionsService struct{ c *Client }

// List returns the account's suppressions.
func (s *SuppressionsService) List(ctx context.Context) (map[string]any, error) {
	var out map[string]any
	return out, s.c.request(ctx, http.MethodGet, "/suppressions", nil, &out)
}

// Add suppresses an address. Reason is optional (pass "").
func (s *SuppressionsService) Add(ctx context.Context, address, reason string) error {
	body := map[string]any{"address": address}
	if reason != "" {
		body["reason"] = reason
	}
	return s.c.request(ctx, http.MethodPost, "/suppressions", body, nil)
}

// Remove un-suppresses an address.
func (s *SuppressionsService) Remove(ctx context.Context, address string) error {
	return s.c.request(ctx, http.MethodDelete, "/suppressions/"+url.PathEscape(address), nil, nil)
}

// DomainsService manages sending domains.
type DomainsService struct{ c *Client }

// List returns the account's sending domains.
func (s *DomainsService) List(ctx context.Context) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodGet, "/domains", nil, &out)
}

// Create adds a sending domain.
func (s *DomainsService) Create(ctx context.Context, domain string) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodPost, "/domains", map[string]any{"domain": domain}, &out)
}

// Get returns one domain with its DNS/DKIM records.
func (s *DomainsService) Get(ctx context.Context, domain string) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodGet, "/domains/"+url.PathEscape(domain), nil, &out)
}

// Verify asks Mailhuset to re-check a domain's DNS.
func (s *DomainsService) Verify(ctx context.Context, domain string) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodPost, "/domains/"+url.PathEscape(domain)+"/verify", nil, &out)
}

// Remove deletes a sending domain.
func (s *DomainsService) Remove(ctx context.Context, domain string) error {
	return s.c.request(ctx, http.MethodDelete, "/domains/"+url.PathEscape(domain), nil, nil)
}

// TemplatesService manages stored templates.
type TemplatesService struct{ c *Client }

// List returns stored templates.
func (s *TemplatesService) List(ctx context.Context) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodGet, "/templates", nil, &out)
}

// Create stores a new template.
func (s *TemplatesService) Create(ctx context.Context, body map[string]any) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodPost, "/templates", body, &out)
}

// Get returns one template.
func (s *TemplatesService) Get(ctx context.Context, id string) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodGet, "/templates/"+url.PathEscape(id), nil, &out)
}

// Update replaces a template.
func (s *TemplatesService) Update(ctx context.Context, id string, body map[string]any) (any, error) {
	var out any
	return out, s.c.request(ctx, http.MethodPut, "/templates/"+url.PathEscape(id), body, &out)
}

// Remove deletes a template.
func (s *TemplatesService) Remove(ctx context.Context, id string) error {
	return s.c.request(ctx, http.MethodDelete, "/templates/"+url.PathEscape(id), nil, nil)
}
