"use client";

import { useState } from "react";
import ChatBubble from "../components/ChatBubble";
import ChatInput from "../components/ChatInput";

interface Message {
  role: "user" | "system";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/chat?prompt=${text}`, {
        method: "POST",
      });

      const data = await res.json();

      const systemMsg: Message = {
        role: "system",
        content: JSON.stringify(data.result),
      };

      setMessages((prev) => [...prev, systemMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", content: "⚠️ Error contacting server" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-white">
      <div className="flex flex-col w-full max-w-4xl mx-auto p-6">
        {/* Header */}
        <h1 className="text-2xl font-semibold mb-4 text-center">
          Neo4j Query Assistant
        </h1>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto space-y-4 px-2">
          {messages.map((msg, i) => (
            <ChatBubble key={i} role={msg.role} content={msg.content} />
          ))}

          {loading && (
            <ChatBubble role="system" content="Thinking..." />
          )}
        </div>

        {/* Input */}
        <ChatInput onSend={sendMessage} />
      </div>
    </div>
  );
}
