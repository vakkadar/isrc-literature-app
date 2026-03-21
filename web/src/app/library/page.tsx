"use client";

import { Suspense, useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import ContentCard from "@/components/ContentCard";
import {
  getContentItems,
  getPersons,
  getLanguages,
  getCategories,
  type ContentFilters,
} from "@/services/api";
import type { ContentItem, Person, Language, Category } from "@/types";

export default function LibraryPageWrapper() {
  return (
    <Suspense
      fallback={
        <div className="flex justify-center py-32">
          <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <LibraryPage />
    </Suspense>
  );
}

const CONTENT_TYPES = [
  { value: "pdf", label: "PDF", icon: "📄" },
  { value: "audio", label: "Audio", icon: "🎧" },
  { value: "video", label: "Video", icon: "🎬" },
];

function LibraryPage() {
  const { loading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page")) || 1);
  const [totalPages, setTotalPages] = useState(1);

  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [persons, setPersons] = useState<Person[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [selPerson, setSelPerson] = useState<number | undefined>(
    searchParams.get("person") ? Number(searchParams.get("person")) : undefined
  );
  const [selCategory, setSelCategory] = useState<number | undefined>(
    searchParams.get("category") ? Number(searchParams.get("category")) : undefined
  );
  const [selLanguage, setSelLanguage] = useState<number | undefined>(
    searchParams.get("language") ? Number(searchParams.get("language")) : undefined
  );
  const [selType, setSelType] = useState<string | undefined>(
    searchParams.get("content_type") || undefined
  );
  const [ordering, setOrdering] = useState(
    searchParams.get("ordering") || "-created_at"
  );

  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    Promise.all([getPersons(), getLanguages(), getCategories()])
      .then(([p, l, c]) => {
        setPersons(p.results);
        setLanguages(l.results);
        setCategories(c.results);
      })
      .catch(() => {});
  }, [authLoading]);

  const syncUrl = useCallback(
    (filters: ContentFilters) => {
      const params = new URLSearchParams();
      if (filters.search) params.set("search", String(filters.search));
      if (filters.person) params.set("person", String(filters.person));
      if (filters.category) params.set("category", String(filters.category));
      if (filters.language) params.set("language", String(filters.language));
      if (filters.content_type) params.set("content_type", filters.content_type);
      if (filters.ordering && filters.ordering !== "-created_at")
        params.set("ordering", filters.ordering);
      if (filters.page && filters.page > 1) params.set("page", String(filters.page));
      const qs = params.toString();
      router.replace(`/library${qs ? `?${qs}` : ""}`, { scroll: false });
    },
    [router]
  );

  const loadContent = useCallback(async () => {
    setLoading(true);
    const filters: ContentFilters = { ordering, page };
    if (search.trim()) filters.search = search.trim();
    if (selPerson) filters.person = selPerson;
    if (selCategory) filters.category = selCategory;
    if (selLanguage) filters.language = selLanguage;
    if (selType) filters.content_type = selType;

    syncUrl(filters);

    try {
      const data = await getContentItems(filters);
      setItems(data.results);
      setCount(data.count);
      const pageSize = data.results.length || 20;
      setTotalPages(Math.max(1, Math.ceil(data.count / pageSize)));
    } catch {
      /* handled by api layer */
    } finally {
      setLoading(false);
    }
  }, [search, selPerson, selCategory, selLanguage, selType, ordering, page, syncUrl]);

  useEffect(() => {
    if (authLoading) return;
    const t = setTimeout(loadContent, 300);
    return () => clearTimeout(t);
  }, [loadContent, authLoading]);

  const hasFilters = selPerson || selCategory || selLanguage || selType || search;

  const clearFilters = () => {
    setSelPerson(undefined);
    setSelCategory(undefined);
    setSelLanguage(undefined);
    setSelType(undefined);
    setSearch("");
    setPage(1);
  };

  const toggleFilter = (
    current: number | undefined,
    value: number,
    setter: (v: number | undefined) => void
  ) => {
    setter(current === value ? undefined : value);
    setPage(1);
  };

  if (authLoading) {
    return (
      <div className="flex justify-center py-32">
        <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex gap-6">
      {/* Mobile filter toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed bottom-28 right-4 z-40 w-12 h-12 rounded-full bg-saffron text-white shadow-lg flex items-center justify-center"
      >
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 4h14M3 10h10M3 16h6" />
        </svg>
      </button>

      {/* Sidebar overlay on mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 lg:z-auto w-72 lg:w-64 shrink-0 bg-white lg:bg-transparent border-r lg:border-r-0 border-cream-dark overflow-y-auto transition-transform lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-5 lg:p-0 space-y-6 lg:sticky lg:top-20">
          <div className="flex items-center justify-between lg:hidden">
            <h3 className="font-bold text-brown">Filters</h3>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-warm-gray"
            >
              ✕
            </button>
          </div>

          {hasFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-red-600 font-medium hover:text-red-700"
            >
              Clear all filters
            </button>
          )}

          <FilterSection label="Person">
            {persons.map((p) => (
              <FilterCheckbox
                key={p.id}
                label={p.name}
                checked={selPerson === p.id}
                onChange={() => toggleFilter(selPerson, p.id, setSelPerson)}
              />
            ))}
          </FilterSection>

          <FilterSection label="Category">
            {categories.map((c) => (
              <FilterCheckbox
                key={c.id}
                label={c.name}
                checked={selCategory === c.id}
                onChange={() => toggleFilter(selCategory, c.id, setSelCategory)}
              />
            ))}
          </FilterSection>

          <FilterSection label="Language">
            {languages.map((l) => (
              <FilterCheckbox
                key={l.id}
                label={l.name}
                checked={selLanguage === l.id}
                onChange={() => toggleFilter(selLanguage, l.id, setSelLanguage)}
              />
            ))}
          </FilterSection>

          <FilterSection label="Content Type">
            <div className="flex flex-wrap gap-2">
              {CONTENT_TYPES.map((t) => (
                <button
                  key={t.value}
                  onClick={() => {
                    setSelType(selType === t.value ? undefined : t.value);
                    setPage(1);
                  }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                    selType === t.value
                      ? "bg-saffron text-white border-saffron"
                      : "bg-white text-brown border-cream-dark hover:border-gold-light"
                  }`}
                >
                  <span>{t.icon}</span>
                  {t.label}
                </button>
              ))}
            </div>
          </FilterSection>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 min-w-0">
        {/* Search + sort bar */}
        <div className="flex gap-3 mb-5">
          <div className="flex-1 relative">
            <svg
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-warm-gray"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="7" cy="7" r="5" />
              <path d="M11 11l3 3" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search titles, persons, tags..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-cream-dark rounded-xl text-sm text-brown focus:outline-none focus:ring-2 focus:ring-saffron/30 focus:border-saffron transition-colors"
            />
          </div>
          <select
            value={ordering}
            onChange={(e) => {
              setOrdering(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2.5 bg-white border border-cream-dark rounded-xl text-sm text-brown focus:outline-none focus:ring-2 focus:ring-saffron/30"
          >
            <option value="-created_at">Newest</option>
            <option value="created_at">Oldest</option>
            <option value="title">Title A-Z</option>
            <option value="-title">Title Z-A</option>
            <option value="year">Year ↑</option>
            <option value="-year">Year ↓</option>
          </select>
        </div>

        {/* Results info */}
        {!loading && (
          <p className="text-xs text-warm-gray mb-4">
            {count} item{count !== 1 && "s"} found
            {hasFilters && " (filtered)"}
          </p>
        )}

        {/* Content grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-warm-gray">No content found.</p>
            {hasFilters && (
              <button
                onClick={clearFilters}
                className="mt-3 text-sm text-saffron-dark font-medium hover:text-saffron"
              >
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-3">
            {items.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-8">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-3 py-2 rounded-lg text-sm border border-cream-dark hover:border-gold-light disabled:opacity-40 transition-colors"
            >
              ← Prev
            </button>
            <span className="text-sm text-warm-gray px-3">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-3 py-2 rounded-lg text-sm border border-cream-dark hover:border-gold-light disabled:opacity-40 transition-colors"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function FilterSection({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  const [expanded, setExpanded] = useState(true);
  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-[11px] font-semibold text-warm-gray uppercase tracking-wider mb-2"
      >
        {label}
        <span className="text-xs">{expanded ? "▾" : "▸"}</span>
      </button>
      {expanded && <div className="space-y-1 max-h-48 overflow-y-auto">{children}</div>}
    </div>
  );
}

function FilterCheckbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <label className="flex items-center gap-2.5 py-1 cursor-pointer group">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 rounded border-cream-dark text-saffron focus:ring-saffron/30 accent-saffron"
      />
      <span
        className={`text-sm transition-colors ${
          checked ? "text-brown font-medium" : "text-warm-gray group-hover:text-brown"
        }`}
      >
        {label}
      </span>
    </label>
  );
}
