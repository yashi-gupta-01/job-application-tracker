import streamlit as st
import pandas as pd
from datetime import date
import altair as alt
import os

# Constants
CSV_FILE = 'job_applications.csv'
COUNTER_FILE = 'counter.txt'
IT_ROLES = [
    'Data Scientist', 'Data Analyst', 'Software Engineer', 'Machine Learning Engineer', 
    'Data Engineer', 'Backend Developer', 'Frontend Developer', 'DevOps Engineer', 
    'Full Stack Developer', 'AI Researcher', 'Business Intelligence Analyst', 
    'Database Administrator', 'Cloud Architect', 'Cybersecurity Analyst', 
    'Network Engineer', 'IT Support Specialist', 'Systems Analyst', 'Product Manager',
    'IT Project Manager', 'Web Developer', 'Other'
]

# Functions
def form_callback(data):
    df = pd.DataFrame([data], columns=["Date", "Company Name", "Company Role", "Application Status", "Notes"])
    df.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
    update_counter()
    st.success("Job application added successfully!")

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df.columns = ["Date", "Company Name", "Company Role", "Application Status", "Notes"]
        return df
    else:
        return pd.DataFrame(columns=["Date", "Company Name", "Company Role", "Application Status", "Notes"])

def update_counter():
    counter = 0
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            counter = int(f.read())
    
    counter += 1
    
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(counter))
    
    if counter >= 10:
        st.balloons()
        st.success("🔥 Congratulations! You've added 10 job applications! 🔥")
        with open(COUNTER_FILE, 'w') as f:
            f.write('0')

# Streamlit UI
st.header("Job Application Tracker")
tab1, tab2 = st.tabs(["Job Application Details", "Job Application Statistics"])
with tab1: 
    st.sidebar.header("Job Entry")
    with st.sidebar.form(key="job_application_form", clear_on_submit=True):
        st.write("Enter Job Application Details")
        
        today_date = date.today().strftime("%Y-%m-%d")
        st.write(f"Date: {today_date}")
        
        company_name_input = st.text_input('Company Name', key='company_name')
        company_role_input = st.selectbox('Company Role', IT_ROLES, key='company_role', index=3)
        application_status_input = st.selectbox('Application Status', ['Applied', 'Interviewing', 'Offered', 'Rejected'], key='application_status')
        notes_input = st.text_area('Notes', key='notes').replace(',', '')
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not company_name_input:
                st.error("Company Name cannot be empty!")
            else:
                form_callback([today_date, company_name_input, company_role_input, application_status_input, notes_input])

    st.info("#### Show contents of the CSV file :point_down:")
    df = load_data()
    st.dataframe(df, height=300)

with tab2: 
    # Show statistics
    df = load_data()

    st.info("### Application Statistics")
    total_applications = len(df)
    applications_per_status = df['Application Status'].value_counts()
    
    st.write(f"Total Applications: {total_applications}")
    for status, count in applications_per_status.items():
        st.write(f"{status}: {count}")

    # Bar Chart
    job_role_counts = df['Company Role'].value_counts().reset_index()
    job_role_counts.columns = ['Company Role', 'Count']

    bar_chart = alt.Chart(job_role_counts).mark_bar().encode(
        y=alt.X('Company Role:O', sort='-x', title='Job Role'),
        x=alt.Y('Count:Q', title='Number of Applications'),
        color=alt.Color('Company Role:O', legend=None)  # Automatically assigns different colors
    ).properties(
        title='Job Applications by Role'
    ).configure_axis(
        labelAngle=0  # Ensures labels are horizontal
    )
    st.altair_chart(bar_chart, use_container_width=True)


    if False:
        st.subheader("Application Status Distribution")
        
        # Count the number of applications per status
        status_counts = df['Application Status'].value_counts().reset_index()
        status_counts.columns = ['Application Status', 'Count']

        # Define a color scale
        color_scale = alt.Scale(domain=status_counts['Application Status'].unique())  

        # Create a pie chart
        pie_chart = alt.Chart(status_counts).mark_arc().encode(
            theta=alt.Theta('Count:Q', stack=True),  # Angle of the pie slices
            color=alt.Color('Application Status:N', scale=color_scale, legend=alt.Legend(title='Application Status')),
            tooltip=['Application Status:N', 'Count:Q']  # Display these details on hover
        ).properties(
            title='Application Status Distribution'
        )

        st.altair_chart(pie_chart, use_container_width=True)


    st.subheader("Applications Over Time")
    df['Date'] = pd.to_datetime(df['Date'])
    applications_over_time = df.groupby('Date').size().reset_index(name='Count')
    applications_over_time.columns = ['Date', 'Count']
    applications_over_time['Date'] = applications_over_time['Date'].apply(lambda x: str(x.date()))

    # Create a line chart with labels
    line_chart = alt.Chart(applications_over_time).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Count:Q', title='Number of Applications')
    ).properties(
        title='Job Applications Over Time'
    )

    # Add labels to the points
    text = line_chart.mark_text(align='left', dx=5, dy=-5).encode(
        text='Count:Q'
    )
    # Combine the line chart and the text labels
    final_chart = line_chart + text
    st.altair_chart(final_chart, use_container_width=True)