import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from twilio.rest import Client


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

def load_data():
    try:
        file_path = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
        df = pd.read_csv(file_path)
        
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

def send_sms_alert(phone_number, location):
    try:
        client = Client("AC5ca73c9f4bdd55877f4c097867dc7335", "c566b70c2e1c9b4fbaa99cff674d7b81")
        message = client.messages.create(
            #body=f"\U0001F6A8 Earthquake Alert: {location} is affected. Take necessary precautions!",
            body=(
                    f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
                    "🔹 Drop, Cover, and Hold On.\n"
                    "🔹 Move to an open area if outside.\n"
                    "🔹 Stay away from windows and heavy objects.\n"
                    "🔹 Keep emergency contacts and supplies ready.\n"
                    "🔹 Follow official updates and stay safe!"
            ),
            from_="+18043921525",
            to=phone_number
        )
        return message.sid
    except Exception as e:
        return f"Error: {e}"

def display_map(df):
    st.subheader("\U0001F5FA Earthquake Affected Areas (Heatmap)")
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
            popup=f"\U0001F4CD {row['location']}<br>\U0001F4C6 {row['datetime'].strftime('%Y-%m-%d')}<br>\U0001F30D Magnitude: {row['magnitude']}"
        ).add_to(m)
    folium_static(m)



def main():
    st.title("Disaster Alert System")
    st.subheader("Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    df, start_date, end_date = load_data()
    
    if df is not None and not df.empty:
        st.write("### Date Range for Analysis")
        st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
        st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
        
        st.subheader("Earthquake Data Table")
        st.dataframe(df)
        display_map(df)
        
        st.subheader("Send Alert")
        selected_state = st.selectbox("Select an affected area to send an alert:", df['state'].unique())
        
        if st.button("Send SMS Alert"):
            if selected_state == 'Delhi':
                send_sms_alert('+917796571177', selected_state)
                send_sms_alert('+918485078849', selected_state)
            elif selected_state == 'Punjab':
                send_sms_alert('+917058622905', selected_state)
            elif selected_state == 'Assam':
                send_sms_alert('+919579395752', selected_state)
            elif selected_state == 'Sikkim':
                send_sms_alert('+917038754097', selected_state)
            elif selected_state == 'Rajasthan':
                send_sms_alert('+918767549928', selected_state)
            elif selected_state == 'Arunachal Pradesh':
                send_sms_alert('+919420637258', selected_state)
            elif selected_state == 'Jammu and Kashmir':
                send_sms_alert('+918483972017', selected_state)
            elif selected_state == 'Himachal Pradesh':
                send_sms_alert('+919807859999', selected_state)
            elif selected_state == 'Ladakh':
                send_sms_alert('+917249678352', selected_state)
            elif selected_state == 'Assam':
                send_sms_alert('+918830094399', selected_state)
            elif selected_state == 'Manipur':
                send_sms_alert('+918855880088', selected_state)
            elif selected_state == 'Odisha':
                send_sms_alert('+919421561115', selected_state)
            elif selected_state == 'Tripura':
                send_sms_alert('+917058380264', selected_state)
            elif selected_state == 'Maharashtra':
                send_sms_alert('+917588620568', selected_state)
            else:
                st.warning('No users found in the selected state.')

if __name__ == "__main__":
    main()