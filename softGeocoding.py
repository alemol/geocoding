# Soft Geocoding for semi-structured data
# Using our own custom API service for Mexico
#
#  Created by Alex Molina
#  February 2023
# 
#  Enhanced June 2023


from thefuzz import fuzz
import urllib.parse as urlparse
import requests
import pandas as pd
import json
import os
from os.path import exists
import sys
import time
import re


def repair_shit(ent_name):
    # 21691 VERACRUZ
    # 10979 GUANAJUATO
    # 10304 DISTRITO FEDERAL
    # 10182 JALISCO
    # 9772 CHIAPAS
    # 8311 ESTADO DE MÉXICO
    # 6671 HIDALGO
    # 4827 NUEVO LEÓN
    # 4397 SONORA
    # 4139 BAJA CALIFORNIA
    # 3938 DURANGO
    # 2983 CIUDAD DE MEXICO
    # 2338 YUCATÁN
    #  343 TAMAULIPAS
    #  330 ESTADO DE MEXICO
    #  265 COAHUILA
    #  253 MORELOS
    #  246 VERACRUZ                      
    #  223 NUEVO LEON
    #  202 CIUDAD DE MÉXICO
    #  134 YUCATAN
    #   98 EDO DE MEXICO
    #   71 QUERÉTARO
    #   59 PUEBLA
    #   59 MICHOACÁN
    #   56 SAN LUIS POTOSÍ
    #   56 NVO. LEON
    #   47 NAYARIT
    #   47 GUANAJUATO 
    #   44 JALISCO                       
    #   43 OAXACA
    #   38 JALISCO 
    #   36 VERACRUZ 
    #   34 AGUASCALIENTES
    #   31 TLAXCALA
    #   30 CD DE MEXICO
    #   25 DURANGO               
    #   25 BAJA CALIFORNIA 
    #   24 TABASCO
    #   24 NUEVO LÉON
    #   22 EDO MEX
    #   21 EDO DE MÉXICO
    #   20 ESTADO DE MÉXICO 
    #   20 CIUDAD DE MÉXICO 
    #   19 CD MX
    #   19 CAMPECHE
    #   18 VER
    #   17 COLIMA
    #   17 COAHUILA DE ZARAGOZA
    #   17 B.C
    #   16 CIUDAD DE MEXICO 
    #   15 QUERETARO
    #   15 NUEVO LEON 
    #   14 OAXACA                        
    #   14 AGUSCALIENTES                 
    #   13 HIDALGO 
    #   12 DF
    #   11 SONORA 
    #   10 EDO MEXICO
    #   10 CD MEXICO
    cdmx = r'(CD MEXICO|DF|CIUDAD DE MEXICO |CD MX|CIUDAD DE MÉXICO |CD DE MEXICO|CIUDAD DE MEXICO|DISTRITO FEDERAL)'
    ver = r'(VERACRUZ|VERACRUZ                      |VERACRUZ |VER)'
    edomex = r'(ESTADO DE MÉXICO|ESTADO DE MEXICO|EDO DE MEXICO|EDO MEX|EDO DE MÉXICO|ESTADO DE MÉXICO |EDO MEXICO)'
    yuc = r'(YUCATÁN|YUCATAN)'
    if not(re.fullmatch(cdmx, ent_name, flags=re.I) is None):
        ent_name = 'Ciudad de México'
    elif not(re.fullmatch(ver, ent_name, flags=re.I) is None):
        ent_name = 'Veracruz de Ignacio de la Llave'
    elif not(re.fullmatch(edomex, ent_name, flags=re.I) is None):
        ent_name = 'Estado de México'
    elif not(re.fullmatch(yuc, ent_name, flags=re.I) is None):
        ent_name = 'Yucatán'
    return ent_name


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
        print('Requesting ',address[:100],'...')
        r = requests.get(url_req)
        if r.ok:
            print('HTTP status 200 OK')
        else:
            print('KO!')
        geocode_info = r.json()
    except Exception as e:
        print("Exception getting geocoding from API:", e)

    return geocode_info

def homogen_adress(address):
    p = r'^Calle|calle'
    new_adress = re.sub(p,'',address)
    p = r'^Avenida|avenida|Av\.|av\.'
    new_adress = re.sub(p,'',new_adress)
    return new_adress

def build_df(p):
    cols = ['folALTERNO','calle','numint','numext','entrecalle','ylacalle', 'colonia', 'muniodel','cp','estado']
    df = pd.read_csv(p,
        header=None,
        names=cols,
        engine="python",
        encoding="UTF-8",
        sep='\t')
    print('Created Data Frame with',len(df),' entries')
    df['estado'] = df['estado'].apply(repair_shit)
    # correcting spaces
    df['calle'] = df['calle'].apply(lambda x: str(x).strip())
    df['colonia'] = df['colonia'].apply(lambda x: str(x).strip())
    df['muniodel'] = df['muniodel'].apply(lambda x: str(x).strip())
    df['estado'] = df['estado'].apply(lambda x: str(x).strip())
    df['query'] = df[['calle', 'numext', 'colonia', 'muniodel', 'estado', 'cp']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    #print(df)
    return(df)

#def APIcall(df, sleepy=0.25):
def APIcall(df, sleepy=0.00):
    #print('Starting API querying . . .')
    list_candidates = list()
    for index, row in df.iterrows():
        print('\n',row['folALTERNO'])
        result = get_geocode_arcgis(row['query'])
        #print(result)
        try:
            candidates = result['candidates']
        except Exception as e:
            candidates = []

        #print(row['folALTERNO'], row['query'], candidates)
        print(len(candidates), 'candidates')
        for c in candidates:
            c = dict(c)
            # homogenizar
            #c['address'] = homogen_adress(c['address'])
            c['folio']=row['folALTERNO']
            c['query']=row['query']
            c['BDcp']=row['cp']
            c['BDcol']=row['colonia']
            list_candidates.append(c)
        time.sleep(sleepy)
    result_df = pd.DataFrame(list_candidates)
    #print(result_df)
    return(result_df)

if __name__ == '__main__':
    DIRCHUNKS='./data/chunks/'
    DIRCANDIDATES='./data/candidates/'

    for (root, directory, files) in os.walk(DIRCHUNKS):
        for file in files:
            if file.startswith('segment'):
                fpath = os.path.join(DIRCHUNKS, file)
                print('\n\nReading ', fpath)
                # check if done skip it
                outname = '{}candidates-{}.tsv'.format(DIRCANDIDATES,os.path.basename(fpath))
                if exists(outname):
                    print('SKIPING', outname, 'already done')
                    continue
                df=build_df(fpath)
                result_df = APIcall(df)
                # Adding Fuzzy String Matching indicators    
                result_df['simple_ratio'] = result_df.apply(lambda row: fuzz.ratio(row['query'].replace(',',' ').lower(),str(row['address']).replace(',',' ').lower()), axis=1)
                result_df['sort_ratio'] = result_df.apply(lambda row: fuzz.token_sort_ratio(row['query'].replace(',',' ').lower(),str(row['address']).replace(',',' ').lower()), axis=1)
                beta = 0.8
                result_df['ratio_score'] = result_df.apply(lambda row: (beta)*row['sort_ratio']+(1.0-beta)*row['simple_ratio'] , axis=1)
                result_df.set_index('folio', inplace=True)
                #print(result_df.head())
                # related by basename chunck
                print('\nWriting resulting data to', outname)
                result_df.to_csv(outname, index='folio', sep='\t')
