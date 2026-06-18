from __future__ import annotations

import os
import html
import hmac
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

APP_NAME = "ConvergeLABS Command OS"
PLATFORM_NAME = "ConvergeLABS"
WORKSPACE_NAME = "RealHype"
PRODUCT_SUBTITLE = "Business Intelligence & Operations Control Center"
VERTICAL_NAME = "Direct Commerce / Instagram Sales / CTT Portugal"
DEFAULT_DB_URL = "sqlite:///realhype_local.db"

# -----------------------------
# Visual
# -----------------------------
st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide")

CUSTOM_CSS = """
<style>
:root {
  --canvas: #0A0A0C; --surface-1: #111114; --surface-2: #18181D; --surface-3: #1F1F26;
  --hairline: #2A2A35; --text-primary: #F0F0F5; --text-secondary: #9CA3AF; --text-muted: #6B7280;
  --accent: #F5C542; --accent-hover: #FFD76A; --accent-soft: rgba(245,197,66,.14);
  --accent-border: rgba(245,197,66,.28); --success: #22C55E; --warning: #F59E0B;
  --danger: #EF4444; --info: #38BDF8; --radius: 10px; --radius-sm: 7px;
  --bg: var(--canvas); --sidebar: var(--canvas); --surface: var(--surface-1); --border: var(--hairline);
  --text: var(--text-primary); --muted: var(--text-secondary); --muted-2: var(--text-muted);
  --gold: var(--accent); --gold-soft: var(--accent-soft); --green: var(--success); --yellow: var(--warning); --red: var(--danger);
  --rh-bg: var(--canvas); --rh-card: var(--surface-1); --rh-card-2: var(--surface-2);
  --rh-gold: var(--accent); --rh-gold-light: var(--accent-hover); --rh-cyan: var(--info);
  --rh-text: var(--text-primary); --rh-muted: var(--text-secondary); --rh-danger: var(--danger); --rh-success: var(--success);
}
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--rh-bg);
  color: var(--rh-text);
}
[data-testid="stHeader"] { background: rgba(10,10,12,.94); backdrop-filter: blur(12px); }
[data-testid="stToolbar"], footer { visibility: hidden; }
.block-container { max-width: 1480px; padding: 1.2rem 2rem 3rem; }
[data-testid="stSidebar"] {
  background: var(--sidebar);
  border-right: 1px solid var(--hairline);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--text-secondary); }
[data-testid="stSidebar"] [role="radiogroup"] label {
  border-radius: var(--radius-sm);
  padding: .3rem .5rem;
  transition: all .2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: var(--accent-soft); color: var(--accent-hover); box-shadow: inset 2px 0 var(--accent);
}
h1, h2, h3 { color: var(--text-primary); letter-spacing: -.01em; }
h2, h3 { border-bottom: 1px solid var(--hairline); padding-bottom: .5rem; }
.rh-brand { font-size: 1.05rem; font-weight: 850; letter-spacing: .1em; color: var(--text-primary); }
.rh-brand span { color: var(--accent); }
.rh-eyebrow { margin: 0 0 .3rem; color: var(--accent); font-size: .68rem; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
.rh-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--accent-border);
  background: linear-gradient(135deg, var(--accent-soft), var(--surface-1) 42%, var(--canvas));
  border-radius: var(--radius);
  padding: 1rem 1.15rem;
  box-shadow: 0 10px 28px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.03);
}
.rh-title { color: var(--text-primary); font-size: clamp(1.3rem, 2.2vw, 1.8rem); font-weight: 800; letter-spacing: -.025em; margin: 0; }
.rh-title span { color: var(--accent); }
.rh-subtitle { color: var(--text-secondary); font-size: .82rem; margin: .35rem 0 .75rem; }
.rh-chip {
  display: inline-block; padding: .28rem .62rem; margin: 0 .35rem .25rem 0;
  border-radius: 999px; border: 1px solid var(--accent-border);
  background: var(--accent-soft); color: var(--accent-hover); font-size: .68rem;
}
.rh-section { margin: 1.35rem 0 .5rem; color: var(--rh-gold-light); font-size: .76rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
.rh-form-card {
  border: 1px solid var(--hairline); border-radius: var(--radius); padding: .3rem .9rem .9rem;
  background: var(--surface-1);
}
.rh-alert { border-left: 3px solid var(--accent); padding: .75rem .9rem; border-radius: var(--radius-sm); background: var(--accent-soft); }
.rh-user { border: 1px solid var(--hairline); background: var(--surface-1); border-radius: var(--radius); padding: .65rem .8rem; margin: .75rem 0 .9rem; }
.rh-ai-layer { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:.2rem 0 1rem; padding:.7rem .85rem; border:1px solid var(--accent-border); border-radius:var(--radius); background:var(--surface-1); }
.rh-ai-layer strong { color:var(--text-primary); font-size:.78rem; }
.rh-ai-layer span { color:var(--text-secondary); font-size:.72rem; }
.rh-ai-layer .rh-ai-name { color:var(--accent); font-weight:800; letter-spacing:.06em; text-transform:uppercase; }
.small-muted { color: var(--rh-muted); font-size: .75rem; }
[data-testid="stMetric"] {
  min-height: 96px; padding: .72rem .82rem; border: 1px solid var(--hairline);
  border-radius: var(--radius); background: var(--surface);
  box-shadow: inset 2px 0 var(--accent-border), 0 6px 16px rgba(0,0,0,.14);
}
[data-testid="stMetric"]:hover { border-color: var(--accent-border); transform: translateY(-1px); }
[data-testid="stMetricLabel"] { color: var(--text-secondary); }
[data-testid="stMetricValue"] { color: var(--text-primary); font-weight: 800; }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border: 1px solid var(--accent) !important; border-radius: var(--radius-sm) !important; color: var(--canvas) !important; font-weight: 750 !important;
  background: var(--accent) !important; box-shadow: none; transition: all .18s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover { background: var(--accent-hover) !important; transform: translateY(-1px); box-shadow: 0 8px 22px rgba(245,197,66,.2); }
.stLinkButton a, a { color: var(--accent) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--hairline); border-radius: var(--radius); overflow: hidden; }
[data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid var(--hairline); }
[data-baseweb="tab"] { border-radius: 9px 9px 0 0; }
[data-baseweb="input"], [data-baseweb="select"] > div, textarea {
  background: var(--surface-2) !important; border-color: var(--hairline) !important;
}
hr { border-color: var(--hairline) !important; }
.rh-badge { display:inline-flex; padding:.16rem .48rem; border-radius:999px; font-size:.72rem; font-weight:700; border:1px solid var(--border); }
.rh-badge-green { color:#86EFAC; background:rgba(34,197,94,.10); }
.rh-badge-yellow { color:#FCD34D; background:rgba(245,158,11,.10); }
.rh-badge-red { color:#FCA5A5; background:rgba(239,68,68,.10); }
.rh-empty { padding:1.3rem; border:1px dashed var(--border); border-radius:var(--radius); background:var(--surface); color:var(--muted); }
.rh-empty b { color:var(--text); }
*:focus-visible { outline:2px solid var(--accent) !important; outline-offset:2px; }
@media (max-width: 768px) { .block-container { padding: 1rem .85rem 2rem; } .rh-hero { padding: 1.2rem; } }
</style>
"""
def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


inject_css()

# -----------------------------
# Database
# -----------------------------
def _normalize_db_url(raw_url: str) -> str:
    scheme, separator, remainder = raw_url.partition("://")
    if separator and scheme in {"postgres", "postgresql"}:
        return f"postgresql+psycopg2{separator}{remainder}"
    return raw_url


def get_db_url() -> str:
    try:
        raw_url = st.secrets["database"]["url"]
        if raw_url:
            return _normalize_db_url(raw_url)
    except Exception:
        pass
    return DEFAULT_DB_URL


@st.cache_resource
def get_engine(db_url: str) -> Engine:
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)


engine = get_engine(get_db_url())


def execute(sql: str, params: Optional[Dict[str, Any]] = None) -> None:
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def query_df(sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    with engine.begin() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def scalar(sql: str, params: Optional[Dict[str, Any]] = None, default: Any = 0) -> Any:
    with engine.begin() as conn:
        val = conn.execute(text(sql), params or {}).scalar()
        return default if val is None else val


def init_db() -> None:
    # SQL compatible with PostgreSQL and SQLite via SQLAlchemy text.
    execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER NOT NULL DEFAULT 0,
        reorder_point INTEGER NOT NULL DEFAULT 1,
        cost_brl NUMERIC(12,2) NOT NULL DEFAULT 0,
        sale_price_eur NUMERIC(12,2),
        active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER NOT NULL DEFAULT 0,
        reorder_point INTEGER NOT NULL DEFAULT 1,
        cost_brl REAL NOT NULL DEFAULT 0,
        sale_price_eur REAL,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        name TEXT NOT NULL,
        contact TEXT,
        ig_handle TEXT,
        channel TEXT DEFAULT 'Instagram',
        interest TEXT,
        stage TEXT NOT NULL DEFAULT 'lead',
        owner TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        ig_handle TEXT,
        channel TEXT DEFAULT 'Instagram',
        interest TEXT,
        stage TEXT NOT NULL DEFAULT 'lead',
        owner TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        lead_id INTEGER NOT NULL,
        direction TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER NOT NULL,
        direction TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        lead_id INTEGER,
        status TEXT NOT NULL DEFAULT 'reservado',
        ctt_status TEXT NOT NULL DEFAULT 'pendente',
        confirmation_status TEXT NOT NULL DEFAULT 'pendente',
        total_eur NUMERIC(12,2) NOT NULL DEFAULT 0,
        total_brl NUMERIC(12,2) NOT NULL DEFAULT 0,
        notes TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        status TEXT NOT NULL DEFAULT 'reservado',
        ctt_status TEXT NOT NULL DEFAULT 'pendente',
        confirmation_status TEXT NOT NULL DEFAULT 'pendente',
        total_eur REAL NOT NULL DEFAULT 0,
        total_brl REAL NOT NULL DEFAULT 0,
        notes TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        unit_price_eur NUMERIC(12,2) NOT NULL,
        unit_cost_brl NUMERIC(12,2) NOT NULL
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        unit_price_eur REAL NOT NULL,
        unit_cost_brl REAL NOT NULL
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        product_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,
        qty INTEGER NOT NULL,
        reason TEXT,
        user_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,
        qty INTEGER NOT NULL,
        reason TEXT,
        user_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        expense_date DATE NOT NULL,
        category TEXT NOT NULL,
        amount_brl NUMERIC(12,2) NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if not get_db_url().startswith("sqlite") else """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount_brl REAL NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    execute("INSERT INTO settings (key, value) VALUES ('eur_brl', '5.80') ON CONFLICT (key) DO NOTHING" if not get_db_url().startswith("sqlite") else "INSERT OR IGNORE INTO settings (key, value) VALUES ('eur_brl', '5.80')")


def _column_exists(table_name: str, column_name: str) -> bool:
    if get_db_url().startswith("sqlite"):
        with engine.begin() as conn:
            columns = conn.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
        return any(column["name"] == column_name for column in columns)
    return bool(scalar("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema='public' AND table_name=:table_name AND column_name=:column_name
    """, {"table_name": table_name, "column_name": column_name}))


def _ensure_column(table_name: str, column_name: str, definition: str) -> None:
    allowed_tables = {"products", "leads", "orders", "stock_movements"}
    if table_name not in allowed_tables or not column_name.replace("_", "").isalnum():
        raise ValueError("Migração inválida.")
    if not _column_exists(table_name, column_name):
        execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def ensure_schema() -> None:
    """Migração aditiva, idempotente e sem remoção de dados existentes."""
    init_db()
    additions = {
        "leads": {
            "temperature": "TEXT DEFAULT 'morno'", "urgency": "TEXT DEFAULT 'normal'",
            "next_action": "TEXT", "next_action_at": "TIMESTAMP", "last_interaction_at": "TIMESTAMP",
        },
        "orders": {
            "channel": "TEXT DEFAULT 'Instagram'", "text_confirmed": "INTEGER DEFAULT 0",
            "address_validated": "INTEGER DEFAULT 0", "phone_validated": "INTEGER DEFAULT 0",
            "pickup_deadline": "DATE", "returned": "INTEGER DEFAULT 0", "return_reason": "TEXT",
        },
        "products": {
            "currency": "TEXT DEFAULT 'EUR'", "description": "TEXT", "tags": "TEXT",
            "warranty_notes": "TEXT", "updated_at": "TIMESTAMP",
        },
        "stock_movements": {"notes": "TEXT", "movement_date": "DATE"},
    }
    for table_name, columns in additions.items():
        for column_name, definition in columns.items():
            _ensure_column(table_name, column_name, definition)

    identity = "INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY" if not get_db_url().startswith("sqlite") else "INTEGER PRIMARY KEY AUTOINCREMENT"
    execute(f"""
        CREATE TABLE IF NOT EXISTS campaign_metrics (
            id {identity}, campaign TEXT NOT NULL, creative TEXT, channel TEXT,
            investment_brl REAL NOT NULL DEFAULT 0, messages_received INTEGER NOT NULL DEFAULT 0,
            leads_count INTEGER NOT NULL DEFAULT 0, sales_count INTEGER NOT NULL DEFAULT 0,
            revenue_brl REAL NOT NULL DEFAULT 0, notes TEXT, metric_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    execute(f"""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id {identity}, actor TEXT, role TEXT, action TEXT NOT NULL, entity_type TEXT,
            entity_id TEXT, before_data TEXT, after_data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    defaults = {
        "app_version": "2026.1", "default_currency": "BRL", "packaging_cost_brl": "0",
        "ctt_cost_brl": "0", "daily_revenue_goal_brl": "0", "monthly_sales_goal": "0",
    }
    for key, value in defaults.items():
        sql = "INSERT INTO settings (key,value) VALUES (:key,:value) ON CONFLICT (key) DO NOTHING" if not get_db_url().startswith("sqlite") else "INSERT OR IGNORE INTO settings (key,value) VALUES (:key,:value)"
        execute(sql, {"key": key, "value": value})


if os.environ.get("REALHYPE_SKIP_DB_INIT") != "1":
    ensure_schema()

# -----------------------------
# Auth
# -----------------------------
def get_users() -> Dict[str, Dict[str, str]]:
    try:
        users = st.secrets.get("users", {})
        if users:
            return {u: dict(v) for u, v in users.items()}
    except Exception:
        pass
    return {}


def login() -> bool:
    if st.session_state.get("auth"):
        return True
    st.markdown("""
    <div class="rh-hero">
      <p class="rh-eyebrow">ConvergeLABS</p>
      <p class="rh-title">ConvergeLABS <span>Command OS</span></p>
      <p class="rh-subtitle">Business Intelligence &amp; Operations Control Center</p>
      <span class="rh-chip">Workspace: RealHype</span><span class="rh-chip">Direct Commerce</span><span class="rh-chip">CTT Portugal</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")
    if ok:
        users = get_users()
        stored_password = str(users.get(username, {}).get("password", ""))
        if username in users and stored_password and hmac.compare_digest(str(password), stored_password):
            st.session_state["auth"] = True
            st.session_state["username"] = username
            st.session_state["role"] = users[username].get("role", "sdr")
            st.session_state["display_name"] = users[username].get("name", username)
            st.rerun()
        else:
            st.error("Login inválido.")
    st.info("Configure os usuarios e senhas em Secrets antes de acessar o dashboard.")
    return False


if not login():
    st.stop()

ROLE = str(st.session_state.get("role", "sdr")).lower()
DISPLAY_NAME = st.session_state.get("display_name", "Usuário")
IS_PARTNER = ROLE == "partner"
SAFE_DISPLAY_NAME = html.escape(str(DISPLAY_NAME))
SAFE_ROLE = html.escape(ROLE.upper())
TZ = ZoneInfo("America/Sao_Paulo")
VALID_SALE_STATUSES = {"confirmado", "preparando envio", "enviado", "entregue"}

# -----------------------------
# Helpers
# -----------------------------
def get_eur_rate() -> float:
    try:
        return float(scalar("SELECT value FROM settings WHERE key='eur_brl'", default="5.80"))
    except Exception:
        return 5.8


def money_eur(v: Any) -> str:
    return f"€ {float(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def money_brl(v: Any) -> str:
    return f"R$ {float(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_conn():
    return engine.begin()


def run_query(sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    return query_df(sql, params)


def execute_query(sql: str, params: Optional[Dict[str, Any]] = None) -> None:
    execute(sql, params)


def require_role(*allowed_roles: str) -> None:
    if ROLE not in allowed_roles:
        st.error("Você não tem permissão para acessar esta área.")
        st.stop()


def log_action(action: str, entity_type: str = "system", entity_id: Any = None, before_data: str = "", after_data: str = "") -> None:
    execute("""
        INSERT INTO audit_logs (actor, role, action, entity_type, entity_id, before_data, after_data)
        VALUES (:actor, :role, :action, :entity_type, :entity_id, :before_data, :after_data)
    """, {"actor": DISPLAY_NAME, "role": ROLE, "action": action[:120], "entity_type": entity_type[:80], "entity_id": str(entity_id or "")[:80], "before_data": before_data[:2000], "after_data": after_data[:2000]})


def money(value: Any, currency: str = "BRL") -> str:
    return money_brl(value) if currency == "BRL" else money_eur(value)


def pct(value: Any) -> str:
    return f"{safe_float(value):.1f}%".replace(".", ",")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def status_badge(status: str) -> str:
    normalized = (status or "info").lower()
    tone = "green" if normalized in {"ok", "cliente", "confirmado", "entregue", "ativo"} else "red" if normalized in {"crítico", "zerado", "devolvido", "cancelado", "perdido"} else "yellow"
    return f'<span class="rh-badge rh-badge-{tone}">{html.escape(status or "—")}</span>'


def priority_badge(priority: str) -> str:
    return status_badge(priority)


def metric_card(label: str, value: Any, delta: Optional[str] = None, help_text: Optional[str] = None) -> None:
    st.metric(label, value, delta=delta, help=help_text)


def page_topbar(title: str, subtitle: str, primary_action: str = "") -> None:
    left, right = st.columns([5, 2])
    with left:
        st.markdown(f"## {title}")
        st.caption(subtitle)
    with right:
        st.caption(datetime.now(TZ).strftime("%d/%m/%Y · %H:%M BRT"))
        if st.button("Atualizar", key=f"refresh_{title}", width="stretch"):
            st.rerun()
    if primary_action:
        st.caption(f"Ação principal · {primary_action}")


def admin_table(data: pd.DataFrame, empty_message: str = "Nenhum registro encontrado.") -> None:
    if data.empty:
        empty_state("Sem dados", empty_message)
    else:
        st.dataframe(data, width="stretch", hide_index=True)


def empty_state(title: str, message: str) -> None:
    st.markdown(f'<div class="rh-empty"><b>{html.escape(title)}</b><br><span>{html.escape(message)}</span></div>', unsafe_allow_html=True)


def export_csv_button(data: pd.DataFrame, filename: str, label: str = "Exportar CSV") -> None:
    st.download_button(label, data.to_csv(index=False).encode("utf-8-sig"), file_name=filename, mime="text/csv", disabled=data.empty)


def calculate_metrics() -> Dict[str, float]:
    sales = query_df("SELECT total_brl, created_at FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue')")
    items = query_df("SELECT oi.qty, oi.unit_cost_brl FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE o.status IN ('confirmado','preparando envio','enviado','entregue')")
    leads_count = safe_int(scalar("SELECT COUNT(*) FROM leads"))
    revenue = safe_float(sales["total_brl"].sum()) if not sales.empty else 0
    cmv = safe_float((items["qty"] * items["unit_cost_brl"]).sum()) if not items.empty else 0
    sales_count = len(sales)
    return {"revenue": revenue, "cmv": cmv, "profit": revenue - cmv, "margin": ((revenue - cmv) / revenue * 100) if revenue else 0, "ticket": revenue / sales_count if sales_count else 0, "conversion": sales_count / leads_count * 100 if leads_count else 0, "sales_count": sales_count, "leads_count": leads_count}


def classify_products_abc() -> pd.DataFrame:
    data = query_df("""
        SELECT p.sku, p.name AS produto, COALESCE(SUM(oi.qty * oi.unit_price_eur),0) AS receita_eur
        FROM products p LEFT JOIN order_items oi ON oi.product_id=p.id
        LEFT JOIN orders o ON o.id=oi.order_id AND o.status IN ('confirmado','preparando envio','enviado','entregue')
        GROUP BY p.id,p.sku,p.name ORDER BY receita_eur DESC
    """)
    if data.empty or safe_float(data["receita_eur"].sum()) == 0:
        return pd.DataFrame()
    data["acumulado_pct"] = data["receita_eur"].cumsum() / data["receita_eur"].sum() * 100
    data["classe"] = data["acumulado_pct"].apply(lambda value: "A" if value <= 80 else "B" if value <= 95 else "C")
    return data


def forecast_revenue_30d() -> Dict[str, float]:
    sales = query_df("SELECT total_brl, created_at FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue') AND created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'" if not get_db_url().startswith("sqlite") else "SELECT total_brl, created_at FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue') AND created_at >= datetime('now','-30 days')")
    if sales.empty:
        return {"daily_average": 0, "forecast_30d": 0, "days": 0}
    sales["created_at"] = pd.to_datetime(sales["created_at"], errors="coerce")
    daily = sales.dropna(subset=["created_at"]).groupby(sales["created_at"].dt.date)["total_brl"].sum()
    average = safe_float(daily.tail(14).mean()) if not daily.empty else 0
    return {"daily_average": average, "forecast_30d": average * 30, "days": len(daily)}


def build_heatmap_data() -> pd.DataFrame:
    sales = query_df("SELECT created_at, total_brl FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue')")
    if sales.empty:
        return pd.DataFrame()
    sales["created_at"] = pd.to_datetime(sales["created_at"], errors="coerce")
    sales = sales.dropna(subset=["created_at"])
    if sales.empty:
        return pd.DataFrame()
    days = {0:"Seg",1:"Ter",2:"Qua",3:"Qui",4:"Sex",5:"Sáb",6:"Dom"}
    sales["dia"] = sales["created_at"].dt.dayofweek.map(days)
    sales["hora"] = sales["created_at"].dt.hour
    result = sales.pivot_table(index="dia", columns="hora", values="total_brl", aggfunc="sum", fill_value=0)
    result.columns = result.columns.astype(str)
    return result


def build_cohort_data() -> pd.DataFrame:
    data = query_df("""
        SELECT l.id, MIN(o.created_at) AS primeira_compra, COUNT(o.id) AS pedidos, COALESCE(SUM(o.total_brl),0) AS receita_brl
        FROM leads l JOIN orders o ON o.lead_id=l.id
        WHERE o.status IN ('confirmado','preparando envio','enviado','entregue') GROUP BY l.id
    """)
    if data.empty:
        return data
    data["primeira_compra"] = pd.to_datetime(data["primeira_compra"], errors="coerce")
    data["coorte"] = data["primeira_compra"].dt.to_period("M").astype(str)
    return data.groupby("coorte", as_index=False).agg(clientes=("id", "count"), pedidos=("pedidos", "sum"), receita_brl=("receita_brl", "sum"))


def detect_alerts() -> pd.DataFrame:
    alerts = []
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    critical = query_df("SELECT sku,name,quantity,reorder_point FROM products WHERE active=1 AND quantity<=reorder_point ORDER BY quantity")
    for row in critical.itertuples():
        severity = "crítico" if safe_int(row.quantity) == 0 else "atenção"
        alerts.append({"Severidade": severity, "Entidade": row.sku, "Descrição": f"{row.name}: {row.quantity} un. (mínimo {row.reorder_point})", "Ação recomendada": "Repor stock ou pausar oferta", "Data": now})
    risky_orders = query_df("SELECT id,status,ctt_status FROM orders WHERE status NOT IN ('entregue','cancelado') AND (confirmation_status='pendente' OR ctt_status='devolvido') ORDER BY id DESC LIMIT 50")
    for row in risky_orders.itertuples():
        alerts.append({"Severidade": "crítico" if row.ctt_status == "devolvido" else "atenção", "Entidade": f"Pedido #{row.id}", "Descrição": "Devolução CTT" if row.ctt_status == "devolvido" else "Confirmação pendente", "Ação recomendada": "Validar cliente e dados de envio", "Data": now})
    stale_sql = "SELECT id,name FROM leads WHERE stage NOT IN ('cliente','perdido') AND COALESCE(last_interaction_at,created_at) < CURRENT_TIMESTAMP - INTERVAL '24 hours' LIMIT 50" if not get_db_url().startswith("sqlite") else "SELECT id,name FROM leads WHERE stage NOT IN ('cliente','perdido') AND COALESCE(last_interaction_at,created_at) < datetime('now','-24 hours') LIMIT 50"
    for row in query_df(stale_sql).itertuples():
        alerts.append({"Severidade":"atenção","Entidade":f"Lead #{row.id}","Descrição":f"{row.name} está sem interação há mais de 24h","Ação recomendada":"Priorizar follow-up do SDR","Data":now})
    idle = query_df("SELECT p.sku,p.name FROM products p WHERE p.active=1 AND p.quantity>0 AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id=p.id) LIMIT 30")
    for row in idle.itertuples():
        alerts.append({"Severidade":"info","Entidade":row.sku,"Descrição":f"{row.name} possui stock e nenhuma venda registrada","Ação recomendada":"Revisar oferta, criativo ou exposição","Data":now})
    rate = get_eur_rate()
    low_margin = query_df("SELECT sku,name,cost_brl,sale_price_eur FROM products WHERE active=1 AND sale_price_eur IS NOT NULL")
    for row in low_margin.itertuples():
        margin = safe_float(row.sale_price_eur)*rate-safe_float(row.cost_brl)
        if margin > 0 and margin < safe_float(row.cost_brl)*0.2:
            alerts.append({"Severidade":"atenção","Entidade":row.sku,"Descrição":f"{row.name} tem margem bruta estimada abaixo de 20% do custo","Ação recomendada":"Revisar preço ou custo","Data":now})
    daily_sales = query_df("SELECT created_at,total_brl FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue')")
    if not daily_sales.empty:
        daily_sales["created_at"] = pd.to_datetime(daily_sales["created_at"],errors="coerce")
        daily = daily_sales.dropna(subset=["created_at"]).groupby(daily_sales["created_at"].dt.date)["total_brl"].sum()
        if len(daily) >= 7:
            baseline = daily.iloc[:-1].tail(14)
            current = safe_float(daily.iloc[-1])
            deviation = safe_float(baseline.std())
            if deviation and abs(current-safe_float(baseline.mean())) > deviation*2:
                alerts.append({"Severidade":"atenção","Entidade":"Receita","Descrição":"Receita diária fora do padrão recente","Ação recomendada":"Verificar campanha, tracking e operação","Data":now})
    return pd.DataFrame(alerts)


# -----------------------------
# Data operations
# -----------------------------
def add_product(sku: str, name: str, category: str, qty: int, reorder_point: int, cost_brl: float, sale_price_eur: float, currency: str = "EUR", description: str = "", tags: str = "", warranty_notes: str = "", active: int = 1):
    execute(
        """
        INSERT INTO products (sku, name, category, quantity, reorder_point, cost_brl, sale_price_eur, currency, description, tags, warranty_notes, active, updated_at)
        VALUES (:sku, :name, :category, :quantity, :reorder_point, :cost_brl, :sale_price_eur, :currency, :description, :tags, :warranty_notes, :active, CURRENT_TIMESTAMP)
        ON CONFLICT (sku) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            quantity = excluded.quantity,
            reorder_point = excluded.reorder_point,
            cost_brl = excluded.cost_brl,
            sale_price_eur = excluded.sale_price_eur,
            currency=excluded.currency, description=excluded.description, tags=excluded.tags,
            warranty_notes=excluded.warranty_notes, active=excluded.active, updated_at=CURRENT_TIMESTAMP
        """ if not get_db_url().startswith("sqlite") else """
        INSERT INTO products (sku, name, category, quantity, reorder_point, cost_brl, sale_price_eur, currency, description, tags, warranty_notes, active, updated_at)
        VALUES (:sku, :name, :category, :quantity, :reorder_point, :cost_brl, :sale_price_eur, :currency, :description, :tags, :warranty_notes, :active, CURRENT_TIMESTAMP)
        ON CONFLICT(sku) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            quantity = excluded.quantity,
            reorder_point = excluded.reorder_point,
            cost_brl = excluded.cost_brl,
            sale_price_eur = excluded.sale_price_eur,
            currency=excluded.currency, description=excluded.description, tags=excluded.tags,
            warranty_notes=excluded.warranty_notes, active=excluded.active, updated_at=CURRENT_TIMESTAMP
        """,
        {"sku": sku, "name": name, "category": category, "quantity": qty, "reorder_point": reorder_point, "cost_brl": cost_brl, "sale_price_eur": sale_price_eur, "currency": currency, "description": description, "tags": tags, "warranty_notes": warranty_notes, "active": active},
    )
    log_action("product_upserted", "product", sku, after_data=f"active={active}; quantity={qty}")


def add_lead(name: str, contact: str, ig_handle: str, channel: str, interest: str, stage: str, notes: str, temperature: str = "morno", urgency: str = "normal", next_action: str = "", next_action_at: Optional[date] = None):
    execute(
        """
        INSERT INTO leads (name, contact, ig_handle, channel, interest, stage, owner, notes, temperature, urgency, next_action, next_action_at)
        VALUES (:name, :contact, :ig_handle, :channel, :interest, :stage, :owner, :notes, :temperature, :urgency, :next_action, :next_action_at)
        """,
        {"name": name, "contact": contact, "ig_handle": ig_handle, "channel": channel, "interest": interest, "stage": stage, "owner": DISPLAY_NAME, "notes": notes, "temperature": temperature, "urgency": urgency, "next_action": next_action or None, "next_action_at": str(next_action_at) if next_action_at else None},
    )
    log_action("lead_created", "lead", after_data=f"status={stage}; canal={channel}")


def update_lead_stage(lead_id: int, stage: str):
    execute("UPDATE leads SET stage=:stage, updated_at=CURRENT_TIMESTAMP WHERE id=:id", {"stage": stage, "id": lead_id})
    log_action("lead_status_updated", "lead", lead_id, after_data=f"status={stage}")


def add_message(lead_id: int, direction: str, content: str):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO messages (lead_id, direction, content) VALUES (:lead_id, :direction, :content)"), {"lead_id": lead_id, "direction": direction, "content": content})
        conn.execute(text("UPDATE leads SET last_interaction_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE id=:lead_id"), {"lead_id": lead_id})
    log_action("message_registered", "lead", lead_id, after_data=f"direction={direction}")


def create_order(lead_id: Optional[int], product_id: int, qty: int, unit_price_eur: float, status: str, confirmation_status: str, ctt_status: str, notes: str, channel: str = "Instagram"):
    rate = get_eur_rate()
    stock_statuses = VALID_SALE_STATUSES
    reduces_stock = status in stock_statuses
    with engine.begin() as conn:
        product_sql = "SELECT quantity, cost_brl FROM products WHERE id=:id"
        if not get_db_url().startswith("sqlite"):
            product_sql += " FOR UPDATE"
        product = conn.execute(text(product_sql), {"id": product_id}).mappings().first()
        if not product:
            raise ValueError("Produto não encontrado.")
        current_qty = int(product["quantity"] or 0)
        if reduces_stock and qty > current_qty:
            raise ValueError(f"Stock insuficiente. Disponível: {current_qty}")
        unit_cost_brl = float(product["cost_brl"] or 0)
        total_eur = unit_price_eur * qty
        total_brl = total_eur * rate
        insert_order = """
            INSERT INTO orders (lead_id, status, ctt_status, confirmation_status, total_eur, total_brl, notes, created_by, channel)
            VALUES (:lead_id, :status, :ctt_status, :confirmation_status, :total_eur, :total_brl, :notes, :created_by, :channel)
        """
        params = {"lead_id": lead_id, "status": status, "ctt_status": ctt_status, "confirmation_status": confirmation_status, "total_eur": total_eur, "total_brl": total_brl, "notes": notes, "created_by": DISPLAY_NAME, "channel": channel}
        if get_db_url().startswith("sqlite"):
            result = conn.execute(text(insert_order), params)
            order_id = result.lastrowid
        else:
            order_id = conn.execute(text(insert_order + " RETURNING id"), params).scalar_one()
        conn.execute(text("""
            INSERT INTO order_items (order_id, product_id, qty, unit_price_eur, unit_cost_brl)
            VALUES (:order_id, :product_id, :qty, :unit_price_eur, :unit_cost_brl)
        """), {"order_id": order_id, "product_id": product_id, "qty": qty, "unit_price_eur": unit_price_eur, "unit_cost_brl": unit_cost_brl})
        if reduces_stock:
            updated = conn.execute(text("UPDATE products SET quantity = quantity - :qty WHERE id=:product_id AND quantity >= :qty"), {"qty": qty, "product_id": product_id})
            if updated.rowcount != 1:
                raise ValueError("Stock alterado por outro usuário. Atualize o painel e tente novamente.")
            conn.execute(text("""
                INSERT INTO stock_movements (product_id, movement_type, qty, reason, user_name)
                VALUES (:product_id, 'saida', :qty, :reason, :user_name)
            """), {"product_id": product_id, "qty": -qty, "reason": f"Venda #{order_id} · {status}", "user_name": DISPLAY_NAME})
        if lead_id and status in stock_statuses:
            conn.execute(text("UPDATE leads SET stage='cliente', updated_at=CURRENT_TIMESTAMP WHERE id=:lead_id"), {"lead_id": lead_id})
    return order_id


def adjust_stock(product_id: int, movement_type: str, qty: int, reason: str, notes: str = "") -> None:
    if qty <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    if not reason.strip():
        raise ValueError("O motivo é obrigatório.")
    delta = qty if movement_type in {"entrada", "ajuste", "devolucao"} else -qty
    with engine.begin() as conn:
        updated = conn.execute(
            text("UPDATE products SET quantity = quantity + :delta WHERE id=:product_id AND quantity + :delta >= 0"),
            {"delta": delta, "product_id": product_id},
        )
        if updated.rowcount != 1:
            raise ValueError("Stock insuficiente para esta saída ou produto não encontrado.")
        conn.execute(
            text("""
                INSERT INTO stock_movements (product_id, movement_type, qty, reason, user_name, notes, movement_date)
                VALUES (:product_id, :movement_type, :qty, :reason, :user_name, :notes, :movement_date)
            """),
            {"product_id": product_id, "movement_type": movement_type, "qty": delta, "reason": reason.strip(), "user_name": DISPLAY_NAME, "notes": notes.strip(), "movement_date": str(date.today())},
        )
    log_action("stock_adjusted", "product", product_id, after_data=f"type={movement_type}; qty={delta}")


def update_order_ctt(order_id: int, text_confirmed: bool, address_validated: bool, phone_validated: bool, pickup_deadline: Optional[date], ctt_status: str, returned: bool, return_reason: str, notes: str) -> None:
    require_role("partner", "sdr")
    execute("""
        UPDATE orders SET text_confirmed=:text_confirmed, address_validated=:address_validated,
            phone_validated=:phone_validated, pickup_deadline=:pickup_deadline, ctt_status=:ctt_status,
            returned=:returned, return_reason=:return_reason, notes=:notes, updated_at=CURRENT_TIMESTAMP
        WHERE id=:order_id
    """, {"text_confirmed": int(text_confirmed), "address_validated": int(address_validated), "phone_validated": int(phone_validated), "pickup_deadline": str(pickup_deadline) if pickup_deadline else None, "ctt_status": ctt_status, "returned": int(returned), "return_reason": return_reason.strip(), "notes": notes.strip(), "order_id": order_id})
    log_action("ctt_order_updated", "order", order_id, after_data=f"ctt_status={ctt_status}; returned={int(returned)}")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown('<div class="rh-brand">CONVERGE<span>LABS</span></div><div class="small-muted">COMMAND OS · Workspace RealHype</div><div class="small-muted"><span class="rh-badge rh-badge-green">AO VIVO</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rh-user"><b>{SAFE_DISPLAY_NAME}</b><br><span class="small-muted">PERFIL · {SAFE_ROLE}</span></div>', unsafe_allow_html=True)
    partner_pages = ["Command Center", "Leads / CRM", "CTT / Pedidos", "Stock", "Growth", "Financeiro", "Configurações", "Vendas", "Produtos", "Alertas"]
    sdr_pages = ["Command Center", "Leads / CRM", "CTT / Pedidos", "Stock", "Vendas", "Alertas"]
    nav_labels = {
        "Command Center": "Pulse", "Leads / CRM": "Sell", "CTT / Pedidos": "Ship",
        "Stock": "Stock", "Growth": "Growth", "Financeiro": "Intel", "Configurações": "Config",
        "Vendas": "Vendas", "Produtos": "Produtos", "Alertas": "Alertas",
    }
    allowed_pages = partner_pages if IS_PARTNER else sdr_pages
    if st.session_state.get("page") == "Visão Geral" or st.session_state.get("page") not in allowed_pages:
        st.session_state["page"] = "Command Center"
    page = st.radio("NAVEGAÇÃO", allowed_pages, key="page", format_func=lambda item: nav_labels.get(item, item))
    st.divider()
    command = st.selectbox("IR PARA / EXECUTAR", ["Selecionar ação", "Novo lead", "Nova venda", "Movimento de stock", "Ver pedidos CTT", "Ver stock crítico", "Ver financeiro"], key="command_palette")
    command_pages = {"Novo lead":"Leads / CRM", "Nova venda":"Vendas", "Movimento de stock":"Stock", "Ver pedidos CTT":"CTT / Pedidos", "Ver stock crítico":"Stock", "Ver financeiro":"Financeiro"}
    if command == "Selecionar ação":
        st.session_state.pop("last_command", None)
    elif command in command_pages and st.session_state.get("last_command") != command:
        target = command_pages[command]
        if target in allowed_pages:
            st.session_state["last_command"] = command
            st.session_state["page"] = target
            st.rerun()
        else:
            st.warning("Ação restrita ao perfil partner.")
    with st.expander("Filtros globais"):
        st.selectbox("Período", ["Hoje", "7 dias", "30 dias", "Todo período"], key="global_period")
        st.selectbox("Canal", ["Todos", "Instagram", "WhatsApp", "Outro"], key="global_channel")
        st.text_input("Responsável", key="global_owner")
    st.divider()
    st.caption(f"● Ao Vivo\n\nAtualizado {datetime.now(TZ).strftime('%d/%m %H:%M')}\n\nConvergeLABS · v2026.1")
    if st.button("Sair", width="stretch"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# Header
# -----------------------------
header_left, header_search, header_right = st.columns([4, 2, 1])
with header_left:
    st.markdown(f"""
<div class="rh-hero">
  <p class="rh-eyebrow">Business Intelligence &amp; Operations Control Center</p>
  <p class="rh-title">ConvergeLABS <span>Command OS</span></p>
  <p class="rh-subtitle">Direct Commerce / Instagram Sales / CTT Portugal</p>
  <span class="rh-chip">Workspace: RealHype</span><span class="rh-chip">Ao Vivo</span><span class="rh-chip">{SAFE_DISPLAY_NAME} · {SAFE_ROLE}</span>
</div>
""", unsafe_allow_html=True)
with header_right:
    st.write("")
    st.write("")
    if st.button("↻ Atualizar painel", width="stretch"):
        st.rerun()
with header_search:
    st.text_input("Command palette", placeholder="Buscar lead, pedido, SKU ou ação...", key="global_search")
st.write("")
st.markdown("""
<div class="rh-ai-layer">
  <div><span class="rh-ai-name">ConvergeLABS AI Layer</span><br><strong>Assistência operacional baseada em sinais</strong></div>
  <span>Sugestões heurísticas; nenhuma ação é executada automaticamente.</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Pages
# -----------------------------
if page == "Command Center":
    page_topbar("Pulse", "Decisões prioritárias da operação em tempo real.", "Revisar alertas")
    today_filter = "DATE(created_at)=CURRENT_DATE" if not get_db_url().startswith("sqlite") else "DATE(created_at)=DATE('now')"
    order_today_filter = "DATE(o.created_at)=CURRENT_DATE" if not get_db_url().startswith("sqlite") else "DATE(o.created_at)=DATE('now')"
    leads_today = scalar(f"SELECT COUNT(*) FROM leads WHERE {today_filter}")
    sales_today = scalar(f"SELECT COUNT(*) FROM orders WHERE {today_filter} AND status IN ('confirmado','preparando envio','enviado','entregue')")
    revenue_today = scalar(f"SELECT COALESCE(SUM(total_brl),0) FROM orders WHERE {today_filter} AND status IN ('confirmado','preparando envio','enviado','entregue')")
    cost_today = scalar(f"SELECT COALESCE(SUM(oi.qty*oi.unit_cost_brl),0) FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE {order_today_filter} AND o.status IN ('confirmado','preparando envio','enviado','entregue')")
    leads_total = scalar("SELECT COUNT(*) FROM leads")
    sales_total = scalar("SELECT COUNT(*) FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue')")
    pending_orders = scalar("SELECT COUNT(*) FROM orders WHERE status NOT IN ('entregue','devolvido','cancelado')")
    low_stock_count = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity <= reorder_point")
    returns = scalar("SELECT COUNT(*) FROM orders WHERE status='devolvido' OR ctt_status='devolvido'")
    kpis = st.columns(4)
    kpis2 = st.columns(4)
    kpis[0].metric("Receita hoje", money_brl(revenue_today) if IS_PARTNER else "Restrito", help="Soma das vendas válidas criadas hoje")
    kpis[1].metric("Lucro estimado hoje", money_brl(safe_float(revenue_today)-safe_float(cost_today)) if IS_PARTNER else "Restrito", help="Receita hoje menos CMV estimado")
    kpis[2].metric("Leads hoje", safe_int(leads_today), help="Leads criados no dia")
    kpis[3].metric("Vendas hoje", safe_int(sales_today), help="Vendas em status operacional válido")
    kpis2[0].metric("Conversão lead → venda", pct(safe_int(sales_total)/safe_int(leads_total)*100 if leads_total else 0), help="Vendas válidas / leads totais")
    kpis2[1].metric("Pedidos pendentes", safe_int(pending_orders), help="Pedidos ainda não entregues, devolvidos ou cancelados")
    kpis2[2].metric("Stock crítico", safe_int(low_stock_count), help="Produtos com unidades abaixo ou iguais ao mínimo")
    kpis2[3].metric("Devoluções / risco CTT", safe_int(returns), help="Pedidos marcados como devolvidos")
    alerts = detect_alerts()
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Ações recomendadas")
        if alerts.empty:
            empty_state("Operação estável", "Nenhuma ação crítica detectada agora.")
        else:
            admin_table(alerts.head(6))
        st.subheader("Atividade recente")
        activity = query_df("SELECT created_at AS Data, action AS Ação, actor AS Responsável, entity_type AS Entidade FROM audit_logs ORDER BY id DESC LIMIT 8")
        admin_table(activity, "As próximas ações registradas aparecerão aqui.")
    with right:
        st.subheader("Produtos que merecem atenção")
        low = query_df('SELECT sku AS "SKU", name AS "Produto", quantity AS "Unidades", reorder_point AS "Mínimo" FROM products WHERE active=1 AND quantity<=reorder_point ORDER BY quantity LIMIT 10')
        admin_table(low, "Nenhum SKU crítico.")
        st.subheader("Próximas ações do SDR")
        next_actions = query_df('SELECT name AS "Lead", urgency AS "Urgência", next_action AS "Próxima ação", next_action_at AS "Quando" FROM leads WHERE next_action IS NOT NULL AND stage NOT IN (\'cliente\',\'perdido\') ORDER BY next_action_at LIMIT 10')
        admin_table(next_actions, "Nenhuma próxima ação agendada.")
    with st.expander("Saúde do negócio · BI rápido"):
        metrics = calculate_metrics()
        forecast = forecast_revenue_30d()
        health_cols = st.columns(4)
        health_cols[0].metric("Margem estimada", pct(metrics["margin"]))
        health_cols[1].metric("Ticket médio", money_brl(metrics["ticket"]))
        health_cols[2].metric("Forecast simples 30d", money_brl(forecast["forecast_30d"]), help="Média diária recente × 30")
        health_cols[3].metric("Base do forecast", f"{forecast['days']} dias")

elif page == "Leads / CRM":
    page_topbar("Sell", "Fila operacional do SDR, prioridades e próximas ações.", "Novo lead")
    stage_counts = query_df("SELECT stage,COUNT(*) AS total FROM leads GROUP BY stage")
    count_map = dict(zip(stage_counts["stage"], stage_counts["total"])) if not stage_counts.empty else {}
    lead_cards = st.columns(4)
    for column, stage_name in zip(lead_cards, ["lead", "prospect", "cliente", "perdido"]):
        column.metric(stage_name.title(), safe_int(count_map.get(stage_name, 0)))
    tab1, tab2, tab3 = st.tabs(["Novo lead", "Pipeline & leads", "Mensagens"])
    with tab1:
        with st.container(border=True):
            st.markdown("#### Adicionar contacto")
            with st.form("lead_form"):
                row1, row2 = st.columns(2)
                name = row1.text_input("Nome do lead")
                contact = row2.text_input("Contacto")
                ig = row1.text_input("Instagram / @")
                channel = row2.selectbox("Canal", ["Instagram", "WhatsApp", "Outro"])
                interest = row1.selectbox("Interesse", ["Cordão fino", "Cordão médio", "Presença forte", "Pingente", "Presente", "Não definido"])
                stage = row2.selectbox("Status", ["lead", "prospect", "cliente", "perdido"])
                temperature = row1.selectbox("Temperatura", ["frio", "morno", "quente"])
                urgency = row2.selectbox("Urgência", ["normal", "atenção", "urgente"])
                next_action = row1.text_input("Próxima ação", placeholder="Responder, enviar catálogo, confirmar dados...")
                next_action_at = row2.date_input("Data da próxima ação", value=date.today())
                notes = st.text_area("Observação")
                if st.form_submit_button("Registrar lead"):
                    if not name.strip():
                        st.error("Informe o nome do lead.")
                    else:
                        add_lead(name.strip(), contact.strip(), ig.strip(), channel, interest, stage, notes.strip(), temperature, urgency, next_action.strip(), next_action_at)
                        st.success("Lead registado.")
                        st.rerun()
    with tab2:
        filter_cols = st.columns(5)
        filter_status = filter_cols[0].selectbox("Status", ["Todos", "lead", "prospect", "cliente", "perdido"], key="lead_filter_status")
        filter_channel = filter_cols[1].selectbox("Canal", ["Todos", "Instagram", "WhatsApp", "Outro"], key="lead_filter_channel")
        filter_urgency = filter_cols[2].selectbox("Urgência", ["Todos", "normal", "atenção", "urgente"], key="lead_filter_urgency")
        filter_owner = filter_cols[3].text_input("Responsável", key="lead_filter_owner")
        search_lead = filter_cols[4].text_input("Buscar", key="lead_search")
        leads = query_df('SELECT id AS "ID", name AS "Nome", contact AS "Contato", ig_handle AS "Instagram", channel AS "Canal", stage AS "Status", urgency AS "Urgência", temperature AS "Temperatura", interest AS "Interesse", last_interaction_at AS "Última interação", next_action AS "Próxima ação", owner AS "Responsável", created_at AS "Data" FROM leads ORDER BY id DESC LIMIT 500')
        if not leads.empty:
            if filter_status != "Todos": leads = leads[leads["Status"] == filter_status]
            if filter_channel != "Todos": leads = leads[leads["Canal"] == filter_channel]
            if filter_urgency != "Todos": leads = leads[leads["Urgência"] == filter_urgency]
            if filter_owner: leads = leads[leads["Responsável"].fillna("").str.contains(filter_owner, case=False, regex=False)]
            if search_lead:
                searchable = leads[["Nome", "Contato", "Instagram", "Próxima ação"]].fillna("").astype(str).agg(" ".join, axis=1)
                leads = leads[searchable.str.contains(search_lead, case=False, regex=False)]
        admin_table(leads, "Nenhum lead corresponde aos filtros.")
        export_csv_button(leads, "realhype_leads.csv")
        if not leads.empty:
            lead_id = st.selectbox("Lead", leads["ID"].tolist(), format_func=lambda x: f"#{x} · {leads[leads.ID==x].iloc[0]['Nome']}")
            new_stage = st.selectbox("Novo status", ["lead", "prospect", "cliente", "perdido"])
            if st.button("Atualizar status"):
                update_lead_stage(int(lead_id), new_stage)
                st.success("Status atualizado.")
                st.rerun()
    with tab3:
        leads = query_df("SELECT id, name FROM leads ORDER BY id DESC")
        if leads.empty:
            st.info("Cadastre um lead primeiro.")
        else:
            lead_id = st.selectbox("Lead da conversa", leads["id"].tolist(), format_func=lambda x: f"#{x} · {leads[leads.id==x].iloc[0]['name']}")
            with st.form("msg_form"):
                direction = st.selectbox("Direção", ["in", "out"], format_func=lambda x: "Cliente → RealHype" if x == "in" else "RealHype → Cliente")
                content = st.text_area("Mensagem")
                if st.form_submit_button("Guardar mensagem"):
                    if content.strip():
                        add_message(int(lead_id), direction, content)
                        st.success("Mensagem registada.")
                    else:
                        st.error("Digite a mensagem.")
            st.subheader("Histórico")
            msgs = query_df("SELECT direction, content, created_at FROM messages WHERE lead_id=:lead_id ORDER BY id DESC", {"lead_id": int(lead_id)})
            st.dataframe(msgs, width="stretch", hide_index=True)

elif page == "Vendas":
    page_topbar("Vendas", "Pedidos, margem e baixa controlada de inventário.", "Nova venda")
    st.subheader("Registrar venda")
    leads = query_df("SELECT id, name FROM leads ORDER BY id DESC")
    products = query_df("SELECT id, sku, name, quantity, sale_price_eur, cost_brl FROM products WHERE active=1 ORDER BY name")
    if products.empty:
        st.info("Cadastre produtos antes de registrar vendas.")
    else:
        with st.container(border=True):
            with st.form("order_form"):
                lead_options = [None] + leads["id"].tolist() if not leads.empty else [None]
                lead_id = st.selectbox("Lead / cliente", lead_options, format_func=lambda x: "Sem cliente vinculado" if x is None else f"#{x} · {leads[leads.id==x].iloc[0]['name']}")
                product_id = st.selectbox("Produto", products["id"].tolist(), format_func=lambda x: f"{products[products.id==x].iloc[0]['sku']} · {products[products.id==x].iloc[0]['name']} · {products[products.id==x].iloc[0]['quantity']} un.")
                selected = products[products.id == product_id].iloc[0]
                sale_col1, sale_col2 = st.columns(2)
                qty = sale_col1.number_input("Quantidade", min_value=1, step=1, value=1)
                default_price = float(selected["sale_price_eur"] or 0)
                unit_price = sale_col2.number_input("Preço unitário (€)", min_value=0.0, value=default_price, step=0.5)
                status = sale_col1.selectbox("Status da venda", ["reservado", "aguardando dados", "confirmado", "preparando envio", "enviado", "entregue", "devolvido", "cancelado"])
                channel = sale_col2.selectbox("Canal", ["Instagram", "WhatsApp", "Outro"])
                confirmation = sale_col2.selectbox("Confirmação", ["pendente", "confirmado_texto", "confirmado_audio"])
                ctt = st.selectbox("Status logístico", ["pendente", "preparar", "enviado", "entregue", "devolvido"])
                notes = st.text_area("Observações")
                st.caption("O stock é reduzido automaticamente em vendas confirmadas, enviadas ou entregues.")
                if st.form_submit_button("Registrar venda"):
                    try:
                        order_id = create_order(None if lead_id is None else int(lead_id), int(product_id), int(qty), float(unit_price), status, confirmation, ctt, notes, channel)
                        log_action("sale_created", "order", order_id, after_data=f"status={status}; qty={int(qty)}")
                        st.success(f"Venda registada. Pedido #{order_id}.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    st.subheader("Últimas vendas")
    orders = query_df("""
        SELECT o.id AS pedido, COALESCE(l.name,'Sem cliente') AS cliente, p.name AS produto, oi.qty AS quantidade,
               o.total_brl AS total_brl, o.status, (o.total_brl-(oi.qty*oi.unit_cost_brl)) AS margem_estimada_brl,
               o.channel AS canal, o.created_at AS data
        FROM orders o
        LEFT JOIN leads l ON l.id = o.lead_id
        JOIN order_items oi ON oi.order_id=o.id JOIN products p ON p.id=oi.product_id
        ORDER BY o.id DESC
        LIMIT 50
    """)
    admin_table(orders, "Nenhuma venda registrada.")
    export_csv_button(orders, "realhype_vendas.csv")

elif page == "CTT / Pedidos":
    page_topbar("Ship", "Validação de envio à cobrança e prevenção de devoluções.", "Atualizar pedido")
    total_orders = safe_int(scalar("SELECT COUNT(*) FROM orders"))
    awaiting = safe_int(scalar("SELECT COUNT(*) FROM orders WHERE confirmation_status='pendente' OR text_confirmed=0"))
    sent = safe_int(scalar("SELECT COUNT(*) FROM orders WHERE ctt_status='enviado'"))
    delivered = safe_int(scalar("SELECT COUNT(*) FROM orders WHERE ctt_status='entregue'"))
    returned_count = safe_int(scalar("SELECT COUNT(*) FROM orders WHERE ctt_status='devolvido' OR returned=1"))
    ctt_cost = safe_float(scalar("SELECT value FROM settings WHERE key='ctt_cost_brl'", default=0))
    ctt_cards = st.columns(6)
    for col,label,value in zip(ctt_cards,["Aguardando confirmação","Enviados","Entregues","Devolvidos","Taxa de devolução","Prejuízo estimado"],[awaiting,sent,delivered,returned_count,pct(returned_count/sent*100 if sent else 0),money_brl(returned_count*ctt_cost)]): col.metric(label,value)
    orders_ctt = query_df('SELECT o.id AS "Pedido", COALESCE(l.name,\'Sem cliente\') AS "Cliente", o.status AS "Venda", o.ctt_status AS "CTT", o.text_confirmed AS "Texto OK", o.address_validated AS "Morada OK", o.phone_validated AS "Telefone OK", o.pickup_deadline AS "Prazo", o.returned AS "Devolvido", o.return_reason AS "Motivo", o.created_at AS "Data" FROM orders o LEFT JOIN leads l ON l.id=o.lead_id ORDER BY o.id DESC LIMIT 200')
    admin_table(orders_ctt, "Nenhum pedido CTT registrado.")
    if not orders_ctt.empty:
        with st.expander("Atualizar validação CTT"):
            with st.form("ctt_update_form"):
                order_id = st.selectbox("Pedido", orders_ctt["Pedido"].tolist(), format_func=lambda value: f"Pedido #{value}")
                c1,c2,c3 = st.columns(3)
                text_ok = c1.checkbox("Confirmação textual recebida")
                address_ok = c2.checkbox("Morada validada")
                phone_ok = c3.checkbox("Telefone validado")
                deadline = c1.date_input("Prazo de levantamento", value=date.today()+timedelta(days=7))
                ctt_status = c2.selectbox("Status CTT", ["pendente","preparar","enviado","entregue","devolvido"])
                returned_flag = c3.checkbox("Devolvido")
                return_reason = st.text_input("Motivo da devolução")
                ctt_notes = st.text_area("Observações")
                if st.form_submit_button("Guardar validação CTT"):
                    update_order_ctt(int(order_id),text_ok,address_ok,phone_ok,deadline,ctt_status,returned_flag,return_reason,ctt_notes)
                    st.success("Pedido CTT atualizado.")
                    st.rerun()
    ctt_alerts = detect_alerts()
    if not ctt_alerts.empty:
        st.subheader("Alertas de risco")
        admin_table(ctt_alerts[ctt_alerts["Entidade"].str.startswith("Pedido")])

elif page == "Stock":
    page_topbar("Stock", "Inventário, capital imobilizado e movimentos seguros.", "Movimento de stock")
    total_units = scalar("SELECT COALESCE(SUM(quantity),0) FROM products WHERE active=1")
    critical_products = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity <= reorder_point")
    active_skus = scalar("SELECT COUNT(*) FROM products WHERE active=1")
    zero_products = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity=0")
    stock_value = scalar("SELECT COALESCE(SUM(quantity*cost_brl),0) FROM products WHERE active=1")
    idle_capital = scalar("SELECT COALESCE(SUM(p.quantity*p.cost_brl),0) FROM products p WHERE p.active=1 AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id=p.id)")
    stock_cards = st.columns(6)
    for col, label, value in zip(stock_cards, ["Unidades totais","SKUs ativos","Produtos críticos","Valor em stock","Produtos zerados","Capital parado"], [safe_int(total_units),safe_int(active_skus),safe_int(critical_products),money_brl(stock_value),safe_int(zero_products),money_brl(idle_capital)]): col.metric(label,value)
    tab1, tab2, tab3 = st.tabs(["Stock atual", "Movimento manual", "Histórico"])
    with tab1:
        toolbar = st.columns([2,1,1])
        stock_search = toolbar[0].text_input("Buscar SKU/produto", key="stock_search")
        category_filter = toolbar[1].selectbox("Categoria", ["Todas"] + query_df("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")["category"].tolist(), key="stock_category")
        status_filter = toolbar[2].selectbox("Status", ["Todos","OK","baixo","zerado"], key="stock_status")
        products = query_df(f"""
            SELECT sku AS "SKU", name AS "Produto", category AS "Categoria", quantity AS "Unidades",
                   reorder_point AS "Mínimo",
                   CASE WHEN quantity = 0 THEN 'zerado' WHEN quantity <= reorder_point THEN 'baixo' ELSE 'OK' END AS "Status",
                   cost_brl AS "Custo BRL", sale_price_eur AS "Preço EUR",
                   ((sale_price_eur*{get_eur_rate()})-cost_brl) AS "Margem est. BRL"
            FROM products WHERE active=1 ORDER BY quantity ASC, name
        """)
        if not products.empty:
            if stock_search:
                mask = products[["SKU","Produto"]].fillna("").astype(str).agg(" ".join,axis=1).str.contains(stock_search,case=False,regex=False)
                products = products[mask]
            if category_filter != "Todas": products = products[products["Categoria"] == category_filter]
            if status_filter != "Todos": products = products[products["Status"] == status_filter]
        if products.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            def color_stock_row(row):
                colors = {"OK": "background-color: rgba(34,197,94,.10); color: #86EFAC", "baixo": "background-color: rgba(245,197,66,.14); color: #FFD76A", "zerado": "background-color: rgba(239,68,68,.12); color: #FCA5A5"}
                return [colors.get(row["Status"], "") for _ in row]
            st.dataframe(products.style.apply(color_stock_row, axis=1), width="stretch", hide_index=True)
        export_csv_button(products, "realhype_stock.csv")
    with tab2:
        stock_products = query_df("SELECT id, sku, name, quantity FROM products WHERE active=1 ORDER BY name")
        if stock_products.empty:
            st.info("Cadastre um produto antes de movimentar o stock.")
        else:
            with st.container(border=True):
                with st.form("stock_movement_form"):
                    product_id = st.selectbox("Produto", stock_products["id"].tolist(), format_func=lambda x: f"{stock_products[stock_products.id==x].iloc[0]['sku']} · {stock_products[stock_products.id==x].iloc[0]['name']} · {stock_products[stock_products.id==x].iloc[0]['quantity']} un.")
                    move_col1, move_col2 = st.columns(2)
                    movement_type = move_col1.selectbox("Movimento", ["entrada", "saida", "ajuste", "perda", "devolucao"], format_func=lambda value: value.replace("saida","saída").replace("devolucao","devolução").title())
                    move_qty = move_col2.number_input("Quantidade", min_value=1, step=1, value=1)
                    reason = st.text_input("Motivo", placeholder="Reposição, correção de inventário, avaria...")
                    movement_notes = st.text_area("Observação")
                    if st.form_submit_button("Confirmar movimento"):
                        try:
                            adjust_stock(int(product_id), movement_type, int(move_qty), reason, movement_notes)
                            st.success("Stock atualizado com segurança.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
    with tab3:
        movements = query_df("""
            SELECT COALESCE(sm.movement_date,DATE(sm.created_at)) AS Data, p.sku AS SKU, p.name AS Produto, sm.movement_type AS Tipo,
                   sm.qty AS Quantidade, sm.reason AS Motivo, sm.notes AS Observação, sm.user_name AS Responsável
            FROM stock_movements sm JOIN products p ON p.id=sm.product_id
            ORDER BY sm.id DESC LIMIT 100
        """)
        if movements.empty:
            st.info("Nenhum movimento de stock registado.")
        else:
            st.dataframe(movements, width="stretch", hide_index=True)

elif page == "Produtos":
    require_role("partner")
    page_topbar("Produtos", "Cadastro estruturado de SKUs, pricing e garantia.", "Novo produto")
    catalog = query_df('SELECT sku AS "SKU", name AS "Produto", category AS "Categoria", quantity AS "Stock", reorder_point AS "Mínimo", cost_brl AS "Custo BRL", sale_price_eur AS "Preço venda", currency AS "Moeda", active AS "Ativo", tags AS "Tags" FROM products ORDER BY name')
    if catalog.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.dataframe(catalog, width="stretch", hide_index=True)
    with st.expander("Adicionar ou atualizar produto", expanded=catalog.empty):
        with st.form("product_form"):
            prod_col1, prod_col2 = st.columns(2)
            sku = prod_col1.text_input("SKU", placeholder="ex: GRUMET3MM")
            name = prod_col2.text_input("Nome do produto", placeholder="ex: Grumet 3MM")
            category = prod_col1.selectbox("Categoria", ["Cordões Finos", "Cordões Médios", "Presença Forte", "Cordões Grossos", "Pingentes", "Outro"])
            qty = prod_col2.number_input("Quantidade inicial / atual", min_value=0, step=1, value=0)
            reorder = prod_col1.number_input("Ponto de reposição", min_value=0, step=1, value=1)
            cost = prod_col2.number_input("Custo unitário (BRL)", min_value=0.0, value=0.0, step=1.0)
            price = prod_col1.number_input("Preço de venda (€)", min_value=0.0, value=0.0, step=0.5)
            currency = prod_col2.selectbox("Moeda", ["EUR", "BRL"])
            active = prod_col1.checkbox("Produto ativo", value=True)
            tags = prod_col2.text_input("Tags", placeholder="masculino, premium, corrente")
            description = st.text_area("Descrição curta")
            warranty = st.text_area("Garantia / observações")
            if st.form_submit_button("Guardar produto"):
                if sku.strip() and name.strip():
                    add_product(sku.strip().upper(), name.strip(), category, int(qty), int(reorder), float(cost), float(price), currency, description.strip(), tags.strip(), warranty.strip(), int(active))
                    st.success("Produto guardado.")
                    st.rerun()
                else:
                    st.error("SKU e nome são obrigatórios.")

elif page == "Financeiro":
    require_role("partner")
    page_topbar("Intel", "Controladoria simples, margem e inteligência de receita.", "Exportar relatório")
    metrics = calculate_metrics()
    revenue_brl, cost_brl = metrics["revenue"], metrics["cmv"]
    today_clause = "DATE(created_at)=CURRENT_DATE" if not get_db_url().startswith("sqlite") else "DATE(created_at)=DATE('now')"
    revenue_today = scalar(f"SELECT COALESCE(SUM(total_brl),0) FROM orders WHERE {today_clause} AND status IN ('confirmado','preparando envio','enviado','entregue')")
    expenses_brl = scalar("SELECT COALESCE(SUM(amount_brl),0) FROM expenses")
    return_cost = safe_int(scalar("SELECT COUNT(*) FROM orders WHERE status='devolvido' OR returned=1")) * safe_float(scalar("SELECT value FROM settings WHERE key='ctt_cost_brl'", default=0))
    finance_cols = st.columns(4); finance_cols2 = st.columns(3)
    for col,label,value in zip(finance_cols,["Receita total","Receita hoje","CMV estimado","Lucro estimado"],[money_brl(revenue_brl),money_brl(revenue_today),money_brl(cost_brl),money_brl(metrics["profit"])]): col.metric(label,value)
    for col,label,value in zip(finance_cols2,["Margem estimada","Ticket médio","Custo devoluções est."],[pct(metrics["margin"]),money_brl(metrics["ticket"]),money_brl(return_cost)]): col.metric(label,value)
    st.warning("Lucro estimado até confirmar custos finais de CTT, embalagem e ads.")

    st.subheader("Vendas consideradas")
    financial_sales = query_df("""
        SELECT o.id AS Pedido, COALESCE(l.name, 'Sem cliente') AS Cliente, o.status AS Status,
               o.total_eur AS Total_EUR, o.total_brl AS Total_BRL, o.created_at AS Data
        FROM orders o LEFT JOIN leads l ON l.id=o.lead_id
        WHERE o.status IN ('confirmado','preparando envio','enviado','entregue') ORDER BY o.id DESC
    """)
    if financial_sales.empty:
        st.info("Ainda não há vendas efetivas para o resumo financeiro.")
    else:
        st.dataframe(financial_sales, width="stretch", hide_index=True)
    export_csv_button(financial_sales, "realhype_financeiro.csv", "Exportar relatório CSV")

    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader("Receita por período")
        daily_finance = query_df("SELECT created_at,total_brl FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue') ORDER BY created_at")
        if daily_finance.empty: empty_state("Sem série histórica", "Registre vendas válidas para formar a curva de receita.")
        else:
            daily_finance["created_at"] = pd.to_datetime(daily_finance["created_at"],errors="coerce")
            daily_chart = daily_finance.dropna().groupby(daily_finance["created_at"].dt.date)["total_brl"].sum()
            st.line_chart(daily_chart,color="#F5C542")
    with chart2:
        st.subheader("Vendas por canal")
        channels = query_df("SELECT channel,COUNT(*) AS vendas FROM orders WHERE status IN ('confirmado','preparando envio','enviado','entregue') GROUP BY channel")
        if channels.empty: empty_state("Sem atribuição", "As vendas por canal aparecerão aqui.")
        else: st.bar_chart(channels.set_index("channel"),color="#F5C542")

    with st.expander("BI avançado · ABC, heatmap, cohort e forecast"):
        abc = classify_products_abc(); heatmap = build_heatmap_data(); cohort = build_cohort_data(); forecast = forecast_revenue_30d()
        st.metric("Forecast simples · 30 dias", money_brl(forecast["forecast_30d"]), help="Média diária dos últimos dias × 30")
        bi1,bi2,bi3 = st.tabs(["Pareto / ABC","Dia e hora","Cohort"])
        with bi1: admin_table(abc, "Ainda não há receita suficiente para classificar produtos.")
        with bi2: admin_table(heatmap.reset_index() if not heatmap.empty else heatmap, "Ainda não há datas suficientes para o heatmap.")
        with bi3: admin_table(cohort, "Ainda não há compras associadas a clientes para cohort.")

    st.subheader("Lançar despesa")
    with st.form("expense_form"):
        exp_date = st.date_input("Data", value=date.today())
        category = st.selectbox("Categoria", ["Ads", "CTT", "Embalagem", "Fornecedor", "Ferramentas", "Outro"])
        amount = st.number_input("Valor (BRL)", min_value=0.0, step=1.0)
        notes = st.text_area("Notas")
        if st.form_submit_button("Guardar despesa"):
            execute("INSERT INTO expenses (expense_date, category, amount_brl, notes) VALUES (:d, :c, :a, :n)", {"d": str(exp_date), "c": category, "a": float(amount), "n": notes})
            log_action("expense_created", "expense", after_data=f"category={category}; amount={float(amount):.2f}")
            st.success("Despesa registada.")
            st.rerun()
    expenses = query_df("SELECT expense_date, category, amount_brl, notes, created_at FROM expenses ORDER BY id DESC LIMIT 50")
    st.dataframe(expenses, width="stretch", hide_index=True)

elif page == "Growth":
    require_role("partner")
    page_topbar("Growth", "Campanhas, criativos e conversão chat → pedido.", "Registrar campanha")
    campaigns = query_df("SELECT * FROM campaign_metrics ORDER BY metric_date DESC,id DESC LIMIT 300")
    if campaigns.empty:
        empty_state("Sem métricas de campanha", "Registre dados agregados; nenhum dado real é inventado automaticamente.")
    else:
        campaigns["custo_por_mensagem"] = campaigns.apply(lambda row: safe_float(row["investment_brl"])/safe_int(row["messages_received"]) if safe_int(row["messages_received"]) else 0,axis=1)
        campaigns["conversao_chat_pedido_pct"] = campaigns.apply(lambda row: safe_int(row["sales_count"])/safe_int(row["messages_received"])*100 if safe_int(row["messages_received"]) else 0,axis=1)
        campaigns["roas_estimado"] = campaigns.apply(lambda row: safe_float(row["revenue_brl"])/safe_float(row["investment_brl"]) if safe_float(row["investment_brl"]) else 0,axis=1)
        gcols=st.columns(4)
        winner=campaigns.sort_values("roas_estimado",ascending=False).iloc[0]
        gcols[0].metric("Criativo vencedor", str(winner.get("creative") or "—"),delta=f"ROAS {safe_float(winner['roas_estimado']):.2f}x")
        gcols[1].metric("Custo por mensagem", money_brl(campaigns["investment_brl"].sum()/campaigns["messages_received"].sum() if campaigns["messages_received"].sum() else 0))
        gcols[2].metric("Vendas atribuídas", safe_int(campaigns["sales_count"].sum()))
        gcols[3].metric("Receita estimada", money_brl(campaigns["revenue_brl"].sum()))
        admin_table(campaigns[["metric_date","campaign","creative","channel","investment_brl","messages_received","leads_count","sales_count","custo_por_mensagem","conversao_chat_pedido_pct","revenue_brl","roas_estimado","notes"]])
        export_csv_button(campaigns,"realhype_growth.csv")
    with st.expander("Registrar métricas de campanha",expanded=campaigns.empty):
        with st.form("campaign_form"):
            g1,g2,g3=st.columns(3)
            campaign=g1.text_input("Campanha"); creative=g2.text_input("Criativo"); growth_channel=g3.selectbox("Canal",["Instagram","WhatsApp","Meta Ads","Outro"])
            investment=g1.number_input("Investimento (BRL)",min_value=0.0); messages=g2.number_input("Mensagens recebidas",min_value=0,step=1); leads_count=g3.number_input("Leads",min_value=0,step=1)
            sales_count=g1.number_input("Vendas",min_value=0,step=1); attributed_revenue=g2.number_input("Receita estimada (BRL)",min_value=0.0); metric_date=g3.date_input("Data",value=date.today())
            growth_notes=st.text_area("Observações")
            if st.form_submit_button("Guardar métricas"):
                if not campaign.strip(): st.error("Informe o nome da campanha.")
                else:
                    execute("INSERT INTO campaign_metrics (campaign,creative,channel,investment_brl,messages_received,leads_count,sales_count,revenue_brl,notes,metric_date) VALUES (:campaign,:creative,:channel,:investment,:messages,:leads,:sales,:revenue,:notes,:metric_date)",{"campaign":campaign.strip(),"creative":creative.strip(),"channel":growth_channel,"investment":float(investment),"messages":int(messages),"leads":int(leads_count),"sales":int(sales_count),"revenue":float(attributed_revenue),"notes":growth_notes.strip(),"metric_date":str(metric_date)})
                    log_action("campaign_metrics_created","campaign",after_data=f"campaign={campaign.strip()}")
                    st.success("Métricas registradas."); st.rerun()

elif page == "Alertas":
    require_role("partner","sdr")
    page_topbar("Alertas", "Exceções operacionais e ações recomendadas.", "Resolver prioridades")
    alerts = detect_alerts()
    if alerts.empty:
        empty_state("Nenhum alerta ativo", "Stock, confirmações e devoluções estão dentro das regras monitoradas.")
    else:
        alert_filter=st.selectbox("Severidade",["Todas","info","atenção","crítico"])
        if alert_filter!="Todas": alerts=alerts[alerts["Severidade"]==alert_filter]
        admin_table(alerts,"Nenhum alerta nesta severidade.")
        export_csv_button(alerts,"realhype_alertas.csv")
    with st.expander("Regras monitoradas"):
        st.markdown("Stock crítico · produto zerado · pedido sem confirmação · devolução CTT. Anomalia de receita, queda de conversão, produto parado e margem baixa usam estrutura de BI e serão refinados conforme a série histórica crescer.")

elif page == "Configurações":
    require_role("partner")
    page_topbar("Config", "Parâmetros operacionais e governança do Command OS.", "Salvar parâmetros")
    current_rate = get_eur_rate()
    setting_values = {row["key"]:row["value"] for _,row in query_df("SELECT key,value FROM settings").iterrows()}
    status_cols=st.columns(4)
    status_cols[0].metric("Conexão","Neon / PostgreSQL" if not get_db_url().startswith("sqlite") else "SQLite local")
    status_cols[1].metric("Ambiente","Streamlit Cloud" if not get_db_url().startswith("sqlite") else "Local")
    status_cols[2].metric("Versão",setting_values.get("app_version","2026.1"))
    status_cols[3].metric("Timezone","America/Sao_Paulo")
    with st.form("settings_form"):
        s1,s2,s3=st.columns(3)
        rate=s1.number_input("Cotação EUR → BRL",min_value=0.0,value=float(current_rate),step=0.01)
        packaging=s2.number_input("Custo padrão embalagem (BRL)",min_value=0.0,value=safe_float(setting_values.get("packaging_cost_brl")),step=1.0)
        ctt_setting=s3.number_input("Custo estimado CTT (BRL)",min_value=0.0,value=safe_float(setting_values.get("ctt_cost_brl")),step=1.0)
        daily_goal=s1.number_input("Meta diária de receita (BRL)",min_value=0.0,value=safe_float(setting_values.get("daily_revenue_goal_brl")),step=10.0)
        monthly_goal=s2.number_input("Meta mensal de vendas",min_value=0,value=safe_int(setting_values.get("monthly_sales_goal")),step=1)
        default_currency=s3.selectbox("Moeda padrão",["BRL","EUR"],index=0 if setting_values.get("default_currency","BRL")=="BRL" else 1)
        if st.form_submit_button("Salvar parâmetros"):
            values={"eur_brl":rate,"packaging_cost_brl":packaging,"ctt_cost_brl":ctt_setting,"daily_revenue_goal_brl":daily_goal,"monthly_sales_goal":monthly_goal,"default_currency":default_currency}
            for key,value in values.items(): execute("UPDATE settings SET value=:value WHERE key=:key",{"value":str(value),"key":key})
            log_action("settings_updated","settings")
            st.success("Parâmetros atualizados."); st.rerun()
    st.subheader("Usuários e roles")
    safe_users=pd.DataFrame([{"Usuário":username,"Nome":data.get("name",username),"Role":data.get("role","sdr")} for username,data in get_users().items()])
    admin_table(safe_users,"Nenhum usuário configurado em Secrets.")
    st.subheader("Audit log")
    audit=query_df('SELECT created_at AS "Data",actor AS "Ator",role AS "Role",action AS "Ação",entity_type AS "Entidade",entity_id AS "ID" FROM audit_logs ORDER BY id DESC LIMIT 100')
    admin_table(audit,"Nenhuma ação auditada ainda.")
    st.markdown("""
    <div class="rh-alert">
      <b>Segurança:</b> no Streamlit Cloud, mantenha utilizadores, senhas e banco apenas em <code>Secrets</code>.
      Nenhuma credencial é armazenada neste código.
    </div>
    """, unsafe_allow_html=True)
