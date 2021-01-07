from dbfread import DBF
import os

def readDBF(dbfFile,field,cont):
	result = ''
	table = DBF(dbfFile,load=True)
	result = 0
	result = table.records[cont][field]
	return result
   

   
file = "watershed_results_wyield_SA_1.dbf"
path = "/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/1_2020_10_6/out/"

#readDBF(file,'wyield_vol')

# Calcular concentraciones para primera ejecucion de INVEST
def calcConcentrations(path,label,cont):
	out_path = os.path.join(path,'01-INVEST_QUALITY')
	awy_file = os.path.join(out_path,'AWY','output','watershed_results_wyield_' + str(label) + '.dbf')
	sdr_file = os.path.join(out_path,'SDR','watershed_results_sdr_' + str(label) + '.dbf')
	ndr_file = os.path.join(out_path,'NDR','watershed_results_ndr_' + str(label) + '.dbf')
	awy_value = readDBF(awy_file,'wyield_vol',cont)*1000 # liters/year
	sdr_value = readDBF(sdr_file,'sed_export',cont) # Ton/year
	ndrn_value = readDBF(ndr_file,'n_exp_tot',cont) # Kg/year
	ndrp_value = readDBF(ndr_file,'p_exp_tot',cont) # Kg/year
	q = awy_value/31556952 # l/s
	sdrW = sdr_value # Ton/year
	ndrnW = ndrn_value # Kg/year
	ndrpW = ndrp_value # Kg/year
	sdr_concentration = (sdr_value*1000000000)/(awy_value) # mg/l
	ndrN_concentration = (ndrn_value*1000000)/(awy_value) # mg/l
	ndrP_concentration = (ndrp_value*1000000)/(awy_value) # mg/l
	return sdr_concentration,ndrN_concentration,ndrP_concentration,q,sdrW,ndrnW,ndrpW
 
#calcConcentrations(path,'SA_1')