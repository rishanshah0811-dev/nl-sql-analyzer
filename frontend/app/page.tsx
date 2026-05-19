"use client";
import { useState } from "react";
import { Database, Trash2 } from "lucide-react";
import FileUpload from "@/components/FileUpload";
import QueryInput from "@/components/QueryInput";
import ResultsPanel from "@/components/ResultsPanel";
import { api, QueryResult, UploadResult } from "@/lib/api";

interface HistoryEntry {
  question: string;
  result: QueryResult;
  timestamp: Date;
}

export default function Home() {
  const [useSample, setUseSample] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const handleQuery = async (question: string) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await api.query(question, useSample);
      setResult(res);
      setHistory((prev) => [{ question, result: res, timestamp: new Date() }, ...prev.slice(0, 19)]);
    } catch (e) {
      console.error(e);
      setResult({
        sql: "",
        columns: [],
        rows: [],
        row_count: 0,
        error: "Failed to connect to backend. Is the FastAPI server running on port 8000?",
        retries: 0,
        chart_suggestion: { type: "none" },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = (info: UploadResult) => {
    setUseSample(false);
    setResult(null);
  };

  const handleClearUpload = () => {
    setUseSample(true);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center border border-green-500/30">
              <Database size={16} className="text-green-400" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-gray-100 tracking-tight">NL &rarr; SQL Analyzer</h1>
              <p className="text-xs text-gray-500 font-mono">Powered by Gemini 2.5 Flash</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs font-mono px-3 py-1 rounded-full border ${
              useSample
                ? "bg-blue-950/30 text-blue-400 border-blue-800"
                : "bg-green-950/30 text-green-400 border-green-800"
            }`}>
              {useSample ? "S&P 500 Sample Dataset" : "Custom CSV"}
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 xl:grid-cols-[320px_1fr] gap-8">
        <aside className="space-y-6">
          <div>
            <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-3">Data Source</h2>
            <FileUpload
              onUpload={handleUpload}
              onClear={handleClearUpload}
              hasUpload={!useSample}
            />
            {useSample && (
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 text-xs font-mono text-gray-500 space-y-1">
                <p className="text-gray-400 font-semibold text-xs mb-2">Pre-loaded Dataset</p>
                <p>&bull; <span className="text-green-400">companies</span> &mdash; 100 S&P 500 stocks</p>
                <p>&bull; <span className="text-blue-400">sectors</span> &mdash; 12 industry sectors</p>
                <p>&bull; <span className="text-yellow-400">financials</span> &mdash; 2021&ndash;2024 metrics</p>
                <p>&bull; <span className="text-purple-400">price_history</span> &mdash; 90 days of prices</p>
                <p>&bull; <span className="text-pink-400">analyst_ratings</span> &mdash; buy/sell ratings</p>
              </div>
            )}
          </div>

          {history.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest">History</h2>
                <button
                  onClick={() => setHistory([])}
                  className="text-gray-600 hover:text-red-400 transition-colors"
                >
                  <Trash2 size={12} />
                </button>
              </div>
              <div className="space-y-1 max-h-72 overflow-y-auto">
                {history.map((h, i) => (
                  <button
                    key={i}
                    onClick={() => setResult(h.result)}
                    className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-gray-800 transition-colors group"
                  >
                    <p className="text-xs text-gray-400 group-hover:text-gray-200 truncate">{h.question}</p>
                    <p className="text-xs text-gray-600 mt-0.5 font-mono">
                      {h.result.row_count} rows &middot; {h.timestamp.toLocaleTimeString()}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </aside>

        <main>
          <div className="bg-gray-900/40 border border-gray-800 rounded-2xl p-6">
            <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">Ask a Question</h2>
            <QueryInput onQuery={handleQuery} loading={loading} />

            {loading && (
              <div className="mt-6 flex items-center gap-3 text-gray-500">
                <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-mono">Generating SQL with Claude Sonnet 4.6...</span>
              </div>
            )}

            {result && !loading && <ResultsPanel result={result} />}
          </div>
        </main>
      </div>
    </div>
  );
}
