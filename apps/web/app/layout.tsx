import type { Metadata } from "next";
import favicon32 from "./assets/favicon/favicon-32x32.png";
import appleTouchIcon from "./assets/favicon/apple-icon-180x180.png";
import "./globals.css";

export const metadata: Metadata = {
  title: "LOOFIO",
  description: "Data-driven opportunity intelligence for hospitals.",
  icons: {
    icon: [{ url: favicon32.src, sizes: "32x32", type: "image/png" }],
    apple: [{ url: appleTouchIcon.src, sizes: "180x180", type: "image/png" }],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
