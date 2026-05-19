import os
import sqlite3
import json
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).parent / "sample_data.db"

SECTORS = [
    "Technology", "Healthcare", "Financials", "Consumer Discretionary",
    "Industrials", "Communication Services", "Consumer Staples",
    "Energy", "Utilities", "Real Estate", "Materials"
]

COMPANIES = [
    ("AAPL", "Apple Inc.", "Technology", "USA", 1976),
    ("MSFT", "Microsoft Corporation", "Technology", "USA", 1975),
    ("GOOGL", "Alphabet Inc.", "Communication Services", "USA", 1998),
    ("AMZN", "Amazon.com Inc.", "Consumer Discretionary", "USA", 1994),
    ("NVDA", "NVIDIA Corporation", "Technology", "USA", 1993),
    ("META", "Meta Platforms Inc.", "Communication Services", "USA", 2004),
    ("TSLA", "Tesla Inc.", "Consumer Discretionary", "USA", 2003),
    ("BRK", "Berkshire Hathaway", "Financials", "USA", 1839),
    ("JPM", "JPMorgan Chase", "Financials", "USA", 1799),
    ("JNJ", "Johnson & Johnson", "Healthcare", "USA", 1886),
    ("V", "Visa Inc.", "Financials", "USA", 1958),
    ("PG", "Procter & Gamble", "Consumer Staples", "USA", 1837),
    ("UNH", "UnitedHealth Group", "Healthcare", "USA", 1977),
    ("HD", "Home Depot", "Consumer Discretionary", "USA", 1978),
    ("MA", "Mastercard Inc.", "Financials", "USA", 1966),
    ("XOM", "ExxonMobil", "Energy", "USA", 1870),
    ("PFE", "Pfizer Inc.", "Healthcare", "USA", 1849),
    ("KO", "Coca-Cola Company", "Consumer Staples", "USA", 1892),
    ("ABBV", "AbbVie Inc.", "Healthcare", "USA", 2013),
    ("COST", "Costco Wholesale", "Consumer Staples", "USA", 1976),
    ("WMT", "Walmart Inc.", "Consumer Staples", "USA", 1945),
    ("DIS", "Walt Disney Company", "Communication Services", "USA", 1923),
    ("CSCO", "Cisco Systems", "Technology", "USA", 1984),
    ("ORCL", "Oracle Corporation", "Technology", "USA", 1977),
    ("CRM", "Salesforce Inc.", "Technology", "USA", 1999),
    ("INTC", "Intel Corporation", "Technology", "USA", 1968),
    ("AMD", "Advanced Micro Devices", "Technology", "USA", 1969),
    ("NFLX", "Netflix Inc.", "Communication Services", "USA", 1997),
    ("ADBE", "Adobe Inc.", "Technology", "USA", 1982),
    ("PYPL", "PayPal Holdings", "Financials", "USA", 1998),
    ("BAC", "Bank of America", "Financials", "USA", 1904),
    ("GS", "Goldman Sachs", "Financials", "USA", 1869),
    ("MS", "Morgan Stanley", "Financials", "USA", 1935),
    ("CVX", "Chevron Corporation", "Energy", "USA", 1879),
    ("LLY", "Eli Lilly", "Healthcare", "USA", 1876),
    ("MRK", "Merck & Co.", "Healthcare", "USA", 1891),
    ("TMO", "Thermo Fisher", "Healthcare", "USA", 1956),
    ("ABT", "Abbott Laboratories", "Healthcare", "USA", 1888),
    ("AMGN", "Amgen Inc.", "Healthcare", "USA", 1980),
    ("DHR", "Danaher Corporation", "Healthcare", "USA", 1969),
    ("NEE", "NextEra Energy", "Utilities", "USA", 1925),
    ("DUK", "Duke Energy", "Utilities", "USA", 1904),
    ("SO", "Southern Company", "Utilities", "USA", 1945),
    ("AMT", "American Tower", "Real Estate", "USA", 1995),
    ("PLD", "Prologis Inc.", "Real Estate", "USA", 1983),
    ("SPG", "Simon Property Group", "Real Estate", "USA", 1993),
    ("CAT", "Caterpillar Inc.", "Industrials", "USA", 1925),
    ("BA", "Boeing Company", "Industrials", "USA", 1916),
    ("GE", "General Electric", "Industrials", "USA", 1892),
    ("HON", "Honeywell International", "Industrials", "USA", 1906),
    ("MMM", "3M Company", "Industrials", "USA", 1902),
    ("UPS", "UPS Inc.", "Industrials", "USA", 1907),
    ("LMT", "Lockheed Martin", "Industrials", "USA", 1912),
    ("RTX", "RTX Corporation", "Industrials", "USA", 1934),
    ("DE", "Deere & Company", "Industrials", "USA", 1837),
    ("NKE", "Nike Inc.", "Consumer Discretionary", "USA", 1964),
    ("MCD", "McDonald's Corporation", "Consumer Discretionary", "USA", 1940),
    ("SBUX", "Starbucks Corporation", "Consumer Discretionary", "USA", 1971),
    ("TGT", "Target Corporation", "Consumer Discretionary", "USA", 1902),
    ("F", "Ford Motor Company", "Consumer Discretionary", "USA", 1903),
    ("GM", "General Motors", "Consumer Discretionary", "USA", 1908),
    ("T", "AT&T Inc.", "Communication Services", "USA", 1983),
    ("VZ", "Verizon Communications", "Communication Services", "USA", 1983),
    ("CMCSA", "Comcast Corporation", "Communication Services", "USA", 1963),
    ("CHTR", "Charter Communications", "Communication Services", "USA", 1993),
    ("LIN", "Linde plc", "Materials", "USA", 1879),
    ("APD", "Air Products", "Materials", "USA", 1940),
    ("FCX", "Freeport-McMoRan", "Materials", "USA", 1912),
    ("NEM", "Newmont Corporation", "Materials", "USA", 1921),
    ("DOW", "Dow Inc.", "Materials", "USA", 1897),
    ("SHW", "Sherwin-Williams", "Materials", "USA", 1866),
    ("ECL", "Ecolab Inc.", "Materials", "USA", 1923),
    ("TSMC", "Taiwan Semiconductor", "Technology", "Taiwan", 1987),
    ("SAP", "SAP SE", "Technology", "Germany", 1972),
    ("ASML", "ASML Holding", "Technology", "Netherlands", 1984),
    ("NVO", "Novo Nordisk", "Healthcare", "Denmark", 1923),
    ("AZN", "AstraZeneca", "Healthcare", "UK", 1999),
    ("SHEL", "Shell plc", "Energy", "UK", 1907),
    ("BP", "BP plc", "Energy", "UK", 1909),
    ("TTE", "TotalEnergies", "Energy", "France", 1924),
    ("BHP", "BHP Group", "Materials", "Australia", 1885),
    ("RIO", "Rio Tinto", "Materials", "UK", 1873),
    ("SNY", "Sanofi", "Healthcare", "France", 1973),
    ("BABA", "Alibaba Group", "Consumer Discretionary", "China", 1999),
    ("TCEHY", "Tencent Holdings", "Communication Services", "China", 1998),
    ("TSM", "Taiwan Semi ADR", "Technology", "Taiwan", 1987),
    ("SONY", "Sony Group", "Consumer Discretionary", "Japan", 1946),
    ("TM", "Toyota Motor", "Consumer Discretionary", "Japan", 1937),
    ("IBN", "ICICI Bank", "Financials", "India", 1994),
    ("HDB", "HDFC Bank", "Financials", "India", 1994),
    ("INFY", "Infosys Ltd.", "Technology", "India", 1981),
    ("WIT", "Wipro Ltd.", "Technology", "India", 1945),
    ("SQ", "Block Inc.", "Fintech", "USA", 2009),
    ("SNOW", "Snowflake Inc.", "Technology", "USA", 2012),
    ("PLTR", "Palantir Technologies", "Technology", "USA", 2003),
    ("UBER", "Uber Technologies", "Technology", "USA", 2009),
    ("LYFT", "Lyft Inc.", "Technology", "USA", 2012),
    ("ABNB", "Airbnb Inc.", "Consumer Discretionary", "USA", 2008),
    ("DASH", "DoorDash Inc.", "Consumer Discretionary", "USA", 2013),
]


def build_sample_db():
    """Build a rich 5-table SQLite database with realistic financial data."""
    random.seed(42)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS analyst_ratings;
        DROP TABLE IF EXISTS price_history;
        DROP TABLE IF EXISTS financials;
        DROP TABLE IF EXISTS companies;
        DROP TABLE IF EXISTS sectors;

        CREATE TABLE sectors (
            sector_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            description TEXT,
            avg_pe_ratio REAL
        );

        CREATE TABLE companies (
            company_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker       TEXT NOT NULL UNIQUE,
            name         TEXT NOT NULL,
            sector_id    INTEGER NOT NULL,
            country      TEXT NOT NULL,
            founded_year INTEGER,
            employees    INTEGER,
            market_cap_b REAL,
            FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
        );

        CREATE TABLE financials (
            financial_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id      INTEGER NOT NULL,
            fiscal_year     INTEGER NOT NULL,
            revenue_m       REAL,
            net_income_m    REAL,
            gross_margin_pct REAL,
            operating_margin_pct REAL,
            net_margin_pct  REAL,
            eps             REAL,
            pe_ratio        REAL,
            debt_to_equity  REAL,
            roe             REAL,
            dividend_yield  REAL,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE price_history (
            price_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id   INTEGER NOT NULL,
            trade_date   TEXT NOT NULL,
            open_price   REAL,
            close_price  REAL,
            high_price   REAL,
            low_price    REAL,
            volume_m     REAL,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE analyst_ratings (
            rating_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id    INTEGER NOT NULL,
            analyst_firm  TEXT NOT NULL,
            rating        TEXT NOT NULL,
            price_target  REAL,
            rating_date   TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
    """)

    sector_meta = {
        "Technology": ("Software, hardware, semiconductors, and IT services", 28.5),
        "Healthcare": ("Pharmaceuticals, biotech, medical devices, and managed care", 22.1),
        "Financials": ("Banks, insurance, investment banks, and payment processors", 14.2),
        "Consumer Discretionary": ("Retail, autos, restaurants, travel, and entertainment", 24.8),
        "Industrials": ("Aerospace, defense, machinery, transportation, construction", 20.3),
        "Communication Services": ("Telecom, media, and internet platforms", 19.6),
        "Consumer Staples": ("Food, beverages, household products, and personal care", 17.4),
        "Energy": ("Oil, gas, renewable energy, and utilities energy", 12.1),
        "Utilities": ("Electric, gas, and water utilities", 18.9),
        "Real Estate": ("REITs, real estate development, and property management", 21.4),
        "Materials": ("Chemicals, metals, mining, paper, and packaging", 16.7),
        "Fintech": ("Financial technology and digital payments", 35.2),
    }

    sector_ids = {}
    for name, (desc, pe) in sector_meta.items():
        c.execute("INSERT INTO sectors (name, description, avg_pe_ratio) VALUES (?,?,?)", (name, desc, pe))
        sector_ids[name] = c.lastrowid

    company_ids = {}
    analyst_firms = [
        "Goldman Sachs", "Morgan Stanley", "JPMorgan", "Bank of America",
        "Citigroup", "Wells Fargo", "Barclays", "Deutsche Bank",
        "Credit Suisse", "UBS", "Raymond James", "Jefferies"
    ]
    ratings_options = ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"]
    ratings_weights = [0.30, 0.35, 0.25, 0.07, 0.03]

    for ticker, name, sector, country, founded in COMPANIES:
        sid = sector_ids.get(sector, sector_ids["Technology"])
        employees = random.randint(1_000, 450_000)
        mcap = round(random.uniform(5, 3000), 1)
        c.execute(
            "INSERT INTO companies (ticker, name, sector_id, country, founded_year, employees, market_cap_b) VALUES (?,?,?,?,?,?,?)",
            (ticker, name, sid, country, founded, employees, mcap)
        )
        company_ids[ticker] = c.lastrowid

    for ticker, cid in company_ids.items():
        base_rev = random.uniform(500, 80_000)
        for year in [2021, 2022, 2023, 2024]:
            growth = random.uniform(0.92, 1.28)
            base_rev *= growth
            revenue = round(base_rev, 1)
            gm = round(random.uniform(18, 72), 1)
            om = round(gm * random.uniform(0.35, 0.75), 1)
            nm = round(om * random.uniform(0.45, 0.90), 1)
            net_income = round(revenue * nm / 100, 1)
            eps = round(net_income / random.uniform(800, 15_000), 2)
            pe = round(random.uniform(8, 55), 1)
            de = round(random.uniform(0.1, 3.5), 2)
            roe = round(random.uniform(5, 45), 1)
            div = round(random.uniform(0, 4.5), 2)
            c.execute(
                """INSERT INTO financials
                   (company_id, fiscal_year, revenue_m, net_income_m, gross_margin_pct,
                    operating_margin_pct, net_margin_pct, eps, pe_ratio, debt_to_equity, roe, dividend_yield)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (cid, year, revenue, net_income, gm, om, nm, eps, pe, de, roe, div)
            )

    import datetime
    end_date = datetime.date(2025, 1, 31)
    trading_days = []
    d = end_date
    while len(trading_days) < 90:
        if d.weekday() < 5:
            trading_days.append(d.isoformat())
        d -= datetime.timedelta(days=1)
    trading_days.reverse()

    for ticker, cid in company_ids.items():
        price = random.uniform(20, 800)
        for dt in trading_days:
            change = random.uniform(-0.04, 0.04)
            open_p = round(price, 2)
            close_p = round(price * (1 + change), 2)
            high_p = round(max(open_p, close_p) * random.uniform(1.001, 1.025), 2)
            low_p = round(min(open_p, close_p) * random.uniform(0.975, 0.999), 2)
            vol = round(random.uniform(0.5, 80), 2)
            c.execute(
                "INSERT INTO price_history (company_id, trade_date, open_price, close_price, high_price, low_price, volume_m) VALUES (?,?,?,?,?,?,?)",
                (cid, dt, open_p, close_p, high_p, low_p, vol)
            )
            price = close_p

    for ticker, cid in company_ids.items():
        num_ratings = random.randint(2, 5)
        firms_used = random.sample(analyst_firms, num_ratings)
        for firm in firms_used:
            rating = random.choices(ratings_options, weights=ratings_weights)[0]
            current_price = 200
            if rating in ("Strong Buy", "Buy"):
                target = round(current_price * random.uniform(1.05, 1.40), 2)
            elif rating == "Hold":
                target = round(current_price * random.uniform(0.97, 1.08), 2)
            else:
                target = round(current_price * random.uniform(0.65, 0.97), 2)
            days_ago = random.randint(1, 90)
            rdate = (datetime.date(2025, 1, 31) - datetime.timedelta(days=days_ago)).isoformat()
            c.execute(
                "INSERT INTO analyst_ratings (company_id, analyst_firm, rating, price_target, rating_date) VALUES (?,?,?,?,?)",
                (cid, firm, rating, target, rdate)
            )

    conn.commit()
    conn.close()
    print(f"[data_ingestion] Sample DB built at {DB_PATH}")
    print(f"  - {len(COMPANIES)} companies across {len(sector_meta)} sectors")
    print(f"  - {len(COMPANIES) * 4} financial records (2021-2024)")
    print(f"  - {len(COMPANIES) * 90} price history records (90 trading days)")


if __name__ == "__main__":
    build_sample_db()
