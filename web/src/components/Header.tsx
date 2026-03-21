"use client";
import { useRouter } from "next/navigation";
import { logout } from "@/services/api";

export default function Header() {
  const router = useRouter();
  const username =
    typeof window !== "undefined" ? localStorage.getItem("username") : null;

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  return (
    <header className="bg-gradient-to-r from-[#4a2c2a] to-[#7b4a3a] text-white">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">ISRC Literature</h1>
          <p className="text-white/70 text-xs">Spiritual Audio & Document Library</p>
        </div>
        <div className="flex items-center gap-4">
          {username && (
            <span className="text-sm text-white/80 hidden sm:inline">{username}</span>
          )}
          <button
            onClick={handleLogout}
            className="text-sm px-3 py-1.5 rounded-lg border border-white/30 hover:bg-white/10 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
