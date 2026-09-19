import { z } from "zod";

import {
  dashboardSchema,
  userSchema,
} from "./schemas";
import type { DashboardPayload, User } from "./types";

const loginResponseSchema = z.object({
  user: userSchema,
});

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

  private async request(path: string, init: RequestInit = {}): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      credentials: "include",
      headers: {
        Accept: "application/json",
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
      ...init,
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
