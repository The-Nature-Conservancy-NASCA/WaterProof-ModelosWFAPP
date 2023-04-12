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
    Acc_BaU  = 0
    Acc_NBS  = 0
    for k in range(1,n+1):

        BaU   = pd.read_csv(os.path.join(PathProject, str(k) + '-INPUTS_BaU.csv'), usecols=NameCol)
        NBS   = pd.read_csv(os.path.join(PathProject, str(k) + '-INPUTS_NBS.csv'), usecols=NameCol)

        BaU = BaU.drop([0])
        NBS = NBS.drop([0])

        # Indicators
        Indicators = ((NBS - BaU)/BaU)*100

        Tmp = [[Indicators['AWY (m3)'].max(),
                Indicators['Wsed (Ton)'].min(),
                Indicators['WN (Kg)'].min(),
                Indicators['WP (kg)'].min(),
                Indicators['BF (m3)'].max(),
                Indicators['WC (Ton)'].max()]]

        if k == 1:
            Acc_BaU  = BaU
            Acc_NBS  = NBS
        else:
            Acc_BaU = Acc_BaU + BaU
            Acc_NBS = Acc_NBS + NBS

        Final_In = pd.DataFrame(data=Tmp, columns=NameCol)

        Indicators = np.round(Indicators,2)
        Final_In   = np.round(Final_In,2)

        Indicators.to_csv(os.path.join(PathProject,str(k) + '-OUTPUTS_Indicators_TimeSeries.csv'), index_label='Time')
        Final_In.to_csv(os.path.join(PathProject, str(k) + '-OUTPUTS_Max_Indicators.csv'), index_label='Time')

    # Integrated Indicator
    Indicators = ((Acc_NBS - Acc_BaU)/Acc_BaU)*100

    Tmp = [[Indicators['AWY (m3)'].max(),
            Indicators['Wsed (Ton)'].min(),
            Indicators['WN (Kg)'].min(),
            Indicators['WP (kg)'].min(),
            Indicators['BF (m3)'].max(),
            Indicators['WC (Ton)'].max()]]

    Final_In = pd.DataFrame(data=Tmp, columns=NameCol)

    Indicators = np.round(Indicators,2)
    Final_In   = np.round(Final_In,2)

    Indicators.to_csv(os.path.join(PathProject,'OUTPUTS-Indicators_TimeSeries_Total.csv'), index_label='Time')
    Final_In.to_csv(os.path.join(PathProject,'OUTPUTS-Max_Indicators_Total.csv'), index_label='Time')

# Tester
#PathProject = r'C:\Users\TNC\Box\01-TNC\28-Project-WaterFund_App\02-Productos-Intermedios\Indicators-WaterFunds\Project'
#Indicators_BaU_NBS(PathProject)