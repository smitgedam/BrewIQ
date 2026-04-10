# BrewIQ — Implementation & Run Guide
**MCA Project | Django 4.2 | Python 3.11+**

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Prerequisites](#2-prerequisites)
3. [Project File Structure](#3-project-file-structure)
4. [Setup — Step by Step](#4-setup--step-by-step)
5. [Running the Project](#5-running-the-project)
6. [Using the Application](#6-using-the-application)
7. [The Intelligence Engine (USP)](#7-the-intelligence-engine-usp)
8. [Troubleshooting Common Issues](#8-troubleshooting-common-issues)
9. [Architecture & Design Decisions](#9-architecture--design-decisions)
10. [Viva Preparation Notes](#10-viva-preparation-notes)

---

## 1. Project Overview

**BrewIQ** is a Django-based Cafe Management System with a built-in AI-like Analytics Engine.

### What makes it unique (USP)
- **Dynamic Pricing Suggestions** — analyses peak-hour sales patterns and suggests optimal price adjustments
- **Demand Forecasting** — predicts tomorrow's item demand using weighted rolling averages
- **Waste Efficiency Score** — daily score (0–100) comparing sold vs wasted inventory
- **Live Kitchen Display System (KDS)** — auto-refreshes every 15 seconds using HTMX (no WebSocket needed)
- **Interactive Revenue Charts** — Chart.js visualisations powered by JSON API endpoints

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 LTS |
| Frontend | Tailwind CSS (CDN) + HTMX + Chart.js |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Analytics | Pandas + NumPy |
| PDF receipts | WeasyPrint |

---

## 2. Prerequisites

### Software Required
- **Python 3.11 or 3.12** — [Download](https://python.org/downloads)
- **pip** — comes bundled with Python 3.11+
- **Git** — [Download](https://git-scm.com/downloads)
- A code editor — **VS Code** is recommended

### Verify Python installation
```bash
python --version        # Should show 3.11.x or higher
# On some systems use:
python3 --version
```

---

## 3. Project File Structure

```
brewiq/
├── manage.py                         # Django entry point
├── requirements.txt                  # All Python dependencies
├── .env.example                      # Environment variable template
├── .gitignore
├── IMPLEMENTATION_GUIDE.md           # This file
│
├── config/                           # Project-level configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py                   # Shared settings
│   │   ├── development.py            # SQLite, DEBUG=True
│   │   └── production.py            # PostgreSQL, DEBUG=False
│   ├── urls.py                       # Root URL dispatcher
│   └── wsgi.py
│
├── apps/                             # All Django applications
│   ├── accounts/                     # Auth, roles, staff management
│   │   ├── models.py                 # StaffProfile (OneToOne → User)
│   │   ├── views.py                  # Login, logout, staff CRUD
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── decorators.py             # @role_required decorator
│   │   └── admin.py
│   │
│   ├── menu/                         # Menu categories & items
│   │   ├── models.py                 # Category, MenuItem
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   │
│   ├── orders/                       # Order lifecycle, KDS, tables
│   │   ├── models.py                 # CafeTable, Order, OrderItem
│   │   ├── views.py                  # Dashboard, KDS, order CRUD
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           └── seed_demo_data.py  # Demo data seeder
│   │
│   ├── inventory/                    # Ingredients, stock movements
│   │   ├── models.py                 # Ingredient, MenuItemIngredient, StockMovement
│   │   ├── views.py
│   │   ├── signals.py                # Auto-deduct on order completion
│   │   └── apps.py                   # Registers signals in ready()
│   │
│   ├── billing/                      # Bills, GST, print receipts
│   │   ├── models.py                 # Bill, GSTRate
│   │   ├── views.py
│   │   └── utils.py                  # Decimal-safe GST computation
│   │
│   └── intelligence/                 # ★ THE USP ★
│       ├── engine.py                 # Pandas/NumPy analytics core
│       ├── models.py                 # PricingSuggestion, DemandForecast
│       ├── views.py                  # Dashboard + JSON chart APIs
│       └── urls.py
│
├── templates/                        # HTML templates
│   ├── base.html                     # Master layout with sidebar
│   ├── partials/
│   │   ├── _kds_list.html            # HTMX-swapped KDS content
│   │   └── _order_status_badge.html
│   ├── accounts/
│   ├── menu/
│   ├── orders/
│   ├── inventory/
│   ├── billing/
│   └── intelligence/
│
├── static/                           # CSS, JS, images
└── media/                            # User uploads (menu images)
```

---

## 4. Setup — Step by Step

### Step 1 — Extract the Project

Unzip the downloaded file into a folder of your choice:
```bash
unzip brewiq.zip -d ~/projects/
cd ~/projects/brewiq
```

### Step 2 — Create a Virtual Environment

A virtual environment isolates this project's dependencies from your system Python.

```bash
# Create the virtual environment
py -3.12 -m venv venv
# OR
python -m venv venv

# Activate it
# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On macOS / Linux:
source venv/bin/activate
```

You should see `(venv)` prefixed in your terminal prompt.

### Step 3 — Create the Environment File

Copy the example file and edit it:
```bash
# On macOS / Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

Open `.env` in your editor. For development, the defaults work fine:
```
SECRET_KEY=my-brewiq-secret-key-change-me-in-prod
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Django, Pandas, NumPy, HTMX helpers, WeasyPrint, and other libraries.
It takes about 2–3 minutes on first run. You should see `Successfully installed ...` at the end.

> **Note for Windows users:** If WeasyPrint fails to install, it requires GTK. Either:
> - Skip WeasyPrint for now (print receipts won't generate PDF, but the HTML print view still works), OR
> - Install GTK from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

### Step 5 — Run Database Migrations

Migrations create all the database tables from the model definitions:
```bash
python manage.py migrate
```

Expected output ends with something like:
```
Applying intelligence.0001_initial... OK
```

### Step 6 — Seed Demo Data

This creates sample menu items, tables, staff accounts, and ingredients so you can explore the system immediately:
```bash
python manage.py seed_demo_data
```

Expected output:
```
🌱 Seeding BrewIQ demo data...
  ✓ Superuser  admin / admin123
  ✓ MANAGER    manager1 / staff123
  ✓ CASHIER    cashier1 / staff123
  ✓ CHEF       chef1 / staff123
  ✓ Menu categories & items
  ✓ 10 cafe tables (T1–T10)
  ✓ Ingredients & menu-item links
  ✓ Default GST rate (5%)

✅ Demo data seeded successfully!
   Admin login → username: admin  password: admin123
```

### Step 7 — Collect Static Files (Optional for dev)

```bash
python manage.py collectstatic --noinput
```

Not strictly required for development, but good practice.

---

## 5. Running the Project

### Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

You will be redirected to the login page automatically.

### Login Credentials

| Role    | Username   | Password  |
|---------|------------|-----------|
| Admin   | admin      | admin123  |
| Manager | manager1   | staff123  |
| Cashier | cashier1   | staff123  |
| Chef    | chef1      | staff123  |

---

## 6. Using the Application

### Workflow — Taking a Complete Order

Follow this sequence to see the full system in action:

**1. Create an order**
- Click **"+ New Order"** in the sidebar
- Select Order Type (Dine In / Takeaway)
- Select a table (for Dine In)
- Click **"Continue to Add Items"**

**2. Add items**
- Click any menu item card to add it to the cart
- Use `+` / `−` buttons to change quantities
- Click **"Confirm Order"** when ready

**3. Kitchen processes it**
- Open a second browser tab and log in as `chef1`
- Go to **Kitchen Display** in the sidebar
- The order appears — click **"Start Preparing"** then **"Mark Ready"**
- The KDS auto-refreshes every 15 seconds without page reload

**4. Generate a bill**
- Go back to the order (as admin or cashier)
- Click **"Generate Bill"** → choose payment mode → **"Confirm Payment"**
- A GST-inclusive bill is generated. Click **"Print"** for the receipt

**5. Check inventory**
- Go to **Inventory** → stock was automatically deducted when the order completed

### Running the Intelligence Engine

1. First, complete several orders over a few days (or use the demo orders)
2. Go to **🧠 BrewIQ Engine** in the sidebar
3. Click **"▶ Run Engine Now"**
4. The engine analyses order history and displays:
   - Pricing suggestions (accept/reject each one)
   - Tomorrow's demand forecast
   - Waste efficiency score
   - Revenue and top-items charts

> **Note:** The engine needs at least 7 days of completed orders to generate pricing suggestions. For a demo, you can temporarily lower `MIN_DAYS_FOR_SUGGESTION = 2` in `apps/intelligence/engine.py`.

---

## 7. The Intelligence Engine (USP)

The file `apps/intelligence/engine.py` contains the entire analytical brain. Here's what each function does:

### `compute_pricing_suggestions()`
```
1. Fetches all completed OrderItem records from the last 30 days
2. Converts to a Pandas DataFrame
3. Groups by menu item → then by hour-of-day
4. Calculates mean hourly demand for each item
5. Finds the peak hour (max demand)
6. Computes deviation = (peak - mean) / mean
7. If deviation ≥ 25%, generates a suggestion:
   suggested_price = base_price × (1 + deviation × 0.4)
8. Returns sorted list of suggestion dicts
```

### `compute_demand_forecasts()`
```
1. Fetches 14 days of completed order history
2. Calculates daily totals per item
3. Applies weekday weighting: same weekday × 0.7 + overall mean × 0.3
4. Returns predicted quantity for each item for tomorrow
```

### `compute_daily_waste_score()`
```
1. Counts auto-deducted stock (from completed orders) as "productive"
2. Counts manually logged WASTE movements as "waste"
3. Score = (productive / total) × 100
4. Maps to grade: Excellent / Good / Fair / Needs Attention
```

### Modifying Thresholds

Open `apps/intelligence/engine.py` and adjust these constants at the top:

```python
PEAK_DEVIATION_THRESHOLD = 0.25   # 0.25 = 25% spike triggers a suggestion
MIN_DAYS_FOR_SUGGESTION  = 7      # Lower to 2 for demo purposes
PRICE_UPLIFT_FACTOR      = 0.40   # How aggressive the price suggestion is
FORECAST_WINDOW_DAYS     = 14     # Days of history for demand forecast
```

---

## 8. Troubleshooting Common Issues

### "ModuleNotFoundError: No module named 'decouple'"
You forgot to activate the virtual environment, or install requirements:
```bash
source venv/bin/activate      # activate first
pip install -r requirements.txt
```

### "django.db.utils.OperationalError: no such table"
Migrations haven't been run:
```bash
python manage.py migrate
```

### "ImproperlyConfigured: SECRET_KEY" error
Your `.env` file is missing. Copy it from the example:
```bash
cp .env.example .env
```

### Port 8000 already in use
Either stop the other process, or run on a different port:
```bash
python manage.py runserver 8080
```

### Static files (CSS) not loading
```bash
python manage.py collectstatic --noinput
```
Or check that `STATICFILES_DIRS` in `config/settings/base.py` points to your `static/` folder.

### WeasyPrint error on Windows
WeasyPrint requires GTK on Windows. As a workaround:
- Comment out the WeasyPrint import in `apps/billing/views.py`
- The HTML print view (`/billing/<pk>/print/`) still works perfectly and can be printed from the browser

### Intelligence engine shows "not enough data"
This is expected on a fresh install — the engine requires at least 7 days of completed orders. For immediate demo:

1. Open `apps/intelligence/engine.py`
2. Change `MIN_DAYS_FOR_SUGGESTION = 7` to `MIN_DAYS_FOR_SUGGESTION = 1`
3. Create and complete a few orders
4. Run the engine

### Django Debug Toolbar not showing
Ensure you're accessing via `http://127.0.0.1:8000` (not `localhost`) — the toolbar only renders for `INTERNAL_IPS = ['127.0.0.1']`.

---

## 9. Architecture & Design Decisions

Understanding these decisions will help in your viva.

### Why Django (not Flask)?
Django is "batteries-included" — it ships with ORM, admin panel, authentication, migrations, and a template engine. Flask requires assembling these separately. For an MCA project with multiple models and relationships, Django reduces boilerplate significantly.

### Why HTMX (not React/Vue)?
HTMX lets the server return HTML fragments directly, which HTMX swaps into the DOM. This gives SPA-like interactivity (no page reload) without writing a single line of JavaScript framework code. The KDS auto-refresh uses `hx-trigger="every 15s"` — one HTML attribute replaces 50 lines of polling JavaScript.

### Why Pandas for analytics (not raw Python)?
Pandas vectorises operations over entire DataFrames in optimised C code. A Python `for` loop over 10,000 order records takes ~50ms; the equivalent Pandas `groupby().sum()` takes ~2ms. More importantly, Pandas code is readable — the intent is clear.

### Why `unit_price` is snapshotted in OrderItem?
Menu prices change over time. If `OrderItem` referenced `MenuItem.current_price` directly, reprinting a 6-month-old bill would show today's price, not the price at the time of order. Snapshotting `unit_price` at order creation is a fundamental financial data integrity requirement.

### Why use Django Signals for inventory deduction?
The signal in `apps/inventory/signals.py` listens for `Order.status → COMPLETED` transitions and automatically deducts ingredient stock. This means the deduction logic does not live inside the billing view — it is triggered regardless of which view changes the order status. This demonstrates the **Observer pattern** and **separation of concerns**.

### Why split settings into base / development / production?
Following the [12-Factor App](https://12factor.net) methodology. Configuration that changes between environments (database URL, secret keys, debug mode) lives in environment variables and environment-specific settings files — not hardcoded. This is the industry standard.

---

## 10. Viva Preparation Notes

These are the questions evaluators commonly ask for MCA-level Django projects:

**Q: What is Django's MTV pattern?**
A: Model (database schema via ORM), Template (HTML with Django template language), View (Python function/class that handles request → returns response). It's Django's interpretation of MVC — the "Controller" logic is in the URL dispatcher.

**Q: How does HTMX work in this project?**
A: The KDS view has `hx-trigger="every 15s" hx-get="/orders/kds/partial/"`. Every 15 seconds, HTMX makes an XHR GET request and swaps the returned HTML into the DOM — no page reload, no JavaScript required.

**Q: What is the N+1 query problem and how did you avoid it?**
A: N+1 occurs when you loop over N objects and make a separate DB query for each related object (N+1 total queries). Fixed with `select_related('table', 'created_by')` for ForeignKey (JOINs) and `prefetch_related('items__menu_item')` for reverse FK / M2M (separate optimised queries).

**Q: How does the Intelligence Engine work?**
A: It fetches completed OrderItem records for the last 30 days using Django ORM, converts them to a Pandas DataFrame, groups by item and hour, computes mean vs peak demand, and flags items with a deviation above 25% as candidates for a price uplift. No external ML library is needed — it's applied statistics.

**Q: Why use Decimal instead of float for money?**
A: IEEE 754 floating-point cannot represent many decimal fractions exactly — `0.1 + 0.2 == 0.30000000000000004` in Python. Financial calculations must use Python's `decimal.Decimal` with `ROUND_HALF_UP` to avoid accumulating rounding errors across thousands of bills.

**Q: How is role-based access control implemented?**
A: The `@role_required('ADMIN', 'MANAGER')` decorator in `apps/accounts/decorators.py` checks `request.user.profile.role` before allowing access to a view. If the role is insufficient, the user is redirected to the dashboard with an error message. Django's built-in `Groups` system could alternatively be used.

**Q: What happens when an order is marked COMPLETED?**
A: A Django signal (`post_save` on `Order`) fires in `apps/inventory/signals.py`. It iterates over each OrderItem, looks up the `MenuItemIngredient` links, and deducts the appropriate quantity of each ingredient from stock — also logging a `StockMovement` record for audit trail.

---

## Quick Reference — Key URLs

| URL | Description |
|-----|-------------|
| `/` | Redirects to dashboard |
| `/accounts/login/` | Login page |
| `/orders/dashboard/` | Main dashboard |
| `/orders/create/` | Create new order |
| `/orders/kds/` | Kitchen Display System |
| `/menu/` | Menu management |
| `/inventory/` | Inventory dashboard |
| `/billing/list/` | Billing history |
| `/intelligence/` | BrewIQ Engine dashboard |
| `/admin/` | Django admin panel |

---

*BrewIQ — MCA Project | Built with Django 4.2, Pandas, HTMX, Tailwind CSS*
