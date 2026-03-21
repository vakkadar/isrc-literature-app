import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_KEYS, API_V1 } from "../constants";
import type { LoginResponse } from "../types";

let cachedToken: string | null = null;

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_V1}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Login failed");
  }

  const data: LoginResponse = await res.json();
  cachedToken = data.token;
  await AsyncStorage.multiSet([
    [STORAGE_KEYS.AUTH_TOKEN, data.token],
    [STORAGE_KEYS.USERNAME, data.username],
  ]);
  return data;
}

export async function logout(): Promise<void> {
  const token = await getToken();
  if (token) {
    await fetch(`${API_V1}/auth/logout/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    }).catch(() => {});
  }
  cachedToken = null;
  await AsyncStorage.multiRemove([STORAGE_KEYS.AUTH_TOKEN, STORAGE_KEYS.USERNAME]);
}

export async function getToken(): Promise<string | null> {
  if (cachedToken) return cachedToken;
  cachedToken = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  return cachedToken;
}

export async function getUsername(): Promise<string | null> {
  return AsyncStorage.getItem(STORAGE_KEYS.USERNAME);
}

export async function isAuthenticated(): Promise<boolean> {
  const token = await getToken();
  return token !== null;
}
