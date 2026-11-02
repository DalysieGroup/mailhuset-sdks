package mailhuset

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

// fakeAPI records each request body and answers like a queued send.
func fakeAPI(t *testing.T, bodies *[]map[string]any) *Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		raw, _ := io.ReadAll(r.Body)
		var body map[string]any
		_ = json.Unmarshal(raw, &body)
		*bodies = append(*bodies, body)
		w.WriteHeader(http.StatusCreated)
		_, _ = w.Write([]byte(`{"id":"msg_1","status":"queued"}`))
	}))
	t.Cleanup(srv.Close)
	c, err := New("mh_test_x", WithBaseURL(srv.URL))
	if err != nil {
		t.Fatal(err)
	}
	return c
}

func TestSendPassesTracking(t *testing.T) {
	var bodies []map[string]any
	c := fakeAPI(t, &bodies)
	_, err := c.Emails.Send(context.Background(), SendParams{
		From: "a@example.com", To: []string{"b@example.com"}, Subject: "Hi",
		Tracking: &Tracking{Opens: Bool(true), Clicks: Bool(false)},
	})
	if err != nil {
		t.Fatal(err)
	}
	tr, ok := bodies[0]["tracking"].(map[string]any)
	if !ok {
		t.Fatalf("tracking missing from body: %v", bodies[0])
	}
	// An explicit false must be sent, not dropped: it overrides the stream default.
	if tr["opens"] != true || tr["clicks"] != false {
		t.Fatalf("tracking = %v, want opens=true clicks=false", tr)
	}
}

func TestSendOmitsUnsetTracking(t *testing.T) {
	var bodies []map[string]any
	c := fakeAPI(t, &bodies)
	if _, err := c.Emails.Send(context.Background(), SendParams{From: "a@example.com", To: []string{"b@example.com"}}); err != nil {
		t.Fatal(err)
	}
	if _, present := bodies[0]["tracking"]; present {
		t.Fatalf("tracking should be omitted: %v", bodies[0])
	}
}
