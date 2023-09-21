# Soft Geocoding for semi-structured data
# Using our own custom service for Mexico
#
#  Created by Alex Molina
#  February 2023
# 
#  Enhanced September 2023
# based on 
# Creating spatial join between points and polygons in GeoPandas
# https://geopandas.org/en/stable/gallery/spatial_joins.html
# In an INNER JOIN (how='inner'), we keep rows from the right and left only where their binary predicate is True. We duplicate them if necessary to represent multiple hits between the two dataframes. We retain attributes of the right and left only if they intersect and lose all rows that do not. An inner join implies that we are interested in retaining the geometries of the left.
# This is equivalent to the PostGIS query:
#                     geom                    | ptid | polyid
# --------------------------------------------+------+--------
#  010100000040A9FBF2D88AD03F349CD47D796CE9BF |    4 |     10
#  010100000048EABE3CB622D8BFA8FBF2D88AA0E9BF |    3 |     10
#  010100000048EABE3CB622D8BFA8FBF2D88AA0E9BF |    3 |     20
#  0101000000F0D88AA0E1A4EEBF7052F7E5B115E9BF |    2 |     20
# https://geopandas.org/en/stable/gallery/spatial_joins.html
import geopandas
from shapely import wkt
from shapely.geometry import Polygon
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


def build_geodf(fpath):
    df = pd.read_csv(fpath, header=0, engine="python", encoding="UTF-8", sep='\t')
    # make a point geometry from string {'x': -101.663262374351, 'y': 21.169852986944}
    #print(df)
    df['Latitude']  = df['location'].apply(lambda s: eval(s)['y'])
    df['Longitude'] = df['location'].apply(lambda s: eval(s)["x"])
    #df['BDcp'] = df.Series(df['BDcp'], dtype="int64")
    df['BDcp'] = df['BDcp'].astype(str, errors='ignore')
    df['BDcp'] = df['BDcp'].apply(lambda x: removesuffix(x, '.0'))
    #print(df)
    #print(df.info(verbose=True))
    gdf = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326")
    #print(gdf.head())
    return(gdf)

def build_extent(aux):
    #Desplegar extent
    aux['out1']=aux['extent'].replace({"{'xmin': ":"", " 'ymin': ":"", " 'xmax': ":"", " 'ymax': ":"", "}":""}, regex=True)
    #Separar columnas por rumbos
    aux[['este', 'sur', 'oeste','norte']] = aux['out1'].str.split(',', expand=True)
    # Generar un WKT DAR COORDENADAS EN ESTE ORDEN:
    # OESTE-SUR,
    # ESTE-SUR,
    # ESTE-NORTE,
    # OESTE-NORTE,
    # OESTE-SUR
    # La sintaxis debe quedar:
    # POLYGON(E S, W S, W N, S N, E S)
    aux['geometry']='POLYGON(('+ aux['este'] + ' ' + aux['sur'] + ','+ aux['oeste'] + ' ' + aux['sur'] + ','+ aux['oeste'] + ' ' + aux['norte'] + ','+ aux['este'] + ' ' + aux['norte'] + ','+ aux['este'] + ' ' + aux['sur'] +'))'
    #CARGAR FORMATO WKT con campo calculado
    aux['geometry'] = aux['geometry'].apply(wkt.loads)
    #Señalar geometrias
    birds_geo = aux.set_geometry('geometry')
    #crear geodataframe asignando campo geometria
    gdf2 = geopandas.GeoDataFrame(birds_geo, geometry='geometry')
    gdf2=gdf2.set_crs("EPSG:4326") #Asignar CRS
    # area extent km2
    gdf2=gdf2.to_crs(6372) #REPROYECTAR CRS
    aux['areakm2'] = round(gdf2['geometry'].area/1000000,3) #KM2
    #print('extent gdf2\n',gdf2)
    return(gdf2)

# Function To Remove a Suffix in Python 3.8
def removesuffix(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    else:
        return text

if __name__ == '__main__':
    DIRCANDIDATES='./data/candidates/'
    DIRSJOINED='./data/joined/'
    COLONIAS='./resources/ine2010_colonias_areas.json'
    # Load colonias MX
    print('Loading colonias MX data')
    file = open(COLONIAS)
    polycols = geopandas.read_file(file)
    # ENTIDAD, MUNICIPIO, NOMBRE, CLASIFICAC, CP, geometry
    polycols['NOMBRE'] = pd.Series(polycols['NOMBRE'], dtype="string")
    polycols['CP'] = pd.Series(polycols['CP'], dtype="int64")
    polycols['CP'] = pd.Series(polycols['CP'], dtype="string")
    print(polycols)
    print(polycols.info(verbose=True))
    # iterate candidate files in dir
    for (root, directory, files) in os.walk(DIRCANDIDATES):
        for file in files:
            if file.startswith('candidates'):
                fpath = os.path.join(DIRCANDIDATES, file)
                print('\n\nReading ', fpath)
                # check if done skip it
                outname = '{}sjoined-{}.geojson'.format(DIRSJOINED,os.path.basename(fpath))
                if exists(outname):
                    print('SKIPING', outname, 'already done')
                    continue
                points = build_geodf(DIRCANDIDATES+file)                
                print('Created GeoDataFrame with',len(points),' entries')
                ############
                # Creating spatial join between points and polygons in GeoPandas
                print('Creating spatial join')
                sjoin_inner = geopandas.sjoin(points, polycols,
                    how='inner',
                    op="within")
                #print('Spatial join\n',sjoin_inner)
                ############
                # extent area Km2 and replace geometry
                #
                extent_gdf = build_extent(sjoin_inner)
                ############
                # adding more filtering criteria features
                # 
                #sjoin_inner['comp-cp']=sjoin_inner.apply(lambda x: 100 if ((x['BDcp'])==str(x['CP'])) else 0, axis=1)
                sjoin_inner['comp-cp']= sjoin_inner.apply(lambda x: fuzz.ratio(str(x['BDcp']),str(x['CP'])), axis=1)
                sjoin_inner['comp-col'] = sjoin_inner.apply(lambda x: fuzz.ratio(str(x['BDcol']).replace(',',' ').upper(),str(x['NOMBRE']).replace(',',' ').upper()), axis=1)
                #sjoin_inner['comp-CPcol']=sjoin_inner.apply(lambda x: ( float(x['comp-cp'])+(x['comp-col']==1) ) else 0, axis=1)
                #sjoin_inner['comp-CPcol']=sjoin_inner.apply(lambda x: 1 if( (x['comp-cp']==1) and (x['comp-col']==1) ) else 0, axis=1)
                ############
                # cleaning df
                sjoin_inner.drop(['out1','este', 'sur', 'oeste','norte','attributes','extent','location','score'], inplace=True,axis=1)
                # Writing results
                print('Writing result', outname)
                sjoin_inner.to_file(outname, driver='GeoJSON')
