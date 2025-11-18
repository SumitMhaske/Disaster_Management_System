import streamlit as st
import pandas as pd
import smtplib
import os
import numpy as np
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from twilio.rest import Client
import random

# Existing credentials and file paths
AUTH_CREDENTIALS = {"admin": "pass"}
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""
DATA_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\users.xlsx"
LOGISTICS_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\logistics.xlsx"
INVENTORY_FILE_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\inventory.xlsx"
HISTORICAL_DATA_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\historical_earthquakes.csv"
DRONE_DEPLOYMENT_PATH = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\drone_deployment.xlsx"

# Existing authentication function
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

# Existing data loading function
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

# Load historical earthquake data for AI forecasting
def load_historical_data():
    try:
        if os.path.exists(HISTORICAL_DATA_PATH):
            df = pd.read_csv(HISTORICAL_DATA_PATH)
            return df
        else:
            # Create sample historical data if file doesn't exist
            regions = ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Sikkim', 'Rajasthan']
            data = []
            
            start_date = datetime.now() - timedelta(days=365*5)  # 5 years of data
            end_date = datetime.now()
            dates = pd.date_range(start=start_date, end=end_date, freq='W')  # Weekly data
            
            for region in regions:
                # More earthquakes for historically active regions
                multiplier = 2.0 if region in ['Assam', 'Sikkim'] else 1.0
                
                for date in dates:
                    # Random earthquake generation based on historical patterns
                    if random.random() < 0.2 * multiplier:  # 20% chance of earthquake, higher for active regions
                        magnitude = round(random.uniform(3.0, 7.5), 1)
                        affected_population = int(random.uniform(1000, 500000))
                        resources_used = {
                            'water_liters': int(affected_population * random.uniform(2, 5)),
                            'food_kg': int(affected_population * random.uniform(0.5, 1.5)),
                            'medicine_units': int(affected_population * random.uniform(0.1, 0.3)),
                            'shelter_kits': int(affected_population / random.uniform(4, 8)),
                            'ambulances': int(affected_population / random.uniform(5000, 10000)),
                            'relief_teams': int(affected_population / random.uniform(10000, 20000))
                        }
                        
                        data.append({
                            'date': date,
                            'region': region,
                            'magnitude': magnitude,
                            'affected_population': affected_population,
                            'water_liters': resources_used['water_liters'],
                            'food_kg': resources_used['food_kg'],
                            'medicine_units': resources_used['medicine_units'],
                            'shelter_kits': resources_used['shelter_kits'],
                            'ambulances_deployed': resources_used['ambulances'],
                            'relief_teams': resources_used['relief_teams']
                        })
            
            historical_df = pd.DataFrame(data)
            historical_df.to_csv(HISTORICAL_DATA_PATH, index=False)
            return historical_df
    except Exception as e:
        st.error(f"❌ Error loading historical data: {e}")
        return pd.DataFrame()

# Load inventory data for IoT-enabled tracking
def load_inventory_data():
    try:
        if os.path.exists(INVENTORY_FILE_PATH):
            inventory_df = pd.read_excel(INVENTORY_FILE_PATH, engine='openpyxl')
            return inventory_df
        else:
            # Create sample inventory data if file doesn't exist
            regions = ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Sikkim', 'Rajasthan']
            inventory_data = {
                'region': [],
                'item_type': [],
                'item_name': [],
                'quantity': [],
                'unit': [],
                'expiry_date': [],
                'last_updated': [],
                'status': [],
                'batch_id': [],
                'reorder_level': [],
                'optimal_level': []
            }
            
            items = [
                {'type': 'Food', 'name': 'Rice', 'unit': 'kg', 'shelf_life': 365, 'min': 500, 'max': 2000},
                {'type': 'Food', 'name': 'Wheat Flour', 'unit': 'kg', 'shelf_life': 180, 'min': 500, 'max': 2000},
                {'type': 'Food', 'name': 'Lentils', 'unit': 'kg', 'shelf_life': 365, 'min': 200, 'max': 1000},
                {'type': 'Food', 'name': 'Salt', 'unit': 'kg', 'shelf_life': 730, 'min': 100, 'max': 500},
                {'type': 'Food', 'name': 'Sugar', 'unit': 'kg', 'shelf_life': 730, 'min': 100, 'max': 500},
                {'type': 'Food', 'name': 'Cooking Oil', 'unit': 'liter', 'shelf_life': 180, 'min': 200, 'max': 1000},
                {'type': 'Water', 'name': 'Drinking Water', 'unit': 'liter', 'shelf_life': 365, 'min': 1000, 'max': 5000},
                {'type': 'Medicine', 'name': 'First Aid Kits', 'unit': 'units', 'shelf_life': 730, 'min': 50, 'max': 300},
                {'type': 'Medicine', 'name': 'Antibiotics', 'unit': 'strips', 'shelf_life': 365, 'min': 100, 'max': 500},
                {'type': 'Medicine', 'name': 'Pain Relievers', 'unit': 'strips', 'shelf_life': 365, 'min': 100, 'max': 500},
                {'type': 'Medicine', 'name': 'ORS', 'unit': 'packets', 'shelf_life': 365, 'min': 200, 'max': 1000},
                {'type': 'Shelter', 'name': 'Tents', 'unit': 'units', 'shelf_life': 1825, 'min': 50, 'max': 200},
                {'type': 'Shelter', 'name': 'Tarpaulins', 'unit': 'units', 'shelf_life': 1095, 'min': 100, 'max': 500},
                {'type': 'Shelter', 'name': 'Blankets', 'unit': 'units', 'shelf_life': 1095, 'min': 200, 'max': 1000},
                {'type': 'Equipment', 'name': 'Search & Rescue Kits', 'unit': 'sets', 'shelf_life': 1825, 'min': 5, 'max': 20},
                {'type': 'Equipment', 'name': 'Solar Lamps', 'unit': 'units', 'shelf_life': 1095, 'min': 100, 'max': 500},
                {'type': 'Equipment', 'name': 'Portable Generators', 'unit': 'units', 'shelf_life': 1825, 'min': 5, 'max': 20}
            ]
            
            # Generate batch IDs
            batch_id_counter = 1001
            
            for region in regions:
                for item in items:
                    # Adjust quantities based on region population (simplified assumption)
                    population_factor = 1.5 if region in ['Delhi', 'Maharashtra'] else 1.0
                    quantity = int(random.uniform(item['min'], item['max']) * population_factor)
                    
                    # Some items might be below reorder level
                    if random.random() < 0.2:
                        quantity = int(item['min'] * random.uniform(0.5, 0.9))
                        status = 'Low'
                    else:
                        status = 'Adequate'
                    
                    expiry_date = datetime.now() + timedelta(days=int(item['shelf_life'] * random.uniform(0.3, 0.9)))
                    batch_id = f"B{batch_id_counter}"
                    batch_id_counter += 1
                    
                    inventory_data['region'].append(region)
                    inventory_data['item_type'].append(item['type'])
                    inventory_data['item_name'].append(item['name'])
                    inventory_data['quantity'].append(quantity)
                    inventory_data['unit'].append(item['unit'])
                    inventory_data['expiry_date'].append(expiry_date)
                    inventory_data['last_updated'].append(datetime.now() - timedelta(days=random.randint(1, 30)))
                    inventory_data['status'].append(status)
                    inventory_data['batch_id'].append(batch_id)
                    inventory_data['reorder_level'].append(item['min'])
                    inventory_data['optimal_level'].append(item['max'])
            
            inventory_df = pd.DataFrame(inventory_data)
            inventory_df.to_excel(INVENTORY_FILE_PATH, index=False)
            return inventory_df
    except Exception as e:
        st.error(f"❌ Error loading inventory data: {e}")
        return pd.DataFrame()

# Load drone deployment data
def load_drone_data():
    try:
        if os.path.exists(DRONE_DEPLOYMENT_PATH):
            drone_df = pd.read_excel(DRONE_DEPLOYMENT_PATH, engine='openpyxl')
            return drone_df
        else:
            # Create sample drone deployment data if file doesn't exist
            regions = ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Sikkim', 'Rajasthan']
            drone_types = ['Surveillance', 'Delivery', 'Communication', 'Assessment']
            
            drone_data = {
                'region': [],
                'drone_id': [],
                'drone_type': [],
                'status': [],
                'battery_level': [],
                'max_payload_kg': [],
                'range_km': [],
                'last_mission': [],
                'total_missions': [],
                'base_location': []
            }
            
            for region in regions:
                # Number of drones per region varies
                num_drones = random.randint(5, 15)
                
                for i in range(num_drones):
                    drone_type = random.choice(drone_types)
                    
                    if drone_type == 'Surveillance':
                        max_payload = 0
                        range_km = random.uniform(30, 50)
                    elif drone_type == 'Delivery':
                        max_payload = random.uniform(3, 10)
                        range_km = random.uniform(15, 30)
                    elif drone_type == 'Communication':
                        max_payload = random.uniform(1, 3)
                        range_km = random.uniform(40, 60)
                    else:  # Assessment
                        max_payload = random.uniform(1, 5)
                        range_km = random.uniform(25, 45)
                    
                    drone_data['region'].append(region)
                    drone_data['drone_id'].append(f"DR-{region[:2].upper()}-{i+101}")
                    drone_data['drone_type'].append(drone_type)
                    drone_data['status'].append(random.choice(['Ready', 'Charging', 'Maintenance', 'Deployed']))
                    drone_data['battery_level'].append(random.randint(30, 100))
                    drone_data['max_payload_kg'].append(round(max_payload, 1))
                    drone_data['range_km'].append(round(range_km, 1))
                    drone_data['last_mission'].append(datetime.now() - timedelta(days=random.randint(0, 30)))
                    drone_data['total_missions'].append(random.randint(0, 50))
                    drone_data['base_location'].append(f"{region} Base {random.randint(1,3)}")
            
            drone_df = pd.DataFrame(drone_data)
            drone_df.to_excel(DRONE_DEPLOYMENT_PATH, index=False)
            return drone_df
    except Exception as e:
        st.error(f"❌ Error loading drone data: {e}")
        return pd.DataFrame()

# Existing user email loading function
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

# Existing logistics resources loading function with enhancements
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
                'emergency_contacts': ['+917796571177', '+917058622905', '+919579395752', '+917588620568', '+917038754097', '+918767549928'],
                'drones_available': [12, 8, 10, 15, 5, 7],
                'autonomous_vehicles': [5, 3, 2, 7, 1, 4],
                'blockchain_txn_id': ['0x8a7f...', '0x9b2c...', '0x7d3e...', '0x5f2a...', '0x3e9b...', '0x1d7c...']
            }
            logistics_df = pd.DataFrame(logistics_data)
            logistics_df.to_excel(LOGISTICS_FILE_PATH, index=False)
            return logistics_df
    except Exception as e:
        st.error(f"❌ Error loading logistics data: {e}")
        return pd.DataFrame()

# Update logistics resources
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

# AI-driven demand forecasting function
def forecast_resource_needs(region, magnitude):
    historical_df = load_historical_data()
    
    if historical_df.empty:
        return {
            'water_liters': 5000,
            'food_kg': 2000,
            'medicine_units': 500,
            'shelter_kits': 200,
            'ambulances': 10,
            'relief_teams': 5
        }
    
    # Filter historical data for the region and similar magnitude events
    similar_events = historical_df[
        (historical_df['region'] == region) & 
        (historical_df['magnitude'] >= magnitude - 0.5) & 
        (historical_df['magnitude'] <= magnitude + 0.5)
    ]
    
    # If no similar events, use all data from region with adjusted weights
    if similar_events.empty:
        similar_events = historical_df[historical_df['region'] == region]
        if similar_events.empty:
            similar_events = historical_df
    
    # Calculate average resource usage, with more weight to higher magnitude events
    similar_events['weight'] = similar_events['magnitude'] / similar_events['magnitude'].sum()
    
    forecasted_resources = {
        'water_liters': int(np.average(similar_events['water_liters'], weights=similar_events['weight'])),
        'food_kg': int(np.average(similar_events['food_kg'], weights=similar_events['weight'])),
        'medicine_units': int(np.average(similar_events['medicine_units'], weights=similar_events['weight'])),
        'shelter_kits': int(np.average(similar_events['shelter_kits'], weights=similar_events['weight'])),
        'ambulances': int(np.average(similar_events['ambulances_deployed'], weights=similar_events['weight'])),
        'relief_teams': int(np.average(similar_events['relief_teams'], weights=similar_events['weight']))
    }
    
    # Adjust based on magnitude (higher magnitude = exponentially more resources)
    magnitude_factor = 1.0 + ((magnitude - 5.0) * 0.2 if magnitude > 5.0 else 0)
    
    for key in forecasted_resources:
        forecasted_resources[key] = int(forecasted_resources[key] * magnitude_factor)
    
    return forecasted_resources

# Check inventory against forecasted needs
def check_inventory_sufficiency(region, forecasted_needs):
    inventory_df = load_inventory_data()
    
    if inventory_df.empty:
        return {}, {}
    
    region_inventory = inventory_df[inventory_df['region'] == region]
    
    # Group by item type and sum quantities
    inventory_summary = region_inventory.groupby('item_type').agg({'quantity': 'sum'}).reset_index()
    
    # Convert to dictionary for easier comparison
    inventory_by_type = dict(zip(inventory_summary['item_type'], inventory_summary['quantity']))
    
    # Map forecasted needs to inventory types
    needs_mapping = {
        'water_liters': 'Water',
        'food_kg': 'Food',
        'medicine_units': 'Medicine',
        'shelter_kits': 'Shelter'
    }
    
    inventory_status = {}
    deficiencies = {}
    
    for need_key, inventory_type in needs_mapping.items():
        available = inventory_by_type.get(inventory_type, 0)
        needed = forecasted_needs.get(need_key, 0)
        
        if available >= needed:
            status = "Sufficient"
            deficit = 0
        else:
            status = "Insufficient"
            deficit = needed - available
        
        inventory_status[inventory_type] = {
            'available': available,
            'needed': needed,
            'status': status,
            'sufficiency_pct': min(100, int((available / max(1, needed)) * 100))
        }
        
        if deficit > 0:
            deficiencies[inventory_type] = deficit
    
    return inventory_status, deficiencies

# Optimize route for emergency vehicles
def optimize_route(start_point, affected_areas, blocked_roads=None):
    # This is a simplified routing algorithm
    # In a real system, this would connect to a GIS service like Google Maps API
    
    # Dummy coordinates for demonstration
    coordinates = {
        'Delhi': (28.7041, 77.1025),
        'Punjab': (31.1471, 75.3412),
        'Assam': (26.2006, 92.9376),
        'Maharashtra': (19.7515, 75.7139),
        'Sikkim': (27.5330, 88.5122),
        'Rajasthan': (27.0238, 74.2179)
    }
    
    if start_point not in coordinates:
        return None, None
    
    if isinstance(affected_areas, str):
        affected_areas = [affected_areas]
    
    # Calculate direct distances (as the crow flies)
    distances = {}
    for area in affected_areas:
        if area in coordinates:
            # Haversine formula for distance between coordinates
            lat1, lon1 = coordinates[start_point]
            lat2, lon2 = coordinates[area]
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            r = 6371  # Radius of earth in kilometers
            
            # Store distance
            distances[area] = c * r
    
    # Sort by distance
    sorted_areas = sorted(distances.items(), key=lambda x: x[1])
    route = [area for area, _ in sorted_areas]
    
    # Calculate total distance
    total_distance = sum(distances.values())
    
    return route, total_distance

# Determine optimal drone deployment strategy
def plan_drone_deployment(affected_region, magnitude, needs_assessment=True, delivery_needed=False):
    drone_df = load_drone_data()
    
    if drone_df.empty:
        return {}
    
    # Filter drones in the region that are ready
    available_drones = drone_df[
        (drone_df['region'] == affected_region) & 
        (drone_df['status'] == 'Ready') & 
        (drone_df['battery_level'] >= 70)  # Ensure sufficient battery
    ]
    
    deployment_plan = {
        'assessment': [],
        'delivery': [],
        'communication': [],
        'surveillance': []
    }
    
    # Select assessment drones
    if needs_assessment:
        assessment_drones = available_drones[available_drones['drone_type'].isin(['Assessment', 'Surveillance'])]
        for _, drone in assessment_drones.head(2).iterrows():  # Deploy up to 2 assessment drones
            deployment_plan['assessment'].append({
                'drone_id': drone['drone_id'],
                'type': drone['drone_type'],
                'range_km': drone['range_km'],
                'mission': 'Rapid damage assessment and search for victims'
            })
    
    # Select delivery drones if needed
    if delivery_needed:
        delivery_drones = available_drones[available_drones['drone_type'] == 'Delivery']
        for _, drone in delivery_drones.head(3).iterrows():  # Deploy up to 3 delivery drones
            deployment_plan['delivery'].append({
                'drone_id': drone['drone_id'],
                'type': drone['drone_type'],
                'payload_kg': drone['max_payload_kg'],
                'mission': 'Deliver emergency medical supplies and water'
            })
    
    # Select communication drones for higher magnitude events
    if magnitude >= 5.5:
        comm_drones = available_drones[available_drones['drone_type'] == 'Communication']
        for _, drone in comm_drones.head(1).iterrows():  # Deploy 1 communication drone
            deployment_plan['communication'].append({
                'drone_id': drone['drone_id'],
                'type': drone['drone_type'],
                'range_km': drone['range_km'],
                'mission': 'Establish emergency communication network'
            })
    
    # Select surveillance drones for continuous monitoring
    surveillance_drones = available_drones[available_drones['drone_type'] == 'Surveillance']
    for _, drone in surveillance_drones.head(2).iterrows():  # Deploy up to 2 surveillance drones
        deployment_plan['surveillance'].append({
            'drone_id': drone['drone_id'],
            'type': drone['drone_type'],
            'range_km': drone['range_km'],
            'mission': 'Continuous monitoring of affected areas and population movements'
        })
    
    return deployment_plan

# Existing email sending function
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

# Existing SMS alert function
def send_sms_alert(phone_number, location, logistics_info=None):
    try:
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

# Existing map display function
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

# Existing severity level calculation
def calculate_severity_level(magnitude):
    if magnitude < 4.0:
        return "Low", "green"
    elif magnitude < 5.5:
        return "Moderate", "orange"
    elif magnitude < 7.0:
        return "High", "red"
    else:
        return "Extreme", "darkred"

# Existing resource allocation function with AI-enhancement
# Existing resource allocation function with AI-enhancement
def get_resource_allocation(region, magnitude):
    logistics_df = load_logistics_resources()
    
    if logistics_df.empty:
        return {}
    
    region_data = logistics_df[logistics_df['region'] == region]
    if region_data.empty:
        return {}
    
    region_data = region_data.iloc[0]
    
    # Use AI to forecast needs based on historical data
    forecasted_needs = forecast_resource_needs(region, magnitude)
    
    # Check current inventory against forecasted needs
    inventory_status, deficiencies = check_inventory_sufficiency(region, forecasted_needs)
    
    # Determine severity level
    severity_level, _ = calculate_severity_level(magnitude)
    
    # Prepare allocation recommendation
    allocation = {
        'shelter_centers': int(region_data['shelter_centers'] * (0.3 if severity_level == "Low" else 0.6 if severity_level == "Moderate" else 1.0)),
        'ambulances': int(region_data['ambulances'] * (0.2 if severity_level == "Low" else 0.5 if severity_level == "Moderate" else 0.8 if severity_level == "High" else 1.0)),
        'medical_teams': int(region_data['medical_teams'] * (0.3 if severity_level == "Low" else 0.6 if severity_level == "Moderate" else 1.0)),
        'emergency_contact': region_data['emergency_contacts'],
        'drones_to_deploy': int(region_data['drones_available'] * (0.2 if severity_level == "Low" else 0.5 if severity_level == "Moderate" else 0.8)),
        'food_required_kg': forecasted_needs['food_kg'],
        'water_required_liters': forecasted_needs['water_liters'],
        'medicine_units_required': forecasted_needs['medicine_units'],
        'shelter_kits_required': forecasted_needs['shelter_kits'],
        'inventory_status': inventory_status,
        'resource_gaps': deficiencies
    }
    
    # Plan optimal routes for resource delivery
    affected_area = region
    logistics_base = region  # Assuming resources come from the same region
    route, distance = optimize_route(logistics_base, affected_area)
    
    if route:
        allocation['optimal_route'] = route
        allocation['route_distance_km'] = round(distance, 2)
    
    # Plan drone deployment
    delivery_needed = bool(deficiencies)  # Need delivery drones if there are resource gaps
    drone_plan = plan_drone_deployment(region, magnitude, needs_assessment=True, delivery_needed=delivery_needed)
    allocation['drone_deployment'] = drone_plan
    
    return allocation

# Main application interface
def main():
    st.set_page_config(page_title="DisasterAlert - AI-Enhanced Earthquake Management", page_icon="🚨", layout="wide")
    
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Sidebar navigation
    st.sidebar.title("🚨 DisasterAlert")
    
    # Authentication
    is_authenticated = authenticate()
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Earthquake Data", "Resource Management", "Emergency Planning", "Communication Center", "Analytics"], key="nav")
    st.session_state.page = page.lower().replace(" ", "_")
    
    # Load data
    df, start_date, end_date = load_data()
    
    # Dashboard
    if st.session_state.page == "dashboard":
        st.title("🌍 Earthquake Monitoring Dashboard")
        st.markdown("### Real-time Detection and Emergency Response System")
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_magnitude = df['magnitude'].max()
                st.metric("Highest Magnitude", f"{max_magnitude:.1f}")
                
            with col2:
                total_events = len(df)
                st.metric("Total Events", total_events)
                
            with col3:
                affected_states = df['state'].nunique()
                st.metric("Affected States", affected_states)
            
            display_map(df)
            
            # Recent alerts
            st.subheader("⚠️ Recent Alerts")
            df_recent = df.sort_values(by='datetime', ascending=False).head(5)
            
            for _, row in df_recent.iterrows():
                severity, color = calculate_severity_level(row['magnitude'])
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background-color: rgba({255 if color == 'green' else 0}, 
                                                      {255 if color in ['green', 'orange'] else 0}, 
                                                      {0}, 0.2); 
                                padding: 10px; border-radius: 5px;'>
                        <h3>{row['location']} - Magnitude {row['magnitude']}</h3>
                        <p>📆 {row['datetime'].strftime('%Y-%m-%d %H:%M')}<br>
                        📍 {row['state']}<br>
                        ⚠️ Severity: <span style='color: {color};'><strong>{severity}</strong></span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if is_authenticated:
                        if st.button(f"Manage Response {row['location']}"):
                            st.session_state.selected_event = {
                                'location': row['location'],
                                'state': row['state'],
                                'magnitude': row['magnitude'],
                                'datetime': row['datetime']
                            }
                            st.session_state.page = "emergency_planning"
                            st.experimental_rerun()
        else:
            st.warning("No earthquake data available in the selected time range.")
    
    # Earthquake data page
    elif st.session_state.page == "earthquake_data":
        st.title("📊 Earthquake Data Analysis")
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Filter Data")
                min_mag, max_mag = st.slider("Magnitude Range", 0.0, 10.0, (3.0, 7.0), 0.1)
                filtered_df = df[(df['magnitude'] >= min_mag) & (df['magnitude'] <= max_mag)]
            
            with col2:
                st.subheader("Select States")
                available_states = df['state'].unique()
                selected_states = st.multiselect("States", available_states, default=available_states)
                if selected_states:
                    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
            
            if not filtered_df.empty:
                st.subheader("Filtered Earthquake Data")
                st.dataframe(filtered_df[['datetime', 'location', 'state', 'latitude', 'longitude', 'magnitude']])
                
                # Display statistics
                st.subheader("📈 Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Magnitude", f"{filtered_df['magnitude'].mean():.2f}")
                
                with col2:
                    st.metric("Max Magnitude", f"{filtered_df['magnitude'].max():.2f}")
                
                with col3:
                    st.metric("Total Events", len(filtered_df))
                
                # Show map with filtered data
                display_map(filtered_df)
            else:
                st.warning("No data available with the selected filters.")
        else:
            st.warning("No earthquake data available.")
    
    # Resource management page
    elif st.session_state.page == "resource_management":
        st.title("📦 Resource Management")
        
        if not is_authenticated:
            st.warning("You need to log in to access this section.")
            return
        
        tab1, tab2, tab3 = st.tabs(["📊 Inventory Status", "🚚 Logistics Resources", "🛒 Resource Allocation"])
        
        with tab1:
            st.subheader("Current Inventory Status")
            inventory_df = load_inventory_data()
            
            if not inventory_df.empty:
                # Filter by region and item type
                regions = inventory_df['region'].unique()
                selected_region = st.selectbox("Select Region", regions)
                
                item_types = inventory_df['item_type'].unique()
                selected_type = st.multiselect("Select Item Type", item_types, default=item_types[0])
                
                filtered_inventory = inventory_df[
                    (inventory_df['region'] == selected_region) & 
                    (inventory_df['item_type'].isin(selected_type))
                ]
                
                if not filtered_inventory.empty:
                    # Show inventory status with color coding
                    for _, row in filtered_inventory.iterrows():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        status_color = "green" if row['status'] == "Adequate" else "red"
                        
                        with col1:
                            st.markdown(f"**{row['item_name']}** ({row['item_type']})")
                        
                        with col2:
                            st.markdown(f"Qty: **{row['quantity']} {row['unit']}**")
                        
                        with col3:
                            expiry = row['expiry_date'].strftime('%Y-%m-%d') if isinstance(row['expiry_date'], datetime) else row['expiry_date']
                            st.markdown(f"Expires: {expiry}")
                        
                        with col4:
                            st.markdown(f"<span style='color:{status_color};'>{row['status']}</span>", unsafe_allow_html=True)
                    
                    # Show summary by item type
                    st.subheader("Inventory Summary")
                    summary = filtered_inventory.groupby('item_type').agg({
                        'quantity': 'sum',
                        'reorder_level': 'sum',
                        'optimal_level': 'sum'
                    }).reset_index()
                    
                    for _, row in summary.iterrows():
                        quantity = row['quantity']
                        reorder = row['reorder_level']
                        optimal = row['optimal_level']
                        
                        # Calculate percentage of optimal level
                        percentage = min(100, int((quantity / optimal) * 100))
                        
                        # Determine color based on stock level
                        if quantity < reorder:
                            color = "red"
                            status = "Low"
                        elif quantity < optimal:
                            color = "orange"
                            status = "Moderate"
                        else:
                            color = "green"
                            status = "Optimal"
                        
                        st.markdown(f"### {row['item_type']}")
                        st.progress(percentage / 100)
                        st.markdown(f"<span style='color:{color};'>{status}: {quantity} units ({percentage}% of optimal)</span>", unsafe_allow_html=True)
                else:
                    st.warning("No inventory data available for the selected filters.")
            else:
                st.warning("No inventory data available.")
        
        with tab2:
            st.subheader("Logistics Resources by Region")
            logistics_df = load_logistics_resources()
            
            if not logistics_df.empty:
                selected_region = st.selectbox("Select Region", logistics_df['region'].unique(), key="logistics_region")
                
                region_data = logistics_df[logistics_df['region'] == selected_region].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Shelter Centers", region_data['shelter_centers'])
                    st.metric("Ambulances", region_data['ambulances'])
                    st.metric("Relief Supplies (tons)", region_data['relief_supplies_tons'])
                
                with col2:
                    st.metric("Medical Teams", region_data['medical_teams'])
                    st.metric("Drones Available", region_data['drones_available'])
                    st.metric("Autonomous Vehicles", region_data['autonomous_vehicles'])
                
                # Resource editing (for authenticated users)
                st.subheader("Update Resources")
                
                resource_to_update = st.selectbox(
                    "Select Resource to Update",
                    ["shelter_centers", "ambulances", "relief_supplies_tons", "medical_teams", "drones_available", "autonomous_vehicles"]
                )
                
                new_value = st.number_input(
                    f"New value for {resource_to_update}",
                    min_value=0,
                    value=int(region_data[resource_to_update])
                )
                
                if st.button("Update Resource"):
                    success = update_logistics_resources(selected_region, resource_to_update, new_value)
                    if success:
                        st.success(f"✅ {resource_to_update} updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Failed to update resource.")
            else:
                st.warning("No logistics data available.")
        
        with tab3:
            st.subheader("Resource Allocation Simulator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                sim_region = st.selectbox("Select Region", df['state'].unique() if not df.empty else ["No data"])
            
            with col2:
                sim_magnitude = st.slider("Earthquake Magnitude", 3.0, 9.0, 5.5, 0.1)
            
            if st.button("Simulate Resource Allocation"):
                # Get AI-enhanced allocation recommendation
                allocation = get_resource_allocation(sim_region, sim_magnitude)
                
                if allocation:
                    severity_level, color = calculate_severity_level(sim_magnitude)
                    
                    st.markdown(f"### Resource Allocation for Magnitude {sim_magnitude} Earthquake in {sim_region}")
                    st.markdown(f"Severity Level: <span style='color:{color};'>{severity_level}</span>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Shelter Centers", allocation['shelter_centers'])
                        st.metric("Ambulances", allocation['ambulances'])
                        st.metric("Medical Teams", allocation['medical_teams'])
                    
                    with col2:
                        st.metric("Food Required (kg)", allocation['food_required_kg'])
                        st.metric("Water Required (L)", allocation['water_required_liters'])
                        st.metric("Medicine Units", allocation['medicine_units_required'])
                    
                    with col3:
                        st.metric("Shelter Kits", allocation['shelter_kits_required'])
                        st.metric("Drones to Deploy", allocation['drones_to_deploy'])
                        if 'route_distance_km' in allocation:
                            st.metric("Resource Delivery Distance", f"{allocation['route_distance_km']} km")
                    
                    # Show inventory status
                    st.subheader("Inventory Status for Required Resources")
                    
                    if allocation['inventory_status']:
                        for item_type, status in allocation['inventory_status'].items():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{item_type}**")
                                st.progress(status['sufficiency_pct'] / 100)
                            
                            with col2:
                                st.markdown(f"Available: **{status['available']}**")
                                st.markdown(f"Needed: **{status['needed']}**")
                            
                            with col3:
                                status_color = "green" if status['status'] == "Sufficient" else "red"
                                st.markdown(f"<span style='color:{status_color};'>{status['status']}</span>", unsafe_allow_html=True)
                                st.markdown(f"**{status['sufficiency_pct']}%** sufficient")
                    
                    # Show resource gaps
                    if allocation['resource_gaps']:
                        st.subheader("Resource Gaps")
                        for item_type, deficit in allocation['resource_gaps'].items():
                            st.warning(f"Insufficient {item_type}: Deficit of {deficit} units")
                    
                    # Show drone deployment plan
                    st.subheader("AI-Optimized Drone Deployment Plan")
                    
                    for drone_type, drones in allocation['drone_deployment'].items():
                        if drones:
                            st.markdown(f"**{drone_type.title()} Drones:**")
                            for drone in drones:
                                st.markdown(f"- **{drone['drone_id']}**: {drone['mission']}")
                else:
                    st.warning("Could not generate resource allocation. Please check your inputs.")
    
    # Emergency planning page
    elif st.session_state.page == "emergency_planning":
        st.title("🚨 Emergency Response Planning")
        
        if not is_authenticated:
            st.warning("You need to log in to access this section.")
            return
        
        selected_event = None
        if "selected_event" in st.session_state:
            selected_event = st.session_state.selected_event
        
        if selected_event or not df.empty:
            if not selected_event:
                # Let user select an event to plan for
                st.subheader("Select Event")
                events = [(f"{row['location']} - Mag {row['magnitude']} - {row['datetime'].strftime('%Y-%m-%d')}", 
                          {'location': row['location'], 'state': row['state'], 'magnitude': row['magnitude'], 'datetime': row['datetime']})
                          for _, row in df.sort_values(by='datetime', ascending=False).iterrows()]
                
                selected = st.selectbox("Select Event for Response Planning", 
                                      [e[0] for e in events], 
                                      index=0)
                
                selected_event = next((e[1] for e in events if e[0] == selected), None)
            
            if selected_event:
                st.markdown(f"### Planning Response for: {selected_event['location']}")
                st.markdown(f"**Magnitude:** {selected_event['magnitude']}  |  **Date:** {selected_event['datetime'].strftime('%Y-%m-%d %H:%M')}  |  **Region:** {selected_event['state']}")
                
                # Get recommended resource allocation
                allocation = get_resource_allocation(selected_event['state'], selected_event['magnitude'])
                
                if allocation:
                    tab1, tab2, tab3 = st.tabs(["📋 Response Plan", "🚁 Resource Deployment", "📱 Communication"])
                    
                    with tab1:
                        st.subheader("AI-Generated Response Plan")
                        
                        severity_level, _ = calculate_severity_level(selected_event['magnitude'])
                        
                        st.markdown(f"""
                        #### Immediate Actions:
                        1. **Activate Emergency Operations Center** for {selected_event['state']}
                        2. **Deploy {allocation['medical_teams']} medical teams** to {selected_event['location']}
                        3. **Mobilize {allocation['ambulances']} ambulances** for casualty evacuation
                        4. **Activate {allocation['shelter_centers']} shelter centers** for displaced populations
                        5. **Deploy {allocation['drones_to_deploy']} drones** for rapid assessment and communication
                        
                        #### Key Objectives:
                        - Conduct search and rescue operations
                        - Provide immediate medical assistance
                        - Establish emergency shelters
                        - Restore essential services (water, electricity)
                        - Maintain communication channels
                        """)
                        
                        # Timeline based on severity
                        st.subheader("Response Timeline")
                        
                        timeline_data = {
                            "Phase": ["Immediate (0-6hrs)", "Short-term (6-24hrs)", "Medium-term (1-7 days)", "Long-term (>7 days)"],
                        }
                        
                        if severity_level == "Low":
                            timeline_data["Actions"] = [
                                "Initial assessment, alert authorities",
                                "Monitor situation, limited resource deployment if needed",
                                "Return to normal operations",
                                "Post-event analysis"
                            ]
                        elif severity_level == "Moderate":
                            timeline_data["Actions"] = [
                                "Deploy assessment teams, activate EOC, initial medical response",
                                "Set up emergency shelters, deploy all assigned resources",
                                "Damage assessment, begin repair of critical infrastructure",
                                "Rehabilitation of affected areas, demobilize resources"
                            ]
                        else:  # High or Extreme
                            timeline_data["Actions"] = [
                                "Full emergency activation, search & rescue, triage medical response, deploy all assigned resources",
                                "Expand shelter operations, request additional resources from neighboring regions, establish field hospitals",
                                "Continue rescue operations, begin infrastructure repairs, address secondary hazards",
                                "Begin reconstruction planning, maintain shelters until safe return possible"
                            ]
                        
                        timeline_df = pd.DataFrame(timeline_data)
                        st.table(timeline_df)
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Activate Emergency Response"):
                                st.success("✅ Emergency response activated! Notifications sent to response teams.")
                        
                        with col2:
                            if st.button("Request Additional Resources"):
                                st.info("📦 Resource request submitted to neighboring regions.")
                        
                        with col3:
                            if st.button("Generate Full Report"):
                                st.info("📄 Generating comprehensive response report...")
                    
                    with tab2:
                        st.subheader("Resource Deployment Strategy")
                        
                        # Display inventory status and deficiencies
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Resource Requirements")
                            st.markdown(f"- **Food:** {allocation['food_required_kg']} kg")
                            st.markdown(f"- **Water:** {allocation['water_required_liters']} liters")
                            st.markdown(f"- **Medicine:** {allocation['medicine_units_required']} units")
                            st.markdown(f"- **Shelter Kits:** {allocation['shelter_kits_required']} kits")
                        
                        with col2:
                            st.markdown("#### Available Resources")
                            
                            for item_type, status in allocation['inventory_status'].items():
                                status_color = "green" if status['status'] == "Sufficient" else "red"
                                st.markdown(f"- **{item_type}:** {status['available']} units <span style='color:{status_color};'>({status['sufficiency_pct']}%)</span>", unsafe_allow_html=True)
                        
                        # Display resource gaps and procurement plan
                        if allocation['resource_gaps']:
                            st.subheader("Resource Gaps and Procurement Plan")
                            
                            for item_type, deficit in allocation['resource_gaps'].items():
                                st.warning(f"⚠️ Gap: {deficit} units of {item_type} needed")
                            
                            # Let user create procurement requests
                            gap_item = st.selectbox("Select Item to Procure", list(allocation['resource_gaps'].keys()))
                            quantity = st.number_input("Quantity", min_value=1, value=allocation['resource_gaps'][gap_item])
                            
                            if st.button("Create Procurement Request"):
                                st.success(f"✅ Procurement request created for {quantity} units of {gap_item}")
                        
                        # Drone deployment plan
                        st.subheader("Drone Deployment Plan")
                        
                        for drone_type, drones in allocation['drone_deployment'].items():
                            if drones:
                                for drone in drones:
                                    col1, col2, col3 = st.columns([2, 2, 1])
                                    
                                    with col1:
                                        st.markdown(f"**{drone['drone_id']}** ({drone_type.title()})")
                                    
                                    with col2:
                                        st.markdown(f"{drone['mission']}")
                                    
                                    with col3:
                                        st.button(f"Deploy {drone['drone_id']}", key=f"deploy_{drone['drone_id']}")
                        
                        # Optimal route
                        if 'optimal_route' in allocation:
                            st.subheader("Optimal Resource Delivery Route")
                            st.markdown(f"**Total Distance:** {allocation['route_distance_km']} km")
                            st.markdown("**Route:** " + " → ".join(allocation['optimal_route']))
                    
                    with tab3:
                        st.subheader("Emergency Communications")
                        
                        tab_email, tab_sms, tab_alerts = st.tabs(["📧 Email Alerts", "📱 SMS Notifications", "📢 Public Alerts"])
                        
                        with tab_email:
                            st.markdown("#### Send Email Alerts to Affected Region")
                            
                            emails = load_user_emails(selected_event['state'])
                            
                            if emails:
                                st.markdown(f"**{len(emails)} recipients** in affected area")
                                
                                subject = st.text_input("Email Subject", f"ALERT: Earthquake in {selected_event['location']}")
                                
                                if st.button("Send Email Alerts"):
                                    success = send_email(subject, selected_event['location'], emails)
                                    if success:
                                        st.success(f"✅ Email alerts sent to {len(emails)} recipients!")
                                    else:
                                        st.error("❌ Failed to send email alerts.")
                            else:
                                st.warning("No email recipients found for the selected region.")
                        
                        with tab_sms:
                            st.markdown("#### Send SMS Alerts")
                            
                            # Get emergency contact from logistics data
                            logistics_df = load_logistics_resources()
                            emergency_contact = None
                            
                            if not logistics_df.empty:
                                region_data = logistics_df[logistics_df['region'] == selected_event['state']]
                                if not region_data.empty:
                                    emergency_contact = region_data.iloc[0]['emergency_contacts']
                            
                            if emergency_contact:
                                st.markdown(f"**Emergency Contact:** {emergency_contact}")
                                
                                # Prepare shelter and medical info
                                shelter_info = f"{allocation['shelter_centers']} centers activated" if allocation else "Local shelters"
                                medical_info = f"{allocation['medical_teams']} teams deployed" if allocation else "Local hospitals"
                                
                                logistics_info = {
                                    'nearest_shelter': shelter_info,
                                    'medical_contact': medical_info
                                }
                                
                                if st.button("Send SMS Alert"):
                                    message_id = send_sms_alert(emergency_contact, selected_event['location'], logistics_info)
                                    if "Error" not in message_id:
                                        st.success(f"✅ SMS alert sent! Message ID: {message_id}")
                                    else:
                                        st.error(f"❌ {message_id}")
                            else:
                                st.warning("No emergency contact found for the selected region.")
                                phone = st.text_input("Enter Phone Number (with country code)")
                                
                                if st.button("Send SMS Alert") and phone:
                                    message_id = send_sms_alert(phone, selected_event['location'])
                                    if "Error" not in message_id:
                                        st.success(f"✅ SMS alert sent! Message ID: {message_id}")
                                    else:
                                        st.error(f"❌ {message_id}")
                        
                        with tab_alerts:
                            st.markdown("#### Public Alert Messages")
                            
                            alert_types = ["Website", "Social Media", "Emergency Broadcast System", "Mobile App Notification"]
                            selected_alerts = st.multiselect("Select Alert Channels", alert_types, default=alert_types)
                            
                            alert_message = st.text_area(
                                "Alert Message",
                                f"EARTHQUAKE ALERT: A magnitude {selected_event['magnitude']} earthquake has affected {selected_event['location']}. " +
                                f"Take immediate safety precautions. Drop, cover, and hold on. " +
                                f"Emergency services have been activated. More information will follow."
                            )
                            
                            if st.button("Broadcast Public Alerts"):
                                if selected_alerts:
                                    st.success(f"✅ Public alerts broadcast through {', '.join(selected_alerts)}!")
                                else:
                                    st.warning("Please select at least one alert channel.")
                else:
                    st.warning("Could not generate resource allocation for this event.")
        else:
            st.warning("No earthquake data available.")
    
    # Communication center
    elif st.session_state.page == "communication_center":
        st.title("📱 Communication Center")
        
        if not is_authenticated:
            st.warning("You need to log in to access this section.")
            return
        
        tab1, tab2 = st.tabs(["📧 Email Management", "📱 SMS Management"])
        
        with tab1:
            st.subheader("Email Alert System")
            
            # Email template editor
            st.markdown("#### Email Template Editor")
            
            email_subject = st.text_input("Email Subject", "ALERT: Earthquake Detected in Your Area")
            email_body = st.text_area("Email Body", 
                                    "🚨 Earthquake Alert: [LOCATION] is affected. Take necessary precautions!\n\n" +
                                    "🔹 Drop, Cover, and Hold On.\n" +
                                    "🔹 Move to an open area if outside.\n" +
                                    "🔹 Stay away from windows and heavy objects.\n" +
                                    "🔹 Keep emergency contacts and supplies ready.\n" +
                                    "🔹 Follow official updates and stay safe!\n\n" +
                                    "Stay Safe,\nDisaster Alert System", height=200)
            
            if st.button("Save Template"):
                st.success("✅ Email template saved successfully!")
            
            # Email recipient management
            st.markdown("#### Email Recipients")
            
            try:
                emails_df = pd.read_excel(EMAIL_FILE_PATH, engine='openpyxl')
                
                if "email" in emails_df.columns and "Location" in emails_df.columns:
                    # Display email recipients by location
                    locations = emails_df['Location'].unique()
                    selected_location = st.selectbox("Filter by Location", ['All'] + list(locations))
                    
                    if selected_location == 'All':
                        filtered_emails = emails_df
                    else:
                        filtered_emails = emails_df[emails_df['Location'] == selected_location]
                    
                    st.dataframe(filtered_emails)
                    
                    # Add new recipient
                    st.subheader("Add New Recipient")
                    new_email = st.text_input("Email Address")
                    new_location = st.text_input("Location")
                    
                    if st.button("Add Recipient") and new_email and new_location:
                        success = add_email_recipient(new_email, new_location)
                        if success:
                            st.success(f"✅ Added {new_email} to recipients!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Failed to add recipient.")
                else:
                    st.warning("Email data file has incorrect format.")
            except Exception as e:
                st.error(f"Error loading email data: {e}")
        
        with tab2:
            st.subheader("SMS Alert System")
            
            # SMS template editor
            st.markdown("#### SMS Template Editor")
            
            sms_template = st.text_area("SMS Message Template", 
                                      "ALERT: Earthquake detected in [LOCATION]. Magnitude [MAGNITUDE]. Take immediate safety measures. More info at disasteralert.gov/eq", 
                                      height=100)
            
            if st.button("Save SMS Template"):
                st.success("✅ SMS template saved successfully!")
            
            # SMS contact management
            st.markdown("#### SMS Contacts")
            
            try:
                sms_df = pd.read_excel(SMS_FILE_PATH, engine='openpyxl')
                
                if "phone" in sms_df.columns and "region" in sms_df.columns:
                    regions = sms_df['region'].unique()
                    selected_region = st.selectbox("Filter by Region", ['All'] + list(regions), key="sms_region")
                    
                    if selected_region == 'All':
                        filtered_sms = sms_df
                    else:
                        filtered_sms = sms_df[sms_df['region'] == selected_region]
                    
                    st.dataframe(filtered_sms)
                    
                    # Add new SMS contact
                    st.subheader("Add New Contact")
                    new_phone = st.text_input("Phone Number (with country code)")
                    new_region = st.text_input("Region")
                    
                    if st.button("Add Contact") and new_phone and new_region:
                        success = add_sms_contact(new_phone, new_region)
                        if success:
                            st.success(f"✅ Added {new_phone} to contacts!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Failed to add contact.")
                else:
                    st.warning("SMS data file has incorrect format.")
            except Exception as e:
                st.error(f"Error loading SMS data: {e}")
    
    # Analytics page
    elif st.session_state.page == "analytics":
        st.title("📊 Earthquake Analytics")
        
        if not df.empty:
            tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "🗺️ Geographic Analysis", "📉 Predictive Analytics"])
            
            with tab1:
                st.subheader("Earthquake Trend Analysis")
                
                # Time filter
                time_period = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"])
                
                # Filter data based on time period
                filtered_df = filter_by_time_period(df, time_period)
                
                if not filtered_df.empty:
                    # Daily earthquake frequency
                    st.markdown("#### Daily Earthquake Frequency")
                    
                    daily_counts = filtered_df.resample('D', on='datetime').size().reset_index(name='count')
                    
                    fig = px.line(daily_counts, x='datetime', y='count', 
                                title=f"Daily Earthquake Frequency ({time_period})")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Magnitude distribution
                    st.markdown("#### Magnitude Distribution")
                    
                    fig = px.histogram(filtered_df, x='magnitude', nbins=20,
                                     title=f"Magnitude Distribution ({time_period})")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top affected states
                    st.markdown("#### Most Affected States")
                    
                    state_counts = filtered_df['state'].value_counts().reset_index()
                    state_counts.columns = ['state', 'count']
                    
                    fig = px.bar(state_counts.head(10), x='state', y='count',
                               title=f"Top 10 Affected States ({time_period})")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No earthquake data available for {time_period}")
            
            with tab2:
                st.subheader("Geographic Analysis")
                
                # Choropleth map of earthquake frequency by state
                st.markdown("#### Earthquake Frequency by State")
                
                state_counts = df['state'].value_counts().reset_index()
                state_counts.columns = ['state', 'count']
                
                # Use plotly for choropleth map
                fig = px.choropleth(state_counts, 
                                  locations='state', 
                                  locationmode='USA-states',
                                  color='count',
                                  color_continuous_scale=px.colors.sequential.Reds,
                                  scope='usa',
                                  title='Earthquake Frequency by State')
                st.plotly_chart(fig, use_container_width=True)
                
                # Heatmap of earthquake intensity
                st.markdown("#### Earthquake Intensity Heatmap")
                
                fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='magnitude', radius=10,
                                      center=dict(lat=37.0902, lon=-95.7129), zoom=3,
                                      mapbox_style="carto-positron",
                                      title="Earthquake Intensity Heatmap")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("AI-Enhanced Predictive Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    prediction_state = st.selectbox("Select State for Prediction", df['state'].unique())
                
                with col2:
                    prediction_days = st.slider("Prediction Window (Days)", 7, 90, 30)
                
                if st.button("Generate Prediction"):
                    with st.spinner("AI is analyzing patterns and generating predictions..."):
                        # Simulate AI prediction generation
                        time.sleep(2)
                        
                        # Generate prediction data (in a real app, this would come from an ML model)
                        prediction_result = generate_earthquake_prediction(df, prediction_state, prediction_days)
                        
                        if prediction_result:
                            # Display prediction chart
                            st.markdown(f"#### Earthquake Probability Forecast for {prediction_state}")
                            st.markdown(f"**Prediction for next {prediction_days} days**")
                            
                            fig = px.line(prediction_result, x='date', y='probability',
                                        title=f"Earthquake Probability Forecast for {prediction_state}")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Risk assessment
                            risk_level = prediction_result['risk_level']
                            risk_color = "green" if risk_level == "Low" else "orange" if risk_level == "Moderate" else "red"
                            
                            st.markdown(f"#### Risk Assessment")
                            st.markdown(f"Overall Risk Level: <span style='color:{risk_color};font-weight:bold;'>{risk_level}</span>", 
                                      unsafe_allow_html=True)
                            
                            # Risk factors
                            st.markdown("**Key Risk Factors:**")
                            for factor in prediction_result['risk_factors']:
                                st.markdown(f"- {factor}")
                            
                            # Recommendations
                            st.markdown("**Recommended Actions:**")
                            for action in prediction_result['recommendations']:
                                st.markdown(f"- {action}")
                        else:
                            st.warning("Could not generate prediction. Not enough historical data.")
        else:
            st.warning("No earthquake data available for analysis.")


if __name__ == "__main__":
    main()