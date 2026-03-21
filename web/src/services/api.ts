import type {
  ContentItem,
  ContentItemDetail,
  Author,
  Subject,
  Tag,
  PaginatedResponse,
  LoginResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Token ${token}` } : {}),
  };
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_V1}${path}`, {
    headers: authHeaders(),
    ...init,
  });
  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("username");
        window.location.href = "/login";
      }
      throw new Error("UNAUTHORIZED");
    }
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_V1}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Login failed");
  }
  const data: LoginResponse = await res.json();
  localStorage.setItem("auth_token", data.token);
  localStorage.setItem("username", data.username);
  return data;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch("/auth/logout/", { method: "POST" });
  } catch {}
  localStorage.removeItem("auth_token");
  localStorage.removeItem("username");
}

export interface ContentFilters {
  search?: string;
  author?: number;
  subject?: number;
  year?: number;
  content_type?: string;
  tag?: string;
  page?: number;
}

export async function getContentList(
  filters: ContentFilters = {}
): Promise<PaginatedResponse<ContentItem>> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== "") {
      params.set(key, String(val));
    }
  });
  const query = params.toString();
  return apiFetch(`/content/${query ? `?${query}` : ""}`);
}

export async function getContentDetail(id: number): Promise<ContentItemDetail> {
  return apiFetch(`/content/${id}/`);
}

export async function getAuthors(): Promise<PaginatedResponse<Author>> {
  return apiFetch("/authors/?page_size=100");
}

export async function getSubjects(): Promise<PaginatedResponse<Subject>> {
  return apiFetch("/subjects/?page_size=100");
}

export async function getTags(): Promise<PaginatedResponse<Tag>> {
  return apiFetch("/tags/?page_size=100");
}
