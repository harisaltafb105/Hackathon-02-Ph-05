import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { AuthProvider } from "@/context/auth-context";
import { TaskProvider } from "@/context/task-context";
import { ChatProvider } from "@/context/chat-context";
import { ChatButton, ChatDrawer } from "@/components/chat";

export const metadata: Metadata = {
  title: "My Tasks - Todo Application",
  description: "A beautiful, responsive todo application built with Next.js",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${GeistSans.variable} ${GeistMono.variable} antialiased`}
      >
        <AuthProvider>
          <TaskProvider>
            <ChatProvider>
              {children}
              <ChatButton />
              <ChatDrawer />
            </ChatProvider>
          </TaskProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
