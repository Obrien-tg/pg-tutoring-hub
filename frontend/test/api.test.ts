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

const materialResponse = {
  id: 7,
  title: "Fractions practice",
  description: "Build confidence with fractions.",
  material_type: "worksheet",
  subject: 2,
  subject_name: "Mathematics",
  difficulty_level: "beginner",
  grade_level: "5",
  estimated_time: 20,
  tags: "fractions, numbers",
  external_link: "https://example.com/fractions",
  file_url: null,
  created_at: "2026-10-01T10:00:00Z",
};

test("getMaterials validates the list response", async () => {
  let requestedUrl = "";
  globalThis.fetch = async (input) => {
    requestedUrl = String(input);
    return new Response(JSON.stringify({
      results: [materialResponse],
      count: 1,
    }), { status: 200 });
  };

  const materials = await new ApiClient().getMaterials();

  assert.equal(requestedUrl, "/api/materials/");
  assert.equal(materials.count, 1);
  assert.equal(materials.results[0].title, "Fractions practice");
});

test("getMaterial validates detail responses", async () => {
  let requestedUrl = "";
  globalThis.fetch = async (input) => {
    requestedUrl = String(input);
    return new Response(JSON.stringify(materialResponse), { status: 200 });
  };

  const material = await new ApiClient().getMaterial(7);

  assert.equal(requestedUrl, "/api/materials/7/");
  assert.equal(material.external_link, "https://example.com/fractions");
});

test("material 404 responses become ApiError instances", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Material not found." }), { status: 404 });

  await assert.rejects(
    () => new ApiClient().getMaterial(99999),
    (error: unknown) =>
      error instanceof ApiError &&
      error.status === 404 &&
      error.message === "Material not found.",
  );
});
