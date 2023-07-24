import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Input values:
Texture_du_sol = str
Densité_apparente_des_motes = float
Densité_apparente_du_sol = float
Profondeur_des_racines = float
Pierrosité = float
Latitude = 48.8534
Longitude = 2.3488
Hauteur_de_linstallation = 4.0
Taux_de_couverture = 3.0
Plant_name = "Courgette"
start_date = "2015-05-20"
end_date = "2015-08-23"

# input dates for pomme de terre:
Plante_a_50_de_levée = ("2015-05-20", "2015-05-20")
de_50_de_levée_a_50_recouvrement = ("2015-05-20", "2015-05-20")
de_50_recouvrement_a_recouvrement_total = ("2015-05-20", "2015-05-20")
recvroument_total_plus_30_jours = ("2015-05-20", "2015-05-20")
recvroument_total_plus_30_jours_a_debut_saison = ("2015-05-20", "2015-05-20")
debut_saison_a_maturite = ("2015-05-20", "2015-05-20")

# input date for courgette 
plantation_a_fleuraison = ("2015-05-20", "2015-06-20")
fleuraison_a_mi_recolte = ("2015-06-20", "2015-07-20")
mi_recolte_fin_recolte = ("2015-07-20", "2015-08-23")

# input date for poireaux
reprise_a_recolte = ("2015-05-20", "2015-05-20")

# input date for carotte
de_0_a_6_semaine_apres_semis = ("2015-05-20", "2015-05-20")
de_6_semaine_au_stade = ("2015-05-20", "2015-05-20")
du_stade_a_recolte = ("2015-05-20", "2015-05-20")

# Define the URL and parameters
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": Latitude,
    "longitude": Longitude,
    "start_date": start_date,
    "end_date": end_date,
    "hourly": "temperature_2m,precipitation,direct_radiation,diffuse_radiation",
    "timezone": "auto",
    "min": "2015-05-20",
    "max": "2015-08-23"
}

# Make the API request
response = requests.get(url, params=params)

# Load the response into a Python dictionary
data = json.loads(response.text)

# Extract the lists from the 'hourly' dictionary
timestamps = data['hourly']['time']
temperature_2m = data['hourly']['temperature_2m']
precipitation = data['hourly']['precipitation']
direct_radiation = data['hourly']['direct_radiation']
diffuse_radiation = data['hourly']['diffuse_radiation']


combined_data = {}

# Iterate over the timestamps and add the data to the combined dictionary
for i, timestamp in enumerate(timestamps):
    combined_data[timestamp] = {
        'temperature_2m': temperature_2m[i],
        'precipitation': precipitation[i],
        'direct_radiation': direct_radiation[i],
        'diffuse_radiation': diffuse_radiation[i]
    }



# Convert the combined_data dictionary into a pandas DataFrame
df = pd.DataFrame.from_dict(combined_data, orient='index')

# Convert the index to datetime
df.index = pd.to_datetime(df.index)

# Calculate the daily mean of the 'temperature_2m', the daily sum of 'precipitation',
# and the daily sum of 'direct_radiation' and 'diffuse_radiation'
daily_data = df.resample('D').agg({
    'temperature_2m': 'mean',
    'precipitation': 'sum',
    'direct_radiation': 'sum',
    'diffuse_radiation': 'sum'
})


def calculate_KC_values(plant_name, date):
    date_format = "%Y-%m-%d"

    plants = {
        "Courgette" : [
            {
                "start_date" : datetime.strptime(plantation_a_fleuraison[0], date_format),
                "end_date" : datetime.strptime(plantation_a_fleuraison[1], date_format),
                "KC" : 0.5
            },
            {
                "start_date" : datetime.strptime(fleuraison_a_mi_recolte[0], date_format),
                "end_date" : datetime.strptime(fleuraison_a_mi_recolte[1], date_format),
                "KC" : 1
            },
            {
                "start_date" : datetime.strptime(mi_recolte_fin_recolte[0], date_format),
                "end_date" : datetime.strptime(mi_recolte_fin_recolte[1], date_format),
                "KC" : 0.7
            }
        ],
        "Poireau" : [
            {
                "start_date" : datetime.strptime(reprise_a_recolte[0], date_format),
                "end_date" : datetime.strptime(reprise_a_recolte[1], date_format),
                "KC" : 0.7
            }
        ],
        "Carotte" : [
            {
                "start_date" : datetime.strptime(de_0_a_6_semaine_apres_semis[0], date_format),
                "end_date" : datetime.strptime(de_0_a_6_semaine_apres_semis[1], date_format),
                "KC" : 0.4
            },
            {
                "start_date" : datetime.strptime(de_6_semaine_au_stade[0], date_format),
                "end_date" : datetime.strptime(de_6_semaine_au_stade[1], date_format),
                "KC" : 0.7
            },
            {
                "start_date" : datetime.strptime(du_stade_a_recolte[0], date_format),
                "end_date" : datetime.strptime(du_stade_a_recolte[1], date_format),
                "KC" : 1
            }
        ],
        "Pomme de terre" : [
            {
                "start_date" : datetime.strptime(Plante_a_50_de_levée[0], date_format),
                "end_date" : datetime.strptime(Plante_a_50_de_levée[1], date_format),
                "KC" : 0.4
            },
            {
                "start_date" : datetime.strptime(de_50_de_levée_a_50_recouvrement[0], date_format),
                "end_date" : datetime.strptime(de_50_de_levée_a_50_recouvrement[1], date_format),
                "KC" : 0.7
            },
            {
                "start_date" : datetime.strptime(de_50_recouvrement_a_recouvrement_total[0], date_format),
                "end_date" : datetime.strptime(de_50_recouvrement_a_recouvrement_total[1], date_format),
                "KC" : 0.9
            },
            {
                "start_date" : datetime.strptime(recvroument_total_plus_30_jours[0], date_format),
                "end_date" : datetime.strptime(recvroument_total_plus_30_jours[1], date_format),
                "KC" : 1.05
            },
            {
                "start_date" : datetime.strptime(recvroument_total_plus_30_jours_a_debut_saison[0], date_format),
                "end_date" : datetime.strptime(recvroument_total_plus_30_jours_a_debut_saison[1], date_format),
                "KC" : 1
            },
            {
                "start_date" : datetime.strptime(debut_saison_a_maturite[0], date_format),
                "end_date" : datetime.strptime(debut_saison_a_maturite[1], date_format),
                "KC" : 0.8
            }
        ]
    }

    if plant_name in plants:
        intervals = plants[plant_name]

        for interval in intervals:
            if interval["start_date"] <= datetime.strptime(date, date_format) <= interval["end_date"]:
                return interval["KC"]
    return None

# Create the ETR sheet

# Add a new column for the daily sum of 'direct_radiation' and 'diffuse_radiation'
daily_data['sum_radiation'] = daily_data[['direct_radiation', 'diffuse_radiation']].sum(axis=1)

# Add a new column for the sum_radiation_cal/j_cm²
daily_data['sum_radiation_cal/j_cm²'] = daily_data['sum_radiation'] * 0.000023885*3600

# Add a new column for ETP
daily_data['ETP'] = 0.013 * (daily_data['sum_radiation_cal/j_cm²'] + 50) * daily_data['temperature_2m'] / (daily_data['temperature_2m'] + 15)

# Add KC values column
daily_data['KC'] = daily_data.index.map(lambda x: calculate_KC_values(Plant_name, x.strftime('%Y-%m-%d')))

# Add ETR values column
daily_data['ETR'] = daily_data['ETP'] * daily_data['KC']

# Add lg_mod Values column
perte_d_ensoleillement = Taux_de_couverture * 0.8 - (Hauteur_de_linstallation - 3.5) * 2.95
daily_data['lg_mod'] = (1-perte_d_ensoleillement/100)*daily_data['sum_radiation_cal/j_cm²']

# Add t_mod values column
daily_data['t_mod'] = daily_data['temperature_2m']

# Add ETP_PV column
daily_data['ETP_PV'] = 0.013*(daily_data['lg_mod']+50)*daily_data['t_mod']/(daily_data['t_mod']+15)

# Add ETR_PV column
daily_data['ETR_PV'] = daily_data['ETP_PV'] * daily_data['KC']


# Create the bilan_hydrique sheet


print(daily_data)

# Save the the result into an Excel file
daily_data.to_excel("output.xlsx", engine='xlsxwriter')