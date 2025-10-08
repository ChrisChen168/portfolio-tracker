# Portfolio Tracker (FastAPI + React)

## Backend (FastAPI)

- Create virtualenv and install deps:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run dev server:

```bash
./run.sh
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

- Env (optional):
  - `DATABASE_URL` (default sqlite+aiosqlite:///./portfolio.db)
  - `FRONTEND_ORIGIN` (default http://localhost:5173)
  - `BOND_{SYMBOL}_PRICE` to mock a bond price

## Frontend (Vite + React + Tailwind)

- Ensure Node.js 18+ is installed.
- Install deps and run dev:

```bash
cd frontend
npm i
npm run dev
# App: http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Features
- Dashboard: total value, allocation pie chart
- Assets table: Symbol, Type, Amount, Current Price, Value, P/L
- Add/Edit/Delete assets
- Price refresh: manual button + 30s refetch of portfolio
- Real-time endpoints: stocks (Yahoo Finance), crypto (CoinGecko), bonds (mock), cash FX (Yahoo Finance)

## Notes
- For crypto symbols, CoinGecko markets lookup is best-effort by symbol.
- For cash, use currency codes like `EUR`, `JPY`, `USD`.

