import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
	page_title="Heart Disease Dashboard",
	page_icon="❤️",
	layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
	return pd.read_csv("heart_disease_dataset.csv")


df = load_data()

st.title("❤️ Heart Disease Dashboard")
st.caption("Explore patient patterns with interactive filters and summary charts.")

st.sidebar.header("🔍 Filters")

age_range = st.sidebar.slider(
	"Age",
	int(df["Age"].min()),
	int(df["Age"].max()),
	(int(df["Age"].min()), int(df["Age"].max())),
)

gender_options = sorted(df["Gender"].dropna().unique().tolist())
gender = st.sidebar.multiselect("Gender", gender_options, default=gender_options)

chest_pain_options = sorted(df["Chest Pain Type"].dropna().unique().tolist())
chest_pain = st.sidebar.multiselect(
	"Chest Pain Type",
	chest_pain_options,
	default=chest_pain_options,
)

smoking_options = sorted(df["Smoking"].dropna().unique().tolist())
smoking = st.sidebar.multiselect("Smoking", smoking_options, default=smoking_options)

family_history_options = sorted(df["Family History"].dropna().unique().tolist())
family_history = st.sidebar.multiselect(
	"Family History",
	family_history_options,
	default=family_history_options,
)

diabetes_options = sorted(df["Diabetes"].dropna().unique().tolist())
diabetes = st.sidebar.multiselect("Diabetes", diabetes_options, default=diabetes_options)

obesity_options = sorted(df["Obesity"].dropna().unique().tolist())
obesity = st.sidebar.multiselect("Obesity", obesity_options, default=obesity_options)

cholesterol_range = st.sidebar.slider(
	"Cholesterol",
	int(df["Cholesterol"].min()),
	int(df["Cholesterol"].max()),
	(int(df["Cholesterol"].min()), int(df["Cholesterol"].max())),
)

blood_pressure_range = st.sidebar.slider(
	"Blood Pressure",
	int(df["Blood Pressure"].min()),
	int(df["Blood Pressure"].max()),
	(int(df["Blood Pressure"].min()), int(df["Blood Pressure"].max())),
)

blood_sugar_range = st.sidebar.slider(
	"Blood Sugar",
	int(df["Blood Sugar"].min()),
	int(df["Blood Sugar"].max()),
	(int(df["Blood Sugar"].min()), int(df["Blood Sugar"].max())),
)

filtered_df = df[
	df["Age"].between(age_range[0], age_range[1])
	& df["Gender"].isin(gender)
	& df["Chest Pain Type"].isin(chest_pain)
	& df["Smoking"].isin(smoking)
	& df["Family History"].isin(family_history)
	& df["Diabetes"].isin(diabetes)
	& df["Obesity"].isin(obesity)
	& df["Cholesterol"].between(cholesterol_range[0], cholesterol_range[1])
	& df["Blood Pressure"].between(blood_pressure_range[0], blood_pressure_range[1])
	& df["Blood Sugar"].between(blood_sugar_range[0], blood_sugar_range[1])
]

if filtered_df.empty:
	st.warning("No records match the selected filters. Adjust the filters to continue.")
	st.stop()

heart_cases = int(filtered_df["Heart Disease"].sum())
heart_rate_avg = round(filtered_df["Heart Rate"].mean(), 1)
age_avg = round(filtered_df["Age"].mean(), 1)
cholesterol_avg = round(filtered_df["Cholesterol"].mean(), 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", len(filtered_df))
col2.metric("Heart Disease Cases", heart_cases)
col3.metric("Average Age", age_avg)
col4.metric("Average Heart Rate", heart_rate_avg)

st.divider()

chart_left, chart_right = st.columns(2)

with chart_left:
	age_fig = px.histogram(
		filtered_df,
		x="Age",
		nbins=15,
		title="Age Distribution",
		color_discrete_sequence=["#E4572E"],
	)
	age_fig.update_layout(title_x=0.5)
	st.plotly_chart(age_fig, use_container_width=True)

with chart_right:
	gender_fig = px.pie(
		filtered_df,
		names="Gender",
		title="Gender Distribution",
		hole=0.4,
	)
	gender_fig.update_layout(title_x=0.5)
	st.plotly_chart(gender_fig, use_container_width=True)

chart_left, chart_right = st.columns(2)

with chart_left:
	hd_counts = (
		filtered_df["Heart Disease"].value_counts().sort_index().reset_index()
	)
	hd_counts.columns = ["Heart Disease", "Count"]
	hd_counts["Heart Disease"] = hd_counts["Heart Disease"].map(
		{0: "No Heart Disease", 1: "Heart Disease"}
	)
	hd_fig = px.bar(
		hd_counts,
		x="Heart Disease",
		y="Count",
		title="Heart Disease Outcome",
		color="Heart Disease",
		color_discrete_sequence=["#1B998B", "#D7263D"],
	)
	hd_fig.update_layout(showlegend=False, title_x=0.5)
	st.plotly_chart(hd_fig, use_container_width=True)

with chart_right:
	bp_fig = px.scatter(
		filtered_df,
		x="Age",
		y="Blood Pressure",
		color="Heart Disease",
		title="Age vs Blood Pressure",
		color_discrete_map={0: "#1B998B", 1: "#D7263D"},
	)
	bp_fig.update_layout(title_x=0.5)
	st.plotly_chart(bp_fig, use_container_width=True)

chol_fig = px.box(
	filtered_df,
	x="Heart Disease",
	y="Cholesterol",
	title="Cholesterol by Heart Disease Outcome",
	color="Heart Disease",
	color_discrete_map={0: "#1B998B", 1: "#D7263D"},
)
chol_fig.update_layout(title_x=0.5, showlegend=False)
st.plotly_chart(chol_fig, use_container_width=True)

st.subheader("Filtered Dataset")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

csv = filtered_df.to_csv(index=False)
st.download_button(
	"Download filtered data",
	csv,
	file_name="filtered_heart_disease_data.csv",
	mime="text/csv",
)

st.info(
	f"Filtered average cholesterol: {cholesterol_avg}. This dashboard is for exploring patterns in the data and is not a diagnostic tool. Always consult a healthcare professional for medical advice."
)
