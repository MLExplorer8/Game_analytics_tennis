import streamlit as st
import pandas as pd
import mysql.connector

# -------------------- Database Connection --------------------
conn = mysql.connector.connect(
    host='localhost',  # or your DB host
    user='root',
    password='password',
    database='database'
)
cursor = conn.cursor()

# -------------------- Helper: Load Data --------------------
def load_data():
    query = '''
        SELECT c.competitor_id, c.name, c.country, cr.rank, cr.movement, cr.points, cr.competitions_played
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    '''
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["competitor_id", "name", "country", "rank", "movement", "points", "competitions_played"])

df = load_data()

# -------------------- Navigation --------------------
page = st.sidebar.radio("Navigate", [
    "Homepage Dashboard",
    "Search & Filter Competitors",
    "Competitor Details",
    "Country-Wise Analysis",
    "Leaderboards"
])

# -------------------- 1. Homepage Dashboard --------------------
if page == "Homepage Dashboard":
    st.title("🏠 Homepage Dashboard")
    st.metric("Total Competitors", df["competitor_id"].nunique())
    st.metric("Countries Represented", df["country"].nunique())
    st.metric("Highest Points", df["points"].max())

# -------------------- 2. Search & Filter Competitors --------------------
elif page == "Search & Filter Competitors":
    st.title("🔍 Search & Filter Competitors")
    name = st.text_input("Search by Name")
    rank_range = st.slider("Rank Range", int(df["rank"].min()), int(df["rank"].max()), (1, 10))
    country = st.selectbox("Filter by Country", ["All"] + sorted(df["country"].unique().tolist()))
    points_threshold = st.slider("Minimum Points", int(df["points"].min()), int(df["points"].max()), 0)

    filtered_df = df.copy()
    if name:
        filtered_df = filtered_df[filtered_df["name"].str.contains(name, case=False)]
    filtered_df = filtered_df[(filtered_df["rank"] >= rank_range[0]) & (filtered_df["rank"] <= rank_range[1])]
    if country != "All":
        filtered_df = filtered_df[filtered_df["country"] == country]
    filtered_df = filtered_df[filtered_df["points"] >= points_threshold]

    st.dataframe(filtered_df)

# -------------------- 3. Competitor Details Viewer --------------------
elif page == "Competitor Details":
    st.title("📋 Competitor Details Viewer")
    selected_name = st.selectbox("Select Competitor", sorted(df["name"].unique()))
    details = df[df["name"] == selected_name].iloc[0]
    st.write(f"**Name**: {details['name']}")
    st.write(f"**Country**: {details['country']}")
    st.write(f"**Rank**: {details['rank']}")
    st.write(f"**Movement**: {details['movement']}")
    st.write(f"**Competitions Played**: {details['competitions_played']}")
    st.write(f"**Points**: {details['points']}")

# -------------------- 4. Country-Wise Analysis --------------------
elif page == "Country-Wise Analysis":
    st.title("🌍 Country-Wise Analysis")
    
    # Grouping and aggregation
    country_stats = df.groupby("country").agg({
        "competitor_id": "nunique",
        "points": "mean"
    }).rename(columns={"competitor_id": "Total Competitors", "points": "Average Points"})
    
    # Round the Average Points to one significant figure
    country_stats["Average Points"] = country_stats["Average Points"].apply(lambda x: round(x, 1) if x > 10 else round(x, 2))
    
    # Display the DataFrame
    st.dataframe(country_stats.sort_values("Total Competitors", ascending=False))
  

# -------------------- 5. Leaderboards --------------------
elif page == "Leaderboards":
    st.title("🏆 Leaderboards")
    
    st.subheader("Top Ranked Competitors")
    top_ranked = df.drop_duplicates(subset="competitor_id", keep="first").sort_values("rank")
    st.dataframe(top_ranked.head(10))  # Show top 10 unique ranked competitors
    
    st.subheader("Highest Point Scorers")
    highest_points = df.drop_duplicates(subset="competitor_id", keep="first").sort_values("points", ascending=False)
    st.dataframe(highest_points.head(10))  # Show top 10 unique point scorers
