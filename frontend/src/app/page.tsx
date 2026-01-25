/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import ChatInput from "../components/ChatInput";

interface Message {
  role: "user" | "system";
  blocks: any[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // to wake up render
    async function wakeUp() {
      const testPrompt = "who owns payment service";
      const res = await fetch(
        `${API_URL}/chat?prompt=${encodeURIComponent(testPrompt)}`,
      );
      console.log(res);
    }
    console.log(API_URL);
    wakeUp();
  }, []);

  const sendMessage = async (text: string) => {
    // USER MESSAGE
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        blocks: [{ type: "text", message: text }],
      },
    ]);

    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}/chat?prompt=${encodeURIComponent(text)}`,
        { method: "POST" },
      );

      const data = await res.json();
      console.log("=== API Response ===");
      console.log("Full response:", data);
      console.log("Result object:", data.result);
      console.log("Type:", data.result?.type);
      console.log("Message:", data.result?.message);
      console.log("Data:", data.result?.data);
      console.log("===================");

      // 🔴 IMPORTANT: result is ONE OBJECT → wrap in array
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          blocks: [data.result],
        },
      ]);
    } catch (error) {
      console.error("Error fetching chat response:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          blocks: [{ type: "text", message: "⚠️ Error contacting server" }],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-white">
      <div className="flex flex-col w-full max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-semibold mb-4 text-center">
          DockGraph - Neo4j Query Assistant
        </h1>

        <div className="flex-1 overflow-y-auto chat-box space-y-4 px-2">
          {messages.map((msg, i) => (
            <ChatBubble key={i} role={msg.role} blocks={msg.blocks} />
          ))}

          {loading && (
            <ChatBubble
              role="system"
              blocks={[{ type: "text", message: "Thinking..." }]}
            />
          )}
        </div>

        <ChatInput onSend={sendMessage} />
      </div>
    </div>
  );
}
