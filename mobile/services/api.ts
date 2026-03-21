import { API_V1 } from "../constants";
import { getToken } from "./auth";
import type {
  ContentItem,
  ContentItemDetail,
  Author,
  Subject,
  Tag,
  PaginatedResponse,
} from "../types";

async function authHeaders(): Promise<Record<string, string>> {
  const token = await getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Token ${token}` } : {}),
  };
}

async function apiFetch<T>(path: string): Promise<T> {
  const headers = await authHeaders();
  const res = await fetch(`${API_V1}${path}`, { headers });
  if (!res.ok) {
    if (res.status === 401) throw new Error("UNAUTHORIZED");
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
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

export async function checkContentUpdate(
  id: number
): Promise<{ changed: boolean; current_hash: string; last_modified: string | null }> {
  return apiFetch(`/content/${id}/check_update/`);
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
