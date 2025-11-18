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
import googlemaps

# Authentication Credentials
AUTH_CREDENTIALS = {"admin": "pass"}

# Authentication user
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

# API & Email Credentials
EMAIL_SENDER = os.getenv("")
EMAIL_PASSWORD = os.getenv("")
TWILIO_SID = os.getenv("")
TWILIO_AUTH_TOKEN = os.getenv("")
TWILIO_PHONE_NUMBER = os.getenv("")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# File Paths
DATA_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"
RESOURCES_FILE_PATH = "resources.xlsx"

# Load Earthquake Data
def load_data():
    df = pd.read_csv(DATA_FILE_PATH)
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert(None)
    start_date = datetime.today() - timedelta(days=10)
    df = df[(df['datetime'] >= start_date)]
    return df

# Load User Emails
def load_user_emails(region):
    emails_df = pd.read_excel(EMAIL_FILE_PATH, engine='openpyxl')
    return emails_df[emails_df["Location"].str.lower() == region.lower()]["email"].tolist()

# Load Resource Data
def load_resources():
    return pd.read_excel(RESOURCES_FILE_PATH, engine='openpyxl')

# Send Email Alert
def send_email(subject, location, recipients):
    message = f"🚨 Earthquake Alert: {location} is affected. Stay safe!"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        for email in recipients:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_SENDER
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))
            server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Email sending failed: {e}")

# Send SMS Alert
def send_sms_alert(phone_number, location):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"🚨 Earthquake Alert: {location} is affected! Stay safe.",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# Find Nearest Supply Center
def find_nearest_supply_center(affected_area, resources_df):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    affected_location = gmaps.geocode(affected_area)[0]['geometry']['location']
    centers = resources_df[['Location', 'Latitude', 'Longitude']]
    distances = []
    
    for _, row in centers.iterrows():
        distance = gmaps.distance_matrix(
            (affected_location['lat'], affected_location['lng']),
            (row['Latitude'], row['Longitude']),
            mode="driving"
        )['rows'][0]['elements'][0]['duration']['text']
        distances.append((row['Location'], distance))
    
    return min(distances, key=lambda x: int(x[1].split()[0])) if distances else None

# Display Earthquake Map
def display_map(df):
    st.subheader("🌍 Earthquake Affected Areas (Heatmap)")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)
    folium_static(m)

# Main Function
def main():
    st.title("🌍 Disaster Alert & Logistics System")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df = load_data()
    if df.empty:
        st.warning("No recent earthquakes detected.")
        return
    
    display_map(df)
    affected_area = st.selectbox("📍 Select an affected area:", df['state'].unique())
    recipient_emails = load_user_emails(affected_area)
    
    if st.button("🚀 Send Email Alert") and recipient_emails:
        send_email(f"🚨 Earthquake Alert: {affected_area}", affected_area, recipient_emails)
        st.success(f"📩 Email alert sent to {len(recipient_emails)} users!")
    
    if st.button("📲 Send SMS Alert"):
        send_sms_alert("+917796571177", affected_area)
        st.success("📩 SMS alert sent!")
    
    resources_df = load_resources()
    nearest_center = find_nearest_supply_center(affected_area, resources_df)
    
    if nearest_center:
        st.success(f"🚚 Nearest Supply Center: {nearest_center[0]} | Estimated Delivery: {nearest_center[1]}")
    else:
        st.warning("No supply centers found.")

if __name__ == "__main__":
    main()
