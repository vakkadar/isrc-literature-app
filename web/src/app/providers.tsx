"use client";

import { type ReactNode } from "react";
import { AuthProvider } from "@/contexts/AuthContext";
import { AudioProvider } from "@/contexts/AudioContext";
import Header from "@/components/Header";
import AudioPlayer from "@/components/AudioPlayer";
import { usePathname } from "next/navigation";

function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const isLogin = pathname === "/login";

  return (
    <>
      {!isLogin && <Header />}
      <main className={!isLogin ? "pb-24" : ""}>{children}</main>
      {!isLogin && <AudioPlayer />}
    </>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AudioProvider>
        <AppShell>{children}</AppShell>
      </AudioProvider>
    </AuthProvider>
  );
}
