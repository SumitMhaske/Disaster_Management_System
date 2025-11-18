import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Function to load data
def load_data():
    try:
        file_path = r"D:\WhatsApp\DisasterAlert (6)\DisasterAlert\data\real_time_india_earthquakes_with_states.csv"
        df = pd.read_csv(file_path)  # Load from fixed path
        
        st.success("File Loaded Successfully!")
        
        # Display raw data for debugging
        st.write("### First 5 rows of the data:")
        st.dataframe(df.head())
        
        # Check required columns
        required_columns = {'datetime', 'location'}
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

# Streamlit UI
def main():
    st.title("Disaster Alert System")
    st.subheader("Real-time Earthquake Data")

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