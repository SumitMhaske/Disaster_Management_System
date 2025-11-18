import streamlit as st
import pandas as pd
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load Data Function
def load_data():
    try:
        file_path = r"C:\Users\HP\Machine Learning Project\Final Hackathon\data\real_time_india_earthquakes_with_states.csv"
        df = pd.read_csv(file_path)

        st.success("✅ File Loaded Successfully!")

        # Convert datetime column properly
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        df['datetime'] = df['datetime'].dt.tz_convert(None)  # Remove timezone for comparison

        # Filter last 10 days
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

        return df, start_date, end_date
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame(), None, None

# Load User Emails for the Selected Region
def load_user_emails(selected_region):
    try:
        email_file = r"C:\Users\HP\Machine Learning Project\Final Hackathon\data\users.xlsx"
        emails_df = pd.read_excel(email_file, engine='openpyxl')  # Ensure 'openpyxl' is installed

        # Check if required columns exist
        if "email" not in emails_df.columns or "Location" not in emails_df.columns:
            st.error("❌ Excel file must contain 'email' and 'Location' columns.")
            return []

        # Filter emails based on the selected region
        filtered_emails = emails_df[emails_df["Location"].str.lower() == selected_region.lower()]["email"].tolist()
        
        return filtered_emails
    except Exception as e:
        st.error(f"❌ Error loading emails: {e}")
        return []

# Send Email Function (Fixed: Sends each email separately)
def send_email(subject, message, recipients):
    sender_email = "srushti.22211386@viit.ac.in"  # Replace with your Gmail
    app_password = "eida xufl uhme yytb"  # Replace with your generated App Password

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)

        for email in recipients:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = email  # Send to one recipient at a time
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            server.sendmail(sender_email, email, msg.as_string())

        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Email sending failed: {e}")
        return False

# Streamlit UI
def main():
    st.title("🌍 Disaster Alert System")
    st.subheader("📊 Real-time Earthquake Data")

    # Load earthquake data
    df, start_date, end_date = load_data()

    # Display Start and End Date
    if df is not None and not df.empty:
        st.write("### 📅 Date Range for Analysis")
        st.write(f"🟢 Start Date: {start_date.strftime('%Y-%m-%d')}")
        st.write(f"🔴 End Date: {end_date.strftime('%Y-%m-%d')}")

        # Display earthquake data
        st.subheader("📌 Earthquake Data Table")
        st.dataframe(df)

        # Dropdown for affected area selection
        st.subheader("📨 Send Alert")
        affected_area = st.selectbox("📍 Select an affected area to send an alert:", df['state'].unique())

        # Load recipient emails for selected region
        recipient_emails = load_user_emails(affected_area)

        if st.button("🚀 Send Email Alert"):
            if recipient_emails:
                email_subject = f"🚨 Earthquake Alert: {affected_area} 🚨"
                email_message = f"""
⚠ URGENT: Earthquake Detected in {affected_area}! ⚠

🔹 Location: {affected_area}
🔹 Date: {datetime.today().strftime('%Y-%m-%d')}
🔹 Recommended Preventive Measures:
   - Stay indoors and take cover under sturdy furniture.
   - Avoid windows, mirrors, and heavy objects that could fall.
   - If outside, move to an open area away from buildings and power lines.
   - Prepare an emergency kit with essentials like water, food, and medications.
   - Stay updated with local authorities for further instructions.

📢 Stay safe and take necessary precautions.

- DisasterAlert System
"""

                if send_email(email_subject, email_message, recipient_emails):
                    st.success(f"📩 Alert email sent successfully to {len(recipient_emails)} users in {affected_area}!")
                else:
                    st.error("❌ Failed to send emails.")
            else:
                st.warning(f"⚠ No users found in {affected_area}. No emails sent.")

        # Preventive Measures Section
        st.subheader("🛑 Preventive Measures")
        st.markdown("""
        - 🏠 *Stay indoors* and take cover under sturdy furniture.
        - 🚪 *Avoid windows, mirrors, and heavy objects* that could fall.
        - 🏞️ *If outside, move to an open area* away from buildings and power lines.
        - 🎒 *Prepare an emergency kit* with essentials like water, food, and medications.
        - 📻 *Stay updated* with local authorities for further instructions.
        """)

    else:
        st.warning("⚠ No data available. Please check the file path.")

if _name_ == "_main_":
    main()