from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import time
import re

if __name__ == '__main__':
    fpath = sys.argv[1]    
    with open(fpath, 'r') as f:
        lines = f.readlines()
        cp_maest = [l.strip('\n') for l in lines]
    sepath = sys.argv[2]
    with open(sepath, 'r') as g:
        liness = g.readlines()
        cp_sepo = [l.strip('\n') for l in liness]

    N_cp_maest = len(cp_maest)
    print('cp_maest', type(cp_maest[0]),N_cp_maest,'\n',cp_maest[0:10],'...',cp_maest[-10:])
    # sets
    set_maest = set(cp_maest)
    N_set_maest = len(set_maest)
    print('set_maest', type(set_maest),N_set_maest,'\n')

    N_cp_sepo = len(cp_sepo)
    print('cp_sepo', type(cp_sepo[0]),N_cp_sepo,'\n',cp_sepo[0:10],'...',cp_sepo[-10:])
    # sets
    set_sepo = set(cp_sepo)
    N_set_sepo = len(set_sepo)
    print('set_sepo', type(set_sepo),N_set_sepo,'\n')
    # set diff
    set_diff = set_maest.difference(set_sepo)
    print('set_diff',len(set_diff),'\n')
    # for e in set_diff:
    #     print(e)
