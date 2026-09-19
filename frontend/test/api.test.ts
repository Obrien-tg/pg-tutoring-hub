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
