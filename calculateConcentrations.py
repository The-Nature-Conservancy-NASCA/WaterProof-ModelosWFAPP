from dbfread import DBF
import os

def readDBF(dbfFile,field):
	result = ''
	table = DBF(dbfFile,load=True)
	result = 0
	for record in table.records:
		result = result + record[field]
	return result
   

   
file = "watershed_results_wyield_SA_1.dbf"
path = "/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/1_2020_10_6/out/"

#readDBF(file,'wyield_vol')

# Calcular concentraciones para primera ejecucion de INVEST
def calcConcentrations(path,label):
	out_path = os.path.join(path,'01-INVEST_QUALITY')
	awy_file = os.path.join(out_path,'AWY','output','watershed_results_wyield_' + str(label) + '.dbf')
	sdr_file = os.path.join(out_path,'SDR','watershed_results_sdr_' + str(label) + '.dbf')
	ndr_file = os.path.join(out_path,'NDR','watershed_results_ndr_' + str(label) + '.dbf')
	awy_value = readDBF(awy_file,'wyield_vol')*1000
	sdr_value = readDBF(sdr_file,'sed_export')*1000000000
	ndrn_value = readDBF(ndr_file,'n_exp_tot')*1000000
	ndrp_value = readDBF(ndr_file,'p_exp_tot')*1000000
	sdr_concentration = sdr_value/awy_value
	ndrN_concentration = ndrn_value/awy_value
	ndrP_concentration = ndrp_value/awy_value
	return sdr_concentration,ndrN_concentration,ndrP_concentration
 
calcConcentrations(path,'SA_1')