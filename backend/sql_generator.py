import re
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from database import execute_sql, get_schema_with_samples

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

FEW_SHOT_EXAMPLES = """
EXAMPLE 1 — Simple SELECT with filter:
Q: Show all technology companies from the USA
SQL:
SELECT c.ticker, c.name, c.country, c.market_cap_b
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
WHERE s.name = 'Technology' AND c.country = 'USA'
ORDER BY c.market_cap_b DESC;

EXAMPLE 2 — Aggregation with GROUP BY:
Q: What is the average market cap by sector?
SQL:
SELECT s.name AS sector, ROUND(AVG(c.market_cap_b), 2) AS avg_market_cap_b,
       COUNT(*) AS company_count
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
GROUP BY s.sector_id, s.name
ORDER BY avg_market_cap_b DESC;

EXAMPLE 3 — HAVING clause:
Q: Which sectors have more than 10 companies?
SQL:
SELECT s.name AS sector, COUNT(*) AS company_count
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
GROUP BY s.sector_id, s.name
HAVING COUNT(*) > 10
ORDER BY company_count DESC;

EXAMPLE 4 — Multi-table JOIN with aliases:
Q: Show the 2024 revenue and net income for all technology companies
SQL:
SELECT c.ticker, c.name, f.revenue_m, f.net_income_m, f.net_margin_pct
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
JOIN financials f ON c.company_id = f.company_id
WHERE s.name = 'Technology' AND f.fiscal_year = 2024
ORDER BY f.revenue_m DESC;

EXAMPLE 5 — Subquery:
Q: Which companies have a market cap above the average?
SQL:
SELECT ticker, name, market_cap_b
FROM companies
WHERE market_cap_b > (SELECT AVG(market_cap_b) FROM companies)
ORDER BY market_cap_b DESC;

EXAMPLE 6 — Window function (RANK):
Q: Rank companies within each sector by 2024 revenue
SQL:
SELECT c.ticker, c.name, s.name AS sector, f.revenue_m,
       RANK() OVER (PARTITION BY s.sector_id ORDER BY f.revenue_m DESC) AS revenue_rank
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
JOIN financials f ON c.company_id = f.company_id
WHERE f.fiscal_year = 2024
ORDER BY s.name, revenue_rank;

EXAMPLE 7 — CTE (Common Table Expression):
Q: Which companies had revenue growth greater than 20% from 2023 to 2024?
SQL:
WITH rev_2023 AS (
    SELECT company_id, revenue_m AS rev_2023
    FROM financials WHERE fiscal_year = 2023
),
rev_2024 AS (
    SELECT company_id, revenue_m AS rev_2024
    FROM financials WHERE fiscal_year = 2024
)
SELECT c.ticker, c.name,
       r3.rev_2023, r4.rev_2024,
       ROUND((r4.rev_2024 - r3.rev_2023) / r3.rev_2023 * 100, 1) AS growth_pct
FROM companies c
JOIN rev_2023 r3 ON c.company_id = r3.company_id
JOIN rev_2024 r4 ON c.company_id = r4.company_id
WHERE (r4.rev_2024 - r3.rev_2023) / r3.rev_2023 > 0.20
ORDER BY growth_pct DESC;

EXAMPLE 8 — Multiple aggregations + date filtering:
Q: What was the highest closing price for each company in January 2025?
SQL:
SELECT c.ticker, c.name, MAX(ph.close_price) AS highest_close,
       MIN(ph.close_price) AS lowest_close,
       ROUND(AVG(ph.close_price), 2) AS avg_close
FROM companies c
JOIN price_history ph ON c.company_id = ph.company_id
WHERE ph.trade_date BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY c.company_id, c.ticker, c.name
ORDER BY highest_close DESC;

EXAMPLE 9 — Nested CTE + window function:
Q: For each sector, show the company with the highest ROE in 2024
SQL:
WITH sector_roe AS (
    SELECT c.company_id, c.ticker, c.name, s.name AS sector,
           f.roe,
           RANK() OVER (PARTITION BY s.sector_id ORDER BY f.roe DESC) AS rnk
    FROM companies c
    JOIN sectors s ON c.sector_id = s.sector_id
    JOIN financials f ON c.company_id = f.company_id
    WHERE f.fiscal_year = 2024
)
SELECT ticker, name, sector, roe
FROM sector_roe
WHERE rnk = 1
ORDER BY roe DESC;

EXAMPLE 10 — Analyst sentiment aggregation:
Q: Which companies have the most 'Strong Buy' ratings?
SQL:
SELECT c.ticker, c.name, COUNT(*) AS strong_buy_count
FROM companies c
JOIN analyst_ratings ar ON c.company_id = ar.company_id
WHERE ar.rating = 'Strong Buy'
GROUP BY c.company_id, c.ticker, c.name
ORDER BY strong_buy_count DESC
LIMIT 10;

EXAMPLE 11 — Self-referencing aggregation:
Q: Compare 2024 profit margins: which sector has the highest average net margin?
SQL:
SELECT s.name AS sector,
       ROUND(AVG(f.net_margin_pct), 2) AS avg_net_margin,
       ROUND(AVG(f.gross_margin_pct), 2) AS avg_gross_margin,
       ROUND(AVG(f.operating_margin_pct), 2) AS avg_operating_margin,
       COUNT(*) AS company_count
FROM sectors s
JOIN companies c ON s.sector_id = c.sector_id
JOIN financials f ON c.company_id = f.company_id
WHERE f.fiscal_year = 2024
GROUP BY s.sector_id, s.name
ORDER BY avg_net_margin DESC;

EXAMPLE 12 — CASE expression:
Q: Categorise companies by market cap size: Large (>500B), Mid (50-500B), Small (<50B)
SQL:
SELECT ticker, name, market_cap_b,
       CASE
           WHEN market_cap_b > 500 THEN 'Large Cap'
           WHEN market_cap_b BETWEEN 50 AND 500 THEN 'Mid Cap'
           ELSE 'Small Cap'
       END AS cap_category
FROM companies
ORDER BY market_cap_b DESC;

EXAMPLE 13 — Year-over-year change with LAG:
Q: Show year-over-year revenue change for Apple
SQL:
SELECT fiscal_year, revenue_m,
       LAG(revenue_m) OVER (ORDER BY fiscal_year) AS prev_year_revenue,
       ROUND((revenue_m - LAG(revenue_m) OVER (ORDER BY fiscal_year)) /
             LAG(revenue_m) OVER (ORDER BY fiscal_year) * 100, 1) AS yoy_growth_pct
FROM financials f
JOIN companies c ON f.company_id = c.company_id
WHERE c.ticker = 'AAPL'
ORDER BY fiscal_year;

EXAMPLE 14 — Complex multi-condition filter:
Q: Find companies with high debt but also high ROE in 2024 (debt_to_equity > 1.5 AND roe > 20)
SQL:
SELECT c.ticker, c.name, s.name AS sector,
       f.debt_to_equity, f.roe, f.net_margin_pct, f.revenue_m
FROM companies c
JOIN sectors s ON c.sector_id = s.sector_id
JOIN financials f ON c.company_id = f.company_id
WHERE f.fiscal_year = 2024
  AND f.debt_to_equity > 1.5
  AND f.roe > 20
ORDER BY f.roe DESC;

EXAMPLE 15 — Rolling average with window:
Q: Show the 7-day rolling average closing price for NVIDIA
SQL:
SELECT ph.trade_date, ph.close_price,
       ROUND(AVG(ph.close_price) OVER (
           ORDER BY ph.trade_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 2) AS rolling_7d_avg
FROM price_history ph
JOIN companies c ON ph.company_id = c.company_id
WHERE c.ticker = 'NVDA'
ORDER BY ph.trade_date;
"""


def build_system_prompt(schema_str: str) -> str:
    return f"""You are an expert SQL data analyst with 20 years of experience. Your ONLY job is to convert natural language questions into perfectly correct SQLite SQL queries.

## DATABASE SCHEMA
{schema_str}

## RULES — FOLLOW EVERY ONE WITHOUT EXCEPTION
1. Output ONLY the raw SQL query. No explanation, no markdown, no code fences, no comments, no preamble.
2. Always use explicit JOIN syntax (never comma-joins like FROM a, b).
3. Always qualify column names with table aliases when more than one table is used.
4. For SQLite: use strftime('%Y', date_column) for year extraction; use LIKE (not ILIKE) for case-insensitive text; use julianday() for date math.
5. For window functions: always include the full OVER() clause.
6. For GROUP BY: include every non-aggregated SELECT column in the GROUP BY clause.
7. Never use LIMIT unless the question explicitly asks for "top N" or "bottom N".
8. When the question involves percentages, always use ROUND(..., 2).
9. If the question is ambiguous, make the most reasonable assumption and proceed.
10. Always ORDER BY the most meaningful column (revenue DESC, date ASC, count DESC, etc.) unless the user specifies otherwise.
11. For year-over-year comparisons, always use CTEs or self-joins — never subqueries inside WHERE clauses.
12. Use double-quotes for identifiers and single-quotes for string literals.

## FEW-SHOT EXAMPLES
{FEW_SHOT_EXAMPLES}

## OUTPUT FORMAT
Return EXACTLY ONE SQL statement. Nothing else. No markdown. No backticks. No comments."""


def extract_sql(text: str) -> str:
    """Strip any accidental markdown fences or leading/trailing text."""
    text = text.strip()
    text = re.sub(r"```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    lines = text.strip().splitlines()
    sql_lines = []
    started = False
    for line in lines:
        stripped = line.strip().upper()
        if not started:
            if any(stripped.startswith(kw) for kw in ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE")):
                started = True
                sql_lines.append(line)
        else:
            sql_lines.append(line)
    return "\n".join(sql_lines).strip() if sql_lines else text.strip()


def nl_to_sql(question: str, db_path, max_retries: int = 3) -> dict:
    """
    Convert a natural language question to SQL and execute it.
    """
    schema_str = get_schema_with_samples(db_path)
    system_prompt = build_system_prompt(schema_str)

    sql_model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=system_prompt,
    )

    conversation = [{"role": "user", "parts": [question]}]
    last_sql = ""
    last_error = ""

    for attempt in range(max_retries):
        if attempt > 0:
            conversation.append({"role": "model", "parts": [last_sql]})
            conversation.append({
                "role": "user",
                "parts": [
                    f"That SQL failed with this error:\n{last_error}\n\n"
                    f"Fix the SQL and return ONLY the corrected query. No explanation."
                ]
            })

        response = sql_model.generate_content(
            conversation,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.0,
            ),
        )

        raw = response.text
        sql = extract_sql(raw)
        last_sql = sql

        result = execute_sql(db_path, sql)
        if result["error"] is None:
            chart = suggest_chart(result["columns"], result["rows"])
            return {
                "sql": sql,
                "columns": result["columns"],
                "rows": result["rows"],
                "row_count": result["row_count"],
                "error": None,
                "retries": attempt,
                "chart_suggestion": chart
            }
        else:
            last_error = result["error"]

    return {
        "sql": last_sql,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "error": f"Failed after {max_retries} attempts. Last error: {last_error}",
        "retries": max_retries,
        "chart_suggestion": {"type": "none"}
    }


def suggest_chart(columns: list, rows: list) -> dict:
    """
    Determine the best chart type based on column names and data types.
    """
    if len(columns) < 2 or len(rows) == 0:
        return {"type": "none"}

    numeric_cols = []
    text_cols = []
    date_cols = []

    for col in columns:
        sample_values = [r[col] for r in rows[:5] if r[col] is not None]
        if not sample_values:
            text_cols.append(col)
            continue
        col_lower = col.lower()
        if any(kw in col_lower for kw in ("date", "time", "year", "month", "day", "period")):
            date_cols.append(col)
        elif all(isinstance(v, (int, float)) for v in sample_values):
            numeric_cols.append(col)
        else:
            text_cols.append(col)

    if date_cols and numeric_cols:
        return {"type": "line", "x": date_cols[0], "y": numeric_cols[0], "extra_y": numeric_cols[1:3]}

    if text_cols and len(numeric_cols) == 1:
        return {"type": "bar", "x": text_cols[0], "y": numeric_cols[0]}

    if text_cols and len(numeric_cols) > 1:
        return {"type": "bar_grouped", "x": text_cols[0], "y": numeric_cols[:3]}

    if len(numeric_cols) >= 2:
        return {"type": "scatter", "x": numeric_cols[0], "y": numeric_cols[1]}

    return {"type": "none"}
