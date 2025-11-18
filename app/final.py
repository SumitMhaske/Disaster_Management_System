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

# Authentication Credentials
AUTH_CREDENTIALS = {"admin": "pass"}

# Email and SMS Credentials
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""

# File Paths
DATA_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"

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
        start_date = end_date - timedelta(days=20)
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

# Send Email Alert
# def send_email(subject, message, recipients):
    # try:
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.starttls()
        # server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        # for email in recipients:
            # msg = MIMEMultipart()
            # msg["From"] = EMAIL_SENDER
            # msg["To"] = email
            # msg["Subject"] = subject
            # msg.attach(MIMEText(message, "plain"))
            # server.sendmail(EMAIL_SENDER, email, msg.as_string())
        # server.quit()
        # return True
    # except Exception as e:
        # st.error(f"❌ Email sending failed: {e}")
        # return False

# Send SMS Alert
def send_sms_alert(phone_number, location):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(
                f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
                "🔹 Drop, Cover, and Hold On.\n"
                "🔹 Move to an open area if outside.\n"
                "🔹 Stay away from windows and heavy objects.\n"
                "🔹 Keep emergency contacts and supplies ready.\n"
                "🔹 Follow official updates and stay safe!"
            ),
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return message.sid
    except Exception as e:
        return f"Error: {e}"

def send_email(subject, location, recipients):
    message = (
        f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
        "🔹 Drop, Cover, and Hold On.\n"
        "🔹 Move to an open area if outside.\n"
        "🔹 Stay away from windows and heavy objects.\n"
        "🔹 Keep emergency contacts and supplies ready.\n"
        "🔹 Follow official updates and stay safe!\n\n"
        "Stay Safe,\nDisaster Alert System"
    )
    
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
        return True
    except Exception as e:
        st.error(f"❌ Email sending failed: {e}")
        return False

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
    st.title("🌍 Disaster Alert System")
    st.subheader("📊 Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df, start_date, end_date = load_data()
    
    if df is not None and not df.empty:
        st.write(f"### 📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        st.subheader("📌 Earthquake Data Table")
        st.dataframe(df)
        display_map(df)
        
        affected_area = st.selectbox("📍 Select an affected area to send an alert:", df['state'].unique())
        recipient_emails = load_user_emails(affected_area)
        if st.button("🚀 Send Email Alert") and recipient_emails:
            send_email(f"🚨 Earthquake Alert: {affected_area} 🚨", "Stay safe!", recipient_emails)
            st.success(f"📩 Email alert sent to {len(recipient_emails)} users in {affected_area}!")
        if st.button("📲 Send SMS Alert"):
            if affected_area == 'Delhi':
                send_sms_alert('+917796571177', affected_area)
                send_sms_alert('+918485078849', affected_area)
            elif affected_area == 'Punjab':
                send_sms_alert('+917058622905', affected_area)
            elif affected_area == 'Assam':
                send_sms_alert('+919579395752', affected_area)
            # elif affected_area == 'Sikkim':
                # send_sms_alert('+917038754097', affected_area)
            # elif affected_area == 'Rajasthan':
                # send_sms_alert('+918767549928', affected_area)
            # elif affected_area == 'Arunachal Pradesh':
                # send_sms_alert('+919420637258', affected_area)
            # elif affected_area == 'Jammu and Kashmir':
                # send_sms_alert('+918483972017', affected_area)
            # elif affected_area == 'Himachal Pradesh':
                # send_sms_alert('+919807859999', affected_area)
            # elif affected_area == 'Ladakh':
                # send_sms_alert('+917249678352', affected_area)
            # elif affected_area == 'Assam':
                # send_sms_alert('+918830094399', affected_area)
            # elif affected_area == 'Manipur':
                # send_sms_alert('+918855880088', affected_area)
            # elif affected_area == 'Odisha':
                # send_sms_alert('+919421561115', affected_area)
            # elif affected_area == 'Tripura':
                # send_sms_alert('+917058380264', affected_area)
            # elif affected_area == 'Maharashtra':
                # send_sms_alert('+917588620568', affected_area)
            else:
                st.warning('No users found in the selected state.')
            st.success(f"📩 SMS alert sent to users in {affected_area}!")

if __name__ == "__main__":
    main()