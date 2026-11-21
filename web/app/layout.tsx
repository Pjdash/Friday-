import type { Metadata, Viewport } from "next";
import { Noto_Sans, Noto_Sans_Devanagari, Noto_Sans_Kannada, Noto_Sans_Tamil } from "next/font/google";
import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { LangProvider } from "@/components/lang-provider";
import { SafetyStrip } from "@/components/safety-banner";
import "./globals.css";

const latin = Noto_Sans({ variable: "--font-noto", subsets: ["latin"], display: "swap" });
const devanagari = Noto_Sans_Devanagari({ variable: "--font-noto-deva", subsets: ["devanagari"], display: "swap" });
const kannada = Noto_Sans_Kannada({ variable: "--font-noto-knda", subsets: ["kannada"], display: "swap" });
const tamil = Noto_Sans_Tamil({ variable: "--font-noto-taml", subsets: ["tamil"], display: "swap" });

export const metadata: Metadata = {
  title: { default: "MitraSeva scheme assistant", template: "%s · MitraSeva" },
  description:
    "Check which welfare schemes you may qualify for, in English, Hindi, Kannada or Tamil. Free to use. Preliminary guidance only.",
  // Keep search engines out until the project owner decides to launch publicly.
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0b5c5a",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${latin.variable} ${devanagari.variable} ${kannada.variable} ${tamil.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <LangProvider>
          <Header />
          <SafetyStrip />
          <main id="main" tabIndex={-1} className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 outline-none">
            {children}
          </main>
          <Footer />
        </LangProvider>
      </body>
    </html>
  );
}
