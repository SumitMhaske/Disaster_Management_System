import streamlit as st
import pandas as pd
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from twilio.rest import Client
import googlemaps  # For route calculation (you need to install this)

# Authentication Credentials
AUTH_CREDENTIALS = {"admin": "pass"}

# Email and SMS Credentials
EMAIL_SENDER = ""
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')  # Replace with your Google Maps API key

# File Paths
DATA_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"
RESOURCE_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\resources.csv"  # Contains available resources

# Initialize Google Maps client for logistics
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# Authenticate User
def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    st.sidebar.title("Authority Login")
    
    if st.session_state.authenticated:
        st.sidebar.success("🔓 Logged in as Admin")
        if st.sidebar.button("Logout 🚪"):
            st.session_state.authenticated = False
            st.sidebar.warning("You have been logged out.")
            st.rerun()
        return True

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in AUTH_CREDENTIALS and AUTH_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.sidebar.success("✅ Login successful!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials. Try again.")
    
    return st.session_state.authenticated

# Load Earthquake Data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        st.success("✅ File Loaded Successfully!")
        
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert(None)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        
        return df, start_date, end_date
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame(), None, None

# Load User Emails
def load_user_emails(region):
    try:
        emails_df = pd.read_excel(EMAIL_FILE_PATH, engine='openpyxl')
        if "email" not in emails_df.columns or "Location" not in emails_df.columns:
            st.error("❌ Excel file must contain 'email' and 'Location' columns.")
            return []
        return emails_df[emails_df["Location"].str.lower() == region.lower()]["email"].tolist()
    except Exception as e:
        st.error(f"❌ Error loading emails: {e}")
        return []

# Load Resource Data
def load_resources():
    try:
        resources_df = pd.read_csv(RESOURCE_FILE_PATH)
        st.success("✅ Resource data loaded successfully!")
        return resources_df
    except Exception as e:
        st.error(f"❌ Error loading resources: {e}")
        return pd.DataFrame()

# Track Available Resources
def track_available_resources():
    resources_df = load_resources()
    st.subheader("🔧 Available Resources")
    st.dataframe(resources_df)
    return resources_df

# Allocate Resources
def allocate_resources(location, resource_type, quantity, resources_df):
    try:
        available = resources_df[(resources_df['resource_type'] == resource_type) & (resources_df['location'] == location)]
        if available['quantity'].sum() >= quantity:
            resources_df.loc[(resources_df['resource_type'] == resource_type) & (resources_df['location'] == location), 'quantity'] -= quantity
            st.success(f"✅ {quantity} units of {resource_type} allocated to {location}")
        else:
            st.warning(f"⚠ Not enough {resource_type} available at {location}.")
        return resources_df
    except Exception as e:
        st.error(f"❌ Error allocating resources: {e}")
        return resources_df

# Find Nearest Supply Center
def find_nearest_supply_center(location, resources_df):
    try:
        available_centers = resources_df[resources_df['quantity'] > 0]
        available_centers['distance'] = available_centers['location'].apply(lambda x: gmaps.distance_matrix(location, x)['rows'][0]['elements'][0]['distance']['value'])
        nearest_center = available_centers.sort_values('distance').iloc[0]
        st.success(f"📍 Nearest supply center is {nearest_center['location']} at a distance of {nearest_center['distance']} meters.")
        return nearest_center['location']
    except Exception as e:
        st.error(f"❌ Error finding nearest supply center: {e}")
        return None

# Estimate Delivery Time
def estimate_delivery_time(source, destination):
    try:
        directions = gmaps.directions(source, destination)
        duration = directions[0]['legs'][0]['duration']['text']
        st.info(f"🚚 Estimated delivery time from {source} to {destination}: {duration}")
        return duration
    except Exception as e:
        st.error(f"❌ Error estimating delivery time: {e}")
        return None

# Send SMS Alert
def send_sms_alert(phone_number, location):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
                  "🔹 Drop, Cover, and Hold On.\n"
                  "🔹 Move to an open area if outside.\n"
                  "🔹 Stay away from windows and heavy objects.\n"
                  "🔹 Keep emergency contacts and supplies ready.\n"
                  "🔹 Follow official updates and stay safe!"),
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return message.sid
    except Exception as e:
        return f"Error: {e}"

# Display Earthquake Map
def display_map(df):
    st.subheader("🌍 Earthquake Affected Areas (Heatmap)")
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

# Main Function
def main():
    st.title("🌍 Disaster Alert and Logistics System")
    st.subheader("📊 Real-time Earthquake Data & Resource Management")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df, start_date, end_date = load_data()
    
    if df is not None and not df.empty:
        st.write(f"### 📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        st.subheader("📌 Earthquake Data Table")
        st.dataframe(df)
        display_map(df)
        
        # Track Available Resources
        resources_df = track_available_resources()

        # Allocate Resources
        affected_area = st.selectbox("📍 Select an affected area to allocate resources:", df['state'].unique())
        resource_type = st.selectbox("🔧 Select resource type:", resources_df['resource_type'].unique())
        quantity = st.number_input(f"Enter quantity of {resource_type} to allocate:", min_value=1)
        
        if st.button("🚀 Allocate Resources"):
            resources_df = allocate_resources(affected_area, resource_type, quantity, resources_df)
        
        # Estimate Delivery Time
        if st.button("🕒 Estimate Delivery Time"):
            nearest_center =
