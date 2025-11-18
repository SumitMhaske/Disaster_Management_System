import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
account_sid = os.getenv("")
auth_token = os.getenv("")
twilio_number = os.getenv("")

# Hardcoded credentials (Replace with a proper authentication system for production)
AUTH_CREDENTIALS = {"admin": "pass"}

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

# Function to load earthquake data
def load_data():
    try:
        file_path = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
        df = pd.read_csv(file_path)  # Load from fixed path
        
        st.success("File Loaded Successfully!")
        
        required_columns = {'datetime', 'location', 'state', 'latitude', 'longitude', 'magnitude'}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing required columns! Ensure your CSV has: {required_columns}")
            return pd.DataFrame(), None, None
        
        df['datetime'] = pd.to_datetime(df['datetime'])
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        
        return df, start_date, end_date
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame(), None, None

# Function to load users.xlsx file
def load_users():
    try:
        file_path = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading users.xlsx: {e}")
        return pd.DataFrame()

# Function to send SMS alert
def send_sms_alert(phone_number, location):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!",
        from_=twilio_number,
        to=str(phone_number)
    )
    return message.sid

# Function to display earthquake locations on map with heatmap
def display_map(df):
    st.subheader("🗺️ Earthquake Affected Areas (Heatmap)")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")
    heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for _, row in df.iterrows()]
    HeatMap(heat_data, min_opacity=0.3, radius=20, blur=15, max_zoom=5).add_to(m)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['magnitude'] * 2,
            color="red" if row['magnitude'] >= 5 else "orange",
            fill=True,
            fill_color="darkred" if row['magnitude'] >= 7 else "red",
            fill_opacity=0.7,
            popup=f"📍 {row['location']}<br>📆 {row['datetime'].strftime('%Y-%m-%d')}<br>🌍 Magnitude: {row['magnitude']}"
        ).add_to(m)
    folium_static(m)

# Streamlit UI
def main():
    st.title("Disaster Alert System")
    st.subheader("Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df, start_date, end_date = load_data()
    users_df = load_users()
    
    if df is not None and not df.empty and users_df is not None and not users_df.empty:
        st.write("### Date Range for Analysis")
        st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
        st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
        
        st.subheader("Earthquake Data Table")
        st.dataframe(df)
        display_map(df)
        
        st.subheader("Send Alert")
        affected_state = st.selectbox("Select an affected area to send an alert:", df['state'].unique())
        
        users_df['Location'] = users_df['Location'].str.lower()
        matching_users = users_df[users_df['Location'] == affected_state.lower()]
        
        if st.button("Send SMS Alert"):
            if not matching_users.empty:
                for _, row in matching_users.iterrows():
                    sid = send_sms_alert(row['Phone'], affected_state)
                    st.success(f"🚨 Alert sent to {row['Name']} ({row['Phone']}) - Message SID: {sid}")
            else:
                st.warning("No users found in the selected state.")

if __name__ == "__main__":
    main()
