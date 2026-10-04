import { z } from "zod";

import {
  dashboardSchema,
  assignmentDetailSchema,
  assignmentSchema,
  materialSchema,
  materialsListSchema,
  submissionSchema,
  userSchema,
} from "./schemas";
import type { AssignmentDetail, DashboardPayload, Material, Submission, User } from "./types";

const loginResponseSchema = z.object({
  user: userSchema,
});

let csrfTokenPromise: Promise<string> | null = null;

export async function getCsrfToken(): Promise<string> {
  if (typeof document === "undefined") {
    return "";
  }
  const meta = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]');
  const existingToken = meta?.content.trim() ?? "";
  if (existingToken) {
    return existingToken;
  }

  csrfTokenPromise ??= fetch("/api/csrf/", { credentials: "include" })
    .then(async (response) => {
      if (!response.ok) {
        throw new ApiError("Could not establish a secure session.", response.status);
      }
      const body = (await response.json()) as { csrfToken?: string };
      if (!body.csrfToken) {
        throw new ApiError("Could not establish a secure session.", response.status);
      }
      if (meta) {
        meta.content = body.csrfToken;
      }
      return body.csrfToken;
    })
    .catch((error) => {
      csrfTokenPromise = null;
      throw error;
    });

  return csrfTokenPromise;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl = "") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async login(username: string, password: string): Promise<User> {
    const response = await this.request("/api/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    return loginResponseSchema.parse(response).user;
  }

  async getCurrentUser(): Promise<User> {
    return userSchema.parse(await this.request("/api/auth/me/"));
  }

  async getDashboard(): Promise<DashboardPayload> {
    return dashboardSchema.parse(await this.request("/api/dashboard/"));
  }

  async getAssignments(): Promise<AssignmentDetail[]> {
    const response = z.object({ results: z.array(assignmentSchema) }).parse(
      await this.request("/api/assignments/"),
    );
    return response.results.map((assignment) => ({ ...assignment, submission: null }));
  }

  async getAssignment(id: number): Promise<AssignmentDetail> {
    return assignmentDetailSchema.parse(await this.request(`/api/assignments/${id}/`));
  }

  async submitAssignment(
    id: number,
    values: { submissionText: string; submissionNotes: string; file?: File },
  ): Promise<Submission> {
    const body = new FormData();
    body.set("submission_text", values.submissionText);
    body.set("submission_notes", values.submissionNotes);
    if (values.file) body.set("submission_file", values.file);
    return submissionSchema.parse(await this.request(`/api/assignments/${id}/submissions/`, {
      method: "POST",
      body,
    }));
  }

  async getMaterials(): Promise<{ results: Material[]; count: number }> {
    return materialsListSchema.parse(await this.request("/api/materials/"));
  }

  async getMaterial(id: number): Promise<Material> {
    return materialSchema.parse(await this.request(`/api/materials/${id}/`));
  }

  private async request(path: string, init: RequestInit = {}): Promise<unknown> {
    const method = (init.method ?? "GET").toUpperCase();
    const headers = new Headers(init.headers);
    headers.set("Accept", "application/json");
    if (init.body && !(init.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
    if (method !== "GET") {
      headers.set("X-CSRFToken", await getCsrfToken());
      headers.set("X-Requested-With", "XMLHttpRequest");
    }
    const response = await fetch(`${this.baseUrl}${path}`, {
      credentials: "include",
      headers,
      ...init,
      method,
    });

    const body = await response.json().catch(() => null);
    if (!response.ok) {
      const detail =
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
          ? body.detail
          : `Request failed with status ${response.status}.`;
      throw new ApiError(detail, response.status);
    }
    return body;
  }
}
