import streamlit as st
import math
import streamlit_analytics

# ==========================================
# 1. CORE MATH FUNCTIONS & UNIT TESTS
# ==========================================

def calc_crl(percentile: float, total_candidates: int) -> int:
    """Converts a JEE Main percentile to a Common Rank List (CRL) rank."""
    if percentile >= 100.0: return 1
    if percentile <= 0.0: return total_candidates
    return round(((100 - percentile) / 100) * total_candidates)

def crl_to_obc(crl: int, r_min: float, r_med: float, r_max: float) -> tuple:
    """Estimates OBC rank from CRL using conservative, median, and optimistic ratios."""
    opt = round(crl / r_max)
    med = round(crl / r_med)
    cons = round(crl / r_min)
    return max(1, opt), max(1, med), max(1, cons)

def obc_to_percentile(obc: int, total_candidates: int, r_min: float, r_med: float, r_max: float) -> tuple:
    """Estimates percentile range from an OBC rank."""
    crl_optimistic_percentile = obc * r_min 
    crl_conservative_percentile = obc * r_max
    crl_med = obc * r_med
    
    p_opt = max(0.0, 100 - (crl_optimistic_percentile * 100 / total_candidates))
    p_cons = max(0.0, 100 - (crl_conservative_percentile * 100 / total_candidates))
    p_med = max(0.0, 100 - (crl_med * 100 / total_candidates))
    
    return p_cons, p_med, p_opt

def run_tests():
    """Simple assertion checks to guarantee math validity on startup."""
    assert calc_crl(96.6, 1560000) == 53040, "CRL calculation failed"
    opt, med, cons = crl_to_obc(53040, 3.2, 3.35, 3.5)
    assert opt == 15154 and cons == 16575, "OBC calculation failed"
run_tests()

# ==========================================
# 2. TRACKING & UI CONFIGURATION
# ==========================================

# Everything inside this 'with' block will be tracked
with streamlit_analytics.track():
    st.set_page_config(page_title="JEE Percentile ⇄ OBC Rank", layout="wide")

    st.title("JEE Percentile ⇄ OBC-NCL Rank Converter")
    st.markdown("Type in either box and hit Enter to instantly convert between Percentile and OBC-NCL Rank.")

    # --- Sidebar Controls ---
    st.sidebar.header("Configuration Parameters")
    total_candidates = st.sidebar.number_input("Total Unique Candidates", min_value=100000, value=1560000, step=10000, key="total_cands")
    st.sidebar.markdown("---")
    st.sidebar.subheader("CRL to OBC Ratios")
    st.sidebar.markdown("*(Ratio = CRL / OBC Rank)*")
    r_min = st.sidebar.number_input("Conservative Ratio (Min)", value=3.2, step=0.05, key="r_min_input")
    r_med = st.sidebar.number_input("Median Ratio", value=3.35, step=0.05, key="r_med_input")
    r_max = st.sidebar.number_input("Optimistic Ratio (Max)", value=3.5, step=0.05, key="r_max_input")

    # --- Session State Initialization ---
    if 'p_input' not in st.session_state: st.session_state.p_input = 96.6
    if 'o_input' not in st.session_state: st.session_state.o_input = 15833 
    if 'last_edited' not in st.session_state: st.session_state.last_edited = 'percentile'

    # --- Callbacks for Bidirectional Updates ---
    def update_from_percentile():
        st.session_state.last_edited = 'percentile'
        p = st.session_state.p_input
        if p is not None and 0.0 <= p <= 100.0:
            crl = calc_crl(p, st.session_state.total_cands)
            _, med, _ = crl_to_obc(crl, st.session_state.r_min_input, st.session_state.r_med_input, st.session_state.r_max_input)
            st.session_state.o_input = int(med)

    def update_from_obc():
        st.session_state.last_edited = 'obc'
        o = st.session_state.o_input
        if o is not None and o > 0:
            _, p_med, _ = obc_to_percentile(o, st.session_state.total_cands, st.session_state.r_min_input, st.session_state.r_med_input, st.session_state.r_max_input)
            st.session_state.p_input = float(round(p_med, 4))

    # ==========================================
    # 3. MAIN INTERFACE (Side-by-Side Panes)
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Percentile (%)")
        p_val = st.number_input(
            "Enter Percentile", 
            min_value=0.0, max_value=100.0, 
            format="%.4f",
            key="p_input", 
            on_change=update_from_percentile,
            label_visibility="collapsed"
        )
        if not (0.0 <= p_val <= 100.0):
            st.error("Percentile must be between 0 and 100.")

    with col2:
        st.subheader("Estimated OBC-NCL Rank")
        o_val = st.number_input(
            "Enter OBC Rank", 
            min_value=1, 
            step=100,
            key="o_input", 
            on_change=update_from_obc,
            label_visibility="collapsed"
        )

    st.markdown("---")

    # ==========================================
    # 4. RESULTS & FORMULAS DISPLAY
    # ==========================================

    st.subheader("Detailed Breakdown")

    if st.session_state.last_edited == 'percentile':
        crl = calc_crl(p_val, total_candidates)
        opt_obc, med_obc, cons_obc = crl_to_obc(crl, r_min, r_med, r_max)
        
        st.write(f"**Intermediate CRL (All India Rank):** {crl:,}")
        
        summary_text = (
            f"With a {p_val}% percentile and {total_candidates:,} candidates:\n"
            f"• CRL ≈ {crl:,}\n"
            f"• OBC Rank ≈ {opt_obc:,} — {cons_obc:,} (Median: {med_obc:,})"
        )
        
        st.code(summary_text, language="text")
        
        with st.expander("Show Formulas Used"):
            st.markdown(f"- **CRL** = `(100 - {p_val}) / 100 * {total_candidates}`")
            st.markdown(f"- **OBC (Conservative)** = `CRL / {r_min}`")
            st.markdown(f"- **OBC (Optimistic)** = `CRL / {r_max}`")

    else:
        p_cons, p_med, p_opt = obc_to_percentile(o_val, total_candidates, r_min, r_med, r_max)
        crl_opt, crl_med, crl_cons = round(o_val * r_min), round(o_val * r_med), round(o_val * r_max)
        
        summary_text = (
            f"To achieve an OBC-NCL Rank of {o_val:,} with {total_candidates:,} candidates:\n"
            f"• Required CRL ≈ {crl_opt:,} — {crl_cons:,}\n"
            f"• Required Percentile ≈ {p_cons:.4f}% — {p_opt:.4f}% (Median: {p_med:.4f}%)"
        )
        
        st.code(summary_text, language="text")
        
        with st.expander("Show Formulas Used"):
            st.markdown(f"- **Implied CRL Range** = `{o_val} * {r_min}` to `{o_val} * {r_max}`")
            st.markdown(f"- **Percentile** = `100 - (CRL * 100 / {total_candidates})`")


    # ==========================================
    # 5. NIT COLLEGE PREDICTION MODULE
    # ==========================================

    st.markdown("---")
    st.subheader("Confirmed Colleges & Estimated Placements")

    NIT_DATA = [
        {"name": "NIT Tiruchirappalli", "min": 250, "max": 400, "lpa": 30.10},
        {"name": "NIT Surathkal", "min": 450, "max": 600, "lpa": 28.12},
        {"name": "NIT Warangal", "min": 550, "max": 750, "lpa": 30.80},
        {"name": "MNNIT Allahabad", "min": 900, "max": 1200, "lpa": 27.95},
        {"name": "NIT Rourkela", "min": 1100, "max": 1400, "lpa": 24.20},
        {"name": "NIT Calicut", "min": 1400, "max": 1800, "lpa": 23.80},
        {"name": "MNIT Jaipur", "min": 1600, "max": 2000, "lpa": 20.40},
        {"name": "VNIT Nagpur", "min": 1800, "max": 2300, "lpa": 19.10},
        {"name": "NIT Kurukshetra", "min": 2200, "max": 2800, "lpa": 21.50},
        {"name": "SVNIT Surat", "min": 2400, "max": 3000, "lpa": 18.26},
        {"name": "NIT Delhi", "min": 2500, "max": 3200, "lpa": 18.50},
        {"name": "NIT Jamshedpur", "min": 2600, "max": 3300, "lpa": 20.50},
        {"name": "MANIT Bhopal", "min": 2800, "max": 3500, "lpa": 18.80},
        {"name": "NIT Durgapur", "min": 3200, "max": 4000, "lpa": 17.90},
        {"name": "NIT Silchar", "min": 3800, "max": 4800, "lpa": 17.10},
        {"name": "NIT Jalandhar", "min": 4000, "max": 5000, "lpa": 16.74},
        {"name": "NIT Raipur", "min": 4500, "max": 5500, "lpa": 15.50},
        {"name": "NIT Hamirpur", "min": 5000, "max": 6500, "lpa": 14.80},
        {"name": "NIT Patna", "min": 5500, "max": 7000, "lpa": 14.50},
        {"name": "NIT Goa", "min": 6000, "max": 7500, "lpa": 13.80},
        {"name": "NIT Agartala", "min": 6500, "max": 8000, "lpa": 14.71},
        {"name": "NIT Uttarakhand", "min": 7000, "max": 8500, "lpa": 12.50},
        {"name": "NIT Puducherry", "min": 7500, "max": 9000, "lpa": 11.80},
        {"name": "NIT Meghalaya", "min": 8000, "max": 9500, "lpa": 12.10},
        {"name": "NIT Andhra Pradesh", "min": 8500, "max": 10000, "lpa": 10.50},
        {"name": "NIT Srinagar", "min": 9000, "max": 11000, "lpa": 11.00},
        {"name": "NIT Sikkim", "min": 9500, "max": 11500, "lpa": 9.80},
        {"name": "NIT Arunachal Pradesh", "min": 10000, "max": 12000, "lpa": 9.50},
        {"name": "NIT Manipur", "min": 11000, "max": 13000, "lpa": 9.20},
        {"name": "NIT Mizoram", "min": 12000, "max": 14000, "lpa": 8.80},
        {"name": "NIT Nagaland", "min": 13000, "max": 15000, "lpa": 8.50}
    ]

    predicted_z = int(st.session_state.o_input)
    matched_colleges = []

    for nit in NIT_DATA:
        x = nit["min"]
        y = nit["max"]
        status = None
        
        if predicted_z < x:
            status = "Safe"
        elif x <= predicted_z <= y:
            status = "Very Likely"
        elif y < predicted_z <= (y + 500):
            status = "Possible"
            
        if status:
            matched_colleges.append({
                "NIT Name": nit["name"],
                "Prediction": status,
                "Cutoff Range (OBC Rank)": f"{x:,} — {y:,}",
                "Mean CSE Package (LPA)": f"₹{nit['lpa']:.2f} LPA"
            })
        
        if len(matched_colleges) == 3:
            break

    if not matched_colleges:
        st.info("No NIT CSE predicted for this rank based on the dataset.")
    else:
        st.table(matched_colleges)
