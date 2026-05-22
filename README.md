# NL -> SQL Analyzer

Ask questions about data in plain English. Get SQL + results + charts back instantly.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit_App-brightgreen?style=for-the-badge)](https://nl-sql-analyzer.vercel.app)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=flat-square&logo=next.js&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

---

## What it does

Type a question like *"Which sectors have the highest average revenue growth?"* and the app:

1. Sends your question + the full database schema to Gemini 2.5 Flash
2. Generates a SQL query with chain-of-thought reasoning
3. Executes it against a SQLite database
4. Returns the results as a table **and** an auto-selected chart (bar, line, scatter, or grouped bar)

No SQL knowledge required. You can also upload your own CSV and query that instead.

## Why I built it

I wanted to explore how far you can push LLM-generated SQL accuracy without fine-tuning. The answer: pretty far, if you give the model enough context. By injecting the full schema with sample rows, 15 few-shot examples, and an auto-retry loop that feeds errors back to the model, the app handles complex queries (JOINs, CTEs, window functions, rolling averages) on the first try.

## Features

- **Natural language to SQL** -- type plain English, get working SQL back
- **Auto-retry loop** -- if a query fails, the error gets sent back to the model for self-correction (up to 3 retries)
- **Auto chart selection** -- backend picks bar/line/scatter/grouped bar based on the column types in the result
- **CSV upload** -- drop in any CSV file and query it immediately
- **Syntax-highlighted SQL** -- generated queries displayed with copy-to-clipboard
- **Query history** -- sidebar tracks your past 20 questions for quick recall
- **Pre-loaded dataset** -- 100 S&P 500 companies across 5 relational tables, ready to query out of the box

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, Tailwind CSS, Recharts, react-syntax-highlighter |
| Backend | FastAPI, Python 3.11, pandas, SQLite |
| LLM | Google Gemini 2.5 Flash via `google-generativeai` SDK |
| Deployment | Vercel (frontend), Railway (backend) |

## How SQL accuracy works

Getting an LLM to write correct SQL is harder than it sounds. Here's the approach:

1. **Schema injection** -- full table structure + 3 sample rows per table get passed to every request, so the model knows exactly what columns exist and what the data looks like
2. **15 few-shot examples** -- hand-written pairs covering SELECT, WHERE, GROUP BY, HAVING, JOINs, subqueries, CTEs, window functions, CASE, LAG, and rolling averages
3. **Chain-of-thought rules** -- 12 explicit SQLite-specific rules in the system prompt (e.g. no ILIKE, use DATE() not CURDATE())
4. **Auto-retry** -- if the SQL throws an error, the error message and failed query get sent back as a follow-up turn for the model to correct itself
5. **Auto chart selection** -- once results come back, the backend inspects column types to pick the right chart

## Sample Dataset

Pre-loaded with 100 global companies across 5 relational tables:

| Table | What's in it |
|-------|-------------|
| `companies` | Ticker, name, sector, country, employees, market cap |
| `sectors` | 12 industry sectors with metadata |
| `financials` | 2021--2024: revenue, margins, EPS, P/E, ROE, dividends |
| `price_history` | 90 trading days of OHLCV data |
| `analyst_ratings` | Buy/Hold/Sell ratings from 12 major banks |

## Run it locally

### 1. Clone and configure
```bash
git clone https://github.com/rishanshah0811-dev/nl-sql-analyzer.git
cd nl-sql-analyzer
cp backend/.env.example backend/.env
# Add your GOOGLE_API_KEY in backend/.env
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

Open [localhost:3000](http://localhost:3000) to use the app locally.

## Project Structure

```
nl-sql-analyzer/
├── backend/
│   ├── main.py              # FastAPI app, routes, CORS
│   ├── sql_generator.py     # Gemini prompt, few-shot examples, retry loop
│   ├── database.py          # Schema extraction, SQL execution, CSV ingestion
│   ├── data_ingestion.py    # Builds the sample SQLite database
│   └── requirements.txt
├── frontend/
│   ├── app/page.tsx          # Main page layout and state
│   ├── components/
│   │   ├── QueryInput.tsx    # Search bar + sample questions
│   │   ├── ResultsPanel.tsx  # SQL display + data table
│   │   ├── ChartView.tsx     # Recharts bar/line/scatter rendering
│   │   └── FileUpload.tsx    # CSV upload + dataset switching
│   └── lib/api.ts            # API client
├── run.py                    # Railway entrypoint
└── README.md
```
