from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Healthcare Dashboard", page_icon=":hospital:", layout="wide")


st.markdown(
	"""
	<style>
		.block-container {
			padding-top: 1.5rem;
			padding-bottom: 2rem;
		}
		.metric-card {
			background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
			color: white;
			padding: 1rem 1.1rem;
			border-radius: 16px;
			border: 1px solid rgba(255, 255, 255, 0.08);
			box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
		}
		.metric-label {
			font-size: 0.85rem;
			opacity: 0.8;
			margin-bottom: 0.35rem;
		}
		.metric-value {
			font-size: 1.8rem;
			font-weight: 700;
			line-height: 1.1;
		}
		.metric-subtitle {
			font-size: 0.8rem;
			opacity: 0.75;
			margin-top: 0.3rem;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


st.title("Healthcare Dashboard")
st.caption("Explore patient demographics, admission patterns, billing, and outcomes.")


@st.cache_data
def load_data(uploaded_file: object | None) -> pd.DataFrame:
	if uploaded_file is not None:
		return pd.read_csv(uploaded_file)

	data_path = Path(__file__).with_name("healthcare_dataset.csv")
	return pd.read_csv(data_path)


uploaded_file = st.sidebar.file_uploader("Upload a healthcare CSV", type=["csv"])
df = load_data(uploaded_file)

if df.empty:
	st.warning("No data available. Upload a CSV or keep the bundled dataset in the project folder.")
	st.stop()


for column in ["Date of Admission", "Discharge Date"]:
	if column in df.columns:
		df[column] = pd.to_datetime(df[column], errors="coerce")

numeric_columns = ["Age", "Billing Amount", "Room Number"]
for column in numeric_columns:
	if column in df.columns:
		df[column] = pd.to_numeric(df[column], errors="coerce")


st.sidebar.header("Filters")

filter_columns = [
	("Gender", "Gender"),
	("Medical Condition", "Medical Condition"),
	("Admission Type", "Admission Type"),
	("Test Results", "Test Results"),
	("Insurance Provider", "Insurance Provider"),
]

filtered_df = df.copy()
for label, column in filter_columns:
	if column in df.columns:
		options = sorted(df[column].dropna().astype(str).unique().tolist())
		selected = st.sidebar.multiselect(label, options, default=options)
		filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]

if filtered_df.empty:
	st.info("No records match the current filters. Adjust the sidebar selections.")
	st.stop()


total_patients = len(filtered_df)
avg_age = filtered_df["Age"].mean() if "Age" in filtered_df.columns else None
avg_billing = filtered_df["Billing Amount"].mean() if "Billing Amount" in filtered_df.columns else None
urgent_share = None
if "Admission Type" in filtered_df.columns:
	urgent_share = (filtered_df["Admission Type"].astype(str).eq("Urgent").mean()) * 100


col1, col2, col3, col4 = st.columns(4)

metrics = [
	(col1, "Total Patients", f"{total_patients:,}", "Filtered records"),
	(col2, "Average Age", f"{avg_age:.1f}" if pd.notna(avg_age) else "N/A", "Years"),
	(col3, "Average Billing", f"${avg_billing:,.2f}" if pd.notna(avg_billing) else "N/A", "Per patient"),
	(col4, "Urgent Admissions", f"{urgent_share:.1f}%" if urgent_share is not None else "N/A", "Share of admissions"),
]

for column, label, value, subtitle in metrics:
	with column:
		st.markdown(
			f"""
			<div class="metric-card">
				<div class="metric-label">{label}</div>
				<div class="metric-value">{value}</div>
				<div class="metric-subtitle">{subtitle}</div>
			</div>
			""",
			unsafe_allow_html=True,
		)


st.divider()

left, right = st.columns(2)

with left:
	st.subheader("Patients by Medical Condition")
	if "Medical Condition" in filtered_df.columns:
		condition_counts = filtered_df["Medical Condition"].value_counts().reset_index()
		condition_counts.columns = ["Medical Condition", "Count"]
		fig = px.bar(
			condition_counts,
			x="Medical Condition",
			y="Count",
			color="Medical Condition",
			text="Count",
			title=None,
		)
		fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Patients")
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Medical Condition column not found.")

with right:
	st.subheader("Billing by Admission Type")
	if {"Admission Type", "Billing Amount"}.issubset(filtered_df.columns):
		billing_by_admission = (
			filtered_df.groupby("Admission Type", as_index=False)["Billing Amount"].mean().sort_values("Billing Amount", ascending=False)
		)
		fig = px.bar(
			billing_by_admission,
			x="Admission Type",
			y="Billing Amount",
			color="Admission Type",
			text_auto="$.2s",
			title=None,
		)
		fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average billing")
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Admission Type or Billing Amount column not found.")


bottom_left, bottom_right = st.columns(2)

with bottom_left:
	st.subheader("Age Distribution")
	if "Age" in filtered_df.columns:
		fig = px.histogram(filtered_df, x="Age", nbins=20, color_discrete_sequence=["#0f766e"], title=None)
		fig.update_layout(xaxis_title="Age", yaxis_title="Patients")
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Age column not found.")

with bottom_right:
	st.subheader("Test Results")
	if "Test Results" in filtered_df.columns:
		test_results = filtered_df["Test Results"].value_counts().reset_index()
		test_results.columns = ["Test Results", "Count"]
		fig = px.pie(test_results, names="Test Results", values="Count", hole=0.45)
		fig.update_traces(textposition="inside", textinfo="percent+label")
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Test Results column not found.")


st.subheader("Filtered Patient Data")
display_columns = [
	column
	for column in [
		"Name",
		"Age",
		"Gender",
		"Medical Condition",
		"Admission Type",
		"Billing Amount",
		"Test Results",
		"Insurance Provider",
	]
	if column in filtered_df.columns
]
st.dataframe(filtered_df[display_columns], use_container_width=True, hide_index=True)