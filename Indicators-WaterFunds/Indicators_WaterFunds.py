# -*- coding: utf-8 -*-
# Import Packages
import numpy as np
import pandas as pd
import glob
import os

def Indicators_BaU_NBS(PathProject):
    # Name Columns
    NameCol = ['AWY (m3)', 'Wsed (Ton)', 'WN (Kg)', 'WP (kg)', 'BF (m3)', 'WC (Ton)']

    # List Basin
    ListBasin = glob.glob(os.path.join(PathProject, '*INPUTS*'))

    n = int(len(ListBasin)/2)
    #k = 1
    for k in range(1,n+1):

        BaU   = pd.read_csv(os.path.join(PathProject, str(k) + '-INPUTS_BaU.csv'), usecols=NameCol)
        NBS   = pd.read_csv(os.path.join(PathProject, str(k) + '-INPUTS_NBS.csv'), usecols=NameCol)

        # Indicators
        Indicators = ((BaU - NBS)/NBS)*100

        Tmp = [[Indicators['AWY (m3)'][Indicators.index[-1]],
                Indicators['Wsed (Ton)'][Indicators.index[-1]],
                Indicators['WN (Kg)'][Indicators.index[-1]],
                Indicators['WP (kg)'][Indicators.index[-1]],
                Indicators['BF (m3)'][Indicators.index[-1]],
                Indicators['WC (Ton)'][Indicators.index[-1]]],
                ]

        if k == 1:
            Acc_BaU  = BaU
            Acc_NBS  = NBS
        else:
            Acc_BaU = Acc_BaU + BaU
            Acc_NBS = Acc_NBS + NBS

        Final_In = pd.DataFrame(data=Tmp, columns=NameCol)

        Indicators.to_csv(os.path.join(PathProject,str(k) + '-OUTPUTS_Indicators_TimeSeries.csv'), index_label='Time')
        Final_In.to_csv(os.path.join(PathProject, str(k) + '-OUTPUTS_Max_Indicators.csv'), index_label='Time')

    # Integrated Indicator
    Indicators = ((Acc_BaU - Acc_NBS)/Acc_NBS)*100

    Tmp = [[Indicators['AWY (m3)'][Indicators.index[-1]],
            Indicators['Wsed (Ton)'][Indicators.index[-1]],
            Indicators['WN (Kg)'][Indicators.index[-1]],
            Indicators['WP (kg)'][Indicators.index[-1]],
            Indicators['BF (m3)'][Indicators.index[-1]],
            Indicators['WC (Ton)'][Indicators.index[-1]]],
            ]

    Final_In = pd.DataFrame(data=Tmp, columns=NameCol)

    Indicators.to_csv(os.path.join(PathProject,'OUTPUTS-Indicators_TimeSeries_Total.csv'), index_label='Time')
    Final_In.to_csv(os.path.join(PathProject,'OUTPUTS-Max_Indicators_Total.csv'), index_label='Time')


# Tester
PathProject = r'C:\Users\TNC\Box\01-TNC\28-Project-WaterFund_App\02-Productos-Intermedios\Indicators-WaterFunds\Project'
Indicators_BaU_NBS(PathProject)
