import type { Metadata } from "next";
import "./globals.css";
import { SiteNav } from "@/components/site/nav";

export const metadata: Metadata = {
  title: "MoodleCloud — SaaS LMS",
  description: "Modern SaaS-style LMS demo (Cyber Project)."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <SiteNav />
        <main className="mx-auto max-w-6xl px-4 py-10">{children}</main>
      </body>
    </html>
  );
}

