import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Flask, request, jsonify, Response
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from pydantic import BaseModel, Field, validator
from typing import Optional, Tuple

app = Flask(__name__)

if not app.debug:
    file_handler = RotatingFileHandler('flask.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


class Configuration(BaseModel):

    # Input values:
    Texture_du_sol : str
    Densité_apparente_des_motes : float
    Densité_apparente_du_sol : float
    Profondeur_des_racines : float
    Pierrosité : float
    Latitude : float
    Longitude : float
    Hauteur_de_linstallation : float
    Taux_de_couverture : float
    Plant_name : str
    start_date : str
    end_date : str

    # input dates for pomme de terre:
    Plante_a_50_de_levée: Optional[Tuple] = None
    de_50_de_levée_a_50_recouvrement: Optional[Tuple] = None
    de_50_recouvrement_a_recouvrement_total: Optional[Tuple] = None
    recvroument_total_plus_30_jours: Optional[Tuple] = None
    recvroument_total_plus_30_jours_a_debut_saison: Optional[Tuple] = None
    debut_saison_a_maturite: Optional[Tuple] = None

    # input date for courgette 
    plantation_a_fleuraison: Optional[Tuple] = None
    fleuraison_a_mi_recolte: Optional[Tuple] = None
    mi_recolte_fin_recolte: Optional[Tuple] = None

    # input date for poireaux
    reprise_a_recolte: Optional[Tuple] = None

    # input date for carotte
    de_0_a_6_semaine_apres_semis: Optional[Tuple] = None
    de_6_semaine_au_stade: Optional[Tuple] = None
    du_stade_a_recolte: Optional[Tuple] = None


@app.route('/bilan_hydrique', methods=['POST'])
def bilan_hydrique():
    
    configuration_data = request.get_json()
    configuration = Configuration(**configuration_data)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": configuration.Latitude,
        "longitude": configuration.Longitude,
        "start_date": configuration.start_date,
        "end_date": configuration.end_date,
        "hourly": "temperature_2m,precipitation,direct_radiation,diffuse_radiation",
        "timezone": "auto",
        "min": "2015-05-20",
        "max": "2015-08-23"
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
            "Courgette" : [
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.plantation_a_fleuraison)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.plantation_a_fleuraison)[1], date_format),
                    "KC" : 0.5
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.fleuraison_a_mi_recolte)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.fleuraison_a_mi_recolte)[1], date_format),
                    "KC" : 1
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.mi_recolte_fin_recolte)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.mi_recolte_fin_recolte)[1], date_format),
                    "KC" : 0.7
                }
            ],
            "Poireau" : [
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.reprise_a_recolte)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.reprise_a_recolte)[1], date_format),
                    "KC" : 0.7
                }
            ],
            "Carotte" : [
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.de_0_a_6_semaine_apres_semis)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.de_0_a_6_semaine_apres_semis)[1], date_format),
                    "KC" : 0.4
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.de_6_semaine_au_stade)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.de_6_semaine_au_stade)[1], date_format),
                    "KC" : 0.7
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.du_stade_a_recolte)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.du_stade_a_recolte)[1], date_format),
                    "KC" : 1
                }
            ],
            "Pomme de terre" : [
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.Plante_a_50_de_levée)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.Plante_a_50_de_levée)[1], date_format),
                    "KC" : 0.4
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.de_50_de_levée_a_50_recouvrement)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.de_50_de_levée_a_50_recouvrement)[1], date_format),
                    "KC" : 0.7
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.de_50_recouvrement_a_recouvrement_total)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.de_50_recouvrement_a_recouvrement_total)[1], date_format),
                    "KC" : 0.9
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.recvroument_total_plus_30_jours)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.recvroument_total_plus_30_jours)[1], date_format),
                    "KC" : 1.05
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.recvroument_total_plus_30_jours_a_debut_saison)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.recvroument_total_plus_30_jours_a_debut_saison)[1], date_format),
                    "KC" : 1
                },
                {
                    "start_date" : safely_parse_date(safely_parse_None(configuration.debut_saison_a_maturite)[0], date_format),
                    "end_date" : safely_parse_date(safely_parse_None(configuration.debut_saison_a_maturite)[1], date_format),
                    "KC" : 0.8
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
    daily_data['sum_radiation'] = daily_data[['direct_radiation', 'diffuse_radiation']].sum(axis=1)

    # Add a new column for the sum_radiation_cal/j_cm²
    daily_data['sum_radiation_cal/j_cm²'] = daily_data['sum_radiation'] * 0.000023885*3600

    # Add a new column for ETP
    daily_data['ETP'] = 0.013 * (daily_data['sum_radiation_cal/j_cm²'] + 50) * daily_data['temperature_2m'] / (daily_data['temperature_2m'] + 15)

    # Add KC values column
    daily_data['KC'] = daily_data.index.map(lambda x: calculate_KC_values(configuration.Plant_name, x.strftime('%Y-%m-%d')))

    # Add ETR values column
    daily_data['ETR'] = daily_data['ETP'] * daily_data['KC']

    # Add lg_mod Values column
    perte_d_ensoleillement = configuration.Taux_de_couverture * 0.8 - (configuration.Hauteur_de_linstallation - 3.5) * 2.95
    daily_data['lg_mod'] = (1-perte_d_ensoleillement/100)*daily_data['sum_radiation_cal/j_cm²']

    # Add t_mod values column
    daily_data['t_mod'] = daily_data['temperature_2m']

    # Add ETP_PV column
    daily_data['ETP_PV'] = 0.013*(daily_data['lg_mod']+50)*daily_data['t_mod']/(daily_data['t_mod']+15)

    # Add ETR_PV column
    daily_data['ETR_PV'] = daily_data['ETP_PV'] * daily_data['KC']


    result = daily_data
    result_json = result.to_json(orient="records")  # You can use a different orientation if you want
    return Response(response=result_json, status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True, port=666)