import axios from "axios";

const BASE = "http://localhost:8000";

export interface QueryResult {
  sql: string;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  error: string | null;
  retries: number;
  chart_suggestion: {
    type: "bar" | "bar_grouped" | "line" | "scatter" | "pie" | "none";
    x?: string;
    y?: string;
    extra_y?: string[];
  };
}

export interface SchemaResult {
  schema: string;
}

export interface UploadResult {
  success: boolean;
  table_name: string;
  rows_loaded: number;
  columns: string[];
}

export const api = {
  query: async (question: string, useSample: boolean): Promise<QueryResult> => {
    const res = await axios.post<QueryResult>(`${BASE}/query`, {
      question,
      use_sample: useSample,
    });
    return res.data;
  },

  getSchema: async (useSample: boolean): Promise<SchemaResult> => {
    const res = await axios.get<SchemaResult>(`${BASE}/schema`, {
      params: { use_sample: useSample },
    });
    return res.data;
  },

  uploadCsv: async (file: File): Promise<UploadResult> => {
    const form = new FormData();
    form.append("file", file);
    const res = await axios.post<UploadResult>(`${BASE}/upload`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  clearUpload: async (): Promise<void> => {
    await axios.delete(`${BASE}/upload`);
  },
};
