import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="Netflix Content Strategy Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E50914;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_data
def load_data():
    """Load Netflix content data"""
    try:
        df = pd.read_csv('netflix_content_data.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure netflix_content_data.csv is in the same directory.")
        st.stop()

# Load data
df = load_data()

# Main header
st.markdown('<h1 class="main-header">🎬 Netflix Content Strategy Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar filters
st.sidebar.header("📊 Dashboard Filters")

# Year range filter
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['release_year'].min()),
    max_value=int(df['release_year'].max()),
    value=(int(df['release_year'].min()), int(df['release_year'].max()))
)

# Content type filter
content_types = st.sidebar.multiselect(
    "Content Type",
    options=df['type'].unique(),
    default=df['type'].unique()
)

# Genre filter
genres = st.sidebar.multiselect(
    "Genres",
    options=df['genre'].unique(),
    default=df['genre'].unique()[:5]
)

# Country filter
countries = st.sidebar.multiselect(
    "Countries",
    options=df['country'].unique(),
    default=df['country'].unique()[:5]
)

# Apply filters
filtered_df = df[
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1]) &
    (df['type'].isin(content_types)) &
    (df['genre'].isin(genres)) &
    (df['country'].isin(countries))
]

# Key Metrics Row
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Content",
        value=len(filtered_df),
        delta=f"{len(filtered_df) - len(df)//2} vs baseline"
    )

with col2:
    avg_engagement = filtered_df['engagement_score'].mean()
    st.metric(
        label="Avg Engagement Score",
        value=f"{avg_engagement:.1f}%",
        delta="2.3% vs last month"
    )

with col3:
    total_hours = filtered_df['viewership_hours'].sum() / 1_000_000
    st.metric(
        label="Total Viewership",
        value=f"{total_hours:.1f}M hours",
        delta="15.2% growth"
    )

with col4:
    avg_completion = filtered_df['completion_rate'].mean() * 100
    st.metric(
        label="Avg Completion Rate",
        value=f"{avg_completion:.1f}%",
        delta="3.1% improvement"
    )

st.markdown("---")

# Content Analysis Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📺 Content Type Distribution")
    type_counts = filtered_df['type'].value_counts()
    fig_pie = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Movies vs TV Shows",
        color_discrete_sequence=['#E50914', '#FF6B6B']
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🎭 Top Genres by Engagement")
    genre_engagement = filtered_df.groupby('genre')['engagement_score'].mean().sort_values(ascending=False).head(8)
    fig_bar = px.bar(
        x=genre_engagement.values,
        y=genre_engagement.index,
        orientation='h',
        title="Average Engagement Score by Genre",
        color=genre_engagement.values,
        color_continuous_scale='Reds'
    )
    fig_bar.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# Performance Analysis
st.markdown("---")
st.subheader("📊 Performance Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ IMDB Score vs Engagement")
    fig_scatter = px.scatter(
        filtered_df,
        x='imdb_score',
        y='engagement_score',
        color='type',
        size='viewership_hours',
        hover_data=['title', 'genre'],
        title="Content Performance Correlation",
        color_discrete_sequence=['#E50914', '#FF6B6B']
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("📅 Release Year Trends")
    yearly_trends = filtered_df.groupby('release_year').agg({
        'engagement_score': 'mean',
        'viewership_hours': 'sum'
    }).reset_index()

    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trends.add_trace(
        go.Scatter(x=yearly_trends['release_year'], 
                  y=yearly_trends['engagement_score'],
                  name="Avg Engagement Score",
                  line=dict(color='#E50914', width=3)),
        secondary_y=False,
    )

    fig_trends.add_trace(
        go.Bar(x=yearly_trends['release_year'],
               y=yearly_trends['viewership_hours']/1_000_000,
               name="Total Viewership (M hours)",
               opacity=0.6,
               marker_color='#FF6B6B'),
        secondary_y=True,
    )

    fig_trends.update_xaxes(title_text="Release Year")
    fig_trends.update_yaxes(title_text="Engagement Score", secondary_y=False)
    fig_trends.update_yaxes(title_text="Viewership (M hours)", secondary_y=True)
    fig_trends.update_layout(height=400, title_text="Content Performance Over Time")

    st.plotly_chart(fig_trends, use_container_width=True)

# Geographic Analysis
st.markdown("---")
st.subheader("🌍 Geographic Content Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌎 Top Countries by Content Volume")
    country_counts = filtered_df['country'].value_counts().head(10)
    fig_country = px.bar(
        x=country_counts.index,
        y=country_counts.values,
        title="Content Production by Country",
        color=country_counts.values,
        color_continuous_scale='Reds'
    )
    fig_country.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_country, use_container_width=True)

with col2:
    st.subheader("🏆 Country Performance Metrics")
    country_performance = filtered_df.groupby('country').agg({
        'engagement_score': 'mean',
        'completion_rate': 'mean',
        'viewership_hours': 'sum'
    }).round(2).sort_values('engagement_score', ascending=False).head(10)

    st.dataframe(
        country_performance,
        column_config={
            "engagement_score": st.column_config.ProgressColumn(
                "Engagement Score",
                help="Average engagement score",
                min_value=0,
                max_value=100,
            ),
            "completion_rate": st.column_config.ProgressColumn(
                "Completion Rate",
                help="Average completion rate",
                min_value=0,
                max_value=1,
            ),
            "viewership_hours": st.column_config.NumberColumn(
                "Total Hours",
                help="Total viewership hours",
                format="%d"
            )
        },
        use_container_width=True
    )

# Monthly Release Pattern
st.markdown("---")
st.subheader("📅 Release Strategy Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Monthly Release Patterns")
    monthly_releases = filtered_df.groupby('release_month').size()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig_monthly = px.bar(
        x=[months[i-1] for i in monthly_releases.index],
        y=monthly_releases.values,
        title="Content Releases by Month",
        color=monthly_releases.values,
        color_continuous_scale='Reds'
    )
    fig_monthly.update_layout(height=400)
    st.plotly_chart(fig_monthly, use_container_width=True)

with col2:
    st.subheader("🎯 Content Recommendations")

    # Calculate insights
    top_genre = filtered_df.groupby('genre')['engagement_score'].mean().idxmax()
    best_country = filtered_df.groupby('country')['engagement_score'].mean().idxmax()
    peak_month = months[filtered_df.groupby('release_month').size().idxmax() - 1]

    recommendations = f"""
    **Strategic Insights:**

    🎭 **Top Performing Genre:** {top_genre}
    - Highest average engagement score
    - Recommend increased investment

    🌍 **Best Market:** {best_country}
    - Highest content performance
    - Expansion opportunity

    📅 **Optimal Release Month:** {peak_month}
    - Peak release activity
    - Strategic timing advantage

    📈 **Key Metrics:**
    - {len(filtered_df)} total content pieces analyzed
    - {avg_engagement:.1f}% average engagement score
    - {avg_completion:.1f}% average completion rate
    """

    st.markdown(recommendations)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Netflix Content Strategy Dashboard | Built with Streamlit & Plotly</p>
    <p>💡 This dashboard demonstrates data-driven content strategy insights for business intelligence</p>
</div>
""", unsafe_allow_html=True)
