import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { isAuthenticated as checkAuth, login as doLogin, logout as doLogout, getUsername } from "./auth";
import type { LoginResponse } from "../types";

interface AuthState {
  isLoggedIn: boolean;
  isLoading: boolean;
  username: string | null;
  login: (username: string, password: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  isLoggedIn: false,
  isLoading: true,
  username: null,
  login: async () => { throw new Error("Not initialized"); },
  logout: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    checkAuth().then((auth) => {
      setIsLoggedIn(auth);
      if (auth) getUsername().then(setUsername);
      setIsLoading(false);
    });
  }, []);

  const login = useCallback(async (user: string, pass: string) => {
    const result = await doLogin(user, pass);
    setIsLoggedIn(true);
    setUsername(result.username);
    return result;
  }, []);

  const logout = useCallback(async () => {
    await doLogout();
    setIsLoggedIn(false);
    setUsername(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, isLoading, username, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
