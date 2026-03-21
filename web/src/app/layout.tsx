import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ISRC Literature",
  description: "Spiritual Audio & Document Library",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#f8f6f3] text-[#2d2d2d] antialiased">{children}</body>
    </html>
  );
}
