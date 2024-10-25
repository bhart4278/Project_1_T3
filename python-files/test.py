import pandas as pd
import requests
import matplotlib.pyplot as plt
from config import API_KEY

# Load the dataset from the URL
url = "https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD"
ev_data = pd.read_csv(url)

# Inspect the dataset structure
print(ev_data.head())

# Your API key from AFDC
api_key = API_KEY

# Base URL for AFDC API
afdc_url = f"https://developer.nrel.gov/api/alt-fuel-stations/v1.json?api_key={api_key}&fuel_type=ELEC&state=WA"

# Fetch charging station data for Washington
response = requests.get(afdc_url)
charging_stations = response.json()

# Convert the response to a DataFrame for analysis
charging_stations_df = pd.json_normalize(charging_stations['fuel_stations'])
print(charging_stations_df.head())

# Merge on location data (assuming both datasets have a 'city' or 'county' column)
merged_data = pd.merge(ev_data, charging_stations_df, how='inner', left_on='City', right_on='city')

# Perform some basic analysis - e.g., number of EVs per charging station in each city
city_analysis = merged_data.groupby('City').agg({
    'VIN (1-10)': 'count',  # Assuming VIN column represents individual EVs
    'station_name': 'nunique'  # Assuming station_name represents unique charging stations
}).rename(columns={'VIN (1-10)': 'EV_Count', 'station_name': 'Charging_Stations'})

# Calculate the ratio of EVs to charging stations
city_analysis['EVs_per_Station'] = city_analysis['EV_Count'] / city_analysis['Charging_Stations']

# Display the result
print(city_analysis.sort_values('EVs_per_Station', ascending=False).head())


# Plot the top 10 cities with the highest EVs per charging station
city_analysis.nlargest(10, 'EVs_per_Station').plot(kind='bar', y='EVs_per_Station', legend=False)
plt.title('Top 10 Cities: EVs per Charging Station')
plt.xlabel('City')
plt.ylabel('EVs per Charging Station')
plt.show()
