import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useAuth } from "../../services/AuthContext";
import { getAllLocalFiles, deleteLocalContent } from "../../services/storage";
import { COLORS } from "../../constants";
import type { LocalFileInfo } from "../../types";

export default function SettingsScreen() {
  const { username, logout } = useAuth();
  const [localFiles, setLocalFiles] = useState<LocalFileInfo[]>([]);

  useEffect(() => {
    getAllLocalFiles().then(setLocalFiles);
  }, []);

  const handleLogout = () => {
    Alert.alert("Logout", "Are you sure you want to log out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: () => logout(),
      },
    ]);
  };

  const handleClearDownloads = () => {
    Alert.alert(
      "Clear Downloads",
      `Delete all ${localFiles.length} downloaded files from this device?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete All",
          style: "destructive",
          onPress: async () => {
            for (const file of localFiles) {
              await deleteLocalContent(file.contentId);
            }
            setLocalFiles([]);
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.label}>Logged in as</Text>
            <Text style={styles.value}>{username || "—"}</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Storage</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.label}>Downloaded files</Text>
            <Text style={styles.value}>{localFiles.length}</Text>
          </View>
          {localFiles.length > 0 && (
            <TouchableOpacity style={styles.dangerBtn} onPress={handleClearDownloads}>
              <Text style={styles.dangerBtnText}>Clear All Downloads</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.section}>
        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutBtnText}>Logout</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.version}>ISRC Literature v1.0.0</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background, padding: 16 },
  section: { marginBottom: 24 },
  sectionTitle: {
    fontSize: 12,
    fontWeight: "600",
    color: COLORS.textSecondary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 8,
    marginLeft: 4,
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 16,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 4,
  },
  label: { fontSize: 15, color: COLORS.text },
  value: { fontSize: 15, color: COLORS.textSecondary, fontWeight: "500" },
  dangerBtn: {
    marginTop: 12,
    padding: 10,
    borderRadius: 8,
    backgroundColor: "#fce4e4",
    alignItems: "center",
  },
  dangerBtnText: { color: COLORS.error, fontWeight: "600", fontSize: 14 },
  logoutBtn: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  logoutBtnText: { color: COLORS.error, fontWeight: "600", fontSize: 16 },
  version: {
    textAlign: "center",
    color: COLORS.textMuted,
    fontSize: 12,
    marginTop: 20,
  },
});
