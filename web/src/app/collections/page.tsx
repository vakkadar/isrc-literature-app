"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { getCollections, getPersons, getCategories } from "@/services/api";
import type { Collection, Person, Category } from "@/types";

export default function CollectionsPage() {
  const { loading: authLoading } = useAuth();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [persons, setPersons] = useState<Person[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selPerson, setSelPerson] = useState<number | undefined>();
  const [selCategory, setSelCategory] = useState<number | undefined>();
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (authLoading) return;
    Promise.all([getPersons(), getCategories()])
      .then(([p, c]) => {
        setPersons(p.results);
        setCategories(c.results);
      })
      .catch(() => {});
  }, [authLoading]);

  const loadCollections = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getCollections({
        search: search.trim() || undefined,
        person: selPerson,
        category: selCategory,
      });
      setCollections(data.results);
      setCount(data.count);
    } catch {
      /* handled */
    } finally {
      setLoading(false);
    }
  }, [search, selPerson, selCategory]);

  useEffect(() => {
    if (authLoading) return;
    const t = setTimeout(loadCollections, 300);
    return () => clearTimeout(t);
  }, [loadCollections, authLoading]);

  if (authLoading) {
    return (
      <div className="flex justify-center py-32">
        <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
      <h1 className="text-2xl font-bold text-brown mb-6">Collections</h1>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
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
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search collections..."
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-cream-dark rounded-xl text-sm text-brown focus:outline-none focus:ring-2 focus:ring-saffron/30 focus:border-saffron transition-colors"
          />
        </div>
        <select
          value={selPerson ?? ""}
          onChange={(e) =>
            setSelPerson(e.target.value ? Number(e.target.value) : undefined)
          }
          className="px-3 py-2.5 bg-white border border-cream-dark rounded-xl text-sm text-brown focus:outline-none"
        >
          <option value="">All Persons</option>
          {persons.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <select
          value={selCategory ?? ""}
          onChange={(e) =>
            setSelCategory(e.target.value ? Number(e.target.value) : undefined)
          }
          className="px-3 py-2.5 bg-white border border-cream-dark rounded-xl text-sm text-brown focus:outline-none"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {!loading && (
        <p className="text-xs text-warm-gray mb-4">
          {count} collection{count !== 1 && "s"} found
        </p>
      )}

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
        </div>
      ) : collections.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-4xl mb-3">📚</div>
          <p className="text-warm-gray">No collections found.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {collections.map((col) => (
            <Link
              key={col.id}
              href={`/collections/${col.id}`}
              className="group bg-white rounded-xl p-5 border border-cream-dark hover:border-saffron/30 hover:shadow-md transition-all"
            >
              <h3 className="font-semibold text-brown group-hover:text-saffron-dark transition-colors line-clamp-2">
                {col.title}
              </h3>
              <p className="text-sm text-warm-gray mt-1.5">
                {col.person_name}
                {col.category_name && ` · ${col.category_name}`}
                {col.year && ` · ${col.year}`}
              </p>
              {col.language_code && (
                <span className="inline-block mt-2 text-[10px] uppercase font-medium px-2 py-0.5 rounded bg-cream text-warm-gray">
                  {col.language_code}
                </span>
              )}
              {col.description && (
                <p className="text-xs text-warm-gray mt-2 line-clamp-2">
                  {col.description}
                </p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
