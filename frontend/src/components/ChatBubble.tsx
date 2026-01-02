/* eslint-disable @typescript-eslint/no-explicit-any */
interface Props {
  role: "user" | "system";
  blocks: any[];
}

export default function ChatBubble({ role, blocks }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] rounded-xl px-4 py-3 text-sm ${
          isUser ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-200"
        }`}
      >
        <div className="space-y-4">
          {blocks.map((block, i) => (
            <BlockRenderer key={i} block={block} />
          ))}
        </div>
      </div>
    </div>
  );
}

function BlockRenderer({ block }: { block: any }) {
  // Primitive or unexpected array fallback
  if (!block || typeof block !== "object") {
    return <div>{String(block)}</div>;
  }

  if (block.type === "text") {
    return <div>{block.message}</div>;
  }

  if (block.type === "path") {
    return (
      <div>
        <div className="font-semibold mb-1">{block.message || "Path"}</div>
        <ul className="list-disc list-inside space-y-1">
          {block.data && block.data.length > 0 ? (
            block.data.map((item: any, i: number) => (
              <li key={i}>{String(item)}</li>
            ))
          ) : (
            <li className="italic text-zinc-500">No results</li>
          )}
        </ul>
      </div>
    );
  }

  if (block.type === "list") {
    return (
      <div>
        <div className="font-semibold mb-1">{block.message}</div>
        <ul className="list-disc list-inside space-y-1">
          {block.data.length > 0 ? (
            block.data.map((item: string) => <li key={item}>{item}</li>)
          ) : (
            <li className="italic text-zinc-500">No results</li>
          )}
        </ul>
      </div>
    );
  }

  if (block.type === "blast_radius") {
    return (
      <div className="space-y-3">
        <div className="font-semibold">{block.message}</div>

        {Object.entries(block.data).map(([section, items]: any) => (
          <div key={section}>
            <div className="text-xs uppercase text-zinc-400 mb-1">
              {section}
            </div>

            {items.length > 0 ? (
              <ul className="list-disc list-inside text-sm space-y-0.5">
                {items.map((item: string) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <div className="italic text-zinc-500 text-sm">None</div>
            )}
          </div>
        ))}
      </div>
    );
  }

  // Safe fallback
  return (
    <pre className="text-xs overflow-x-auto">
      {JSON.stringify(block, null, 2)}
    </pre>
  );
}
