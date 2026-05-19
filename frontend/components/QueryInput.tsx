"use client";
import { useState, KeyboardEvent } from "react";
import { Send, Loader2, Zap } from "lucide-react";

interface Props {
  onQuery: (question: string) => void;
  loading: boolean;
}

const SAMPLE_QUESTIONS = [
  "Which sector has the highest average net profit margin in 2024?",
  "Show revenue and net income for all technology companies in 2024",
  "Which companies had revenue growth greater than 20% from 2023 to 2024?",
  "Rank companies within each sector by 2024 revenue",
  "What is the 7-day rolling average closing price for NVIDIA?",
  "Find companies with high debt but also high ROE in 2024",
  "Which analysts issued the most Strong Buy ratings?",
  "Compare average P/E ratios across all sectors",
];

export default function QueryInput({ onQuery, loading }: Props) {
  const [value, setValue] = useState("");

  const submit = () => {
    const q = value.trim();
    if (!q || loading) return;
    onQuery(q);
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask anything about your data in plain English..."
          rows={3}
          className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 pr-14
            text-gray-100 placeholder-gray-600 text-sm font-mono
            focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/30
            resize-none transition-colors"
        />
        <button
          onClick={submit}
          disabled={loading || !value.trim()}
          className="absolute right-3 bottom-3 p-2 rounded-lg bg-green-600 hover:bg-green-500
            disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          {loading
            ? <Loader2 size={16} className="animate-spin text-white" />
            : <Send size={16} className="text-white" />
          }
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-600 flex items-center gap-1 mr-1">
          <Zap size={10} className="text-yellow-500" /> Try:
        </span>
        {SAMPLE_QUESTIONS.slice(0, 4).map((q) => (
          <button
            key={q}
            onClick={() => { setValue(q); onQuery(q); }}
            className="text-xs bg-gray-800/60 hover:bg-gray-700 text-gray-400 hover:text-gray-200
              border border-gray-700 hover:border-gray-600 rounded-lg px-3 py-1.5 transition-all
              text-left max-w-xs truncate"
          >
            {q.length > 52 ? q.slice(0, 52) + "…" : q}
          </button>
        ))}
      </div>
    </div>
  );
}
