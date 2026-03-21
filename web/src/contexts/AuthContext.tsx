"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import { login as apiLogin, logout as apiLogout } from "@/services/api";

interface AuthState {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const t = localStorage.getItem("auth_token");
    const u = localStorage.getItem("username");
    setToken(t);
    setUsername(u);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!loading && !token && pathname !== "/login") {
      router.replace("/login");
    }
  }, [loading, token, pathname, router]);

  const login = useCallback(
    async (user: string, pass: string) => {
      const data = await apiLogin(user, pass);
      setToken(data.token);
      setUsername(data.username);
      router.replace("/home");
    },
    [router]
  );

  const logout = useCallback(async () => {
    await apiLogout();
    setToken(null);
    setUsername(null);
    router.replace("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        token,
        username,
        isAuthenticated: !!token,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
