import assert from "node:assert/strict";
import test from "node:test";

import dashboardResponse from "../src/fixtures/dashboard-response.json";
import { dashboardSchema } from "../src/schemas";

test("captured dashboard response matches the Django contract", () => {
  const result = dashboardSchema.safeParse(dashboardResponse);

  assert.equal(
    result.success,
    true,
    result.success ? undefined : result.error.message,
  );
});
