import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { COLORS } from "../constants";
import { isDownloaded } from "../services/storage";
import type { ContentItem } from "../types";

interface Props {
  item: ContentItem;
  onPress: (item: ContentItem) => void;
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function formatSize(bytes: number | null): string {
  if (!bytes) return "";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
}

export default function ContentCard({ item, onPress }: Props) {
  const [local, setLocal] = useState(false);

  useEffect(() => {
    isDownloaded(item.id).then(setLocal);
  }, [item.id]);

  return (
    <TouchableOpacity style={styles.card} onPress={() => onPress(item)} activeOpacity={0.7}>
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
        <View style={[styles.badge, local ? styles.badgeLocal : styles.badgeRemote]}>
          <Text style={[styles.badgeText, local ? styles.badgeLocalText : styles.badgeRemoteText]}>
            {local ? "Downloaded" : "Cloud"}
          </Text>
        </View>
      </View>

      <View style={styles.meta}>
        <Text style={styles.metaText}>{item.author_name}</Text>
        <Text style={styles.metaDot}>·</Text>
        <Text style={styles.metaText}>{item.subject_name}</Text>
        {item.year && (
          <>
            <Text style={styles.metaDot}>·</Text>
            <Text style={styles.metaText}>{item.year}</Text>
          </>
        )}
      </View>

      <View style={styles.footer}>
        <View style={styles.tags}>
          {item.tags.slice(0, 3).map((tag) => (
            <View key={tag.id} style={styles.tag}>
              <Text style={styles.tagText}>{tag.name}</Text>
            </View>
          ))}
        </View>
        <View style={styles.info}>
          {item.duration_seconds ? (
            <Text style={styles.infoText}>{formatDuration(item.duration_seconds)}</Text>
          ) : null}
          {item.file_size_bytes ? (
            <Text style={styles.infoText}>{formatSize(item.file_size_bytes)}</Text>
          ) : null}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: "600",
    color: COLORS.text,
    flex: 1,
    marginRight: 8,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  badgeLocal: { backgroundColor: COLORS.downloadedBg },
  badgeRemote: { backgroundColor: COLORS.remoteBg },
  badgeText: { fontSize: 11, fontWeight: "600" },
  badgeLocalText: { color: COLORS.downloadedText },
  badgeRemoteText: { color: COLORS.remoteText },
  meta: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  metaText: { fontSize: 13, color: COLORS.textSecondary },
  metaDot: { fontSize: 13, color: COLORS.textMuted, marginHorizontal: 6 },
  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  tags: { flexDirection: "row", gap: 4 },
  tag: {
    backgroundColor: COLORS.tagBg,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  tagText: { fontSize: 11, color: COLORS.tagText },
  info: { flexDirection: "row", gap: 10 },
  infoText: { fontSize: 12, color: COLORS.textMuted },
});
