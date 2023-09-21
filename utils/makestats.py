from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import time
import re


if __name__ == '__main__':
    # total de registros en la tabla
    N=104003
    fpath = sys.argv[1]
    df = pd.read_csv(fpath,
        header=None,
        engine="python",
        encoding="UTF-8",
        sep='\t')
    print(df)
    df.columns = ['frecuencia', 'variante']
    #print('Deciles:\n',df['frecuencia'].describe([.1,.2,.3,.4,.5,.6,.7,.8,.9,.99]))
    print('\n',df['frecuencia'].describe())
    s = df['frecuencia'].sum()
    print('Suma', s)
    # conteo para un número razonable de correcciones
    # Cuántos (en qué porcentaje se salvan para f = 10)
    f = 10
    filtered = df.loc[df['frecuencia'] >= f]
    print('Filtro para frecuencia igual o mayor a',f)
    sumfilter = filtered['frecuencia'].sum()
    print('Suma filtrados', sumfilter)
    print('Proporción de ', sumfilter/s)
    #ax = df.plot.hist(bins=100, alpha=0.5)
    #plt.show()
    #ax = df.plot.hist(column=["age"],figsize=(10, 8))
