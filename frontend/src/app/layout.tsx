import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerLens AI | Intelligent Career & Resume Intelligence",
  description: "Enterprise multi-agent resume analysis and talent intelligence platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="light">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-indigo-100 selection:text-indigo-900">
        {children}
      </body>
    </html>
  );
}

