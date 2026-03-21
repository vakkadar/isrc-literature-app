"use client";

import { useAudio } from "@/contexts/AudioContext";

function formatTime(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  const pad = (n: number) => n.toString().padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(sec)}` : `${m}:${pad(sec)}`;
}

export default function AudioPlayer() {
  const {
    currentTrack,
    playlist,
    playlistIndex,
    isPlaying,
    currentTime,
    duration,
    volume,
    minimized,
    togglePlay,
    next,
    previous,
    seek,
    setVolume,
    setMinimized,
    stop,
  } = useAudio();

  if (!currentTrack) return null;

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  const hasNext = playlistIndex < playlist.length - 1;
  const hasPrev = playlistIndex > 0;

  const onProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    seek(ratio * duration);
  };

  if (minimized) {
    return (
      <div className="fixed bottom-0 inset-x-0 z-50 bg-brown text-cream h-12 flex items-center px-4 shadow-2xl">
        <button
          onClick={togglePlay}
          className="w-8 h-8 flex items-center justify-center rounded-full bg-saffron text-brown text-sm font-bold hover:bg-saffron-dark transition-colors"
        >
          {isPlaying ? "⏸" : "▶"}
        </button>
        <span className="ml-3 text-sm truncate flex-1">{currentTrack.title}</span>
        <button
          onClick={() => setMinimized(false)}
          className="ml-2 text-cream/60 hover:text-cream text-xs"
        >
          ▲
        </button>
        <button
          onClick={stop}
          className="ml-2 text-cream/60 hover:text-cream text-xs"
        >
          ✕
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 inset-x-0 z-50 bg-brown text-cream shadow-2xl">
      <div
        className="h-1 bg-cream/10 cursor-pointer relative group"
        onClick={onProgressClick}
      >
        <div
          className="h-full bg-saffron transition-[width] duration-200"
          style={{ width: `${progress}%` }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-saffron opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ left: `${progress}%`, transform: `translateX(-50%) translateY(-50%)` }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <button
            onClick={previous}
            disabled={!hasPrev}
            className="w-8 h-8 flex items-center justify-center rounded-full text-cream/70 hover:text-cream disabled:opacity-30 transition-colors"
          >
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M3 2h2v12H3V2zm3 6l8-6v12L6 8z" />
            </svg>
          </button>
          <button
            onClick={togglePlay}
            className="w-10 h-10 flex items-center justify-center rounded-full bg-saffron text-brown hover:bg-saffron-dark transition-colors"
          >
            {isPlaying ? (
              <svg width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <rect x="3" y="2" width="4" height="12" rx="1" />
                <rect x="9" y="2" width="4" height="12" rx="1" />
              </svg>
            ) : (
              <svg width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M4 2l10 6-10 6V2z" />
              </svg>
            )}
          </button>
          <button
            onClick={next}
            disabled={!hasNext}
            className="w-8 h-8 flex items-center justify-center rounded-full text-cream/70 hover:text-cream disabled:opacity-30 transition-colors"
          >
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M11 2h2v12h-2V2zm-3 6L0 2v12l8-6z" />
            </svg>
          </button>
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{currentTrack.title}</p>
          <p className="text-xs text-cream/50 truncate">
            {currentTrack.personName}
            {currentTrack.collectionTitle && ` — ${currentTrack.collectionTitle}`}
          </p>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-cream/50 tabular-nums">
          <span>{formatTime(currentTime)}</span>
          <span>/</span>
          <span>{formatTime(duration)}</span>
        </div>

        <div className="hidden sm:flex items-center gap-2">
          <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16" className="text-cream/50">
            <path d="M8 2a1 1 0 011 1v5.268l1.562-.781a1 1 0 01.894 1.789l-3 1.5a1 1 0 01-.912 0l-3-1.5a1 1 0 11.894-1.789L7 8.268V3a1 1 0 011-1z" />
          </svg>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            className="w-20 accent-saffron"
          />
        </div>

        <button
          onClick={() => setMinimized(true)}
          className="text-cream/50 hover:text-cream transition-colors"
          title="Minimize"
        >
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2 8h12v1.5H2z" />
          </svg>
        </button>
        <button
          onClick={stop}
          className="text-cream/50 hover:text-cream transition-colors"
          title="Close"
        >
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M4.646 4.646a.5.5 0 01.708 0L8 7.293l2.646-2.647a.5.5 0 01.708.708L8.707 8l2.647 2.646a.5.5 0 01-.708.708L8 8.707l-2.646 2.647a.5.5 0 01-.708-.708L7.293 8 4.646 5.354a.5.5 0 010-.708z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
