"use client";
import { useState } from "react";
import { Copy, Check, ChevronDown, ChevronUp, AlertCircle, Table2 } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import ChartView from "./ChartView";
import type { QueryResult } from "@/lib/api";

interface Props {
  result: QueryResult;
}

function isNumeric(val: unknown): boolean {
  return typeof val === "number";
}

export default function ResultsPanel({ result }: Props) {
  const [copied, setCopied] = useState(false);
  const [sqlExpanded, setSqlExpanded] = useState(true);

  const handleCopy = () => {
    navigator.clipboard.writeText(result.sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (result.error) {
    return (
      <div className="mt-6 border border-red-800 bg-red-950/20 rounded-xl p-4">
        <div className="flex items-center gap-2 text-red-400 mb-2">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">Query Failed</span>
        </div>
        <pre className="text-xs text-red-300 font-mono whitespace-pre-wrap">{result.error}</pre>
        {result.sql && (
          <div className="mt-3">
            <p className="text-xs text-gray-500 mb-1">Last attempted SQL:</p>
            <SyntaxHighlighter language="sql" style={vscDarkPlus} customStyle={{ borderRadius: 8, fontSize: 12, margin: 0 }}>
              {result.sql}
            </SyntaxHighlighter>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="border border-gray-700 rounded-xl overflow-hidden">
        <div
          onClick={() => setSqlExpanded(!sqlExpanded)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setSqlExpanded(!sqlExpanded); }}
          className="w-full flex items-center justify-between px-4 py-3 bg-gray-800/70 hover:bg-gray-800 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-green-400 font-semibold uppercase tracking-widest">SQL</span>
            {result.retries > 0 && (
              <span className="text-xs bg-yellow-900/50 text-yellow-400 px-2 py-0.5 rounded-full border border-yellow-800">
                Fixed in {result.retries} {result.retries === 1 ? "retry" : "retries"}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); handleCopy(); }}
              className="text-gray-500 hover:text-gray-300 transition-colors p-1"
            >
              {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
            </button>
            {sqlExpanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
          </div>
        </div>
        {sqlExpanded && (
          <SyntaxHighlighter
            language="sql"
            style={vscDarkPlus}
            customStyle={{ margin: 0, borderRadius: 0, fontSize: 13, maxHeight: 300 }}
          >
            {result.sql}
          </SyntaxHighlighter>
        )}
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
        <Table2 size={12} />
        <span>{result.row_count.toLocaleString()} rows · {result.columns.length} columns</span>
      </div>

      <ChartView data={result.rows} chart={result.chart_suggestion} />

      <div className="overflow-x-auto overflow-y-auto max-h-96 rounded-xl border border-gray-800">
        <table className="result-table">
          <thead>
            <tr>
              {result.columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, i) => (
              <tr key={i}>
                {result.columns.map((col) => (
                  <td key={col} className={isNumeric(row[col]) ? "numeric" : ""}>
                    {row[col] === null || row[col] === undefined
                      ? <span className="text-gray-600">null</span>
                      : typeof row[col] === "number"
                      ? (row[col] as number) % 1 === 0
                        ? (row[col] as number).toLocaleString()
                        : (row[col] as number).toFixed(2)
                      : String(row[col])
                    }
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
