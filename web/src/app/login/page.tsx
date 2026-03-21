"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError("Please enter username and password");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await login(username.trim(), password);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-cream via-warm-bg to-cream-dark">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <div className="text-5xl mb-3">🪷</div>
          <h1 className="text-3xl font-bold text-brown">ISRC Literature</h1>
          <p className="text-warm-gray mt-2 text-sm">
            Digital Library of Sahaj Marg Literature
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl shadow-lg shadow-brown/5 p-8 border border-cream-dark"
        >
          <h2 className="text-xl font-semibold text-brown mb-6">Sign In</h2>

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm mb-5 border border-red-100">
              {error}
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-brown-light mb-1.5">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 border border-cream-dark rounded-lg bg-cream/30 text-brown focus:outline-none focus:ring-2 focus:ring-saffron/30 focus:border-saffron transition-colors"
              placeholder="Enter username"
              autoComplete="username"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-brown-light mb-1.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-cream-dark rounded-lg bg-cream/30 text-brown focus:outline-none focus:ring-2 focus:ring-saffron/30 focus:border-saffron transition-colors"
              placeholder="Enter password"
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-saffron to-saffron-dark text-white rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-60 shadow-md shadow-saffron/20"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in...
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
