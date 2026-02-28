import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from pathlib import Path


st.set_page_config(page_title="Satark-Recover Demo", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

    :root {
        --brand: #0f766e;
        --brand-soft: #ccfbf1;
        --ink: #0f172a;
        --muted: #475569;
        --card: #ffffff;
        --bg: linear-gradient(135deg, #f8fafc 0%, #eef2ff 40%, #ecfeff 100%);
    }

    html, body, [class*="css"] {
        font-family: "Manrope", sans-serif;
    }

    .stApp {
        background: var(--bg);
    }

    .stApp {
        color: var(--ink);
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {
        color: var(--ink);
    }

    [data-testid="stSelectbox"] label,
    [data-testid="stRadio"] label,
    [data-testid="stSelectbox"] div,
    [data-testid="stRadio"] div {
        color: var(--ink) !important;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] * {
        color: var(--ink) !important;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 0.6rem 0.9rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--brand);
        font-weight: 800;
    }

    .satark-banner {
        background: linear-gradient(90deg, #134e4a 0%, #0f766e 45%, #0ea5a4 100%);
        color: white;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin: 0.4rem 0 1rem 0;
        box-shadow: 0 10px 30px rgba(15, 118, 110, 0.25);
    }

    .satark-banner p {
        margin: 0;
        opacity: 0.95;
        color: #f8fafc;
    }

    [data-testid="stAlert"] * {
        color: inherit !important;
    }

    button[title="View fullscreen"],
    [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }

    .hero-wrap {
        position: relative;
        min-height: 58vh;
        border-radius: 24px;
        padding: 2.2rem 2.2rem 1.8rem 2.2rem;
        background:
            radial-gradient(circle at 78% 22%, rgba(15, 118, 110, 0.18), transparent 35%),
            radial-gradient(circle at 18% 80%, rgba(14, 165, 164, 0.12), transparent 40%),
            linear-gradient(135deg, #ffffff 0%, #f0fdfa 52%, #ecfeff 100%);
        border: 1px solid #ccfbf1;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
        overflow: hidden;
    }

    .hero-kicker {
        display: inline-block;
        color: #0f766e;
        background: #ccfbf1;
        border: 1px solid #99f6e4;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.02em;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-size: clamp(2.2rem, 5.6vw, 5.2rem);
        font-weight: 800;
        line-height: 1.02;
        color: #0b1220 !important;
        margin: 0 0 0.55rem 0;
    }

    .hero-subtitle {
        font-size: clamp(1rem, 1.6vw, 1.36rem);
        line-height: 1.5;
        color: #1e293b;
        max-width: 760px;
        margin-bottom: 1rem;
    }

    .hero-stat {
        display: inline-block;
        margin-right: 0.6rem;
        margin-bottom: 0.45rem;
        background: #ffffff;
        border: 1px solid #d1fae5;
        border-radius: 12px;
        padding: 0.35rem 0.7rem;
        font-weight: 700;
        color: #0f766e;
    }
    /* Style ALL Streamlit buttons including download buttons */
div.stDownloadButton > button,
div.stButton > button {
    background-color: #0f766e !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
}

div.stDownloadButton > button:hover,
div.stButton > button:hover {
    background-color: #0e5f58 !important;
    color: white !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def risk_to_score(level):
    mapping = {"Low": 1, "Moderate": 2, "High": 3}
    return mapping.get(level, 1)


def projected_risk_level(health_score):
    if health_score < 45:
        return "High"
    if health_score < 60:
        return "Moderate"
    return "Low"


def get_recommended_action(risk_level):
    if risk_level == "High":
        return "Contact in 24h + restructure review"
    if risk_level == "Moderate":
        return "Weekly check-in + payment reminder"
    return "Routine monitoring"


def build_timeline(row):
    months = pd.date_range(end=pd.Timestamp.today(), periods=6, freq="M")
    jitter = [2, -1, 1, -2, 1, 0]
    slope = {"High": -3, "Moderate": -1, "Low": 1}.get(row["risk_level"], -1)
    regional_drag = 1 if row["regional_npa"] == "High" else -1

    values = []
    peer_values = []
    for i in range(6):
        reverse_offset = (5 - i) * slope
        health = clamp(int(row["health_score"] + reverse_offset + regional_drag + jitter[i]))
        peer = clamp(int(row["peer_score"] + jitter[i]))
        values.append(health)
        peer_values.append(peer)

    return pd.DataFrame(
        {
            "month": months.strftime("%b %Y"),
            "Borrower Health": values,
            "Peer Benchmark": peer_values,
        }
    )


def risk_breakdown(row):
    peer_gap = max(0, int(row["peer_score"] - row["health_score"]))
    regional_pressure = 72 if row["regional_npa"] == "High" else 24
    repayment_irregularity = clamp(90 - int(row["health_score"]))
    cashflow_stress = clamp(80 - int(row["health_score"]) + (12 if row["regional_npa"] == "High" else 0))
    peer_divergence = clamp(peer_gap * 8)

    return {
        "Repayment irregularity": repayment_irregularity,
        "Cashflow stress": cashflow_stress,
        "Peer divergence": peer_divergence,
        "Regional pressure": regional_pressure,
    }


def action_plan(risk_level):
    plans = {
        "High": [
            "Call relationship manager within 24 hours.",
            "Request temporary restructuring or moratorium assessment.",
            "Share cashflow estimate for next 30 days.",
        ],
        "Moderate": [
            "Pay minimum EMI before due date.",
            "Review non-essential expenses for this cycle.",
            "Opt in for weekly reminder from bank support team.",
        ],
        "Low": [
            "Continue on-time repayment behavior.",
            "Set auto-pay if not already enabled.",
            "Review loan health score monthly.",
        ],
    }
    return plans.get(risk_level, plans["Low"])


def intervention_projection(score, intervention):
    delta_map = {
        "No intervention": 0,
        "Advisory call": 3,
        "Repayment reminder + counseling": 5,
        "EMI moratorium": 7,
        "Restructuring support": 10,
        "Combined support package": 14,
    }
    delta = delta_map[intervention]
    projected = clamp(score + delta)
    return projected, delta


def transparent_cutout(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    near_white = (rgb[:, :, 0] > 240) & (rgb[:, :, 1] > 240) & (rgb[:, :, 2] > 240)
    alpha[near_white] = 0
    arr[:, :, 3] = alpha
    return Image.fromarray(arr)


data = pd.read_csv("data.csv")
region_coords = {
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550},
}
interventions = [
    "No intervention",
    "Advisory call",
    "Repayment reminder + counseling",
    "EMI moratorium",
    "Restructuring support",
    "Combined support package",
]
demo_scenes = [
    {
        "title": "Portfolio Snapshot",
        "page": "Bank Dashboard",
        "borrower": "Rahul",
        "intervention": "No intervention",
        "narration": "Bank starts with portfolio KPIs and prioritization queue to detect early stress clusters.",
    },
    {
        "title": "High-Risk Deep Dive",
        "page": "Bank Dashboard",
        "borrower": "Amit",
        "intervention": "Restructuring support",
        "narration": "Officer opens a high-risk profile and inspects trend + explainable drivers behind stress.",
    },
    {
        "title": "Intervention Impact",
        "page": "Bank Dashboard",
        "borrower": "Amit",
        "intervention": "Combined support package",
        "narration": "Intervention simulator projects improvement in health score and risk category.",
    },
    {
        "title": "Borrower Transparency",
        "page": "Borrower Dashboard",
        "borrower": "Rahul",
        "intervention": "Advisory call",
        "narration": "Borrower sees personal score, peer benchmark, and plain-language stress explanation.",
    },
    {
        "title": "Action Plan + Export",
        "page": "Borrower Dashboard",
        "borrower": "Rahul",
        "intervention": "Repayment reminder + counseling",
        "narration": "Platform provides 30-day action plan and downloadable report for follow-up.",
    },
]

st.sidebar.title("Satark-Recover")
if "demo_step" not in st.session_state:
    st.session_state["demo_step"] = 0
demo_mode = st.sidebar.toggle("Demo Mode (60-sec guided flow)", value=False)
default_logo_path = Path("logo-2.png")
if demo_mode:
    if st.session_state["demo_step"] >= len(demo_scenes):
        st.session_state["demo_step"] = 0
    active_scene = demo_scenes[st.session_state["demo_step"]]
    st.sidebar.markdown(f"**Scene {st.session_state['demo_step'] + 1}/{len(demo_scenes)}**")
    st.sidebar.write(active_scene["title"])
    c_prev, c_next, c_reset = st.sidebar.columns(3)
    if c_prev.button("Prev", use_container_width=True):
        st.session_state["demo_step"] = (st.session_state["demo_step"] - 1) % len(demo_scenes)
        st.rerun()
    if c_next.button("Next", use_container_width=True):
        st.session_state["demo_step"] = (st.session_state["demo_step"] + 1) % len(demo_scenes)
        st.rerun()
    if c_reset.button("Reset", use_container_width=True):
        st.session_state["demo_step"] = 0
        st.rerun()
    page = active_scene["page"]
else:
    page = st.sidebar.radio("Select View", ["Bank Dashboard", "Borrower Dashboard"])
st.sidebar.caption("Prototype: Simulated CBHM outputs for demo")

st.title("Satark-Recover: AI Early Stress Detection Platform")
hero_left, hero_right = st.columns([1.45, 1], vertical_alignment="center")
with hero_left:
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-kicker">Satark Setu Intelligence Layer</div>
            <div class="hero-title">SATARK SETU</div>
            <div class="hero-subtitle">
                Contextual Early Stress Detection for lending portfolios with transparent borrower insights,
                explainable risk signals, and intervention simulation.
            </div>
            <span class="hero-stat">CBHM Simulation</span>
            <span class="hero-stat">Bank + Borrower Views</span>
            <span class="hero-stat">Intervention Forecasting</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hero_right:
    if default_logo_path.exists():
        logo_image = Image.open(default_logo_path)
        logo_cutout = transparent_cutout(logo_image)
        st.image(logo_cutout, use_container_width=True, caption="Satark Setu")
    else:
        st.warning("Logo file not found: logo-2.png")
st.markdown(
    """
    <div class="satark-banner">
        <p><strong>Contextual Borrower Health Model (Simulated)</strong><br>
        Live demo of borrower health, peer benchmarks, regional risk context, and intervention simulation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
if demo_mode:
    active_scene = demo_scenes[st.session_state["demo_step"]]
    st.info(
        f"Demo Scene {st.session_state['demo_step'] + 1}/{len(demo_scenes)} - "
        f"**{active_scene['title']}**\n\n{active_scene['narration']}"
    )
    st.progress((st.session_state["demo_step"] + 1) / len(demo_scenes))

if page == "Bank Dashboard":
    st.header("Bank Risk Monitoring Dashboard")

    high_risk_count = int((data["risk_level"] == "High").sum())
    moderate_risk_count = int((data["risk_level"] == "Moderate").sum())
    avg_health = round(float(data["health_score"].mean()), 1)
    total_exposure = int(data["loan_amount"].sum())
    high_stress_regions = int(data[data["regional_npa"] == "High"]["region"].nunique())

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Exposure", f"INR {total_exposure:,}")
    k2.metric("Avg Health Score", avg_health)
    k3.metric("High Risk Borrowers", high_risk_count)
    k4.metric("Moderate Risk", moderate_risk_count)
    k5.metric("High-Stress Regions", high_stress_regions)

    st.subheader("Alerts and Prioritization Queue")
    alerts_df = data.copy()
    alerts_df["priority_score"] = (
        alerts_df["risk_level"].map(risk_to_score) * 40
        + (100 - alerts_df["health_score"])
        + alerts_df["regional_npa"].map({"High": 15, "Low": 0})
    )
    alerts_df["recommended_action"] = alerts_df["risk_level"].apply(get_recommended_action)
    alerts_df = alerts_df.sort_values("priority_score", ascending=False)
    st.dataframe(
        alerts_df[
            [
                "borrower_id",
                "name",
                "region",
                "scheme",
                "health_score",
                "risk_level",
                "priority_score",
                "recommended_action",
            ]
        ],
        use_container_width=True,
    )

    st.download_button(
        "Download Alerts Queue (CSV)",
        data=alerts_df.to_csv(index=False),
        file_name="satark_alert_queue.csv",
        mime="text/csv",
    )

    st.subheader("Regional Stress View")
    map_df = (
        data.groupby(["region", "regional_npa"], as_index=False)["loan_amount"]
        .sum()
        .rename(columns={"loan_amount": "exposure"})
    )
    map_df["lat"] = map_df["region"].map(lambda r: region_coords[r]["lat"])
    map_df["lon"] = map_df["region"].map(lambda r: region_coords[r]["lon"])
    map_df["stress_marker"] = map_df["regional_npa"].map({"High": 300, "Low": 120})
    st.map(map_df.rename(columns={"lon": "lon", "lat": "lat"}), use_container_width=True)
    st.caption("Larger concentration implies higher stress context and exposure in that region.")

    st.subheader("Borrower Deep Dive")
    if demo_mode:
        st.session_state["bank_borrower"] = active_scene["borrower"]
    borrower = st.selectbox("Select Borrower", data["name"], key="bank_borrower")
    row = data[data["name"] == borrower].iloc[0]

    st.markdown(f"**Borrower:** {row['name']} ({row['borrower_id']}) | **Scheme:** {row['scheme']} | **Region:** {row['region']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Health Score", row["health_score"])
    c2.metric("Peer Score", row["peer_score"])
    c3.metric("Regional Stress", row["regional_npa"])
    c4.metric("Loan Amount", f"INR {row['loan_amount']:,}")

    timeline = build_timeline(row)
    st.markdown("**Risk Timeline (Last 6 Months, Simulated)**")
    st.line_chart(timeline.set_index("month"), use_container_width=True)

    st.markdown("**Explainable Risk Breakdown**")
    factors = risk_breakdown(row)
    for factor, value in factors.items():
        st.write(f"{factor}: {value}/100")
        st.progress(value / 100)

    st.markdown("**Intervention Simulator**")
    if demo_mode:
        st.session_state["bank_intervention"] = active_scene["intervention"]
    intervention = st.selectbox(
        "Select intervention",
        interventions,
        key="bank_intervention",
    )
    projected_score, improvement = intervention_projection(int(row["health_score"]), intervention)
    projected_risk = projected_risk_level(projected_score)

    p1, p2, p3 = st.columns(3)
    p1.metric("Projected Health Score", projected_score, delta=improvement)
    p2.metric("Current Risk", row["risk_level"])
    p3.metric("Projected Risk", projected_risk)

    if projected_risk == "High":
        st.error("Projected outlook remains high risk. Immediate support still required.")
    elif projected_risk == "Moderate":
        st.warning("Projected outlook improves to moderate risk. Monitor weekly.")
    else:
        st.success("Projected outlook becomes low risk with selected intervention.")

if page == "Borrower Dashboard":
    st.header("Borrower Loan Health Dashboard")

    if demo_mode:
        st.session_state["borrower_name"] = active_scene["borrower"]
    borrower = st.selectbox("Select Your Name", data["name"], key="borrower_name")
    row = data[data["name"] == borrower].iloc[0]

    st.subheader(f"Your Loan Health: {row['name']} ({row['borrower_id']})")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Your Health Score", row["health_score"])
    col2.metric("Peer Average", row["peer_score"])
    col3.metric("Loan Amount", f"INR {row['loan_amount']:,}")
    col4.metric("Risk Level", row["risk_level"])

    st.write(f"**Region:** {row['region']}")
    st.write(f"**Scheme:** {row['scheme']}")
    st.write(f"**Regional Stress Level:** {row['regional_npa']}")

    if row["health_score"] < row["peer_score"]:
        st.info("You are below peer benchmark. Early action can prevent repayment stress.")
    else:
        st.success("You are on par with or above peer benchmark.")

    st.subheader("Your 6-Month Trend (Simulated)")
    timeline = build_timeline(row)
    st.line_chart(timeline.set_index("month"), use_container_width=True)

    st.subheader("Why this risk level?")
    factors = risk_breakdown(row)
    for factor, value in factors.items():
        st.write(f"{factor}: {value}/100")
        st.progress(value / 100)

    st.subheader("What-if Intervention Simulator")
    if demo_mode:
        st.session_state["borrower_intervention"] = active_scene["intervention"]
    borrower_intervention = st.selectbox(
        "Choose support option",
        interventions,
        key="borrower_intervention",
    )

    projected_score, improvement = intervention_projection(int(row["health_score"]), borrower_intervention)
    projected_risk = projected_risk_level(projected_score)

    b1, b2 = st.columns(2)
    b1.metric("Projected Health", projected_score, delta=improvement)
    b2.metric("Projected Risk", projected_risk)

    st.subheader("30-Day Action Plan")
    for idx, item in enumerate(action_plan(row["risk_level"]), start=1):
        st.write(f"{idx}. {item}")

    if row["risk_level"] == "High":
        st.error("High stress detected. Please contact bank for restructuring support.")
    elif row["risk_level"] == "Moderate":
        st.warning("Moderate stress. Try paying minimum EMI this cycle.")
    else:
        st.success("Your loan is healthy.")

    report_df = pd.DataFrame(
        {
            "field": [
                "borrower_id",
                "name",
                "scheme",
                "region",
                "loan_amount",
                "current_health_score",
                "peer_score",
                "regional_npa",
                "current_risk",
                "projected_health",
                "projected_risk",
            ],
            "value": [
                row["borrower_id"],
                row["name"],
                row["scheme"],
                row["region"],
                row["loan_amount"],
                row["health_score"],
                row["peer_score"],
                row["regional_npa"],
                row["risk_level"],
                projected_score,
                projected_risk,
            ],
        }
    )

    st.download_button(
        "Download My Risk Report (CSV)",
        data=report_df.to_csv(index=False),
        file_name=f"satark_report_{row['borrower_id']}.csv",
        mime="text/csv",
    )
