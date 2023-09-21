from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import time
import re

if __name__ == '__main__':
    fpath = sys.argv[1]
    df = pd.read_csv(fpath,
        header=0,
        engine="python",
        encoding="UTF-8",
        sep=',')
    print('loaded file', fpath)
    # folio,address,location,score,attributes,extent,query,BDcp,BDcol,simple_rat,sort_ratio,ratio_scor,key,este,sur,oeste,norte,ctd_x,ctd_y,d_codigo,SETT_NAME,comp-cp,comp-col,comp-CPcol,areakm2
    print(df)
    ################################
    print('▓▒▒░░░   LEX    ░░░▒▒▓█')
    print('\ncoincidencia ordenada de tokens:')
    print(df['simple_rat'].describe())
    print('\ncoincidencia no ordenada de tokens:')
    print(df['sort_ratio'].describe())
    print('\nscore lineal de tokens:')
    print(df['ratio_scor'].describe())
    # # ideas de clasificación
    # # bajo:   (00.0-64.00]
    # # medio:  (64.0-72.00]
    # # alto :  (73.0-100.00]
    # #
    print('▓▒▒░░░   GEO    ░░░▒▒▓█')
    print('\ncoincidencia de cp:')
    print(df['comp-cp'].describe())
    cpmatches = sum(df['comp-cp'] == 1)
    cpunmatches = sum(df['comp-cp'] == 0)
    print('  coincidencias  comp-cp global: ',cpmatches)
    print('incoincidencias  comp-cp global: ',cpunmatches)
    # #
    print('\ncoincidencia de col:')
    print(df['comp-col'].describe())
    colmatches = sum(df['comp-col'] == 1)
    colunmatches = sum(df['comp-col'] == 0)
    print('  coincidencias  comp-col global: ',colmatches)
    print('incoincidencias  comp-col global: ',colunmatches)
    #
    print('\ncoincidencia de CPcol:')
    print(df['comp-CPcol'].describe())
    CPcolmatches = sum(df['comp-CPcol'] == 1)
    CPcolunmatches = sum(df['comp-CPcol'] == 0)
    print('  coincidencias  comp-CPcol global: ',CPcolmatches)
    print('incoincidencias  comp-CPcol global: ',CPcolunmatches)
    #
    print('\nárea de extent (Km2):')
    print(df['areakm2'].describe())
    #
    # alto:   (00.0-??] 
    # medio:  (??-??] 
    # bajo :  (??-??] 
    # 
    print('▓▒▒░░░    FOLIO    ░░░▒▒▓█')
    #folio,ncands,
    folio_s = df.groupby(['folio']).size()
    folio_s.name = "ncands"
    #print(type(folio_s))
    #print(folio_s)
    #print(folio_s.describe())
    #matchcp,matchcol,matchcpcol,
    matchcp_s = df.groupby('folio')['comp-cp'].sum()
    matchcp_s.name = "matchcp"
    matchcol_s = df.groupby('folio')['comp-col'].sum()
    matchcol_s.name = "matchcol"
    matchcpcol_s = df.groupby('folio')['comp-CPcol'].sum()
    matchcpcol_s.name = "matchcpcol"
    #print(type(matchcp_s))
    #print(matchcp_s)
    #print(matchcp_s.describe())
    #ratiomin,ratioavg,ratiomax
    ratiomin_s = df.groupby('folio')['simple_rat'].min()
    ratiomin_s.name = "ratiomin"
    ratioavg_s = df.groupby('folio')['simple_rat'].mean()
    ratioavg_s.name = "ratioavg"
    ratiomax_s = df.groupby('folio')['simple_rat'].max()
    ratiomax_s.name = "ratiomax"
    ### areas
    #areamin,areaavg,areamax
    amin_s = df.groupby('folio')['areakm2'].min()
    amin_s.name = "areamin"
    aavg_s = df.groupby('folio')['areakm2'].mean()
    aavg_s.name = "areaavg"
    amax_s = df.groupby('folio')['areakm2'].max()
    amax_s.name = "areamax"
    ##########
    apis_s = df.groupby('folio')['score'].mean()
    apis_s.name = "apiavg"
    ##
    result = pd.concat([folio_s,
        matchcp_s,
        matchcol_s,
        matchcpcol_s,
        ratiomin_s,
        ratioavg_s,
        ratiomax_s,
        amin_s,
        aavg_s,
        amax_s,
        apis_s
        ], axis=1)
    print(result)
    print(result.describe())
    print('Writing resulting data')
    result.to_csv('data-indicators-out4.tsv',
        index='folio',
        sep='\t')
    ###################################
    # ejemplo de criterio basado en condiciones
    # 
    # el punto del candidato de la API tiene correspondencia en la cp indicada en los datos
    # df['comp-cp'] == 1
    #
    # los elementos en la dirección de la address de la API del candidato tienen alta similitud con la dirección que se logró establecer mediante concatenación de los campos de los datos
    # df['simple_rat'] in (64.0-72.0]
    #
    # df['areakm2'] in in (0.0-50.0) Km2
    #display(df.loc[(dataFrame['Salary']>=100000) & (dataFrame['Age']< 40) & (dataFrame['JOB'].str.startswith('D')), ['Name','JOB']])
    #filter_df = df[(df['comp-cp']==1) and
    #(df['simple_rat'] > 64 and df['simple_rat'] < 72) and
    #(df['areakm2'] > 0 and df['areakm2'] < 50)]
    f1_df = df[df['comp-CPcol'] == 1]
    f2_df = f1_df[f1_df['simple_rat']>73.0]
    f3_df = f2_df[f2_df['areakm2'] < 50]
    print(f3_df)
    f3_df.to_csv('results-out6.tsv', sep='\t',
        index=False)
    # Reducción a un punto por folio y simplificación
    # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
    idx = df.groupby(['folio'])['simple_rat'].transform(max) == df['simple_rat']
    simpledf=f3_df[idx]
    simpledf[['folio','simple_rat','query','address','location','ctd_x','ctd_y','key','este','sur','oeste','norte']].to_csv('results-simple.tsv', sep='\t', index=False)
