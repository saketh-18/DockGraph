interface Props {
  role: "user" | "system";
  content: string;
}

export default function ChatBubble({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 text-sm
          ${isUser ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-200"}`}
      >
        {typeof content === "string" ? renderText(content) : content}
      </div>
    </div>
  );
}


function renderText(text: string) {
  const lines = text.split("\n");

  return (
    <div className="space-y-1">
      {lines.map((line, i) => {
        // Bullet lines
        if (line.trim().startsWith("-")) {
          return (
            <div key={i} className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              <span>{line.replace("-", "").trim()}</span>
            </div>
          );
        }

        // Normal line
        return (
          <div key={i}>{line}</div>
        );
      })}
    </div>
  );
}
