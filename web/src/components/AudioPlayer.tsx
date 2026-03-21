"use client";
import { useRef, useState, useEffect } from "react";

interface Props {
  src: string;
  title: string;
}

export default function AudioPlayer({ src, title }: Props) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTime = () => setCurrent(audio.currentTime);
    const onMeta = () => setDuration(audio.duration || 0);
    const onEnd = () => setPlaying(false);
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("ended", onEnd);
    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("ended", onEnd);
    };
  }, []);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
  };

  const seek = (offset: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(duration, audio.currentTime + offset));
  };

  const onProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    audio.currentTime = ratio * duration;
  };

  const fmt = (s: number) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = Math.floor(s % 60);
    const pad = (n: number) => n.toString().padStart(2, "0");
    return h > 0 ? `${h}:${pad(m)}:${pad(sec)}` : `${m}:${pad(sec)}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#e0ddd9]">
      <audio ref={audioRef} src={src} preload="metadata" />
      <p className="text-sm font-semibold text-center mb-4 truncate">{title}</p>

      <div className="mb-4 cursor-pointer" onClick={onProgressClick}>
        <div className="h-1.5 bg-[#e0ddd9] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#4a2c2a] rounded-full transition-all duration-200"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-1.5 text-xs text-[#999]">
          <span>{fmt(currentTime)}</span>
          <span>{fmt(duration)}</span>
        </div>
      </div>

      <div className="flex items-center justify-center gap-6">
        <button
          onClick={() => seek(-15)}
          className="text-sm font-semibold text-[#7b4a3a] hover:text-[#4a2c2a] transition-colors px-2 py-1"
        >
          −15s
        </button>
        <button
          onClick={toggle}
          className="w-14 h-14 rounded-full bg-[#4a2c2a] text-white flex items-center justify-center hover:bg-[#7b4a3a] transition-colors text-xl"
        >
          {playing ? "⏸" : "▶"}
        </button>
        <button
          onClick={() => seek(15)}
          className="text-sm font-semibold text-[#7b4a3a] hover:text-[#4a2c2a] transition-colors px-2 py-1"
        >
          +15s
        </button>
      </div>
    </div>
  );
}
