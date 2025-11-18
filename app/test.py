import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Hardcoded credentials (Replace with a proper authentication system for production)
AUTH_CREDENTIALS = {"admin": "password123"}

def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    st.sidebar.title("Authority Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in AUTH_CREDENTIALS and AUTH_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.sidebar.success("Login successful!")
        else:
            st.sidebar.error("Invalid credentials. Try again.")
    
    return st.session_state.authenticated

# Function to load data
def load_data():
    try:
        file_path = "D:/WhatsApp/DisasterAlert (8)/DisasterAlert (8)/data/real_time_india_earthquakes_with_states.csv"
        df = pd.read_csv(file_path)  # Load from fixed path
        
        st.success("File Loaded Successfully!")
        
        # Check required columns
        required_columns = {'datetime', 'location', 'state'}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing required columns! Ensure your CSV has: {required_columns}")
            return pd.DataFrame(), None, None
        
        # Convert datetime column
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Filter last 10 days
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        
        return df, start_date, end_date
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame(), None, None
# Function to display earthquake locations on map with heatmap
def display_map(df):
    st.subheader("🗺️ Earthquake Affected Areas (Heatmap)")

    # Initialize map centered in India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")

    # Add Heatmap
    heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for _, row in df.iterrows()]
    HeatMap(heat_data, min_opacity=0.3, radius=20, blur=15, max_zoom=5).add_to(m)

    # Add markers for affected areas
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['magnitude'] * 2,  # Higher magnitude = larger marker
            color="red" if row['magnitude'] >= 5 else "orange",
            fill=True,
            fill_color="darkred" if row['magnitude'] >= 7 else "red",
            fill_opacity=0.7,
            popup=f"📍 {row['location']}<br>📆 {row['datetime'].strftime('%Y-%m-%d')}<br>🌍 Magnitude: {row['magnitude']}<br>⚠️ Risk Level: {row.get('predicted_risk', 'Unknown')}"
        ).add_to(m)

    folium_static(m)

# Streamlit UI
def main():
    st.title("Disaster Alert System")
    st.subheader("Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    # Load data
    df, start_date, end_date = load_data()

    # Display Start and End Date
    if df is not None and not df.empty:
        st.write("### Date Range for Analysis")
        st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
        st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")

        # Display full CSV table
        st.subheader("Earthquake Data Table")
        st.dataframe(df)

        display_map(df)

        # Dropdown to select affected area
        st.subheader("Send Alert")
        affected_area = st.selectbox("Select an affected area to send an alert:", df['state'].unique())

        if st.button("Send SMS Alert"):
            st.success(f"🚨 Alert sent to {affected_area} 🚨")
            # Here, integrate actual SMS API if required
        
        # Preventive Measures Section
        st.subheader("Preventive Measures")
        st.markdown("""
        - **Stay indoors** and take cover under sturdy furniture.
        - **Avoid windows, mirrors, and heavy objects** that could fall.
        - **If outside**, move to an **open area away from buildings and power lines**.
        - **Prepare an emergency kit** with essentials like **water, food, and medications**.
        - **Stay updated** with **local authorities** for further instructions.
        """)
    else:
        st.warning("⚠ No data available. Please check the file path.")

if __name__ == "__main__":
    main()