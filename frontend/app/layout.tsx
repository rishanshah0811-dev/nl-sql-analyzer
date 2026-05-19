import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NL -> SQL Analyzer",
  description: "Ask questions about your data in plain English",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-gray-950 text-gray-100 font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
