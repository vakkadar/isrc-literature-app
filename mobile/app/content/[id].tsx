import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import AudioPlayer from "../../components/AudioPlayer";
import { getContentDetail, checkContentUpdate } from "../../services/api";
import {
  isDownloaded,
  downloadContent,
  deleteLocalContent,
  getLocalFileInfo,
  hasRemoteUpdate,
} from "../../services/storage";
import { COLORS } from "../../constants";
import type { ContentItemDetail } from "../../types";

export default function ContentDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [item, setItem] = useState<ContentItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloaded, setDownloaded] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [hasUpdate, setHasUpdate] = useState(false);
  const [checkingUpdate, setCheckingUpdate] = useState(false);
  const [localPath, setLocalPath] = useState<string | null>(null);

  useEffect(() => {
    loadDetail();
  }, [id]);

  const loadDetail = async () => {
    try {
      const contentId = parseInt(id!, 10);
      const data = await getContentDetail(contentId);
      setItem(data);

      const isLocal = await isDownloaded(contentId);
      setDownloaded(isLocal);

      if (isLocal) {
        const info = await getLocalFileInfo(contentId);
        if (info) setLocalPath(info.localPath);
      }
    } catch (e: any) {
      console.error("Failed to load detail:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!item) return;
    setDownloading(true);
    setDownloadProgress(0);
    try {
      const info = await downloadContent(item, setDownloadProgress);
      setDownloaded(true);
      setLocalPath(info.localPath);
      setHasUpdate(false);
      Alert.alert("Downloaded", "File saved to device");
    } catch (e: any) {
      Alert.alert("Download Failed", e.message);
    } finally {
      setDownloading(false);
    }
  };

  const handleDelete = () => {
    if (!item) return;
    Alert.alert("Remove Download", "Delete the local copy of this file?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          await deleteLocalContent(item.id);
          setDownloaded(false);
          setLocalPath(null);
        },
      },
    ]);
  };

  const handleCheckUpdate = async () => {
    if (!item) return;
    setCheckingUpdate(true);
    try {
      const result = await checkContentUpdate(item.id);
      if (result.changed) {
        setHasUpdate(true);
        Alert.alert(
          "Update Available",
          "The remote file has changed. Would you like to re-download?",
          [
            { text: "Later", style: "cancel" },
            { text: "Download", onPress: handleDownload },
          ]
        );
      } else {
        setHasUpdate(false);
        Alert.alert("Up to Date", "Your local copy matches the latest version.");
      }
    } catch (e: any) {
      Alert.alert("Check Failed", e.message);
    } finally {
      setCheckingUpdate(false);
    }
  };

  const formatDuration = (seconds: number | null): string => {
    if (!seconds) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    return `${m}m ${s}s`;
  };

  const formatSize = (bytes: number | null): string => {
    if (!bytes) return "—";
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  if (!item) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Content not found</Text>
      </View>
    );
  }

  const audioUri = downloaded && localPath ? localPath : item.drive_url;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{item.title}</Text>

      <View style={styles.metaCard}>
        <MetaRow label="Author" value={item.author.name} />
        <MetaRow label="Subject" value={item.subject.name} />
        {item.year && <MetaRow label="Year" value={String(item.year)} />}
        <MetaRow label="Type" value={item.content_type.toUpperCase()} />
        <MetaRow label="Duration" value={formatDuration(item.duration_seconds)} />
        <MetaRow label="Size" value={formatSize(item.file_size_bytes)} />
      </View>

      {item.tags.length > 0 && (
        <View style={styles.tagsRow}>
          {item.tags.map((tag) => (
            <View key={tag.id} style={styles.tag}>
              <Text style={styles.tagText}>{tag.name}</Text>
            </View>
          ))}
        </View>
      )}

      {item.description ? (
        <Text style={styles.description}>{item.description}</Text>
      ) : null}

      {/* Storage status */}
      <View style={styles.statusCard}>
        <View style={styles.statusRow}>
          <View
            style={[
              styles.statusBadge,
              downloaded ? styles.statusLocal : styles.statusRemote,
              hasUpdate && styles.statusUpdate,
            ]}
          >
            <Text
              style={[
                styles.statusText,
                downloaded ? styles.statusLocalText : styles.statusRemoteText,
                hasUpdate && styles.statusUpdateText,
              ]}
            >
              {hasUpdate ? "Update Available" : downloaded ? "Downloaded" : "Cloud Only"}
            </Text>
          </View>
        </View>

        <View style={styles.actionRow}>
          {!downloaded ? (
            <TouchableOpacity
              style={styles.actionBtn}
              onPress={handleDownload}
              disabled={downloading}
            >
              {downloading ? (
                <View style={styles.progressRow}>
                  <ActivityIndicator size="small" color="#fff" />
                  <Text style={styles.actionBtnText}>
                    {Math.round(downloadProgress * 100)}%
                  </Text>
                </View>
              ) : (
                <Text style={styles.actionBtnText}>Download to Device</Text>
              )}
            </TouchableOpacity>
          ) : (
            <>
              <TouchableOpacity
                style={[styles.actionBtn, styles.actionBtnSecondary]}
                onPress={handleCheckUpdate}
                disabled={checkingUpdate}
              >
                {checkingUpdate ? (
                  <ActivityIndicator size="small" color={COLORS.primary} />
                ) : (
                  <Text style={styles.actionBtnSecondaryText}>Check for Update</Text>
                )}
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionBtn, styles.actionBtnDanger]}
                onPress={handleDelete}
              >
                <Text style={styles.actionBtnDangerText}>Remove Download</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>

      {/* Audio player */}
      {item.content_type === "audio" && (
        <AudioPlayer uri={audioUri} title={item.title} />
      )}
    </ScrollView>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metaRow}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={styles.metaValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  errorText: { fontSize: 16, color: COLORS.error },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: COLORS.text,
    marginBottom: 16,
  },
  metaCard: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
    borderBottomWidth: 0.5,
    borderBottomColor: COLORS.border,
  },
  metaLabel: { fontSize: 14, color: COLORS.textSecondary },
  metaValue: { fontSize: 14, fontWeight: "500", color: COLORS.text },
  tagsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 12,
  },
  tag: {
    backgroundColor: COLORS.tagBg,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  tagText: { fontSize: 12, color: COLORS.tagText, fontWeight: "500" },
  description: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
    marginBottom: 16,
  },
  statusCard: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  statusRow: { marginBottom: 12 },
  statusBadge: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 6,
  },
  statusLocal: { backgroundColor: COLORS.downloadedBg },
  statusRemote: { backgroundColor: COLORS.remoteBg },
  statusUpdate: { backgroundColor: COLORS.updateBg },
  statusText: { fontSize: 13, fontWeight: "600" },
  statusLocalText: { color: COLORS.downloadedText },
  statusRemoteText: { color: COLORS.remoteText },
  statusUpdateText: { color: COLORS.updateText },
  actionRow: { gap: 8 },
  actionBtn: {
    backgroundColor: COLORS.primary,
    borderRadius: 10,
    padding: 12,
    alignItems: "center",
  },
  actionBtnText: { color: "#fff", fontWeight: "600", fontSize: 14 },
  actionBtnSecondary: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  actionBtnSecondaryText: { color: COLORS.primary, fontWeight: "600", fontSize: 14 },
  actionBtnDanger: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  actionBtnDangerText: { color: COLORS.error, fontWeight: "600", fontSize: 14 },
  progressRow: { flexDirection: "row", gap: 8, alignItems: "center" },
});
