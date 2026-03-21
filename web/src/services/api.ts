import type {
  Person,
  Language,
  Category,
  Tag,
  Collection,
  CollectionDetail,
  ContentItem,
  ContentItemDetail,
  Discovery,
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
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

function toQuery(params: Record<string, string | number | boolean | undefined | null> | object): string {
  const entries = Object.entries(params) as [string, unknown][];
  const sp = new URLSearchParams();
  entries.forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_V1}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Invalid credentials");
  }
  const data: LoginResponse = await res.json();
  localStorage.setItem("auth_token", data.token);
  localStorage.setItem("username", data.username);
  return data;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch("/auth/logout/", { method: "POST" });
  } catch {
    /* ignore */
  }
  localStorage.removeItem("auth_token");
  localStorage.removeItem("username");
}

export async function getPersons(): Promise<PaginatedResponse<Person>> {
  return apiFetch("/persons/?page_size=200");
}

export async function getLanguages(): Promise<PaginatedResponse<Language>> {
  return apiFetch("/languages/?page_size=200");
}

export async function getCategories(): Promise<PaginatedResponse<Category>> {
  return apiFetch("/categories/?page_size=200");
}

export async function getTags(): Promise<PaginatedResponse<Tag>> {
  return apiFetch("/tags/?page_size=200");
}

export interface ContentFilters {
  search?: string;
  person?: number;
  category?: number;
  language?: number;
  content_type?: string;
  collection?: number;
  year?: number;
  page?: number;
  ordering?: string;
}

export async function getContentItems(
  filters: ContentFilters = {}
): Promise<PaginatedResponse<ContentItem>> {
  return apiFetch(`/content/${toQuery(filters)}`);
}

export async function getContentItem(id: number): Promise<ContentItemDetail> {
  return apiFetch(`/content/${id}/`);
}

export interface CollectionFilters {
  person?: number;
  category?: number;
  language?: number;
  search?: string;
  page?: number;
}

export async function getCollections(
  filters: CollectionFilters = {}
): Promise<PaginatedResponse<Collection>> {
  return apiFetch(`/collections/${toQuery(filters)}`);
}

export async function getCollection(id: number): Promise<CollectionDetail> {
  return apiFetch(`/collections/${id}/`);
}

export async function getDiscoveries(): Promise<PaginatedResponse<Discovery>> {
  return apiFetch("/discoveries/");
}
