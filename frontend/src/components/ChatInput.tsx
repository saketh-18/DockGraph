"use client";

import { useState } from "react";

interface Props {
  onSend: (text: string) => void;
}

export default function ChatInput({ onSend }: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="mt-4 flex gap-2">
      <input
        className="flex-1 rounded-lg bg-zinc-900 px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-blue-500"
        placeholder="Ask something about your graph..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
      />
      <button
        onClick={submit}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
      >
        Send
      </button>
    </div>
  );
}
