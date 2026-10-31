# Mailhuset — Go

Official Go client for the [Mailhuset](https://mailhuset.com) transactional email API.

## Install

```bash
go get github.com/DalysieGroup/mailhuset-sdks/go@latest
```

```go
import mailhuset "github.com/DalysieGroup/mailhuset-sdks/go"
```

## Usage

```go
package main

import (
	"context"
	"log"

	mailhuset "github.com/DalysieGroup/mailhuset-sdks/go"
)

func main() {
	mh, err := mailhuset.New("mh_live_…")
	if err != nil {
		log.Fatal(err)
	}

	res, err := mh.Emails.Send(context.Background(), mailhuset.SendParams{
		From:    "you@yourdomain.com",
		To:      []string{"user@example.com"},
		Subject: "Verify your email",
		HTML:    "<p>Welcome</p>",
	})
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("queued %s (%s)", res.ID, res.Status)
}
```

## Resources

- `mh.Emails.Send`, `.Batch`, `.Get`, `.List`
- `mh.Suppressions.List`, `.Add`, `.Remove`
- `mh.Domains.List`, `.Create`, `.Get`, `.Verify`, `.Remove`
- `mh.Templates.List`, `.Create`, `.Get`, `.Update`, `.Remove`

## Errors

A non-2xx response returns a `*mailhuset.Error` carrying the HTTP `Status`,
`Message`, and (when present) an error `Code`:

```go
res, err := mh.Emails.Send(ctx, params)
var apiErr *mailhuset.Error
if errors.As(err, &apiErr) {
	log.Printf("status %d: %s", apiErr.Status, apiErr.Message)
}
```

## Options

```go
mh, _ := mailhuset.New(key,
	mailhuset.WithBaseURL("https://api.mailhuset.com/v1"),
	mailhuset.WithHTTPClient(&http.Client{Timeout: 15 * time.Second}),
)
```
