# Soft Geocoding for semi-structured data
# Using our own custom API service for Mexico
#
#  Created by Alex Molina
#  February 2023

import urllib.parse as urlparse
import requests
import pandas as pd
import json
import sys
import time

def call_geoAPI(query):
    """Geocoding service custom for Mexico
    """
    API_url ="https://www.geoparsing.com.mx/ws/"
    data = dict({"query" : query})
    try:
        response = requests.post(API_url, json = data, headers={"Content-Type":"application/json"})
        jresponse = response.json()
    except Exception as e:
        print('Exception:', e)
        jresponse = None
    return jresponse


def get_geocode_arcgis(address, format="pjson"):
    OSM_GEOCODE_ARCGIS = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?'
    params = {
              'Address': address,
              'f': 'JSON',
            }

    urlparams = urlparse.urlencode(params)
    url_req = '{}{}'.format(OSM_GEOCODE_ARCGIS, urlparams)

    geocode_info = {}
    try:
        r = requests.get(url_req)
        geocode_info = r.json()
    except Exception as e:
        print("exception", e)
        geocode_info = {}

    return geocode_info


def adress_maker(df):
    df['query'] = df['CALLE']+', '+df['COL']+', '+df['MUN']+', '+df['EDO']+', '+str(df['CP'])
    return df['query']

if __name__ == '__main__':
    
    fpath = sys.argv[1]
    #print(fpath)
    df = pd.read_csv(fpath,
        header=0,
        engine="python",
        encoding="UTF-8",
        sep=',')
    #df['query'] = df['CALLE']+'  '+df['COL']+'  '+df['MUN']+'  '+df['EDO']+'  '+df['CP']
    df['query'] = df[['CALLE', 'COL', 'MUN', 'EDO', 'CP']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df = df[['FOLIO_NO','CALLE', 'COL', 'MUN', 'EDO', 'CP', 'query']]
    #print(df.head())

    for index, row in df.iterrows():
        #print(row['query'])
        result = get_geocode_arcgis(row['query'])
        #print(result['candidates'])        
        try:
            georef = result['candidates'][0]
            row['x'] = georef['location']['x']
            row['y'] = georef['location']['y']
            row['score'] = georef['score']
            row['xmin'] = georef['extent']['xmin']
            row['ymin'] = georef['extent']['ymin']
            row['xmax'] = georef['extent']['xmax']
            row['ymax'] = georef['extent']['ymax']
            s='{}\t{}\t{}\t{}\t{}'.format(row['FOLIO_NO'],
                georef['location']['x'],
                georef['location']['y'],
                georef['score'],
                row['query'],
                )
            print(s)
        except Exception as e:
            georef = None
            row['x'] = None
            row['y'] = None
            row['score'] = None
            row['xmin'] = None
            row['ymin'] = None
            row['xmax'] = None
            row['ymax'] = None
        #print(georef)
        time.sleep(0.25)
    #df[['FOLIO_NO','x','y','score','xmin','ymin','xmax','ymax','query']].to_csv('INSP_geocoded_address.csv', index=False)
