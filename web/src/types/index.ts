export interface Person {
  id: number;
  name: string;
  role: "master" | "disciple" | "researcher" | "other";
  description: string;
}

export interface Language {
  id: number;
  name: string;
  code: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface Collection {
  id: number;
  title: string;
  person: number;
  person_name: string;
  category: number | null;
  category_name: string | null;
  language: number | null;
  language_code: string | null;
  description: string;
  year: number | null;
}

export interface CollectionDetail {
  id: number;
  title: string;
  person: Person;
  category: Category | null;
  language: Language | null;
  description: string;
  year: number | null;
  items: ContentItemNested[];
}

export interface ContentItemNested {
  id: number;
  title: string;
  content_type: ContentType;
  file_url: string | null;
  external_url: string;
  chapter_number: number | null;
  duration_seconds: number | null;
  file_size_bytes: number | null;
}

export type ContentType = "pdf" | "audio" | "video" | "image" | "link";

export interface ContentItem {
  id: number;
  title: string;
  person: number;
  person_name: string;
  category: number | null;
  category_name: string | null;
  language: number | null;
  language_code: string | null;
  collection: number | null;
  collection_title: string | null;
  content_type: ContentType;
  file_url: string | null;
  external_url: string;
  description: string;
  year: number | null;
  chapter_number: number | null;
  duration_seconds: number | null;
  file_size_bytes: number | null;
  created_at: string;
}

export interface ContentItemDetail {
  id: number;
  title: string;
  collection: Collection | null;
  person: Person;
  category: Category | null;
  language: Language | null;
  tags: Tag[];
  content_type: ContentType;
  file_url: string | null;
  source_url: string;
  external_url: string;
  description: string;
  year: number | null;
  chapter_number: number | null;
  duration_seconds: number | null;
  file_size_bytes: number | null;
  created_at: string;
  updated_at: string;
}

export interface Discovery {
  id: number;
  title: string;
  url: string;
  source: string;
  content_type: string;
  snippet: string;
  thumbnail_url: string;
  person_mentioned: number | null;
  person_mentioned_name: string | null;
  search_term_used: string;
  status: string;
  discovered_at: string;
  reviewed_at: string | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LoginResponse {
  token: string;
  user_id: number;
  username: string;
}
