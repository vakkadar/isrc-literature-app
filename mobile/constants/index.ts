import { Platform } from "react-native";

const getApiUrl = () => {
  if (Platform.OS === "android") {
    return "http://10.0.2.2:8000";
  }
  return "http://localhost:8000";
};

export const API_BASE_URL = getApiUrl();
export const API_V1 = `${API_BASE_URL}/api/v1`;

export const COLORS = {
  primary: "#4a2c2a",
  primaryLight: "#7b4a3a",
  background: "#f8f6f3",
  card: "#ffffff",
  text: "#2d2d2d",
  textSecondary: "#666666",
  textMuted: "#999999",
  border: "#e0ddd9",
  tagBg: "#ede8e3",
  tagText: "#4a2c2a",
  success: "#2e7d32",
  error: "#c62828",
  info: "#1565c0",
  downloadedBg: "#e8f5e9",
  downloadedText: "#2e7d32",
  remoteBg: "#e3f2fd",
  remoteText: "#1565c0",
  updateBg: "#fff3e0",
  updateText: "#e65100",
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: "auth_token",
  USERNAME: "username",
  LOCAL_FILES: "local_files_map",
} as const;
