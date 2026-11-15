import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import { TAB_BOOT_SCRIPT } from "@/lib/tabs";
import "./globals.css";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "BUMI360",
  description:
    "BUMI360 helps Malaysian farmers check which crops suit their soil pH, temperature and seasonal water, with fertiliser and planting guides for each crop.",
};

export const viewport: Viewport = {
  themeColor: "#060a18",
  colorScheme: "dark",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // data-tab is set before paint by the script below, so React should not complain about it.
    <html lang="en" data-tab="home" className={`${inter.variable} ${spaceGrotesk.variable} antialiased`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: TAB_BOOT_SCRIPT }} />
      </head>
      <body className="bg-bg font-sans text-fg">{children}</body>
    </html>
  );
}
