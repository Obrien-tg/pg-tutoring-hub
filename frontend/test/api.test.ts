import assert from "node:assert/strict";
import { afterEach, test } from "node:test";

import dashboardResponse from "../src/fixtures/dashboard-response.json";
import { ApiClient, ApiError } from "../src/api";

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

test("getDashboard sends session credentials and validates the response", async () => {
  let requestedUrl = "";
  let requestedCredentials = "";
  globalThis.fetch = async (input, init) => {
    requestedUrl = String(input);
    requestedCredentials = String(init?.credentials);
    return new Response(JSON.stringify(dashboardResponse), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  const dashboard = await new ApiClient("https://hub.example").getDashboard();

  assert.equal(requestedUrl, "https://hub.example/api/dashboard/");
  assert.equal(requestedCredentials, "include");
  assert.equal(dashboard.role, "student");
  assert.equal(dashboard.total_assignments, 1);
});

test("login validates and returns the authenticated user", async () => {
  globalThis.fetch = async (_input, init) => {
    assert.equal(init?.method, "POST");
    assert.equal(init?.body, JSON.stringify({
      username: "ada",
      password: "secret",
    }));
    return new Response(
      JSON.stringify({
        user: {
          id: 1,
          username: "ada",
          email: "ada@example.com",
          first_name: "Ada",
          last_name: "Learner",
          user_type: "student",
          full_name: "Ada Learner",
        },
      }),
      { status: 200 },
    );
  };

  const user = await new ApiClient().login("ada", "secret");

  assert.equal(user.user_type, "student");
  assert.equal(user.full_name, "Ada Learner");
});

test("non-success responses become ApiError instances", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Invalid credentials." }), {
      status: 401,
    });

  await assert.rejects(
    () => new ApiClient().login("ada", "wrong"),
    (error: unknown) =>
      error instanceof ApiError &&
      error.status === 401 &&
      error.message === "Invalid credentials.",
  );
});

test("schema mismatches fail before reaching the UI", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ role: "student", total_assignments: "one" }), {
      status: 200,
    });

  await assert.rejects(() => new ApiClient().getDashboard());
});

const chatRoom = {
  id: 4,
  name: "Chat with Teacher",
  participants: [1, 2],
  is_group_chat: false,
  created_by: 1,
  created_at: "2026-10-12T10:00:00Z",
  latest_message: null,
};

test("chat methods validate list and message responses", async () => {
  const requests: string[] = [];
  globalThis.fetch = async (input, init) => {
    requests.push(`${init?.method ?? "GET"} ${String(input)}`);
    const path = String(input);
    if (path.endsWith("/with-teacher/")) {
      return new Response(JSON.stringify(chatRoom), { status: 201 });
    }
    if (path.endsWith("/messages/") && init?.method === "POST") {
      return new Response(JSON.stringify({
        id: 8,
        room: 4,
        sender: 1,
        sender_username: "ada",
        message_type: "text",
        content: "Hello",
        file: null,
        timestamp: "2026-10-12T10:01:00Z",
        is_read: false,
      }), { status: 201 });
    }
    if (path.endsWith("/messages/")) {
      return new Response(JSON.stringify({ results: [], count: 0 }), { status: 200 });
    }
    return new Response(JSON.stringify({ results: [chatRoom], count: 1 }), { status: 200 });
  };

  const client = new ApiClient();
  assert.equal((await client.getRooms()).count, 1);
  assert.equal((await client.openTeacherChat()).id, 4);
  assert.equal((await client.getMessages(4)).count, 0);
  assert.equal((await client.sendMessage(4, "Hello")).content, "Hello");
  assert.deepEqual(requests, [
    "GET /api/chat/rooms/",
    "POST /api/chat/rooms/with-teacher/",
    "GET /api/chat/rooms/4/messages/",
    "POST /api/chat/rooms/4/messages/",
  ]);
});

test("chat methods preserve 401 and 404 API errors", async () => {
  let status = 404;
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Chat room not found." }), { status });

  await assert.rejects(
    () => new ApiClient().getMessages(99),
    (error: unknown) => error instanceof ApiError && error.status === 404,
  );
  status = 401;
  await assert.rejects(
    () => new ApiClient().getRooms(),
    (error: unknown) => error instanceof ApiError && error.status === 401,
  );
});
