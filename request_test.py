import requests
import json

configuration_data = {
    "Texture_du_sol": "Limon sableux",
    "Densité_apparente_des_motes_Bool": True,
    "Densité_apparente_des_motes": 1.68,
    "Densité_apparente_du_sol": 1.68,
    "Profondeur_des_racines": 50,
    "Pierrosité": 6.3,
    "Latitude": 60.456,
    "Longitude": 40.012,
    "Hauteur_de_linstallation": 2,
    "Taux_de_couverture": 25,
    "Plant_name": "Courgette",
    "start_date": "2015-05-20",
    "end_date": "2015-08-23",
    "plantation_a_fleuraison": ("2015-05-20", "2015-06-20"),
    "fleuraison_a_mi_recolte": ("2015-06-20", "2015-08-10"),
    "mi_recolte_fin_recolte": ("2015-08-10", "2015-08-23")
}

api_endpoint = 'http://82.165.34.79/bilan_hydrique'

response = requests.post(api_endpoint, json=configuration_data)

if response.status_code == 200:

    result = response.json()
    print(result)  
else:
    print("Error occurred. Status code:", response.status_code)
    print(response.text) 
