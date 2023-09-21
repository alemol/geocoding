from ipyleaflet import (Map,
                        Marker,
                        basemaps,
                        basemap_to_tiles,
                        MarkerCluster,
                        CircleMarker,
                        Popup,
                        AwesomeIcon)
from ipywidgets import HTML
import geopandas
import pandas as pd
import numpy as np
import os
from os.path import exists
import sys
import time
import re


if __name__ == '__main__':
    # CONSTANTS & LOCALES
    MEX=(24.25, -99.07)
    DATPATH='./geoESMaestras.csv'
    cols = ['folio','score_address','address','latitude','longitude','ine_entcode','ine_muncode','ine_colname','ine_coltype','ine_cp','areakm2','score_compcp','score_compcol','geometry']
    data = pd.read_csv(
        DATPATH,
        header=0,
        names=cols,
        engine="python",
        encoding="UTF-8",
        sep='\t')
    print(data.head())
    # Create the map
    print('Building map . . . may take a while')
    m = Map(center=MEX, zoom=6)
    # Add data layers
    markers = []
    for folio, addres, lon, lat in data[['folio', 'address', "longitude", "latitude"]].values:
        # custom icon
        myicon = AwesomeIcon(name='home', icon_color='purple', marker_color='purple', spin= False)
        # custom popup message
        message = HTML(value='<p style="color:purple;"><b>folio {}</b>: {}.</p>'.format(folio, addres))
        # create pin
        pin = Marker(icon=myicon,
                    location=(lat, lon),
                    draggable=False,
                    #opacity=0.85,
                    title='{}:{}'.format(folio,addres),
                    )
        pin.popup = message
        markers.append(pin)
    # Clustering
    marker_cluster = MarkerCluster(markers=markers)
    m.add_layer(marker_cluster)
    m.layout.height="1024px"
    # display the map
    #display(m)
    m.save('map_geoESMaestras.html')
