import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils import teneurSol

# ************ Input values: **************
Texture_du_sol = "Limon sableux"
Densité_apparente_des_motes_Bool = True
Densité_apparente_des_motes = 1.68
Densité_apparente_du_sol = 1.68
Profondeur_des_racines = 50
Pierrosité = 6.3
Latitude = 48.8534
Longitude = 2.3488
Hauteur_de_linstallation = 2
Taux_de_couverture = 25
Plant_name = "Courgette"
start_date = "2015-05-20"
end_date = "2015-08-23"

# input dates for pomme de terre:
Plante_a_50_de_levée = ("2015-05-20", "2015-06-20")
de_50_de_levée_a_50_recouvrement = ("2015-06-20", "2015-07-20")
de_50_recouvrement_a_recouvrement_total = ("2015-07-20", "2015-07-30")
recvroument_total_plus_30_jours = ("2015-07-30", "2015-08-02")
recvroument_total_plus_30_jours_a_debut_saison = ("2015-08-02", "2015-08-10")
debut_saison_a_maturite = ("2015-08-10", "2015-08-23")

# input date for courgette
plantation_a_fleuraison = ("2015-05-20", "2015-06-20")
fleuraison_a_mi_recolte = ("2015-06-20", "2015-08-10")
mi_recolte_fin_recolte = ("2015-08-10", "2015-08-23")

# input date for poireaux
reprise_a_recolte = None

# input date for carotte
de_0_a_6_semaine_apres_semis = None
de_6_semaine_au_stade = None
du_stade_a_recolte = None

# ***********________**************

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": Latitude,
    "longitude": Longitude,
    "start_date": start_date,
    "end_date": end_date,
    "hourly": "temperature_2m,precipitation,direct_radiation,diffuse_radiation",
    "timezone": "auto",
    "min": start_date,
    "max": end_date
}

response = requests.get(url, params=params)

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


def safely_parse_date(date_string, date_format):
    return datetime.strptime(date_string, date_format) if date_string is not None else None


def safely_parse_None(my_tuple):
    return my_tuple if my_tuple is not None else ("2000-01-01", "2000-01-10")


def calculate_KC_values(plant_name, date):
    date_format = "%Y-%m-%d"

    plants = {
        "Courgette": [
            {
                "start_date": safely_parse_date(safely_parse_None(plantation_a_fleuraison)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(plantation_a_fleuraison)[1], date_format),
                "KC": 0.5
            },
            {
                "start_date": safely_parse_date(safely_parse_None(fleuraison_a_mi_recolte)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(fleuraison_a_mi_recolte)[1], date_format),
                "KC": 1
            },
            {
                "start_date": safely_parse_date(safely_parse_None(mi_recolte_fin_recolte)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(mi_recolte_fin_recolte)[1], date_format),
                "KC": 0.7
            }
        ],
        "Poireau": [
            {
                "start_date": safely_parse_date(safely_parse_None(reprise_a_recolte)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(reprise_a_recolte)[1], date_format),
                "KC": 0.7
            }
        ],
        "Carotte": [
            {
                "start_date": safely_parse_date(safely_parse_None(de_0_a_6_semaine_apres_semis)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(de_0_a_6_semaine_apres_semis)[1], date_format),
                "KC": 0.4
            },
            {
                "start_date": safely_parse_date(safely_parse_None(de_6_semaine_au_stade)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(de_6_semaine_au_stade)[1], date_format),
                "KC": 0.7
            },
            {
                "start_date": safely_parse_date(safely_parse_None(du_stade_a_recolte)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(du_stade_a_recolte)[1], date_format),
                "KC": 1
            }
        ],
        "Pomme de terre": [
            {
                "start_date": safely_parse_date(safely_parse_None(Plante_a_50_de_levée)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(Plante_a_50_de_levée)[1], date_format),
                "KC": 0.4
            },
            {
                "start_date": safely_parse_date(safely_parse_None(de_50_de_levée_a_50_recouvrement)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(de_50_de_levée_a_50_recouvrement)[1], date_format),
                "KC": 0.7
            },
            {
                "start_date": safely_parse_date(safely_parse_None(de_50_recouvrement_a_recouvrement_total)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(de_50_recouvrement_a_recouvrement_total)[1], date_format),
                "KC": 0.9
            },
            {
                "start_date": safely_parse_date(safely_parse_None(recvroument_total_plus_30_jours)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(recvroument_total_plus_30_jours)[1], date_format),
                "KC": 1.05
            },
            {
                "start_date": safely_parse_date(safely_parse_None(recvroument_total_plus_30_jours_a_debut_saison)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(recvroument_total_plus_30_jours_a_debut_saison)[1], date_format),
                "KC": 1
            },
            {
                "start_date": safely_parse_date(safely_parse_None(debut_saison_a_maturite)[0], date_format),
                "end_date": safely_parse_date(safely_parse_None(debut_saison_a_maturite)[1], date_format),
                "KC": 0.8
            }
        ]
    }

    if plant_name in plants:
        intervals = plants[plant_name]

        for interval in intervals:
            if interval["start_date"] <= safely_parse_date(date, date_format) <= interval["end_date"]:
                return interval["KC"]
    return None

# Create the ETR sheet


# Add a new column for the daily sum of 'direct_radiation' and 'diffuse_radiation'
daily_data['sum_radiation'] = daily_data[[
    'direct_radiation', 'diffuse_radiation']].sum(axis=1)

# Add a new column for the sum_radiation_cal/j_cm²
daily_data['sum_radiation_cal/j_cm²'] = daily_data['sum_radiation'] * \
    0.000023885*3600

# Add a new column for ETP
daily_data['ETP'] = 0.013 * (daily_data['sum_radiation_cal/j_cm²'] + 50) * \
    daily_data['temperature_2m'] / (daily_data['temperature_2m'] + 15)

# Add KC values column
daily_data['KC'] = daily_data.index.map(
    lambda x: calculate_KC_values(Plant_name, x.strftime('%Y-%m-%d')))

# Add ETR values column
daily_data['ETR'] = daily_data['ETP'] * daily_data['KC']

# Add lg_mod Values column
perte_d_ensoleillement = Taux_de_couverture * \
    0.8 - (Hauteur_de_linstallation - 3.5) * 2.95
daily_data['lg_mod'] = (1-perte_d_ensoleillement/100) * \
    daily_data['sum_radiation_cal/j_cm²']

# Add t_mod values column
daily_data['t_mod'] = daily_data['temperature_2m']

# Add ETP_PV column
daily_data['ETP_PV'] = 0.013*(daily_data['lg_mod']+50) * \
    daily_data['t_mod']/(daily_data['t_mod']+15)

# Add ETR_PV column
daily_data['ETR_PV'] = daily_data['ETP_PV'] * daily_data['KC']


# calcul Réserve Utile Maximum
if Densité_apparente_des_motes_Bool:
    for keys in teneurSol[Texture_du_sol]:
        if keys[0] <= Densité_apparente_des_motes <= keys[1]:
            absolute_values = []
            keys_float = []
            for key_float in teneurSol[Texture_du_sol][keys]:
                absolute_difference = abs(
                    key_float - Densité_apparente_des_motes)
                absolute_values.append(absolute_difference)
                keys_float.append(key_float)
            if absolute_values[0] < absolute_values[1]:
                Teneur_eau_sol = teneurSol[Texture_du_sol][keys][keys_float[0]]["RU"]
                Reserve_Utile_maximun = (
                    Teneur_eau_sol * 10000 / 1000) * Profondeur_des_racines * (1 - (Pierrosité / 100))
                Reserve_dificilement_utilisable = 1 / 3 * Reserve_Utile_maximun

            else:
                Teneur_eau_sol = teneurSol[Texture_du_sol][keys][keys_float[1]]["RU"]
                Reserve_Utile_maximun = (
                    Teneur_eau_sol * 10000 / 1000) * Profondeur_des_racines * (1 - (Pierrosité / 100))
                Reserve_dificilement_utilisable = 1 / 3 * Reserve_Utile_maximun

else:
    RU_list = []
    for keys in teneurSol[Texture_du_sol]:
        for key_float in teneurSol[Texture_du_sol][keys]:
            RU_list.append(teneurSol[Texture_du_sol][keys][key_float]["RU"])
    RU_mediane = sum(RU_list) / len(RU_list) + 1
    Reserve_Utile_maximun = (RU_mediane * 10000 / 1000) * \
        Profondeur_des_racines * (1 - (Pierrosité / 100))
    Reserve_dificilement_utilisable = 1 / 3 * Reserve_Utile_maximun


# add RDU column
daily_data["RDU"] = Reserve_dificilement_utilisable

# Add capacité au champ column
daily_data["capacité au champs"] = Reserve_Utile_maximun


# Add eau utile & irrigation columns & eau_utile_PV and irrigation_PV

# irrigation = 2 / 3 * D2 if (K2 + G2 - J2) < 2 / 3 * D2 else 0
# eau_utile_PV = calculate_value(P2, G2, Q2, O2, C2, D2)
# irrigation_PV = 2 / 3 * D3 if (P3 + G3 - O3) < 2 / 3 * D3 else 0

def calculate_eau_utile_value(K2, G2, L2, J2, C2, D2):
    value = K2 + G2 + L2 - J2

    if value >= C2:
        return C2
    elif value > D2:
        return value
    elif value > 0:
        return value * (K2 / D2)
    else:
        return value * (K2 / D2)


daily_data.loc[start_date,
               "eau_utile"] = daily_data.loc[start_date, "capacité au champs"]
daily_data.loc[start_date,
               "eau_utile_pv"] = daily_data.loc[start_date, "capacité au champs"]

for index, row in daily_data.iterrows():
    if daily_data.loc[index, "eau_utile"] == daily_data.loc[start_date, "capacité au champs"]:
        continue
    else:
        previous_date = (index - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
        daily_data.loc[previous_date, "irrigation"] = 2/3 * daily_data.loc[previous_date, "RDU"] if (
            daily_data.loc[previous_date, "eau_utile"] + daily_data.loc[previous_date, "precipitation"] - daily_data.loc[previous_date, "ETR"]) < 2/3 * daily_data.loc[previous_date, "RDU"] else 0
        daily_data.loc[index, "eau_utile"] = calculate_eau_utile_value(daily_data.loc[previous_date, "eau_utile"], daily_data.loc[previous_date, "precipitation"], daily_data.loc[
                                                                       previous_date, "irrigation"], daily_data.loc[previous_date, "ETR"], daily_data.loc[previous_date, "capacité au champs"], daily_data.loc[previous_date, "RDU"])

        daily_data.loc[previous_date, "irrigation_pv"] = 2/3 * daily_data.loc[previous_date, "RDU"] if (
            daily_data.loc[previous_date, "eau_utile_pv"] + daily_data.loc[previous_date, "precipitation"] - daily_data.loc[previous_date, "ETR_PV"]) < 2/3 * daily_data.loc[previous_date, "RDU"] else 0
        daily_data.loc[index, "eau_utile_pv"] = calculate_eau_utile_value(daily_data.loc[previous_date, "eau_utile_pv"], daily_data.loc[previous_date, "precipitation"], daily_data.loc[
                                                                          previous_date, "irrigation_pv"], daily_data.loc[previous_date, "ETR_PV"], daily_data.loc[previous_date, "capacité au champs"], daily_data.loc[previous_date, "RDU"])
daily_data.loc[end_date, "irrigation"] = 2/3 * daily_data.loc[end_date, "RDU"] if (
    daily_data.loc[end_date, "eau_utile"] + daily_data.loc[end_date, "precipitation"] - daily_data.loc[end_date, "ETR"]) < 2/3 * daily_data.loc[end_date, "RDU"] else 0
daily_data.loc[end_date, "irrigation_pv"] = 2/3 * daily_data.loc[end_date, "RDU"] if (
    daily_data.loc[end_date, "eau_utile_pv"] + daily_data.loc[end_date, "precipitation"] - daily_data.loc[end_date, "ETR_PV"]) < 2/3 * daily_data.loc[end_date, "RDU"] else 0

# print(Reserve_Utile_maximun, Reserve_dificilement_utilisable)

# Save the the result into an Excel file
daily_data.to_excel("output.xlsx", engine='xlsxwriter')
