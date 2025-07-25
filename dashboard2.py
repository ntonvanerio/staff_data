# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ----- PAGE & STYLE SETUP -----
st.set_page_config(page_title="GoFundMe Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #f6f8fa !important;
        border-radius: 10px;
        box-shadow: 0px 4px 24px rgba(0,0,0,0.03);
    }
    h1, h2, h3 {
        color: #10754c;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
    }
    .highlight-box {
        background: #fff;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #e3e3e3;
        box-shadow: 0 2px 8px rgba(34,34,34,0.04);
    }
    </style>
""", unsafe_allow_html=True)

# ----- HEADER / BRANDING -----
# If you have a logo file, replace 'logo.png' with your path
# st.image("logo.png", width=120)
st.title("GoFundMe Campaign Performance Dashboard")
st.markdown("<h5 style='text-align: center; color: #555;'>by Nicolás Ton | July 2025</h5>", unsafe_allow_html=True)

st.markdown("""
<div class='highlight-box'>
    <b>Explore GoFundMe campaign and donor analytics from Jan to Jul 2025.</b><br>
    Use the sidebar filters to customize your view.
</div>
""", unsafe_allow_html=True)

# ----- SIMULATED DATA -----
today = datetime(2025, 7, 24)
start_date = datetime(2025, 1, 1)
days_range = (today - start_date).days

np.random.seed(42)
categories = ['Health', 'Education', 'Natural Disasters', 'Animals', 'Community']
countries = ['Argentina', 'USA', 'Brazil', 'Mexico', 'Spain']
n_campaigns = 300

campaigns = pd.DataFrame({
    'id': range(1, n_campaigns + 1),
    'name': [f'Campaign {i}' for i in range(1, n_campaigns + 1)],
    'category': np.random.choice(categories, n_campaigns),
    'country': np.random.choice(countries, n_campaigns),
    'goal_usd': np.random.randint(5000, 50000, n_campaigns),
    'created_at': start_date + pd.to_timedelta(np.random.randint(0, days_range, n_campaigns), unit='D')
})
campaigns['raised_usd'] = campaigns['goal_usd'] * np.random.uniform(0.2, 1.3, n_campaigns)
campaigns['status'] = np.where(campaigns['raised_usd'] >= campaigns['goal_usd'], 'Goal Reached', 'In Progress')

# ----- SIDEBAR FILTERS -----
min_date = campaigns['created_at'].min().date()
max_date = campaigns['created_at'].max().date()
st.sidebar.title("Filters")
st.sidebar.info("Refine dashboard views using the filters below.")

selected_country = st.sidebar.multiselect("Country", options=countries, default=countries)
selected_category = st.sidebar.multiselect("Category", options=categories, default=categories)
selected_date_range = st.sidebar.slider(
    "Creation Date Range",
    min_value=min_date, max_value=max_date,
    value=(min_date, max_date), format="YYYY-MM-DD"
)

df = campaigns[
    (campaigns['country'].isin(selected_country)) &
    (campaigns['category'].isin(selected_category)) &
    (campaigns['created_at'] >= pd.to_datetime(selected_date_range[0])) &
    (campaigns['created_at'] <= pd.to_datetime(selected_date_range[1]))
]

st.sidebar.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), "filtered_campaigns.csv", "text/csv")

# ----- TABS LAYOUT -----
tab1, tab2, tab3 = st.tabs(["📊 Campaigns", "🤝 Donors", "💼 Salaries"])

# ----- TAB 1: CAMPAIGNS -----
with tab1:
    st.subheader("Campaign KPIs")
    total_raised = df['raised_usd'].sum()
    total_goal = df['goal_usd'].sum()
    success_rate = (df['status'] == 'Goal Reached').mean() * 100
    avg_donation = df['raised_usd'].mean()
    reached_goal = (df['status'] == 'Goal Reached').sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💵 Total Raised", f"${total_raised:,.0f}")
    k2.metric("🎯 Total Goal", f"${total_goal:,.0f}")
    k3.metric("✅ Success Rate", f"{success_rate:.1f}%")
    k4.metric("📈 Avg Raised/Campaign", f"${avg_donation:,.0f}")
    k5.metric("🏆 Reached Goal", f"{reached_goal} / {len(df)}")

    st.markdown("---")
    st.subheader("Campaign Performance Visualizations")

    c1, c2 = st.columns(2)
    cat_chart = df.groupby('category')['raised_usd'].sum().reset_index()
    c1.plotly_chart(
        px.bar(
            cat_chart, x='category', y='raised_usd',
            title="Funds Raised by Category",
            color='category',
            color_discrete_sequence=px.colors.sequential.Teal,
            template='plotly_white',
            labels={'raised_usd': 'Raised (USD)', 'category': 'Category'},
            hover_data={'raised_usd':':,.0f'}
        ).update_layout(showlegend=False),
        use_container_width=True
    )
    # Timeline chart
    df['month'] = df['created_at'].dt.to_period('M').dt.to_timestamp()
    timeline = df.groupby('month')['raised_usd'].sum().reset_index()
    c2.plotly_chart(
        px.line(
            timeline, x='month', y='raised_usd',
            markers=True, title="Monthly Raised Amount",
            template='plotly_white',
            labels={'raised_usd': 'Raised (USD)', 'month': 'Month'},
            hover_data={'raised_usd':':,.0f'}
        ),
        use_container_width=True
    )

    t1, t2 = st.columns(2)
    geo = df.groupby('country')['raised_usd'].sum().reset_index()
    geo['iso'] = geo['country'].map({'Argentina': 'ARG', 'USA': 'USA', 'Brazil': 'BRA', 'Mexico': 'MEX', 'Spain': 'ESP'})
    t1.plotly_chart(
        px.choropleth(
            geo, locations='iso', color='raised_usd',
            hover_name='country',
            title='Funds Raised by Country',
            color_continuous_scale='teal',
            template='plotly_white',
            labels={'raised_usd': 'Raised (USD)'}
        ),
        use_container_width=True
    )

    # Top campaigns table and chart
    st.markdown("#### Top Performing Campaigns")
    top = df.sort_values('raised_usd', ascending=False).head(10)
    top_display = top[['name', 'category', 'country', 'goal_usd', 'raised_usd', 'status']].copy()
    top_display['goal_usd'] = top_display['goal_usd'].map('${:,.0f}'.format)
    top_display['raised_usd'] = top_display['raised_usd'].map('${:,.0f}'.format)
    c3, c4 = st.columns(2)
    c3.dataframe(top_display, use_container_width=True)
    c4.plotly_chart(
        px.bar(
            top, x='name', y='raised_usd', color='category',
            title='Top Campaigns by Raised USD',
            template='plotly_white',
            labels={'raised_usd': 'Raised (USD)', 'name': 'Campaign'},
            color_discrete_sequence=px.colors.sequential.Teal
        ).update_layout(showlegend=False),
        use_container_width=True
    )

# ----- TAB 2: DONORS -----
with tab2:
    st.subheader("Donor Analytics")
    donors = pd.DataFrame({
        'donor_id': range(1, len(df)//2 + 1),
        'donations': np.random.poisson(2, len(df)//2),
        'channel': np.random.choice(['Email', 'Social', 'Referral', 'Direct'], len(df)//2),
        'total_donated': np.random.uniform(10, 500, len(df)//2)
    })
    num_donors = len(donors)
    new_donors = (donors['donations'] == 1).sum()
    retention = (donors['donations'] > 1).mean() * 100
    avg_donor_val = donors['total_donated'].mean()

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("🙋‍♂️ Donors", f"{num_donors}")
    d2.metric("🆕 New Donors (%)", f"{new_donors/num_donors*100:.1f}%")
    d3.metric("🔁 Retention Rate", f"{retention:.1f}%")
    d4.metric("💰 Avg Donor Value", f"${avg_donor_val:.0f}")

    st.markdown("---")
    st.subheader("Donation Channel Breakdown")
    channel_sum = donors.groupby('channel')['total_donated'].sum().reset_index()
    st.plotly_chart(
        px.pie(
            channel_sum, names='channel', values='total_donated',
            title='Donations by Channel',
            template='plotly_white'
        ),
        use_container_width=True
    )

# ----- TAB 3: SALARIES -----
with tab3:
    st.subheader("Employee Salary Overview")
    roles = ['Analyst', 'Engineer', 'Manager', 'Director']
    sectors = ['Product', 'Data', 'Marketing', 'Operations']
    genders = ['Male', 'Female', 'Non-binary']
    ages = np.random.randint(22, 60, 200)
    salary_data = pd.DataFrame({
        'role': np.random.choice(roles, 200),
        'sector': np.random.choice(sectors, 200),
        'country': np.random.choice(countries, 200),
        'gender': np.random.choice(genders, 200),
        'age': ages,
        'salary_usd': np.random.normal(50000, 15000, 200).round(0)
    })
    s1, s2 = st.columns(2)
    s1.plotly_chart(
        px.box(
            salary_data, x='role', y='salary_usd',
            title="Salary by Role", template='plotly_white'
        ),
        use_container_width=True
    )
    s2.plotly_chart(
        px.box(
            salary_data, x='country', y='salary_usd',
            title="Salary by Country", template='plotly_white'
        ),
        use_container_width=True
    )
    s3, s4 = st.columns(2)
    s3.plotly_chart(
        px.box(
            salary_data, x='sector', y='salary_usd',
            title="Salary by Sector", template='plotly_white'
        ),
        use_container_width=True
    )
    s4.plotly_chart(
        px.box(
            salary_data, x='gender', y='salary_usd',
            title="Salary by Gender", template='plotly_white'
        ),
        use_container_width=True
    )
