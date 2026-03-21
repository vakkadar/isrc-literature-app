"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const NAV_ITEMS = [
  { label: "Home", href: "/home" },
  { label: "Library", href: "/library" },
  { label: "Collections", href: "/collections" },
];

export default function Header() {
  const { username, logout, isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!isAuthenticated) return null;

  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-brown to-brown-light shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link href="/home" className="flex items-center gap-2.5 shrink-0">
            <span className="text-2xl" role="img" aria-label="lotus">
              🪷
            </span>
            <span className="text-lg font-bold text-cream tracking-tight">
              ISRC Literature
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const active =
                pathname === item.href ||
                (item.href !== "/home" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? "bg-white/15 text-white"
                      : "text-cream/70 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            {username && (
              <span className="text-sm text-cream/70">{username}</span>
            )}
            <button
              onClick={logout}
              className="text-sm px-3.5 py-1.5 rounded-lg border border-cream/30 text-cream/80 hover:bg-white/10 hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-cream/80 hover:text-white"
            aria-label="Toggle menu"
          >
            {mobileOpen ? (
              <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 6l12 12M6 18L18 6" />
              </svg>
            ) : (
              <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-4 border-t border-cream/10 mt-1 pt-3 space-y-1">
            {NAV_ITEMS.map((item) => {
              const active =
                pathname === item.href ||
                (item.href !== "/home" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? "bg-white/15 text-white"
                      : "text-cream/70 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
            <div className="flex items-center justify-between px-4 pt-3 border-t border-cream/10 mt-2">
              {username && (
                <span className="text-sm text-cream/70">{username}</span>
              )}
              <button
                onClick={() => {
                  setMobileOpen(false);
                  logout();
                }}
                className="text-sm px-3.5 py-1.5 rounded-lg border border-cream/30 text-cream/80 hover:bg-white/10"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
