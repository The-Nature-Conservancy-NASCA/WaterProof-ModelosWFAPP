# -*- coding: utf-8 -*-
# Import Packages
import os
import pandas as pd

ruta = os.environ["PATH_FILES"]

def Select_PTAP(PathProject_PTAP):
    print("Select_PTAP")
    # Leer Archivos de entrada
    AWY = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS","1_WI_AWY.csv"),  index_col=0)
    N   = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS","3_WI_WN.csv"),  index_col=0)
    P   = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS","4_WI_WP.csv"),  index_col=0)
    S   = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS","2_WI_WSed.csv"),  index_col=0)
    NQ  = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS",'7_NormQuality.csv'))
    SelectQuality   = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS",'6_Table_Select_Quality.csv'))
    SelectPTAP      = pd.read_csv(os.path.join(ruta,"salidas","ptap_test","INPUTS",'5_Table_Select_PTAP.csv'))

    # Check AWY = 0  -> 0.0031536 m3 = 0.1 l/s
    id = AWY  == 0
    AWY[id] = 0.0031536

    # Factor
    # Kg/m3 -> mg/l
    Factor_1 = 1000

    # Integración de calidades
    CN = N.sum(1)/AWY.sum(1)*Factor_1
    CP = P.sum(1)/AWY.sum(1)*Factor_1
    CS = S.sum(1)/AWY.sum(1)*Factor_1*1000

     # Select PTAP - Water Quality - SST
    if (CS[1] >= SelectPTAP['SST'][0]) and (CS[1] < SelectPTAP['SST'][1]):
        Type_SST = 1
    elif (CS[1] >= SelectPTAP['SST'][1]) and (CS[1] < SelectPTAP['SST'][2]):
        Type_SST = 2
    elif (CS[1] >= SelectPTAP['SST'][2]) and (CS[1] < SelectPTAP['SST'][3]):
        Type_SST = 3
    elif (CS[1] >= SelectPTAP['SST'][3]):
        Type_SST = 4

    # Select PTAP - Water Quality - N
    if (CN[1] >= SelectPTAP['N'][0]) and (CN[1] < SelectPTAP['N'][1]):
        Type_N = 1
    elif (CN[1] >= SelectPTAP['N'][1]) and (CN[1] < SelectPTAP['N'][2]):
        Type_N = 2
    elif (CN[1] >= SelectPTAP['N'][2]) and (CN[1] < SelectPTAP['N'][3]):
        Type_N = 3
    elif (CN[1] >= SelectPTAP['N'][3]):
        Type_N = 4

    # Select PTAP - Water Quality - P
    if (CP[1] >= SelectPTAP['P'][0]) and (CP[1] < SelectPTAP['P'][1]):
        Type_P = 1
    elif (CP[1] >= SelectPTAP['P'][1]) and (CP[1] < SelectPTAP['P'][2]):
        Type_P = 2
    elif (CP[1] >= SelectPTAP['P'][2]) and (CP[1] < SelectPTAP['P'][3]):
        Type_P = 3
    elif (CP[1] >= SelectPTAP['P'][3]):
        Type_P = 4

    # Water Quality
    WQ = max([Type_SST, Type_N, Type_P])
    # Normative Quality
    NQ = NQ.values[0][0]

    # Select PTAP - Water Quality + Normative
    SelectQuality = SelectQuality.set_index('Quatily')
    Tmp     = SelectQuality.values
    FQ      = Tmp[WQ-1,NQ-1]
    FQ_L    = ['','A','B','C','D','E','F','G']

    Results = pd.DataFrame(data=[FQ_L[FQ]],columns=['Type'])
    # Results.to_csv( os.path.join(PathProject_PTAP,'OUTPUTS','1-Type_PTAP.csv'), index=False)
    # Results = 0

    return Results["Type"][0], AWY.sum(1)[1],CN[1],CP[1],CS[1],N.sum(1)[1],P.sum(1)[1],S.sum(1)[1]

# # -----------------------------------------------------------------------------------
# # Tester
# # -----------------------------------------------------------------------------------
# PathProject_PTAP = r'C:\Users\jonathan.nogales\Music\Select_PTAP_WaterFunds\Project'
# Select_PTAP(PathProject_PTAP)