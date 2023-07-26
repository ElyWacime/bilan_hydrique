import requests
import json

configuration_data = {
    "Texture_du_sol": "sample_value",
    "Densité_apparente_des_motes": 1.0,
    "Densité_apparente_du_sol": 1.0,
    "Profondeur_des_racines": 1.0,
    "Pierrosité": 1.0,
    "Latitude": 60.456,
    "Longitude": 40.012,
    "Hauteur_de_linstallation": 1.0,
    "Taux_de_couverture": 1.0,
    "Plant_name": "Pomme de terre",
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "Plante_a_50_de_levée": ["2023-01-05", "2023-01-10"],
    "de_50_de_levée_a_50_recouvrement": ["2023-01-11", "2023-01-15"],
    "de_50_recouvrement_a_recouvrement_total": ["2023-01-16", "2023-01-20"],
    "recvroument_total_plus_30_jours": ["2023-01-21", "2023-01-25"],
    "recvroument_total_plus_30_jours_a_debut_saison": ["2023-01-26", "2023-01-27"],
    "debut_saison_a_maturite": ["2023-01-28", "2023-01-31"]
}

api_endpoint = 'http://82.165.34.79/bilan_hydrique'

response = requests.post(api_endpoint, json=configuration_data)

if response.status_code == 200:

    result = response.json()
    print(result)  
else:
    print("Error occurred. Status code:", response.status_code)
    print(response.text) 
