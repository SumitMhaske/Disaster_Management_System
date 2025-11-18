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

AUTH_CREDENTIALS = {"admin": "pass"}
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""
DATA_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"
LOGISTICS_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\logistics.xlsx"

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

def load_logistics_resources():
    try:
        if os.path.exists(LOGISTICS_FILE_PATH):
            logistics_df = pd.read_excel(LOGISTICS_FILE_PATH, engine='openpyxl')
            return logistics_df
        else:
            logistics_data = {
                'region': ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Sikkim', 'Rajasthan'],
                'shelter_centers': [15, 12, 8, 20, 5, 10],
                'ambulances': [25, 18, 15, 30, 8, 20],
                'relief_supplies_tons': [50, 40, 35, 60, 20, 45],
                'medical_teams': [10, 8, 7, 12, 4, 9],
                'emergency_contacts': ['+917796571177', '+917058622905', '+919579395752', '+917588620568', '+917038754097', '+918767549928']
            }
            logistics_df = pd.DataFrame(logistics_data)
            logistics_df.to_excel(LOGISTICS_FILE_PATH, index=False)
            return logistics_df
    except Exception as e:
        st.error(f"❌ Error loading logistics data: {e}")
        return pd.DataFrame()

def update_logistics_resources(region, resource_type, new_value):
    try:
        logistics_df = load_logistics_resources()
        if not logistics_df.empty:
            idx = logistics_df[logistics_df['region'] == region].index
            if len(idx) > 0:
                logistics_df.loc[idx, resource_type] = new_value
                logistics_df.to_excel(LOGISTICS_FILE_PATH, index=False)
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error updating logistics data: {e}")
        return False

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

def send_sms_alert(phone_number, location, logistics_info=None):
    try:
        # base_message = (
            # f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
            # "🔹 Drop, Cover, and Hold On.\n"
            # "🔹 Move to an open area if outside.\n"
            # "🔹 Stay away from windows and heavy objects.\n"
            # "🔹 Keep emergency contacts and supplies ready.\n"
            # "🔹 Follow official updates and stay safe!"
        # )
        # 
        # if logistics_info:
            # logistics_details = (
                # f"\n\nNearest Shelter: {logistics_info['nearest_shelter']}\n"
                # f"Medical Help: {logistics_info['medical_contact']}\n"
                # f"Relief Supplies Available at: {logistics_info['relief_center']}"
            # )
            # base_message += logistics_details

                # Create a single concise message with essential information and logistics
        if logistics_info:
            base_message = (
                f"Earthquake Alert: {location} affected. Take precautions! \n"
                f"Shelter: {logistics_info['nearest_shelter']}. \n"
                f"Medical: {logistics_info['medical_contact']}. \n"
                "Drop, Cover, Hold On. Move to open area if outside."
            )
        else:
            base_message = (
                f"Earthquake Alert: {location} affected. Take precautions! "
                "Drop, Cover, Hold On. Move to open area if outside."
            )
            
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=base_message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return message.sid
    except Exception as e:
        return f"Error: {e}"

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

def calculate_severity_level(magnitude):
    if magnitude < 4.0:
        return "Low", "green"
    elif magnitude < 5.5:
        return "Moderate", "orange"
    elif magnitude < 7.0:
        return "High", "red"
    else:
        return "Extreme", "darkred"

def get_resource_allocation(severity, population=None):
    if severity == "Low":
        return {
            "ambulances": 5,
            "relief_teams": 2,
            "shelter_capacity": 200,
            "food_supplies_days": 3
        }
    elif severity == "Moderate":
        return {
            "ambulances": 15,
            "relief_teams": 5,
            "shelter_capacity": 500,
            "food_supplies_days": 7
        }
    elif severity == "High":
        return {
            "ambulances": 30,
            "relief_teams": 10,
            "shelter_capacity": 1000,
            "food_supplies_days": 14
        }
    else:  # Extreme
        return {
            "ambulances": 50,
            "relief_teams": 20,
            "shelter_capacity": 2500,
            "food_supplies_days": 30
        }

def display_logistics_management(df, logistics_df):
    st.subheader("🚚 Logistics Management")
    
    affected_area = st.selectbox("📍 Select an area for logistics management:", df['state'].unique())
    
    if affected_area:
        affected_data = df[df['state'] == affected_area]
        max_magnitude = affected_data['magnitude'].max() if not affected_data.empty else 0
        severity, color = calculate_severity_level(max_magnitude)
        
        st.markdown(f"### Area: {affected_area}")
        st.markdown(f"### Severity: <span style='color:{color};'>{severity}</span>", unsafe_allow_html=True)
        
        resources = get_resource_allocation(severity)
        
        area_logistics = logistics_df[logistics_df['region'] == affected_area]
        if not area_logistics.empty:
            st.markdown("### Available Resources:")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Shelter Centers", area_logistics['shelter_centers'].values[0])
                st.metric("Ambulances", area_logistics['ambulances'].values[0])
            
            with col2:
                st.metric("Relief Supplies (tons)", area_logistics['relief_supplies_tons'].values[0])
                st.metric("Medical Teams", area_logistics['medical_teams'].values[0])
            
            st.markdown("### Recommended Resource Allocation:")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Ambulances Needed", resources['ambulances'])
                st.metric("Relief Teams Needed", resources['relief_teams'])
            
            with col2:
                st.metric("Shelter Capacity Needed", resources['shelter_capacity'])
                st.metric("Food Supplies (days)", resources['food_supplies_days'])
            
            st.markdown("### Update Resource Availability:")
            resource_type = st.selectbox("Select resource to update:", 
                                         ['shelter_centers', 'ambulances', 'relief_supplies_tons', 'medical_teams'])
            new_value = st.number_input("New value:", min_value=0, 
                                       value=int(area_logistics[resource_type].values[0]))
            
            if st.button("Update Resources"):
                if update_logistics_resources(affected_area, resource_type, new_value):
                    st.success(f"✅ Resources updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update resources")
            
            logistics_info = {
                "nearest_shelter": f"Shelter #{area_logistics['shelter_centers'].values[0]} at City Center",
                "medical_contact": f"Emergency Medical Team: {area_logistics['emergency_contacts'].values[0]}",
                "relief_center": f"Main Distribution Center with {area_logistics['relief_supplies_tons'].values[0]} tons of supplies"
            }
            
            return affected_area, logistics_info
        else:
            st.warning(f"No logistics data available for {affected_area}")
    
    return affected_area, None

def main():
    st.title("🌍 Disaster Alert System")
    st.subheader("📊 Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df, start_date, end_date = load_data()
    
    if df is not None and not df.empty:
        st.write(f"### 📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        tab1, tab2, tab3 = st.tabs(["📋 Data", "🌍 Map", "🚚 Logistics"])
        
        with tab1:
            st.subheader("📌 Earthquake Data Table")
            st.dataframe(df)
        
        with tab2:
            display_map(df)
        
        with tab3:
            logistics_df = load_logistics_resources()
            affected_area, logistics_info = display_logistics_management(df, logistics_df)
        
        st.subheader("🚨 Send Alerts")
        alert_area = st.selectbox("📍 Select an affected area to send an alert:", df['state'].unique())
        recipient_emails = load_user_emails(alert_area)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Send Email Alert") and recipient_emails:
                send_email(f"🚨 Earthquake Alert: {alert_area} 🚨", alert_area, recipient_emails)
                st.success(f"📩 Email alert sent to {len(recipient_emails)} users in {alert_area}!")
        
        with col2:
            if st.button("📲 Send SMS Alert with Logistics Info"):
                logistics_df = load_logistics_resources()
                area_logistics = logistics_df[logistics_df['region'] == alert_area]
                
                if not area_logistics.empty:
                    logistics_info = {
                        "nearest_shelter": f"Shelter #{area_logistics['shelter_centers'].values[0]} at City Center",
                        "medical_contact": f"Emergency Medical Team: {area_logistics['emergency_contacts'].values[0]}",
                        "relief_center": f"Main Distribution Center with {area_logistics['relief_supplies_tons'].values[0]} tons of supplies"
                    }
                    
                    if alert_area == 'Delhi':
                        send_sms_alert('+917796571177', alert_area, logistics_info)
                        send_sms_alert('+918485078849', alert_area, logistics_info)
                    elif alert_area == 'Punjab':
                        send_sms_alert('+917058622905', alert_area, logistics_info)
                    elif alert_area == 'Assam':
                        send_sms_alert('+919579395752', alert_area, logistics_info)
                    else:
                        contact = area_logistics['emergency_contacts'].values[0] if not area_logistics.empty else None
                        if contact:
                            send_sms_alert(contact, alert_area, logistics_info)
                        else:
                            st.warning('No users found in the selected state.')
                    
                    st.success(f"📩 SMS alert with logistics info sent to users in {alert_area}!")
                else:
                    st.warning(f"No logistics data available for {alert_area}")

if __name__ == "__main__":
    main()