# NL -> SQL Analyzer

Ask questions about data in plain English. Get SQL + results + charts back instantly.

**Live demo:** https://nl-sql-analyzer.vercel.app

## Stack
- **Backend**: FastAPI + Python 3.11, SQLite, pandas, Google Generative AI SDK
- **Frontend**: Next.js 15, Tailwind CSS, Recharts
- **LLM**: Gemini 2.5 Flash with 15 few-shot examples + schema injection + auto-retry

## Setup

### 1. Clone and configure
```bash
cp backend/.env.example backend/.env
# Fill in GOOGLE_API_KEY in backend/.env
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

The sample database builds automatically on first run (~2 seconds).

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — or visit the live app at **https://nl-sql-analyzer.vercel.app**

## Sample Dataset

Pre-loaded with 100 global companies across 5 relational tables:

- **companies** (ticker, name, sector, country, employees, market cap)
- **sectors** (12 industry sectors with metadata)
- **financials** (2021-2024: revenue, margins, EPS, P/E, ROE, dividends)
- **price_history** (90 trading days of OHLCV data)
- **analyst_ratings** (Buy/Hold/Sell ratings from 12 major banks)

## Architecture: How SQL Accuracy Works

1. **Schema injection** - full table structure + 3 sample rows per table passed to every LLM call
2. **15 few-shot examples** - covering SELECT, WHERE, GROUP BY, HAVING, JOINs, subqueries, CTEs, window functions, CASE, LAG, rolling averages
3. **Chain-of-thought rules** - 12 explicit SQLite-specific rules in the system prompt
4. **Auto-retry loop** - if SQL fails, the error and failed query are sent back for correction (up to 3 retries)
5. **Auto chart selection** - backend infers bar/line/scatter based on column types
