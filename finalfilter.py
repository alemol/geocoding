# Soft Geocoding for semi-structured data
# Using our own custom service for Mexico
#
#  Created by Alex Molina
#  February 2023
# 
#  Enhanced September 2023


import geopandas
import pandas as pd
import numpy as np
import os
from os.path import exists
import sys
import time
import re


if __name__ == '__main__':
    DIRSJOINED='./data/joined/'
    DIRFILTER='./data/filtered/'
    for (root, directory, files) in os.walk(DIRSJOINED):
        for file in files:
            if file.startswith('sjoined'):
                fpath = os.path.join(DIRSJOINED, file)
                print('\n\nReading ', fpath)
                # check if done skip it
                outname = '{}filtered-{}.csv'.format(DIRFILTER,os.path.basename(fpath))
                if exists(outname):
                    print('SKIPING', outname, 'already done')
                    continue
                gdf = geopandas.read_file(fpath)
                df = pd.DataFrame(gdf)
                #df.set_index('folio', inplace=True)
                print(df)
                ###################################
                # Criterio basado en condiciones
                # 
                f1_df = df[df['comp-cp'] > 79]
                f2_df = f1_df[f1_df['simple_ratio']>75.0]
                f3_df = f2_df[f2_df['areakm2'] < 10]
                print(f3_df)
                # Reducción a un punto por folio y simplificación
                # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
                idx = df.groupby(['folio'])['simple_ratio'].transform(max) == df['simple_ratio']
                simpledf=f3_df[idx]
                # folio address query   BDcp    BDcol   simple_ratio    sort_ratio  ratio_score Latitude    Longitude   index_right ENTIDAD MUNICIPIO   NOMBRE  CLASIFICAC  CP  areakm2 comp-cp comp-col    geometry
                simpledf=simpledf[['folio','simple_ratio','address','Latitude','Longitude','ENTIDAD', 'MUNICIPIO',   'NOMBRE',  'CLASIFICAC',  'CP',  'areakm2', 'comp-cp', 'comp-col','geometry']]                
                ################
                # set new final names
                newnames={'folio':'folio','simple_ratio':'score_address','address':'address','Latitude':'latitude','Longitude':'longitude','ENTIDAD':'ine_entcode','MUNICIPIO':'ine_muncode','NOMBRE':'ine_colname','CLASIFICAC':'ine_coltype','CP':'ine_cp', 'areakm2':'areakm2','comp-cp':'score_compcp','comp-col':'score_compcol','geometry':'geometry'}
                simpledf.rename(columns = newnames, inplace = True)
                simpledf.drop_duplicates(subset=['folio'], inplace=True)
                simpledf.sort_values(by=['folio'], inplace=True)
                print('Writing result', outname)
                #simpledf.to_file(outname, driver='GeoJSON')
                simpledf.to_csv(outname, sep='\t', index=False)
