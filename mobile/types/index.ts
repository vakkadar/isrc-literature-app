export interface Author {
  id: number;
  name: string;
  description: string;
}

export interface Subject {
  id: number;
  name: string;
  description: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface ContentItem {
  id: number;
  title: string;
  author: number;
  author_name: string;
  subject: number;
  subject_name: string;
  year: number | null;
  tags: Tag[];
  content_type: "audio" | "pdf";
  drive_file_id: string;
  duration_seconds: number | null;
  file_size_bytes: number | null;
  description: string;
  created_at: string;
}

export interface ContentItemDetail extends Omit<ContentItem, "author" | "subject" | "author_name" | "subject_name"> {
  author: Author;
  subject: Subject;
  drive_url: string;
  file_hash: string;
  last_modified_remote: string | null;
  updated_at: string;
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

export interface LocalFileInfo {
  contentId: number;
  localPath: string;
  downloadedAt: string;
  fileHash: string;
}
