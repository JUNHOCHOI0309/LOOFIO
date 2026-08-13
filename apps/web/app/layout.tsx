import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LOOFIO",
  description: "Data-driven opportunity intelligence for hospitals.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
