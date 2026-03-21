import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import ContentCard from "../../components/ContentCard";
import { getContentList, getAuthors, getSubjects, type ContentFilters } from "../../services/api";
import { COLORS } from "../../constants";
import type { ContentItem, Author, Subject } from "../../types";

export default function LibraryScreen() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState("");
  const [authors, setAuthors] = useState<Author[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedAuthor, setSelectedAuthor] = useState<number | undefined>();
  const [selectedSubject, setSelectedSubject] = useState<number | undefined>();
  const [selectedType, setSelectedType] = useState<string | undefined>();
  const [showFilters, setShowFilters] = useState(false);
  const router = useRouter();

  const loadContent = useCallback(async () => {
    try {
      const filters: ContentFilters = {};
      if (search.trim()) filters.search = search.trim();
      if (selectedAuthor) filters.author = selectedAuthor;
      if (selectedSubject) filters.subject = selectedSubject;
      if (selectedType) filters.content_type = selectedType;

      const data = await getContentList(filters);
      setItems(data.results);
    } catch (e: any) {
      console.error("Failed to load content:", e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [search, selectedAuthor, selectedSubject, selectedType]);

  const loadFilters = async () => {
    try {
      const [authorsData, subjectsData] = await Promise.all([
        getAuthors(),
        getSubjects(),
      ]);
      setAuthors(authorsData.results);
      setSubjects(subjectsData.results);
    } catch (e) {
      console.error("Failed to load filters:", e);
    }
  };

  useEffect(() => {
    loadFilters();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(loadContent, 300);
    return () => clearTimeout(timeout);
  }, [loadContent]);

  const onRefresh = () => {
    setRefreshing(true);
    loadContent();
  };

  const clearFilters = () => {
    setSelectedAuthor(undefined);
    setSelectedSubject(undefined);
    setSelectedType(undefined);
    setSearch("");
  };

  const hasActiveFilters = selectedAuthor || selectedSubject || selectedType || search;

  const handleItemPress = (item: ContentItem) => {
    router.push(`/content/${item.id}`);
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.searchInput}
          value={search}
          onChangeText={setSearch}
          placeholder="Search title, author, subject..."
          placeholderTextColor={COLORS.textMuted}
        />
        <TouchableOpacity
          style={[styles.filterBtn, showFilters && styles.filterBtnActive]}
          onPress={() => setShowFilters(!showFilters)}
        >
          <Text style={[styles.filterBtnText, showFilters && styles.filterBtnTextActive]}>
            Filters
          </Text>
        </TouchableOpacity>
      </View>

      {showFilters && (
        <View style={styles.filtersPanel}>
          <Text style={styles.filterLabel}>Author</Text>
          <View style={styles.chipRow}>
            {authors.map((a) => (
              <TouchableOpacity
                key={a.id}
                style={[styles.chip, selectedAuthor === a.id && styles.chipActive]}
                onPress={() => setSelectedAuthor(selectedAuthor === a.id ? undefined : a.id)}
              >
                <Text style={[styles.chipText, selectedAuthor === a.id && styles.chipTextActive]}>
                  {a.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.filterLabel}>Subject</Text>
          <View style={styles.chipRow}>
            {subjects.map((s) => (
              <TouchableOpacity
                key={s.id}
                style={[styles.chip, selectedSubject === s.id && styles.chipActive]}
                onPress={() => setSelectedSubject(selectedSubject === s.id ? undefined : s.id)}
              >
                <Text style={[styles.chipText, selectedSubject === s.id && styles.chipTextActive]}>
                  {s.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.filterLabel}>Type</Text>
          <View style={styles.chipRow}>
            {["audio", "pdf"].map((t) => (
              <TouchableOpacity
                key={t}
                style={[styles.chip, selectedType === t && styles.chipActive]}
                onPress={() => setSelectedType(selectedType === t ? undefined : t)}
              >
                <Text style={[styles.chipText, selectedType === t && styles.chipTextActive]}>
                  {t.toUpperCase()}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {hasActiveFilters ? (
            <TouchableOpacity onPress={clearFilters} style={styles.clearBtn}>
              <Text style={styles.clearBtnText}>Clear All Filters</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      )}

      {loading ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={COLORS.primary} />
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <ContentCard item={item} onPress={handleItemPress} />
          )}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={COLORS.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.centered}>
              <Text style={styles.emptyText}>No content found</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  searchRow: {
    flexDirection: "row",
    padding: 12,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    backgroundColor: COLORS.card,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
    color: COLORS.text,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  filterBtn: {
    backgroundColor: COLORS.card,
    borderRadius: 10,
    paddingHorizontal: 14,
    justifyContent: "center",
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  filterBtnActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  filterBtnText: { fontSize: 13, fontWeight: "600", color: COLORS.text },
  filterBtnTextActive: { color: "#fff" },
  filtersPanel: {
    backgroundColor: COLORS.card,
    marginHorizontal: 12,
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
  },
  filterLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: COLORS.textSecondary,
    marginBottom: 6,
    marginTop: 8,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: COLORS.tagBg,
  },
  chipActive: { backgroundColor: COLORS.primary },
  chipText: { fontSize: 13, color: COLORS.tagText },
  chipTextActive: { color: "#fff" },
  clearBtn: { marginTop: 12, alignSelf: "center" },
  clearBtnText: { fontSize: 13, color: COLORS.error, fontWeight: "500" },
  list: { padding: 12, paddingTop: 4 },
  centered: { flex: 1, justifyContent: "center", alignItems: "center", paddingTop: 60 },
  emptyText: { fontSize: 15, color: COLORS.textMuted },
});
