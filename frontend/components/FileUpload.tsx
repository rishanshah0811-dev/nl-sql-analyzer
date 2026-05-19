"use client";
import { useRef, useState } from "react";
import { Upload, X, Database, CheckCircle } from "lucide-react";
import { api, UploadResult } from "@/lib/api";

interface Props {
  onUpload: (result: UploadResult) => void;
  onClear: () => void;
  hasUpload: boolean;
}

export default function FileUpload({ onUpload, onClear, hasUpload }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<UploadResult | null>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      setError("Please upload a .csv file.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await api.uploadCsv(file);
      setInfo(result);
      onUpload(result);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleClear = async () => {
    await api.clearUpload();
    setInfo(null);
    onClear();
  };

  return (
    <div className="mb-6">
      {!info ? (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-6 cursor-pointer transition-all text-center
            ${dragging
              ? "border-green-400 bg-green-950/20"
              : "border-gray-700 hover:border-gray-500 bg-gray-900/50"
            }`}
        >
          <Upload className="mx-auto mb-2 text-gray-500" size={28} />
          <p className="text-sm text-gray-400">
            {loading ? "Uploading..." : "Drop a CSV here or click to browse"}
          </p>
          <p className="text-xs text-gray-600 mt-1">or use the pre-loaded S&P 500 sample dataset below</p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <div className="flex items-center justify-between bg-green-950/30 border border-green-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-400" size={20} />
            <div>
              <p className="text-sm font-medium text-green-300">{info.table_name}</p>
              <p className="text-xs text-gray-500">{info.rows_loaded.toLocaleString()} rows · {info.columns.length} columns</p>
            </div>
          </div>
          <button
            onClick={handleClear}
            className="text-gray-500 hover:text-red-400 transition-colors p-1"
          >
            <X size={16} />
          </button>
        </div>
      )}
      {error && (
        <p className="text-red-400 text-xs mt-2 font-mono">{error}</p>
      )}
    </div>
  );
}
