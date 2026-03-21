import * as FileSystem from "expo-file-system";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_KEYS } from "../constants";
import type { LocalFileInfo, ContentItemDetail } from "../types";

const CONTENT_DIR = `${FileSystem.documentDirectory}isrc-content/`;

async function ensureContentDir(): Promise<void> {
  const info = await FileSystem.getInfoAsync(CONTENT_DIR);
  if (!info.exists) {
    await FileSystem.makeDirectoryAsync(CONTENT_DIR, { intermediates: true });
  }
}

function getLocalPath(contentId: number, contentType: string): string {
  const ext = contentType === "pdf" ? "pdf" : "mp3";
  return `${CONTENT_DIR}${contentId}.${ext}`;
}

async function getLocalFilesMap(): Promise<Record<number, LocalFileInfo>> {
  const raw = await AsyncStorage.getItem(STORAGE_KEYS.LOCAL_FILES);
  return raw ? JSON.parse(raw) : {};
}

async function saveLocalFilesMap(map: Record<number, LocalFileInfo>): Promise<void> {
  await AsyncStorage.setItem(STORAGE_KEYS.LOCAL_FILES, JSON.stringify(map));
}

export async function getLocalFileInfo(contentId: number): Promise<LocalFileInfo | null> {
  const map = await getLocalFilesMap();
  return map[contentId] || null;
}

export async function isDownloaded(contentId: number): Promise<boolean> {
  const info = await getLocalFileInfo(contentId);
  if (!info) return false;
  const fileInfo = await FileSystem.getInfoAsync(info.localPath);
  return fileInfo.exists;
}

export async function downloadContent(
  item: ContentItemDetail,
  onProgress?: (progress: number) => void
): Promise<LocalFileInfo> {
  await ensureContentDir();
  const localPath = getLocalPath(item.id, item.content_type);

  const callback = (downloadProgress: FileSystem.DownloadProgressData) => {
    if (onProgress && downloadProgress.totalBytesExpectedToWrite > 0) {
      const progress =
        downloadProgress.totalBytesWritten /
        downloadProgress.totalBytesExpectedToWrite;
      onProgress(progress);
    }
  };

  const downloadResumable = FileSystem.createDownloadResumable(
    item.drive_url,
    localPath,
    {},
    callback
  );

  const result = await downloadResumable.downloadAsync();
  if (!result) throw new Error("Download failed");

  const localFileInfo: LocalFileInfo = {
    contentId: item.id,
    localPath,
    downloadedAt: new Date().toISOString(),
    fileHash: item.file_hash,
  };

  const map = await getLocalFilesMap();
  map[item.id] = localFileInfo;
  await saveLocalFilesMap(map);

  return localFileInfo;
}

export async function deleteLocalContent(contentId: number): Promise<void> {
  const map = await getLocalFilesMap();
  const info = map[contentId];
  if (info) {
    const fileInfo = await FileSystem.getInfoAsync(info.localPath);
    if (fileInfo.exists) {
      await FileSystem.deleteAsync(info.localPath);
    }
    delete map[contentId];
    await saveLocalFilesMap(map);
  }
}

export async function hasRemoteUpdate(
  contentId: number,
  remoteHash: string
): Promise<boolean> {
  const info = await getLocalFileInfo(contentId);
  if (!info) return false;
  return info.fileHash !== remoteHash && remoteHash !== "";
}

export async function getAllLocalFiles(): Promise<LocalFileInfo[]> {
  const map = await getLocalFilesMap();
  return Object.values(map);
}
