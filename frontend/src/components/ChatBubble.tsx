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

  // ==================== ERROR TYPE ====================
  if (block.type === "error") {
    return (
      <div className="text-red-400">
        <div className="font-semibold mb-1">⚠️ Error</div>
        <div>{block.message}</div>
      </div>
    );
  }

  // ==================== TEXT TYPE ====================
  // Simple text responses (yes/no, confirmations, explanations)
  if (block.type === "text") {
    return <div className="whitespace-pre-wrap">{block.message}</div>;
  }

  // ==================== LIST TYPE ====================
  // Node/team name lists (ownership, dependencies, search results)
  if (block.type === "list") {
    const listData = block.data || [];
    return (
      <div>
        <div className="font-semibold mb-2 text-zinc-100">{block.message}</div>
        {listData.length > 0 ? (
          <ul className="space-y-1.5">
            {listData.map((item: string, i: number) => (
              <li key={i} className="flex items-start">
                <span className="mr-2 text-blue-400 mt-0.5">•</span>
                <span className="bg-zinc-700/50 px-2 py-0.5 rounded text-sm">
                  {item}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="italic text-zinc-500">No results</div>
        )}
      </div>
    );
  }

  // ==================== PATH TYPE ====================
  // Ordered path between nodes
  if (block.type === "path") {
    const pathData = block.data || [];
    return (
      <div>
        <div className="font-semibold mb-2 text-zinc-100">
          {block.message || "Path"}
        </div>
        {pathData.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2">
            {pathData.map((item: string, i: number) => (
              <span key={i} className="flex items-center">
                <span className="bg-blue-600/20 border border-blue-500/30 px-3 py-1 rounded text-sm font-medium">
                  {item}
                </span>
                {i < pathData.length - 1 && (
                  <span className="mx-2 text-blue-400 text-lg">→</span>
                )}
              </span>
            ))}
          </div>
        ) : (
          <div className="italic text-zinc-500">No path found</div>
        )}
      </div>
    );
  }

  // ==================== NODE DETAIL TYPE ====================
  // Single node with properties
  if (block.type === "node_detail") {
    const nodeData = block.data || {};
    return (
      <div>
        <div className="font-semibold mb-2 text-zinc-100">{block.message}</div>
        <div className="bg-zinc-900/50 rounded-lg p-3 space-y-2">
          {Object.entries(nodeData).map(([key, value]: [string, any]) => (
            <div key={key} className="flex">
              <span className="text-zinc-400 min-w-25 capitalize">{key}:</span>
              <span className="text-zinc-200 font-medium">
                {typeof value === "object"
                  ? JSON.stringify(value)
                  : String(value)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ==================== TABLE TYPE ====================
  // Multiple nodes with properties
  if (block.type === "table") {
    const tableData: any[] = block.data || [];
    if (tableData.length === 0) {
      return (
        <div>
          <div className="font-semibold mb-2 text-zinc-100">
            {block.message}
          </div>
          <div className="italic text-zinc-500">No results</div>
        </div>
      );
    }

    // Get all unique keys from all objects
    const allKeys = Array.from(
      new Set(tableData.flatMap((item) => Object.keys(item))),
    );

    return (
      <div>
        <div className="font-semibold mb-2 text-zinc-100">{block.message}</div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b-2 border-zinc-600">
                {allKeys.map((key) => (
                  <th
                    key={key}
                    className="text-left py-2 px-3 font-semibold text-zinc-300 capitalize"
                  >
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr
                  key={idx}
                  className={`border-b border-zinc-700 ${
                    idx % 2 === 0 ? "bg-zinc-800/30" : ""
                  }`}
                >
                  {allKeys.map((key) => (
                    <td key={key} className="py-2 px-3 text-zinc-200">
                      {typeof row[key] === "object"
                        ? JSON.stringify(row[key])
                        : row[key] || "-"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ==================== BLAST RADIUS TYPE ====================
  // Impact analysis with upstream/downstream/teams
  if (block.type === "blast_radius") {
    const blastData = block.data || {};
    const categoryLabels: Record<string, string> = {
      upstream: "Upstream Dependents",
      downstream: "Downstream Dependencies",
      teams: "Teams Involved",
    };

    return (
      <div className="space-y-4">
        <div className="font-bold text-base text-zinc-100">{block.message}</div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b-2 border-zinc-600">
                <th className="text-left py-2 px-3 font-semibold text-zinc-300">
                  Category
                </th>
                <th className="text-left py-2 px-3 font-semibold text-zinc-300">
                  Nodes Impacted
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(blastData).map(
                ([section, items]: [string, any], idx) => (
                  <tr
                    key={section}
                    className={`border-b border-zinc-700 ${
                      idx % 2 === 0 ? "bg-zinc-800/30" : ""
                    }`}
                  >
                    <td className="py-3 px-3">
                      <div className="font-semibold text-zinc-100">
                        {categoryLabels[section] ||
                          section
                            .split(/[-_]/)
                            .map(
                              (word: string) =>
                                word.charAt(0).toUpperCase() + word.slice(1),
                            )
                            .join(" ")}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      {Array.isArray(items) && items.length > 0 ? (
                        <ul className="space-y-1">
                          {items.map((item: string, i: number) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2 text-blue-400">•</span>
                              <span className="text-zinc-200">{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="italic text-zinc-500">None</div>
                      )}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ==================== FALLBACK ====================
  // Show message if available, otherwise JSON
  if (block.message) {
    return <div className="whitespace-pre-wrap">{block.message}</div>;
  }

  return (
    <pre className="text-xs overflow-x-auto bg-zinc-900 p-2 rounded">
      {JSON.stringify(block, null, 2)}
    </pre>
  );
}
