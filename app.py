import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. PAGE CONFIG & CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="Kitchen Ops · Workforce Intelligence",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLORS: Dict[str, str] = {
    "primary": "#6366F1", "primary_light": "#A5B4FC", "primary_dark": "#4338CA",
    "success": "#10B981", "success_light": "#D1FAE5",
    "warning": "#F59E0B", "warning_light": "#FEF3C7",
    "danger": "#EF4444", "danger_light": "#FEE2E2",
    "info": "#3B82F6",
    "bg": "#F8FAFC", "surface": "#FFFFFF", "border": "#E2E8F0",
    "text": "#0F172A", "text_secondary": "#64748B", "text_muted": "#94A3B8",
    "chart_1": "#6366F1", "chart_2": "#8B5CF6", "chart_3": "#EC4899",
    "chart_4": "#F59E0B", "chart_5": "#10B981", "chart_6": "#3B82F6",
    "chart_7": "#F97316", "chart_8": "#14B8A6",
}
CHART_SERIES = [COLORS[f"chart_{i}"] for i in range(1, 9)]

HOURLY_WAGE_CHF = 32.0

PLOTLY_TEMPLATE = dict(
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text"], size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=24, r=24, t=48, b=24),
    hoverlabel=dict(
        bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
        font=dict(family="Inter, system-ui, sans-serif", size=13, color=COLORS["text"]),
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5,
        font=dict(size=11, color=COLORS["text_secondary"]),
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
    ),
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=11, color=COLORS["text_secondary"])),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", gridwidth=1, zeroline=False,
               showline=False, tickfont=dict(size=11, color=COLORS["text_secondary"])),
)


def apply_layout(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    fig.update_layout(
        **PLOTLY_TEMPLATE,
        title=dict(text=title, font=dict(size=16, color=COLORS["text"]), x=0.01, xanchor="left") if title else {},
        height=height,
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. CSS INJECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, .stApp {{
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background: {COLORS["bg"]}; color: {COLORS["text"]};
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{ padding: 2rem 3rem 3rem 3rem; max-width: 1440px; }}

    .kpi-card {{
        background: {COLORS["surface"]}; border: 1px solid {COLORS["border"]};
        border-radius: 14px; padding: 1.35rem 1.5rem;
        transition: all 0.25s cubic-bezier(.4,0,.2,1);
        position: relative; overflow: hidden;
    }}
    .kpi-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["chart_3"]});
        opacity: 0; transition: opacity 0.25s ease;
    }}
    .kpi-card:hover {{
        box-shadow: 0 8px 30px rgba(99,102,241,.10), 0 2px 8px rgba(0,0,0,.04);
        transform: translateY(-2px); border-color: {COLORS["primary_light"]};
    }}
    .kpi-card:hover::before {{ opacity: 1; }}
    .kpi-label {{
        font-size: 0.78rem; font-weight: 500; letter-spacing: 0.04em;
        text-transform: uppercase; color: {COLORS["text_secondary"]}; margin-bottom: 0.35rem;
    }}
    .kpi-value {{ font-size: 1.85rem; font-weight: 700; color: {COLORS["text"]}; line-height: 1.15; }}
    .kpi-delta {{ font-size: 0.82rem; font-weight: 500; margin-top: 0.3rem; }}
    .kpi-delta.positive {{ color: {COLORS["success"]}; }}
    .kpi-delta.negative {{ color: {COLORS["danger"]}; }}
    .kpi-delta.neutral  {{ color: {COLORS["text_muted"]}; }}

    .section-header {{
        font-size: 1.15rem; font-weight: 600; color: {COLORS["text"]};
        margin: 2.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 1px solid {COLORS["border"]};
    }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {COLORS["border"]}; }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif; font-weight: 500; font-size: 0.88rem;
        padding: 0.6rem 1.25rem; color: {COLORS["text_secondary"]};
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLORS["primary"]} !important;
        border-bottom: 2px solid {COLORS["primary"]} !important;
        background: transparent !important;
    }}
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS["border"]}; border-radius: 3px; }}
    </style>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. DATA MANAGEMENT – FIX #3: @st.cache_data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data(ttl=300, show_spinner=False)
def build_sample_data(sector: str) -> pd.DataFrame:
    """
    FIX #3: @st.cache_data mit TTL=5min.
    Verhindert redundante Neuberechnung bei jedem Streamlit-Rerun.
    In Produktion: DB-Query hier cachen, TTL an Datenfrische anpassen.
    """
    np.random.seed(42 if sector == "Küche" else 99)
    n = 60
    base_date = pd.Timestamp("2025-06-16")
    roles = (["Koch", "Sous-Chef", "Commis", "Küchenhilfe"]
             if sector == "Küche"
             else ["Serviceleitung", "Servicemitarbeiter", "Aushilfe", "Barista"])
    tasks_map = {
        "Küche": {
            "Vorbereitung":  ["Mise en Place", "Gemüse schneiden", "Saucen vorbereiten"],
            "Produktion":    ["Mittagsservice", "Abendservice", "Bankett kochen"],
            "Warenannahme":  ["Lieferung prüfen", "Lager einräumen"],
            "Reinigung":     ["Küche reinigen", "Geräte reinigen", "Boden wischen"],
            "Administration":["Bestellung aufgeben", "Inventur", "Dienstplan prüfen"],
        },
        "Gastrodienste": {
            "Service":       ["Tisch eindecken", "Gäste bedienen", "Abräumen"],
            "Bar":           ["Getränke zubereiten", "Bar reinigen"],
            "Kasse":         ["Abrechnung", "Tagesabschluss"],
            "Reinigung":     ["Gastraum reinigen", "Toiletten reinigen"],
            "Administration":["Reservierungen", "Schichtübergabe"],
        },
    }[sector]

    records = []
    for i in range(n):
        role = np.random.choice(roles)
        category = np.random.choice(list(tasks_map.keys()))
        task = np.random.choice(tasks_map[category])
        start_hour = np.random.choice(range(6, 20))
        start_min = np.random.choice([0, 15, 30, 45])
        duration_min = int(np.random.choice([15, 30, 45, 60, 90, 120]))
        start_dt = base_date + timedelta(hours=int(start_hour), minutes=int(start_min))
        end_dt = start_dt + timedelta(minutes=duration_min)
        required_skill = np.random.randint(1, 6)
        actual_skill = max(1, min(5, required_skill + np.random.randint(-2, 3)))
        planned_min = duration_min
        actual_min = max(5, int(duration_min + np.random.normal(0, duration_min * 0.15)))
        records.append({
            "employee_id": f"E{np.random.randint(100, 200)}",
            "employee_name": f"Mitarbeiter {i+1}",
            "role": role, "category": category, "task": task,
            "start": start_dt, "end": end_dt,
            "planned_min": planned_min, "actual_min": actual_min,
            "required_skill": required_skill, "actual_skill": actual_skill,
            "cost_chf": round(actual_min / 60 * HOURLY_WAGE_CHF, 2),
        })

    df = pd.DataFrame(records)
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    return df


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. WORKLOAD ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class WorkloadEngine:
    INTERVAL = pd.Timedelta(minutes=15)

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._build_grid()

    def _build_grid(self):
        t_min = self.df["start"].min().floor("15min")
        t_max = self.df["end"].max().ceil("15min")
        self.grid = pd.date_range(t_min, t_max, freq="15min")

    def demand_curve(self, mode: str = "minutes") -> pd.DataFrame:
        starts = self.df["start"].values
        ends = self.df["end"].values
        actual_min = self.df["actual_min"].values.astype(float)
        duration_min = ((ends - starts) / np.timedelta64(1, "m"))

        records = []
        for slot_start in self.grid[:-1]:
            slot_end = slot_start + self.INTERVAL
            s, e = slot_start.to_datetime64(), slot_end.to_datetime64()
            overlaps = (starts < e) & (ends > s)
            if not overlaps.any():
                records.append({"time": slot_start, "demand": 0.0})
                continue
            overlap_start = np.maximum(starts[overlaps], s)
            overlap_end = np.minimum(ends[overlaps], e)
            overlap_min = (overlap_end - overlap_start) / np.timedelta64(1, "m")
            frac = np.where(duration_min[overlaps] > 0, overlap_min / duration_min[overlaps], 0.0)
            weighted = (actual_min[overlaps] * frac).sum()
            value = weighted if mode == "minutes" else weighted / 60.0 * HOURLY_WAGE_CHF
            records.append({"time": slot_start, "demand": round(value, 2)})
        return pd.DataFrame(records)

    def capacity_curve(self, mode: str = "minutes") -> pd.DataFrame:
        emp_ids = self.df["employee_id"].values
        starts = self.df["start"].values
        ends = self.df["end"].values
        records = []
        for slot_start in self.grid[:-1]:
            s = slot_start.to_datetime64()
            e = (slot_start + self.INTERVAL).to_datetime64()
            overlaps = (starts < e) & (ends > s)
            unique_emps = len(set(emp_ids[overlaps]))
            cap = unique_emps * 15.0
            value = cap if mode == "minutes" else cap / 60.0 * HOURLY_WAGE_CHF
            records.append({"time": slot_start, "capacity": round(value, 2)})
        return pd.DataFrame(records)

    def merged_curves(self, mode: str = "minutes") -> pd.DataFrame:
        return self.demand_curve(mode).merge(self.capacity_curve(mode), on="time", how="outer").fillna(0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. KPI ENGINE – FIX #1 & #2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KPIEngine:
    def __init__(self, df: pd.DataFrame, mode: str = "minutes"):
        self.df = df
        self.mode = mode

    def _to_display(self, minutes_val: float) -> Tuple[float, str]:
        if self.mode == "minutes":
            return round(minutes_val, 1), "Min"
        return round(minutes_val / 60 * HOURLY_WAGE_CHF, 2), "CHF"

    def total_workload(self) -> dict:
        total = self.df["actual_min"].sum()
        val, unit = self._to_display(total)
        return {"label": f"Gesamtaufwand ({unit})", "value": f"{val:,.0f}",
                "delta": None, "delta_direction": "neutral"}

    def avg_efficiency(self) -> dict:
        eff = (self.df["planned_min"].sum() / self.df["actual_min"].sum()) * 100
        direction = "positive" if eff >= 95 else "negative"
        return {"label": "Effizienz (Soll / Ist)", "value": f"{eff:.1f} %",
                "delta": "✓ Im Ziel" if eff >= 95 else "⚠ Unter Ziel",
                "delta_direction": direction}

    # ── FIX #1: Individualisierte Auslastungsrate ──
    def utilisation_rate(self) -> dict:
        """
        VORHER (fehlerhaft):
            capacity = n_employees × globale Zeitspanne
            → Mitarbeiter mit kurzer Schicht bekamen volle Tages-Kapazität

        JETZT (korrekt):
            Kapazität = Summe der individuellen Schichtspannen pro Mitarbeiter.
            Jeder MA bekommt nur die Minuten zwischen seinem frühesten Start
            und spätesten Ende zugeschrieben.
        """
        emp_capacity = (
            self.df
            .groupby("employee_id")
            .apply(
                lambda g: pd.Series({
                    "span_min": (g["end"].max() - g["start"].min()).total_seconds() / 60,
                    "worked_min": g["actual_min"].sum(),
                }),
                include_groups=False,
            )
        )
        total_capacity = emp_capacity["span_min"].sum()
        total_worked = emp_capacity["worked_min"].sum()

        # Guard gegen Division durch Null
        util = (total_worked / total_capacity * 100) if total_capacity > 0 else 0

        n_emp = self.df["employee_id"].nunique()
        avg_span_h = (total_capacity / n_emp / 60) if n_emp > 0 else 0

        direction = "positive" if util >= 70 else ("neutral" if util >= 50 else "negative")
        return {
            "label": "Auslastung",
            "value": f"{util:.1f} %",
            "delta": f"{n_emp} MA · Ø {avg_span_h:.1f}h Schicht",
            "delta_direction": direction,
        }

    def skill_mismatch_rate(self) -> dict:
        mismatch = (self.df["actual_skill"] < self.df["required_skill"]).sum()
        total = len(self.df)
        rate = (mismatch / total) * 100 if total > 0 else 0
        direction = "positive" if rate < 15 else "negative"
        return {"label": "Skill-Mismatch", "value": f"{rate:.1f} %",
                "delta": f"{mismatch} von {total} Aufgaben",
                "delta_direction": direction}

    # ── FIX #2: Gewichtete Überzeit-KPI ────────────
    def overtime_metrics(self) -> dict:
        """
        VORHER: Nur Anzahl Tasks mit actual > planned (ungewichtet).
                → 2 Min Überzeit = 60 Min Überzeit = gleich schlimm.

        JETZT: Zwei Perspektiven in einer Card:
            1. Überzeitquote = Anteil Tasks mit Überzeit (wie vorher)
            2. Gewichteter Mehraufwand = tatsächliche Excess-Minuten
               relativ zum Gesamtsoll (aussagekräftiger)
        """
        excess = (self.df["actual_min"] - self.df["planned_min"]).clip(lower=0)
        tasks_over = (excess > 0).sum()
        total_tasks = len(self.df)

        # Gewichtete Überzeit: Excess-Minuten / Planned-Gesamt
        planned_total = self.df["planned_min"].sum()
        weighted_pct = (excess.sum() / planned_total * 100) if planned_total > 0 else 0

        # Ungewichtete Quote bleibt als Headline
        count_pct = (tasks_over / total_tasks * 100) if total_tasks > 0 else 0

        # Anzeige: Excess in aktuellem Modus
        val, unit = self._to_display(excess.sum())

        direction = "positive" if weighted_pct < 10 else "negative"
        return {
            "label": "Überzeitquote",
            "value": f"{count_pct:.1f} %",
            "delta": f"{weighted_pct:.1f} % gewichtet · +{val:,.0f} {unit}",
            "delta_direction": direction,
        }

    def cost_per_category(self) -> pd.DataFrame:
        return (self.df
                .groupby("category", as_index=False)
                .agg(total_min=("actual_min", "sum"),
                     total_chf=("cost_chf", "sum"),
                     task_count=("task", "count"))
                .sort_values("total_min", ascending=False))

    def per_role_summary(self) -> pd.DataFrame:
        """Rollen-Zusammenfassung – ohne fragile Lambda in .agg()."""
        base = (self.df
                .groupby("role", as_index=False)
                .agg(tasks=("task", "count"),
                     total_min=("actual_min", "sum"),
                     total_planned=("planned_min", "sum"),
                     total_chf=("cost_chf", "sum")))
        # Effizienz sicher als separater Schritt (kein Lambda-Index-Bug)
        base["avg_efficiency"] = (base["total_planned"] / base["total_min"] * 100).round(1)
        return base.sort_values("total_min", ascending=False)

    def all_kpis(self) -> List[dict]:
        return [
            self.total_workload(),
            self.avg_efficiency(),
            self.utilisation_rate(),
            self.skill_mismatch_rate(),
            self.overtime_metrics(),   # FIX #2: gewichtete Version
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. CHART BUILDERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_load_chart(wl: WorkloadEngine, mode: str) -> go.Figure:
    mc = wl.merged_curves(mode)
    y_label = "Minuten" if mode == "minutes" else "CHF"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mc["time"], y=mc["demand"], name="Bedarf",
        line=dict(color=COLORS["chart_1"], width=2.5), fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=mc["time"], y=mc["capacity"], name="Kapazität",
        line=dict(color=COLORS["success"], width=2, dash="dot"),
    ))
    apply_layout(fig, f"Auslastungskurve ({y_label})", 380)
    fig.update_yaxes(title_text=y_label)
    return fig


def build_category_bar(kpi: KPIEngine) -> go.Figure:
    cat = kpi.cost_per_category()
    fig = go.Figure(go.Bar(
        x=cat["category"], y=cat["total_min"], marker_color=CHART_SERIES[:len(cat)],
        text=cat["total_min"].apply(lambda v: f"{v:,.0f}"), textposition="outside",
    ))
    apply_layout(fig, "Aufwand nach Kategorie (Min)", 360)
    return fig


def build_role_table(kpi: KPIEngine) -> pd.DataFrame:
    return kpi.per_role_summary()


def build_skill_scatter(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df["required_skill"], y=df["actual_skill"], mode="markers",
        marker=dict(size=8, color=COLORS["chart_3"], opacity=0.6),
        text=df["task"],
    ))
    fig.add_shape(type="line", x0=0.5, y0=0.5, x1=5.5, y1=5.5,
                  line=dict(dash="dash", color=COLORS["text_muted"]))
    apply_layout(fig, "Skill-Match (Soll vs. Ist)", 360)
    fig.update_xaxes(title_text="Benötigtes Skill-Level")
    fig.update_yaxes(title_text="Tatsächliches Skill-Level")
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. UI HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_kpi_card(kpi: dict):
    delta_html = ""
    if kpi.get("delta"):
        cls = kpi.get("delta_direction", "neutral")
        delta_html = f'<div class="kpi-delta {cls}">{kpi["delta"]}</div>'
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{kpi["label"]}</div>
        <div class="kpi-value">{kpi["value"]}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. MAIN APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    inject_css()

    # ── Sector Switcher ──
    col_title, col_switch = st.columns([4, 1])
    with col_title:
        st.markdown("""
        <h1 style="font-size:1.75rem;font-weight:700;margin:0 0 0.25rem 0;">
            🍳 Kitchen Ops · Workforce Intelligence
        </h1>
        <p style="color:#64748B;font-size:0.9rem;margin:0;">
            Echtzeitanalyse der Personalauslastung und Leistungskennzahlen
        </p>
        """, unsafe_allow_html=True)
    with col_switch:
        sector = st.selectbox("Bereich", ["Küche", "Gastrodienste"], label_visibility="collapsed")

    mode = st.radio("Ansicht", ["minutes", "CHF"], horizontal=True,
                    format_func=lambda x: "⏱ Minuten" if x == "minutes" else "💰 CHF")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Data ──
    df = build_sample_data(sector)
    kpi_engine = KPIEngine(df, mode)
    wl_engine = WorkloadEngine(df)

    # ── KPI Cards ──
    kpis = kpi_engine.all_kpis()
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(kpi)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Tabs ──
    tab_load, tab_detail, tab_skills = st.tabs(["📈 Auslastung", "📊 Detailanalyse", "🎯 Skills"])

    with tab_load:
        section_header("Belastungs- & Kapazitätskurve")
        st.plotly_chart(build_load_chart(wl_engine, mode), use_container_width=True)

    with tab_detail:
        c1, c2 = st.columns(2)
        with c1:
            section_header("Aufwand nach Kategorie")
            st.plotly_chart(build_category_bar(kpi_engine), use_container_width=True)
        with c2:
            section_header("Zusammenfassung nach Rolle")
            role_df = build_role_table(kpi_engine)
            st.dataframe(role_df.style.format({
                "total_min": "{:,.0f}", "total_planned": "{:,.0f}",
                "total_chf": "{:,.2f}", "avg_efficiency": "{:.1f}%"
            }), use_container_width=True, hide_index=True)

    with tab_skills:
        section_header("Skill-Level: Soll vs. Ist")
        st.plotly_chart(build_skill_scatter(df), use_container_width=True)
        mismatch_df = df[df["actual_skill"] < df["required_skill"]][
            ["employee_name", "role", "task", "required_skill", "actual_skill"]
        ].sort_values("required_skill", ascending=False)
        if not mismatch_df.empty:
            st.markdown(f"**{len(mismatch_df)} Aufgaben** mit Skill-Defizit:")
            st.dataframe(mismatch_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
