from __future__ import annotations

import os
from datetime import date
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

APP_NAME = "REALHYPE OS"
DEFAULT_DB_URL = "sqlite:///realhype_local.db"

# -----------------------------
# Visual
# -----------------------------
st.set_page_config(page_title="REALHYPE Control Center", page_icon="⚡", layout="wide")

CUSTOM_CSS = """
<style>
:root {
  --rh-bg: #080A0F;
  --rh-card: #111827;
  --rh-card-2: #12151F;
  --rh-gold: #D4AF37;
  --rh-gold-light: #F2D675;
  --rh-cyan: #00E5FF;
  --rh-text: #F8FAFC;
  --rh-muted: #94A3B8;
  --rh-danger: #FF5C72;
  --rh-success: #35D07F;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--rh-bg);
  color: var(--rh-text);
}
[data-testid="stHeader"] { background: rgba(8,10,15,.82); }
.block-container { max-width: 1480px; padding: 1.5rem 2rem 3rem; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A0D14 0%, #080A0F 100%);
  border-right: 1px solid rgba(212,175,55,.18);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #CBD5E1; }
[data-testid="stSidebar"] [role="radiogroup"] label {
  border-radius: 10px;
  padding: .35rem .55rem;
  transition: all .2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(0,229,255,.07);
}
h1, h2, h3 { color: #F8FAFC; letter-spacing: .02em; }
h2, h3 { border-bottom: 1px solid rgba(212,175,55,.13); padding-bottom: .55rem; }
.rh-brand { font-size: 1.15rem; font-weight: 900; letter-spacing: .14em; color: var(--rh-gold-light); }
.rh-eyebrow { margin: 0 0 .35rem; color: var(--rh-cyan); font-size: .72rem; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }
.rh-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(212,175,55,.32);
  background: radial-gradient(circle at 88% 15%, rgba(0,229,255,.15), transparent 30%),
              linear-gradient(135deg, rgba(212,175,55,.13), rgba(17,24,39,.97) 48%, rgba(8,10,15,.98));
  border-radius: 20px;
  padding: 1.55rem 1.75rem;
  box-shadow: 0 18px 55px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04);
}
.rh-title { color: #FFF; font-size: clamp(1.65rem, 3vw, 2.45rem); font-weight: 900; letter-spacing: .055em; margin: 0; }
.rh-title span { color: var(--rh-gold-light); }
.rh-subtitle { color: var(--rh-muted); font-size: .88rem; margin: .45rem 0 .9rem; }
.rh-chip {
  display: inline-block; padding: .28rem .62rem; margin: 0 .35rem .25rem 0;
  border-radius: 999px; border: 1px solid rgba(0,229,255,.30);
  background: rgba(0,229,255,.055); color: #7EEBFA; font-size: .7rem;
}
.rh-section { margin: 1.35rem 0 .5rem; color: var(--rh-gold-light); font-size: .76rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
.rh-form-card {
  border: 1px solid rgba(212,175,55,.18); border-radius: 16px; padding: .35rem 1rem 1rem;
  background: linear-gradient(180deg, rgba(18,21,31,.96), rgba(11,14,21,.98));
}
.rh-alert { border-left: 3px solid var(--rh-gold); padding: .8rem 1rem; border-radius: 10px; background: rgba(212,175,55,.075); }
.rh-user { border: 1px solid rgba(0,229,255,.16); background: rgba(0,229,255,.045); border-radius: 12px; padding: .7rem .85rem; margin: .8rem 0 1rem; }
.small-muted { color: var(--rh-muted); font-size: .75rem; }
[data-testid="stMetric"] {
  min-height: 126px; padding: 1rem 1.05rem; border: 1px solid rgba(212,175,55,.16);
  border-radius: 15px; background: linear-gradient(145deg, rgba(17,24,39,.98), rgba(12,15,23,.98));
  box-shadow: 0 10px 28px rgba(0,0,0,.22);
}
[data-testid="stMetric"]:hover { border-color: rgba(0,229,255,.32); transform: translateY(-1px); }
[data-testid="stMetricLabel"] { color: #94A3B8; }
[data-testid="stMetricValue"] { color: #FFF; font-weight: 800; }
.stButton > button, .stFormSubmitButton > button {
  border: 0 !important; border-radius: 10px !important; color: #090B10 !important; font-weight: 800 !important;
  background: linear-gradient(135deg, #B88A20 0%, #F2D675 52%, #C69B2D 100%) !important;
  box-shadow: 0 7px 20px rgba(212,175,55,.17); transition: all .18s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover { transform: translateY(-1px); box-shadow: 0 9px 24px rgba(212,175,55,.28); }
[data-testid="stDataFrame"] { border: 1px solid rgba(0,229,255,.12); border-radius: 14px; overflow: hidden; }
[data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid rgba(212,175,55,.15); }
[data-baseweb="tab"] { border-radius: 9px 9px 0 0; }
[data-baseweb="input"], [data-baseweb="select"] > div, textarea {
  background: #0D111A !important; border-color: rgba(148,163,184,.18) !important;
}
hr { border-color: rgba(148,163,184,.11) !important; }
@media (max-width: 768px) { .block-container { padding: 1rem .85rem 2rem; } .rh-hero { padding: 1.2rem; } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Database
# -----------------------------
def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
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


if os.environ.get("REALHYPE_SKIP_DB_INIT") != "1":
    init_db()

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
      <p class="rh-title">REALHYPE OS</p>
      <p class="rh-subtitle">Painel operacional para stock, leads, vendas e decisões críticas.</p>
      <span class="rh-chip">Direct</span><span class="rh-chip">CTT</span><span class="rh-chip">Street Luxury</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")
    if ok:
        users = get_users()
        if username in users and password == users[username].get("password"):
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


# -----------------------------
# Data operations
# -----------------------------
def add_product(sku: str, name: str, category: str, qty: int, reorder_point: int, cost_brl: float, sale_price_eur: float):
    execute(
        """
        INSERT INTO products (sku, name, category, quantity, reorder_point, cost_brl, sale_price_eur)
        VALUES (:sku, :name, :category, :quantity, :reorder_point, :cost_brl, :sale_price_eur)
        ON CONFLICT (sku) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            quantity = excluded.quantity,
            reorder_point = excluded.reorder_point,
            cost_brl = excluded.cost_brl,
            sale_price_eur = excluded.sale_price_eur,
            active = 1
        """ if not get_db_url().startswith("sqlite") else """
        INSERT INTO products (sku, name, category, quantity, reorder_point, cost_brl, sale_price_eur)
        VALUES (:sku, :name, :category, :quantity, :reorder_point, :cost_brl, :sale_price_eur)
        ON CONFLICT(sku) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            quantity = excluded.quantity,
            reorder_point = excluded.reorder_point,
            cost_brl = excluded.cost_brl,
            sale_price_eur = excluded.sale_price_eur,
            active = 1
        """,
        {"sku": sku, "name": name, "category": category, "quantity": qty, "reorder_point": reorder_point, "cost_brl": cost_brl, "sale_price_eur": sale_price_eur},
    )


def add_lead(name: str, contact: str, ig_handle: str, channel: str, interest: str, stage: str, notes: str):
    execute(
        """
        INSERT INTO leads (name, contact, ig_handle, channel, interest, stage, owner, notes)
        VALUES (:name, :contact, :ig_handle, :channel, :interest, :stage, :owner, :notes)
        """,
        {"name": name, "contact": contact, "ig_handle": ig_handle, "channel": channel, "interest": interest, "stage": stage, "owner": DISPLAY_NAME, "notes": notes},
    )


def update_lead_stage(lead_id: int, stage: str):
    execute("UPDATE leads SET stage=:stage, updated_at=CURRENT_TIMESTAMP WHERE id=:id", {"stage": stage, "id": lead_id})


def add_message(lead_id: int, direction: str, content: str):
    execute("INSERT INTO messages (lead_id, direction, content) VALUES (:lead_id, :direction, :content)", {"lead_id": lead_id, "direction": direction, "content": content})


def create_order(lead_id: Optional[int], product_id: int, qty: int, unit_price_eur: float, status: str, confirmation_status: str, ctt_status: str, notes: str):
    rate = get_eur_rate()
    stock_statuses = {"confirmado", "enviado", "entregue"}
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
            INSERT INTO orders (lead_id, status, ctt_status, confirmation_status, total_eur, total_brl, notes, created_by)
            VALUES (:lead_id, :status, :ctt_status, :confirmation_status, :total_eur, :total_brl, :notes, :created_by)
        """
        params = {"lead_id": lead_id, "status": status, "ctt_status": ctt_status, "confirmation_status": confirmation_status, "total_eur": total_eur, "total_brl": total_brl, "notes": notes, "created_by": DISPLAY_NAME}
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


def adjust_stock(product_id: int, movement_type: str, qty: int, reason: str) -> None:
    if qty <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    delta = qty if movement_type == "entrada" else -qty
    with engine.begin() as conn:
        updated = conn.execute(
            text("UPDATE products SET quantity = quantity + :delta WHERE id=:product_id AND quantity + :delta >= 0"),
            {"delta": delta, "product_id": product_id},
        )
        if updated.rowcount != 1:
            raise ValueError("Stock insuficiente para esta saída ou produto não encontrado.")
        conn.execute(
            text("""
                INSERT INTO stock_movements (product_id, movement_type, qty, reason, user_name)
                VALUES (:product_id, :movement_type, :qty, :reason, :user_name)
            """),
            {"product_id": product_id, "movement_type": movement_type, "qty": delta, "reason": reason.strip() or "Ajuste manual", "user_name": DISPLAY_NAME},
        )

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown('<div class="rh-brand">REALHYPE</div><div class="small-muted">CONTROL CENTER · ADMIN</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rh-user"><b>{DISPLAY_NAME}</b><br><span class="small-muted">PERFIL · {ROLE.upper()}</span></div>', unsafe_allow_html=True)
    partner_pages = ["Visão Geral", "Leads / CRM", "Vendas", "Stock", "Produtos", "Financeiro", "Configurações"]
    sdr_pages = ["Visão Geral", "Leads / CRM", "Vendas", "Stock"]
    page = st.radio("NAVEGAÇÃO", partner_pages if IS_PARTNER else sdr_pages, key="page")
    st.divider()
    st.caption("RealHype Operations · online")
    if st.button("Sair", width="stretch"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# Header
# -----------------------------
header_left, header_right = st.columns([6, 1])
with header_left:
    st.markdown(f"""
<div class="rh-hero">
  <p class="rh-eyebrow">Operations intelligence</p>
  <p class="rh-title">REALHYPE <span>CONTROL CENTER</span></p>
  <p class="rh-subtitle">Olá, {DISPLAY_NAME}. Visibilidade operacional, CRM, vendas e stock num único painel.</p>
  <span class="rh-chip">{ROLE.upper()}</span><span class="rh-chip">NEON CONNECTED</span><span class="rh-chip">LIVE OPERATIONS</span>
</div>
""", unsafe_allow_html=True)
with header_right:
    st.write("")
    st.write("")
    if st.button("↻ Atualizar painel", width="stretch"):
        st.rerun()
st.write("")

# -----------------------------
# Pages
# -----------------------------
if page == "Visão Geral":
    st.markdown('<div class="rh-section">Pulso da operação</div>', unsafe_allow_html=True)
    leads_total = scalar("SELECT COUNT(*) FROM leads")
    leads_today = scalar("SELECT COUNT(*) FROM leads WHERE DATE(created_at)=CURRENT_DATE" if not get_db_url().startswith("sqlite") else "SELECT COUNT(*) FROM leads WHERE DATE(created_at)=DATE('now')")
    orders_count = scalar("SELECT COUNT(*) FROM orders WHERE status IN ('confirmado','enviado','entregue')")
    revenue_eur = scalar("SELECT COALESCE(SUM(total_eur),0) FROM orders WHERE status IN ('confirmado','enviado','entregue')")
    stock_units = scalar("SELECT COALESCE(SUM(quantity),0) FROM products WHERE active=1")
    products_in_stock = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity > 0")
    low_stock_count = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity <= reorder_point")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi4, kpi5, kpi6 = st.columns(3)
    kpi1.metric("Leads totais", int(leads_total), help="Todos os contactos do CRM")
    kpi2.metric("Leads de hoje", int(leads_today), help="Novos contactos no dia")
    kpi3.metric("Vendas totais", int(orders_count), help="Confirmadas, enviadas ou entregues")
    kpi4.metric("Faturamento total", money_eur(revenue_eur) if IS_PARTNER else "Restrito", help="Visível integralmente para partner")
    kpi5.metric("Produtos em stock", int(products_in_stock), delta=f"{int(stock_units)} unidades", delta_color="off")
    kpi6.metric("Produtos com stock baixo", int(low_stock_count), delta="atenção" if low_stock_count else "saudável", delta_color="inverse" if low_stock_count else "normal")

    overview_left, overview_right = st.columns([1.15, 1])
    with overview_left:
        st.subheader("Funil de Leads")
        funnel = query_df("SELECT stage, COUNT(*) AS total FROM leads GROUP BY stage ORDER BY total DESC")
        if funnel.empty:
            st.info("Ainda não há leads registados.")
        else:
            st.bar_chart(funnel.set_index("stage"), color="#D4AF37")
            st.dataframe(funnel, width="stretch", hide_index=True)
    with overview_right:
        st.subheader("Alertas de Stock")
        low = query_df("SELECT sku AS SKU, name AS Produto, quantity AS Unidades, reorder_point AS Mínimo FROM products WHERE active=1 AND quantity <= reorder_point ORDER BY quantity ASC")
        if low.empty:
            st.success("Operação saudável: nenhum produto crítico.")
        else:
            st.warning("Itens no ponto de reposição ou abaixo dele.")
            st.dataframe(low, width="stretch", hide_index=True)

elif page == "Leads / CRM":
    st.markdown('<div class="rh-section">CRM · relacionamento e conversão</div>', unsafe_allow_html=True)
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
                notes = st.text_area("Observação")
                if st.form_submit_button("Registrar lead"):
                    if not name.strip():
                        st.error("Informe o nome do lead.")
                    else:
                        add_lead(name.strip(), contact.strip(), ig.strip(), channel, interest, stage, notes.strip())
                        st.success("Lead registado.")
                        st.rerun()
    with tab2:
        leads = query_df('SELECT id AS "ID", name AS "Nome", contact AS "Contacto", ig_handle AS "Instagram", channel AS "Canal", stage AS "Status", interest AS "Interesse", notes AS "Observação", created_at AS "Criado_em" FROM leads ORDER BY id DESC')
        st.dataframe(leads, width="stretch", hide_index=True)
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
    st.markdown('<div class="rh-section">Comercial · pedidos e fulfillment</div>', unsafe_allow_html=True)
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
                status = sale_col1.selectbox("Status da venda", ["reservado", "confirmado", "enviado", "entregue", "devolvido"])
                confirmation = sale_col2.selectbox("Confirmação", ["pendente", "confirmado_texto", "confirmado_audio"])
                ctt = st.selectbox("Status logístico", ["pendente", "preparar", "enviado", "entregue", "devolvido"])
                notes = st.text_area("Observações")
                st.caption("O stock é reduzido automaticamente em vendas confirmadas, enviadas ou entregues.")
                if st.form_submit_button("Registrar venda"):
                    try:
                        order_id = create_order(None if lead_id is None else int(lead_id), int(product_id), int(qty), float(unit_price), status, confirmation, ctt, notes)
                        st.success(f"Venda registada. Pedido #{order_id}.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    st.subheader("Últimas vendas")
    orders = query_df("""
        SELECT o.id, l.name AS lead, o.status, o.confirmation_status, o.ctt_status, o.total_eur, o.total_brl, o.created_by, o.created_at
        FROM orders o
        LEFT JOIN leads l ON l.id = o.lead_id
        ORDER BY o.id DESC
        LIMIT 50
    """)
    st.dataframe(orders, width="stretch", hide_index=True)

elif page == "Stock":
    st.markdown('<div class="rh-section">Inventário · disponibilidade em tempo real</div>', unsafe_allow_html=True)
    total_units = scalar("SELECT COALESCE(SUM(quantity),0) FROM products WHERE active=1")
    critical_products = scalar("SELECT COUNT(*) FROM products WHERE active=1 AND quantity <= reorder_point")
    stock_col1, stock_col2 = st.columns(2)
    stock_col1.metric("Total de unidades", int(total_units))
    stock_col2.metric("Produtos críticos", int(critical_products), delta="reposição" if critical_products else "stock saudável", delta_color="inverse" if critical_products else "normal")
    tab1, tab2, tab3 = st.tabs(["Stock atual", "Movimento manual", "Histórico"])
    with tab1:
        products = query_df("""
            SELECT sku AS "SKU", name AS "Produto", category AS "Categoria", quantity AS "Unidades",
                   reorder_point AS "Mínimo",
                   CASE WHEN quantity = 0 THEN 'zerado' WHEN quantity <= reorder_point THEN 'baixo' ELSE 'OK' END AS "Status"
            FROM products WHERE active=1 ORDER BY quantity ASC, name
        """)
        if products.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            def color_stock_row(row):
                colors = {"OK": "background-color: rgba(53,208,127,.10); color: #B7F7D2", "baixo": "background-color: rgba(212,175,55,.12); color: #F2D675", "zerado": "background-color: rgba(255,92,114,.12); color: #FF9AAA"}
                return [colors.get(row["Status"], "") for _ in row]
            st.dataframe(products.style.apply(color_stock_row, axis=1), width="stretch", hide_index=True)
    with tab2:
        stock_products = query_df("SELECT id, sku, name, quantity FROM products WHERE active=1 ORDER BY name")
        if stock_products.empty:
            st.info("Cadastre um produto antes de movimentar o stock.")
        else:
            with st.container(border=True):
                with st.form("stock_movement_form"):
                    product_id = st.selectbox("Produto", stock_products["id"].tolist(), format_func=lambda x: f"{stock_products[stock_products.id==x].iloc[0]['sku']} · {stock_products[stock_products.id==x].iloc[0]['name']} · {stock_products[stock_products.id==x].iloc[0]['quantity']} un.")
                    move_col1, move_col2 = st.columns(2)
                    movement_type = move_col1.selectbox("Movimento", ["entrada", "saida"], format_func=lambda value: "Entrada" if value == "entrada" else "Saída")
                    move_qty = move_col2.number_input("Quantidade", min_value=1, step=1, value=1)
                    reason = st.text_input("Motivo", placeholder="Reposição, correção de inventário, avaria...")
                    if st.form_submit_button("Confirmar movimento"):
                        try:
                            adjust_stock(int(product_id), movement_type, int(move_qty), reason)
                            st.success("Stock atualizado com segurança.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
    with tab3:
        movements = query_df("""
            SELECT sm.created_at AS Data, p.sku AS SKU, p.name AS Produto, sm.movement_type AS Tipo,
                   sm.qty AS Quantidade, sm.reason AS Motivo, sm.user_name AS Usuário
            FROM stock_movements sm JOIN products p ON p.id=sm.product_id
            ORDER BY sm.id DESC LIMIT 100
        """)
        if movements.empty:
            st.info("Nenhum movimento de stock registado.")
        else:
            st.dataframe(movements, width="stretch", hide_index=True)

elif page == "Produtos":
    if not IS_PARTNER:
        st.warning("Área restrita ao perfil partner.")
        st.stop()
    st.markdown('<div class="rh-section">Catálogo · produtos e pricing</div>', unsafe_allow_html=True)
    catalog = query_df("SELECT sku AS SKU, name AS Produto, category AS Categoria, quantity AS Stock, reorder_point AS Mínimo, cost_brl AS Custo_BRL, sale_price_eur AS Preço_EUR, active AS Ativo FROM products ORDER BY name")
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
            if st.form_submit_button("Guardar produto"):
                if sku.strip() and name.strip():
                    add_product(sku.strip().upper(), name.strip(), category, int(qty), int(reorder), float(cost), float(price))
                    st.success("Produto guardado.")
                    st.rerun()
                else:
                    st.error("SKU e nome são obrigatórios.")

elif page == "Financeiro":
    if not IS_PARTNER:
        st.warning("Área restrita ao perfil partner.")
        st.stop()
    st.markdown('<div class="rh-section">Financeiro · leitura estimada da operação</div>', unsafe_allow_html=True)
    revenue_eur = scalar("SELECT COALESCE(SUM(total_eur),0) FROM orders WHERE status IN ('confirmado','enviado','entregue')")
    revenue_brl = scalar("SELECT COALESCE(SUM(total_brl),0) FROM orders WHERE status IN ('confirmado','enviado','entregue')")
    cost_brl = scalar("SELECT COALESCE(SUM(oi.qty * oi.unit_cost_brl),0) FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE o.status IN ('confirmado','enviado','entregue')")
    expenses_brl = scalar("SELECT COALESCE(SUM(amount_brl),0) FROM expenses")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento total", money_brl(revenue_brl), delta=money_eur(revenue_eur), delta_color="off")
    col2.metric("Custo estimado", money_brl(cost_brl), help="Custo dos produtos vendidos")
    col3.metric("Lucro bruto estimado", money_brl(float(revenue_brl) - float(cost_brl)), help="Receita menos custo dos produtos vendidos")
    col4.metric("Despesas lançadas", money_brl(expenses_brl))
    st.caption("Indicadores estimados: lucro bruto = receita de vendas efetivas − custo dos produtos vendidos. Não substitui apuração contabilística.")

    st.subheader("Vendas consideradas")
    financial_sales = query_df("""
        SELECT o.id AS Pedido, COALESCE(l.name, 'Sem cliente') AS Cliente, o.status AS Status,
               o.total_eur AS Total_EUR, o.total_brl AS Total_BRL, o.created_at AS Data
        FROM orders o LEFT JOIN leads l ON l.id=o.lead_id
        WHERE o.status IN ('confirmado','enviado','entregue') ORDER BY o.id DESC
    """)
    if financial_sales.empty:
        st.info("Ainda não há vendas efetivas para o resumo financeiro.")
    else:
        st.dataframe(financial_sales, width="stretch", hide_index=True)

    st.subheader("Lançar despesa")
    with st.form("expense_form"):
        exp_date = st.date_input("Data", value=date.today())
        category = st.selectbox("Categoria", ["Ads", "CTT", "Embalagem", "Fornecedor", "Ferramentas", "Outro"])
        amount = st.number_input("Valor (BRL)", min_value=0.0, step=1.0)
        notes = st.text_area("Notas")
        if st.form_submit_button("Guardar despesa"):
            execute("INSERT INTO expenses (expense_date, category, amount_brl, notes) VALUES (:d, :c, :a, :n)", {"d": str(exp_date), "c": category, "a": float(amount), "n": notes})
            st.success("Despesa registada.")
            st.rerun()
    expenses = query_df("SELECT expense_date, category, amount_brl, notes, created_at FROM expenses ORDER BY id DESC LIMIT 50")
    st.dataframe(expenses, width="stretch", hide_index=True)

elif page == "Configurações":
    if not IS_PARTNER:
        st.warning("Área restrita ao perfil partner.")
        st.stop()
    st.markdown('<div class="rh-section">Administração · parâmetros operacionais</div>', unsafe_allow_html=True)
    current_rate = get_eur_rate()
    rate = st.number_input("Cotação EUR → BRL", min_value=0.0, value=float(current_rate), step=0.01)
    if st.button("Salvar cotação"):
        execute("UPDATE settings SET value=:v WHERE key='eur_brl'", {"v": str(rate)})
        st.success("Cotação atualizada.")
        st.rerun()
    st.markdown("""
    <div class="rh-alert">
      <b>Segurança:</b> no Streamlit Cloud, mantenha utilizadores, senhas e banco apenas em <code>Secrets</code>.
      Nenhuma credencial é armazenada neste código.
    </div>
    """, unsafe_allow_html=True)
