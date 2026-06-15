from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
	page_title="Employee Dashboard",
	page_icon="📊",
	layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
	data_path = Path(__file__).with_name("employee_data.csv")
	frame = pd.read_csv(data_path)
	frame.columns = [column.strip() for column in frame.columns]
	return frame


def format_currency(value: float) -> str:
	return f"${value:,.0f}"


def main() -> None:
	st.title("Employee Dashboard")
	st.caption("Overview of salary, experience, position, and gender distribution.")

	frame = load_data()

	st.sidebar.header("Filters")

	positions = sorted(frame["Position"].dropna().unique().tolist())
	genders = sorted(frame["Gender"].dropna().unique().tolist())

	selected_positions = st.sidebar.multiselect(
		"Position",
		options=positions,
		default=positions,
	)
	selected_genders = st.sidebar.multiselect(
		"Gender",
		options=genders,
		default=genders,
	)

	min_exp = int(frame["Experience (Years)"].min())
	max_exp = int(frame["Experience (Years)"].max())
	experience_range = st.sidebar.slider(
		"Experience (Years)",
		min_value=min_exp,
		max_value=max_exp,
		value=(min_exp, max_exp),
	)

	filtered = frame[
		frame["Position"].isin(selected_positions)
		& frame["Gender"].isin(selected_genders)
		& frame["Experience (Years)"].between(*experience_range)
	].copy()

	if filtered.empty:
		st.warning("No records match the selected filters.")
		st.stop()

	total_employees = len(filtered)
	avg_salary = filtered["Salary"].mean()
	avg_experience = filtered["Experience (Years)"].mean()
	unique_positions = filtered["Position"].nunique()

	metric_cols = st.columns(4)
	metric_cols[0].metric("Employees", f"{total_employees}")
	metric_cols[1].metric("Average Salary", format_currency(avg_salary))
	metric_cols[2].metric("Average Experience", f"{avg_experience:.1f} years")
	metric_cols[3].metric("Unique Positions", f"{unique_positions}")

	chart_cols = st.columns(2)

	with chart_cols[0]:
		st.subheader("Employees by Position")
		position_counts = filtered["Position"].value_counts().reset_index()
		position_counts.columns = ["Position", "Count"]
		st.bar_chart(position_counts.set_index("Position"))

	with chart_cols[1]:
		st.subheader("Salary by Gender")
		salary_by_gender = filtered.groupby("Gender", as_index=False)["Salary"].mean()
		st.bar_chart(salary_by_gender.set_index("Gender"))

	st.subheader("Salary vs Experience")
	scatter_data = filtered[["Experience (Years)", "Salary", "Position", "Gender"]]
	st.scatter_chart(scatter_data, x="Experience (Years)", y="Salary", color=None)

	st.subheader("Employee Records")
	st.dataframe(
		filtered.sort_values(["Salary", "Experience (Years)"], ascending=[False, False]),
		use_container_width=True,
	)


if __name__ == "__main__":
	main()
