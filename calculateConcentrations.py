from dbfread import DBF
import os
import aqueduct

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
def calcConcentrations(path,label,cont,sub_dir,year_dir):
	#sub_dir = '01-INVEST_QUALITY'
	print ("calcConcentrations :: path: %s, label: %s, cont: %s ,sub_dir: %s ,year_dir: %s" % (path,label,cont,sub_dir,year_dir))
	path_file = os.path.join(path,sub_dir,'AWY',year_dir,'output','watershed_results_wyield_%s.dbf' % str(label))
	print (path_file)
	awy_file = path_file
	
	path_file = os.path.join(path,sub_dir,'SDR',year_dir,'watershed_results_sdr_%s.dbf' % str(label))
	print (path_file)
	sdr_file = path_file
	
	path_file = os.path.join(path,sub_dir,'NDR',year_dir,'watershed_results_ndr_%s.dbf' % str(label))
	print (path_file)
	ndr_file = path_file
	
	path_file = os.path.join(path,sub_dir,'SWY',year_dir,'aggregated_results_swy_%s.dbf' % str(label))
	print (path_file)
	swy_file = path_file

	swy_file_shp = swy_file.replace(".dbf",".shp")
	area = 0.0
	bf_value = 0.0
	try:
		area =  aqueduct.calculateArea(swy_file_shp)
		bf_value = readDBF(swy_file,'qb',cont)  # mm
		bf_value = (bf_value*area)/1000 # m3
	except:
		print("error executing swy model, maybe is not required...")

	awy_value = readDBF(awy_file,'wyield_vol',cont) # m3
	sdr_value = readDBF(sdr_file,'sed_export',cont) # Ton/year
	ndrn_value = readDBF(ndr_file,'n_exp_tot',cont) # Kg/year
	ndrp_value = readDBF(ndr_file,'p_exp_tot',cont) # Kg/year

	print("awy_value : %s :: sdr_value: %s :: ndrn_value : %s :: ndrp_value : %s" % (awy_file, sdr_value, ndrn_value, ndrp_value))	
	
	sdrW = sdr_value # Ton/year
	ndrnW = ndrn_value # Kg/year
	ndrpW = ndrp_value # Kg/year
	sdr_concentration = (sdr_value*1000000000)/(awy_value*1000) # mg/l
	ndrN_concentration = (ndrn_value*1000000)/(awy_value*1000) # mg/l
	ndrP_concentration = (ndrp_value*1000000)/(awy_value*1000) # mg/l
	return sdr_concentration,ndrN_concentration,ndrP_concentration,awy_value,sdrW,ndrnW,ndrpW,bf_value
 
#calcConcentrations(path,'SA_1')