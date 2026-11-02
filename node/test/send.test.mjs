// Request-shape checks against a fake fetch. Run with `npm test` (builds first).
import { test } from "node:test";
import assert from "node:assert/strict";
import { Mailhuset } from "../dist/index.js";

function client() {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, init, body: init.body ? JSON.parse(init.body) : undefined });
    return new Response(JSON.stringify({ id: "msg_1", status: "queued" }), { status: 201 });
  };
  return { mh: new Mailhuset("mh_test_x", { fetch }), calls };
}

test("send passes tracking through", async () => {
  const { mh, calls } = client();
  await mh.emails.send({
    from: "a@example.com",
    to: "b@example.com",
    subject: "Hi",
    tracking: { opens: true, clicks: false },
  });
  assert.equal(calls[0].url, "https://api.mailhuset.com/v1/email");
  assert.deepEqual(calls[0].body.tracking, { opens: true, clicks: false });
  assert.deepEqual(calls[0].body.to, ["b@example.com"]);
});

test("send omits tracking when it is not set", async () => {
  const { mh, calls } = client();
  await mh.emails.send({ from: "a@example.com", to: "b@example.com", subject: "Hi" });
  assert.equal("tracking" in calls[0].body, false);
});

test("batch passes tracking per message", async () => {
  const { mh, calls } = client();
  await mh.emails.batch([
    { from: "a@example.com", to: "b@example.com", tracking: { clicks: true } },
    { from: "a@example.com", to: "c@example.com" },
  ]);
  assert.deepEqual(calls[0].body.messages[0].tracking, { clicks: true });
  assert.equal("tracking" in calls[0].body.messages[1], false);
});
