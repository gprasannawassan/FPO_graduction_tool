import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
.main-title-card {
    background-color: #0073e6;
    padding: 3px;
    border-radius: 4px;
    margin-bottom: 8px;
}
.main-title-card h1 {
    color: white;
    font-size: 22px;
    font-weight: bold;
    text-align: left;
    margin: 0;
}

.section-card {
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
    color: black;
}

.section-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    color: black;
}

.section-text {
    font-size: 20px;
    font-weight: bold;
    color: black;
}

.progress-container {
    width: 100%;
    background-color: #ddd;
    border-radius: 8px;
    margin-top: 8px;
}

.progress-bar {
    height: 10px;
    border-radius: 8px;
}

.overall-card {
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    margin-top: 30px;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CLEAN FUNCTIONS
# ==============================
def clean_text(x):
    return str(x).strip().lower()

def normalize(val):
    val = clean_text(val)
    if val in ["yes", "y"]:
        return "yes"
    elif val in ["no", "n"]:
        return "no"
    return val

def maturity_label(percent):
    if percent < 50:
        return "Nascent", "red"
    elif percent < 80:
        return "Somewhat Mature", "orange"
    elif percent < 100:
        return "Near Mature", "lightgreen"
    else:
        return "Mature", "green"

# ==============================
# LOAD DATA
# ==============================
file_path = "FPO_Dashboard.xlsx"

response_df = pd.read_excel(file_path, sheet_name="Response")
mature_df = pd.read_excel(file_path, sheet_name="Mature")

try:
    rules_df = pd.read_excel(file_path, sheet_name="Rules")
    rules_df = rules_df.applymap(clean_text)
    rules_df.columns = rules_df.columns.str.strip().str.lower().str.replace(" ", "_")
except ValueError:
    st.warning("⚠️ Rules sheet not found in Excel. Please add a sheet named 'Rules'.")
    rules_df = pd.DataFrame(columns=["percentage", "area_of_improvements", "action_plan"])

response_df = response_df.applymap(clean_text)
mature_df = mature_df.applymap(clean_text)

response_df.columns = response_df.columns.map(clean_text)
mature_df.columns = mature_df.columns.map(clean_text)

# ==============================
# CREATE MATURE MAP
# ==============================
mature_map = {}
for i in range(len(mature_df)):
    key = clean_text(mature_df.iloc[i, 0])
    val = normalize(mature_df.iloc[i, 1])
    if key not in ["nan", "", "none"]:
        mature_map[key] = val

# ==============================
# SESSION STATE
# ==============================
if "selected_section" not in st.session_state:
    st.session_state.selected_section = None
if "selected_percent" not in st.session_state:
    st.session_state.selected_percent = None

# ==============================
# MAIN DASHBOARD VIEW
# ==============================
if st.session_state.selected_section is None:
    st.markdown('<div class="main-title-card"><h1>FPO Graduation Tool</h1></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1,2])
    with col1:
        selected_fpo = st.selectbox("Select FPO", response_df["fpo_registration-fpo_name"].unique())

    filtered_df = response_df[response_df["fpo_registration-fpo_name"] == selected_fpo]

    sections = {
        "FPO Registration": [
            "fpo_registration-registration_certificate",
            "fpo_registration-filing_regularly",
            "fpo_registration-notice_non-filing_returns",
            "fpo_registration-display_certificate",
            "fpo_registration-bylaws_copy_available"
        ],
        "Membership": [
            "fpo_membership-membership_forms_available",
            "fpo_membership-membership_receipts_available",
            "fpo_membership-membership_data_available",
            "fpo_membership-share_certificates_issued",
            "fpo_membership-share_certificates_acknowledged",
            "fpo_membership-active_shareholders_50percent"
        ],
        "Institutional Strength and Governance": [
            "strength_governanace-bod-tenure_rotation_rules",
            "strength_governanace-bod-bod_meet_once_a_month",
            "strength_governanace-bod-meeting_quorum",
            "strength_governanace-bod-meetings_documented",
            "strength_governanace-bod-financial_update_bod_meeting",
            "strength_governanace-bod-bod_sanctions_annual_budget",
            "strength_governanace-fpg-members_organized_fpgs",
            "strength_governanace-fpg-financial_update_in_fpg",
            "strength_governanace-fpg-bod_minutes_in_fpg",
            "strength_governanace-fpg-fpg_with_1_or_2_leaders",
            "strength_governanace-fpg-fpg_minutes_in_bod",
            "strength_governanace-capacity_building-member_education",
            "strength_governanace-capacity_building-bod_fpo_staff_trainings_last_2_years",
            "strength_governanace-agm_patronage_bonus-agm_every_year",
            "strength_governanace-agm_patronage_bonus-max_patronage_bonus",
            "strength_governanace-agm_patronage_bonus-annual_report"
        ]
    }

    # Calculate performance
    section_scores = {}
    for section, cols in sections.items():
        total = 0
        correct = 0
        for col in cols:
            clean_col = clean_text(col)
            if clean_col in response_df.columns and clean_col in mature_map:
                response_val = normalize(filtered_df.iloc[0][clean_col])
                mature_val = mature_map[clean_col]
                total += 1
                if response_val == mature_val:
                    correct += 1
        percent = (correct / total) * 100 if total > 0 else 0
        section_scores[section] = {"percent": round(percent)}

    # Display section cards
    cols = st.columns(3)
    for j, (section, data) in enumerate(section_scores.items()):
        with cols[j]:
            percent = data["percent"]
            label, color = maturity_label(percent)

            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">{section}</div>
                <p class='section-text' style='color:{color};'>{percent}% - {label}</p>
                <div class="progress-container">
                    <div class="progress-bar" style="width:{percent}%; background-color:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"View Recommendations", key=section):
                st.session_state.selected_section = section
                st.session_state.selected_percent = percent

    # Overall performance
    overall = sum([v["percent"] for v in section_scores.values()]) / len(section_scores)
    st.markdown(f"""
    <div class="overall-card" style="color:black;">
    Overall Performance : {round(overall)}%
    </div>
    """, unsafe_allow_html=True)

# ==============================
# RECOMMENDATIONS PAGE VIEW
# ==============================
else:
    section = st.session_state.selected_section
    percent = st.session_state.selected_percent

    st.markdown(f'<div class="main-title-card"><h1>{section} - Recommendations</h1></div>', unsafe_allow_html=True)

    threshold = ">50%" if percent >= 50 else "<50%"
    section_rules = rules_df[rules_df["percentage"] == clean_text(threshold)]

    if not section_rules.empty:
        tab1, tab2 = st.tabs(["Area of Improvements", "Action Plan"])
        with tab1:
            for _, row in section_rules.iterrows():
                # Capitalize first letter, no bullet
                st.write(row['area_of_improvements'].capitalize())
        with tab2:
            for _, row in section_rules.iterrows():
                st.write(row['action_plan'].capitalize())
    else:
        st.write("No improvement/action plan data available for this threshold.")

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.selected_section = None
        st.session_state.selected_percent = None
