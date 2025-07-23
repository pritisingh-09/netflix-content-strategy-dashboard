# Netflix Content Analysis Script
# Additional analysis functions for the dashboard

import pandas as pd
import numpy as np
from datetime import datetime

def load_and_analyze_data():
    """Load Netflix data and perform basic analysis"""
    df = pd.read_csv('netflix_content_data.csv')

    print("=== NETFLIX CONTENT ANALYSIS REPORT ===\n")

    # Basic statistics
    print(f"Total Content Pieces: {len(df)}")
    print(f"Movies: {len(df[df['type'] == 'Movie'])}")
    print(f"TV Shows: {len(df[df['type'] == 'TV Show'])}")
    print(f"Date Range: {df['release_year'].min()} - {df['release_year'].max()}")

    # Engagement insights
    print("\n=== ENGAGEMENT INSIGHTS ===")
    avg_engagement = df['engagement_score'].mean()
    print(f"Average Engagement Score: {avg_engagement:.1f}%")

    top_genres = df.groupby('genre')['engagement_score'].mean().sort_values(ascending=False).head(3)
    print("\nTop 3 Genres by Engagement:")
    for genre, score in top_genres.items():
        print(f"  {genre}: {score:.1f}%")

    # Geographic insights
    print("\n=== GEOGRAPHIC INSIGHTS ===")
    top_countries = df.groupby('country').size().sort_values(ascending=False).head(3)
    print("Top 3 Content Producing Countries:")
    for country, count in top_countries.items():
        print(f"  {country}: {count} titles")

    # Performance correlation
    correlation = df['imdb_score'].corr(df['engagement_score'])
    print(f"\nIMDB-Engagement Correlation: {correlation:.3f}")

    return df

def generate_business_recommendations(df):
    """Generate strategic business recommendations"""
    print("\n=== STRATEGIC RECOMMENDATIONS ===")

    # Best performing content type
    type_performance = df.groupby('type')['engagement_score'].mean()
    best_type = type_performance.idxmax()
    print(f"1. Focus on {best_type}s - {type_performance[best_type]:.1f}% avg engagement")

    # Genre recommendation
    genre_roi = df.groupby('genre').agg({
        'engagement_score': 'mean',
        'viewership_hours': 'mean'
    })
    best_genre = genre_roi['engagement_score'].idxmax()
    print(f"2. Invest in {best_genre} content - highest engagement potential")

    # Release timing
    monthly_performance = df.groupby('release_month')['engagement_score'].mean()
    best_month = monthly_performance.idxmax()
    months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    print(f"3. Optimal release month: {months[best_month]} - {monthly_performance[best_month]:.1f}% avg engagement")

    # Market expansion
    country_potential = df.groupby('country').agg({
        'engagement_score': 'mean',
        'title': 'count'
    })
    # Find countries with high engagement but low content count
    country_potential['opportunity_score'] = country_potential['engagement_score'] / country_potential['title']
    top_opportunity = country_potential['opportunity_score'].idxmax()
    print(f"4. Market expansion opportunity: {top_opportunity}")

if __name__ == "__main__":
    df = load_and_analyze_data()
    generate_business_recommendations(df)
