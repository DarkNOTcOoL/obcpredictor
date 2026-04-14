import math
import numpy as np
from scipy.interpolate import PchipInterpolator
import streamlit as st
import streamlit_analytics2 as streamlit_analytics

# ==========================================
# 1. CORE MATH FUNCTIONS
# ==========================================

def calc_crl(percentile: float, total_candidates: int) -> int:
    """Converts a JEE Main percentile to a Common Rank List (CRL) rank."""
    if percentile >= 100.0: return 1
    if percentile <= 0.0: return total_candidates
    return round(((100 - percentile) / 100) * total_candidates)

def crl_to_percentile_gen(crl: int, total_candidates: int) -> float:
    """Converts CRL directly back to Percentile (General Category)."""
    return max(0.0, 100 - (crl * 100 / total_candidates))

def crl_to_cat(crl: int, r_min: float, r_med: float, r_max: float) -> tuple:
    """Estimates Category rank from CRL using conservative, median, and optimistic ratios."""
    r_max, r_med, r_min = max(0.01, r_max), max(0.01, r_med), max(0.01, r_min)
    opt = round(crl / r_max)
    med = round(crl / r_med)
    cons = round(crl / r_min)
    return max(1, opt), max(1, med), max(1, cons)

def cat_to_percentile(cat: int, total_candidates: int, r_min: float, r_med: float, r_max: float) -> tuple:
    """Estimates percentile range from a Category rank."""
    crl_opt = cat * r_min 
    crl_cons = cat * r_max
    crl_med = cat * r_med
    
    p_opt = max(0.0, 100 - (crl_opt * 100 / total_candidates))
    p_cons = max(0.0, 100 - (crl_cons * 100 / total_candidates))
    p_med = max(0.0, 100 - (crl_med * 100 / total_candidates))
    return p_cons, p_med, p_opt



import numpy as np
from scipy.interpolate import PchipInterpolator

def get_obc_ratio(p: float) -> float:
    # xp: Percentiles
    # fp: Corresponding CRL/OBC Ratios
    xp = [
        0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 80.0, 
        85.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 96.666, 
        97.0, 97.5, 98.0, 99.0, 99.5, 99.9, 100.0
    ]
    fp = [
        2.07, 2.08, 2.09, 2.11, 2.13, 2.16, 2.22, 2.31, 2.38, 2.47, 
        2.58, 2.75, 2.80, 2.86, 2.93, 3.01, 3.10, 3.22, 3.35, 
        3.52, 3.75, 4.05, 4.60, 5.15, 5.85, 6.00
    ]

    interpolator = PchipInterpolator(xp, fp)
    
    # Clamp the input percentile between 0 and 100
    p = max(0.0, min(100.0, p))
    
    return float(interpolator(p))

def get_ews_ratio(p: float) -> float:
    """High-precision interpolation for CRL/EWS ratio based on updated density."""
    xp = [
        0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 85.0, 90.0, 91.0, 92.0, 93.0, 
        94.0, 95.0, 96.0, 96.5, 97.0, 97.5, 97.55, 98.0, 98.5, 99.0, 99.5, 99.9
    ]
    fp = [
        9.80, 9.80, 9.80, 9.75, 9.70, 9.60, 9.40, 9.10, 8.40, 7.90, 7.40, 7.15, 6.90, 6.50, 
        5.90, 5.50, 5.70, 5.85, 6.00, 6.30, 6.30, 6.70, 6.90, 7.40, 8.20, 10.40
    ]
    return float(np.interp(p, xp, fp))

def get_active_ratio(p: float, category: str) -> float:
    if category == "OBC-NCL": return get_obc_ratio(p)
    if category == "EWS": return get_ews_ratio(p)
    return 1.0

# ==========================================
# 2. TRACKING & UI CONFIGURATION
# ==========================================

with streamlit_analytics.track():
    st.set_page_config(page_title="JEE Rank Predictor", layout="wide")
    st.title("JEE Percentile ⇄ Rank Converter")

    # --- Session State Initialization ---
    if 'p_input' not in st.session_state: st.session_state.p_input = 96.6
    if 'last_edited' not in st.session_state: st.session_state.last_edited = 'percentile'
    
    def update_category():
        """Instantly updates ratios and inputs when radio button changes."""
        cat = st.session_state.category
        total_c = st.session_state.get('total_cands', 1550000)
        p = st.session_state.get('p_input', 96.6)
        
        if cat != "General":
            base_ratio = get_active_ratio(p, cat)
            st.session_state.r_med_input = float(round(base_ratio, 2))
            
            crl = calc_crl(p, total_c)
            _, med, _ = crl_to_cat(crl, max(0.01, st.session_state.r_med_input - 0.15), st.session_state.r_med_input, st.session_state.r_med_input + 0.15)
            st.session_state.r_input = int(med)
        else:
            crl = calc_crl(p, total_c)
            st.session_state.r_input = int(crl)

    # 1. Category Selection First
    category = st.radio(
        "Select your Category:", 
        ["General", "OBC-NCL", "EWS"], 
        horizontal=True,
        key="category",
        on_change=update_category
    )

    st.markdown("Type in either box and hit Enter to instantly convert between Percentile and Rank.")

    if 'r_input' not in st.session_state: st.session_state.r_input = 53040 if category == "General" else 15833 
    
    if 'r_med_input' not in st.session_state: 
        base_init = get_active_ratio(st.session_state.p_input, category)
        st.session_state.r_med_input = float(round(base_init, 2))

    # --- Sidebar Controls ---
    st.sidebar.header("Configuration Parameters")
    total_candidates = st.sidebar.number_input("Total Unique Candidates", min_value=100000, value=1550000, step=10000, key="total_cands")
    
    if category != "General":
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"CRL to {category} Ratio (Auto-Adjusting)")
        st.sidebar.markdown(f"*(Ratio = CRL / {category} Rank)*")
        r_med = st.sidebar.number_input("Median Ratio", min_value=0.01, step=0.05, key="r_med_input")
        r_min = max(0.01, r_med - 0.15)
        r_max = r_med + 0.15
    else:
        r_min, r_med, r_max = 1.0, 1.0, 1.0

    # --- Callbacks for Bidirectional Updates ---
    def update_from_percentile():
        st.session_state.last_edited = 'percentile'
        p = st.session_state.p_input
        if p is not None and 0.0 <= p <= 100.0:
            crl = calc_crl(p, st.session_state.total_cands)
            
            if st.session_state.category == "General":
                st.session_state.r_input = crl
            else:
                base_ratio = get_active_ratio(p, st.session_state.category)
                st.session_state.r_med_input = float(round(base_ratio, 2))
                temp_min = max(0.01, st.session_state.r_med_input - 0.15)
                temp_max = st.session_state.r_med_input + 0.15

                _, med, _ = crl_to_cat(crl, temp_min, st.session_state.r_med_input, temp_max)
                st.session_state.r_input = int(med)

    def update_from_rank():
        st.session_state.last_edited = 'rank'
        r = st.session_state.r_input
        if r is not None and r > 0:
            if st.session_state.category == "General":
                p_final = crl_to_percentile_gen(r, st.session_state.total_cands)
                st.session_state.p_input = float(round(p_final, 4))
            else:
                current_med = st.session_state.r_med_input
                temp_min = max(0.01, current_med - 0.15)
                temp_max = current_med + 0.15
                
                _, p_med_rough, _ = cat_to_percentile(r, st.session_state.total_cands, temp_min, current_med, temp_max)
                
                base_ratio = get_active_ratio(p_med_rough, st.session_state.category)
                st.session_state.r_med_input = float(round(base_ratio, 2))
                
                new_min = max(0.01, st.session_state.r_med_input - 0.15)
                new_max = st.session_state.r_med_input + 0.15

                _, p_med_final, _ = cat_to_percentile(r, st.session_state.total_cands, new_min, st.session_state.r_med_input, new_max)
                st.session_state.p_input = float(round(p_med_final, 4))

    # ==========================================
    # 3. MAIN INTERFACE (Side-by-Side Panes)
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Percentile (%)")
        p_val = st.number_input(
            "Enter Percentile", 
            min_value=0.0, max_value=100.0, 
            step=0.1,
            format="%.4f",
            key="p_input", 
            on_change=update_from_percentile,
            label_visibility="collapsed"
        )
        if not (0.0 <= p_val <= 100.0):
            st.error("Percentile must be between 0 and 100.")

    with col2:
        rank_label = "CRL Rank" if category == "General" else f"{category} Rank"
        st.subheader(f"Estimated {rank_label}")
        r_val = st.number_input(
            f"Enter {rank_label}", 
            min_value=1, 
            step=100,
            key="r_input", 
            on_change=update_from_rank,
            label_visibility="collapsed"
        )

    st.markdown("---")

    # ==========================================
    # 4. RESULTS & FORMULAS DISPLAY
    # ==========================================

    st.subheader("Detailed Breakdown")

    if st.session_state.last_edited == 'percentile':
        crl = calc_crl(p_val, total_candidates)
        
        if category == "General":
            summary_text = (
                f"With a {p_val}% percentile and {total_candidates:,} candidates:\n"
                f"• CRL ≈ {crl:,}"
            )
            st.code(summary_text, language="text")
            with st.expander("Show Formulas Used"):
                st.markdown(f"- **CRL** = `(100 - {p_val}) / 100 * {total_candidates}`")
        else:
            opt_cat, med_cat, cons_cat = crl_to_cat(crl, r_min, r_med, r_max)
            st.write(f"**Intermediate CRL (All India Rank):** {crl:,}")
            summary_text = (
                f"With a {p_val}% percentile and {total_candidates:,} candidates:\n"
                f"• CRL ≈ {crl:,}\n"
                f"• {category} Rank ≈ {opt_cat:,} — {cons_cat:,}"
            )
            st.code(summary_text, language="text")
            with st.expander("Show Formulas Used"):
                st.markdown(f"- **CRL** = `(100 - {p_val}) / 100 * {total_candidates}`")
                st.markdown(f"- **{category} (Conservative)** = `CRL / {r_min:.2f}`")
                st.markdown(f"- **{category} (Optimistic)** = `CRL / {r_max:.2f}`")

    else:
        if category == "General":
            p_final = crl_to_percentile_gen(r_val, total_candidates)
            summary_text = (
                f"To achieve a CRL of {r_val:,} with {total_candidates:,} candidates:\n"
                f"• Required Percentile ≈ {p_final:.4f}%"
            )
            st.code(summary_text, language="text")
            with st.expander("Show Formulas Used"):
                st.markdown(f"- **Percentile** = `100 - (CRL * 100 / {total_candidates})`")
        else:
            p_cons, p_med, p_opt = cat_to_percentile(r_val, total_candidates, r_min, r_med, r_max)
            crl_opt, crl_med, crl_cons = round(r_val * r_min), round(r_val * r_med), round(r_val * r_max)
            summary_text = (
                f"To achieve an {category} Rank of {r_val:,} with {total_candidates:,} candidates:\n"
                f"• Required CRL ≈ {crl_opt:,} — {crl_cons:,}\n"
                f"• Required Percentile ≈ {p_cons:.4f}% — {p_opt:.4f}%"
            )
            st.code(summary_text, language="text")
            with st.expander("Show Formulas Used"):
                st.markdown(f"- **Implied CRL Range** = `{r_val} * {r_min:.2f}` to `{r_val} * {r_max:.2f}`")
                st.markdown(f"- **Percentile** = `100 - (CRL * 100 / {total_candidates})`")

    # ==========================================
    # 5. NIT COLLEGE PREDICTION MODULE
    # ==========================================

    st.markdown("---")
    st.subheader("Confirmed Colleges & Estimated Placements *(works only for OBC)*")

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

    predicted_z = int(st.session_state.r_input)
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
                f"Cutoff Range ({category} Rank)": f"{x:,} — {y:,}",
                "Mean CSE Package (LPA)": f"₹{nit['lpa']:.2f} LPA"
            })
        
        if len(matched_colleges) == 3:
            break

    if not matched_colleges:
        st.info("No NIT CSE predicted for this rank based on the dataset.")
    else:
        st.table(matched_colleges)