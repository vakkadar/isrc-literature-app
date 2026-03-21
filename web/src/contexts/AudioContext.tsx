"use client";

import {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import type { ContentItemNested } from "@/types";

export interface AudioTrack {
  id: number;
  title: string;
  personName?: string;
  fileUrl: string;
  collectionTitle?: string;
}

interface AudioState {
  currentTrack: AudioTrack | null;
  playlist: AudioTrack[];
  playlistIndex: number;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  minimized: boolean;
  play: (track: AudioTrack) => void;
  playCollection: (tracks: AudioTrack[], startIndex?: number) => void;
  pause: () => void;
  resume: () => void;
  togglePlay: () => void;
  next: () => void;
  previous: () => void;
  seek: (time: number) => void;
  setVolume: (v: number) => void;
  setMinimized: (v: boolean) => void;
  stop: () => void;
}

const AudioContext = createContext<AudioState | null>(null);

export function collectionItemsToTracks(
  items: ContentItemNested[],
  personName?: string,
  collectionTitle?: string
): AudioTrack[] {
  return items
    .filter((i) => i.content_type === "audio" && i.file_url)
    .map((i) => ({
      id: i.id,
      title: i.title,
      personName,
      fileUrl: i.file_url!,
      collectionTitle,
    }));
}

export function AudioProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentTrack, setCurrentTrack] = useState<AudioTrack | null>(null);
  const [playlist, setPlaylist] = useState<AudioTrack[]>([]);
  const [playlistIndex, setPlaylistIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(1);
  const [minimized, setMinimized] = useState(false);

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.volume = 1;
    }
    const audio = audioRef.current;

    const onTime = () => setCurrentTime(audio.currentTime);
    const onMeta = () => setDuration(audio.duration || 0);
    const onEnd = () => {
      setIsPlaying(false);
      setPlaylistIndex((prev) => {
        const nextIdx = prev + 1;
        if (nextIdx < playlist.length) {
          setTimeout(() => playByIndex(nextIdx), 0);
        }
        return prev;
      });
    };
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("ended", onEnd);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);

    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("ended", onEnd);
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playlist]);

  const playByIndex = useCallback(
    (idx: number) => {
      const audio = audioRef.current;
      if (!audio || idx < 0 || idx >= playlist.length) return;
      const track = playlist[idx];
      setCurrentTrack(track);
      setPlaylistIndex(idx);
      audio.src = track.fileUrl;
      audio.play().catch(() => {});
    },
    [playlist]
  );

  const play = useCallback((track: AudioTrack) => {
    const audio = audioRef.current;
    if (!audio) return;
    setPlaylist([track]);
    setPlaylistIndex(0);
    setCurrentTrack(track);
    audio.src = track.fileUrl;
    audio.play().catch(() => {});
  }, []);

  const playCollection = useCallback(
    (tracks: AudioTrack[], startIndex = 0) => {
      const audio = audioRef.current;
      if (!audio || tracks.length === 0) return;
      setPlaylist(tracks);
      setPlaylistIndex(startIndex);
      setCurrentTrack(tracks[startIndex]);
      audio.src = tracks[startIndex].fileUrl;
      audio.play().catch(() => {});
    },
    []
  );

  const pause = useCallback(() => {
    audioRef.current?.pause();
  }, []);

  const resume = useCallback(() => {
    audioRef.current?.play().catch(() => {});
  }, []);

  const togglePlay = useCallback(() => {
    if (isPlaying) pause();
    else resume();
  }, [isPlaying, pause, resume]);

  const next = useCallback(() => {
    const nextIdx = playlistIndex + 1;
    if (nextIdx < playlist.length) playByIndex(nextIdx);
  }, [playlistIndex, playlist.length, playByIndex]);

  const previous = useCallback(() => {
    const prevIdx = playlistIndex - 1;
    if (prevIdx >= 0) playByIndex(prevIdx);
  }, [playlistIndex, playByIndex]);

  const seek = useCallback((time: number) => {
    const audio = audioRef.current;
    if (audio) audio.currentTime = time;
  }, []);

  const setVolume = useCallback((v: number) => {
    setVolumeState(v);
    if (audioRef.current) audioRef.current.volume = v;
  }, []);

  const stop = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.src = "";
    }
    setCurrentTrack(null);
    setPlaylist([]);
    setPlaylistIndex(0);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  }, []);

  return (
    <AudioContext.Provider
      value={{
        currentTrack,
        playlist,
        playlistIndex,
        isPlaying,
        currentTime,
        duration,
        volume,
        minimized,
        play,
        playCollection,
        pause,
        resume,
        togglePlay,
        next,
        previous,
        seek,
        setVolume,
        setMinimized,
        stop,
      }}
    >
      {children}
    </AudioContext.Provider>
  );
}

export function useAudio(): AudioState {
  const ctx = useContext(AudioContext);
  if (!ctx) throw new Error("useAudio must be used within AudioProvider");
  return ctx;
}
