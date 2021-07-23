
from getDataWB import generateCsvTopology, generateCsvPerc, generateCsvData, generateCsvDataDis,generateCsvDataDisPTAP, generateCsvQ, generateCsvQDisPTAP

# Generación de csv para la segunda ejecución del Water Balance en Intake
def DataInWB( id_intake, path_data_wb_in):
    generateCsvTopology( id_intake, '__wpgettopologybycatchment', path_data_wb_in)
    generateCsvPerc( id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv", path_data_wb_in)
    generateCsvData( id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv", path_data_wb_in)
    generateCsvData( id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv", path_data_wb_in)
    generateCsvData( id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv", path_data_wb_in)
    generateCsvData( id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv", path_data_wb_in)
    generateCsvQ( [id_intake], '__wpgetqbycatchment', "3_Water_Extraction.csv", path_data_wb_in)

# Generación de csv para la segunda ejecución del Water Balance en PTAP
def DataInWBPTAP(id_ptap, path_data_wb_in):
    generateCsvTopology(id_ptap, '__wpgettopologybyptap', path_data_wb_in)
    generateCsvPerc(id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv", path_data_wb_in)
    generateCsvData(id_ptap, '__wpgetawybyptap', "2_WI_AWYInputs.csv", path_data_wb_in)
    generateCsvData(id_ptap, '__wpgetsedbyptap', "2_WI_WSedInputs.csv", path_data_wb_in)
    generateCsvData(id_ptap, '__wpgetnbyptap', "2_WI_WNInputs.csv", path_data_wb_in)
    generateCsvData(id_ptap, '__wpgetpbyptap', "2_WI_WPInputs.csv", path_data_wb_in)
    generateCsvQ([id_ptap], '__wpgetqbyptap', "3_Water_Extraction.csv", path_data_wb_in)

# Genera los csv para la ejecución de WB en Intakes de dissagregation para el escenario BAU
def DataInBAU(id_intake, path_data_wb_in, path_data_ds_out,study_case_id):
    OUT_BAU_CSV = '02-OUTPUTS_BaU.csv'
    generateCsvTopology(id_intake, '__wpgettopologybycatchment', path_data_wb_in)
    generateCsvPerc(id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv", path_data_wb_in)
    generateCsvDataDis(id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv", 1, OUT_BAU_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv", 2, OUT_BAU_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv", 3, OUT_BAU_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv", 4, OUT_BAU_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvQ([id_intake,study_case_id], '__wpgetqbycatchmentdis', "3_Water_Extraction.csv",path_data_wb_in)

# Genera los csv para la ejecución de WB en Intakes de dissagregation para el escenario NBS
def DataInNBS(id_intake, path_data_wb_in, path_data_ds_out,study_case_id):
    OUT_NBS_CSV = '02-OUTPUTS_NBS.csv'
    generateCsvTopology(id_intake, '__wpgettopologybycatchment', path_data_wb_in)
    generateCsvPerc(id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv", path_data_wb_in)
    generateCsvDataDis(id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv", 1, OUT_NBS_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv", 2, OUT_NBS_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv", 3, OUT_NBS_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvDataDis(id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv", 4, OUT_NBS_CSV, path_data_wb_in, path_data_ds_out)
    generateCsvQ([id_intake,study_case_id], '__wpgetqbycatchmentdis', "3_Water_Extraction.csv", path_data_wb_in)
    
# Genera los csv para la ejecución de WB en PTAP de dissagregation para el escenario BAU
def DataInBAUPTAP(id_ptap,studycase_id, path_data_wb_in, path_data_ds_out):
    generateCsvTopology( id_ptap, '__wpgettopologybyptap', path_data_wb_in)
    generateCsvPerc( id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv", path_data_wb_in )
    generateCsvDataDisPTAP( id_ptap,studycase_id, '__wpgetawybyptap', "2_WI_AWYInputs.csv", 'awy', 'BAU', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,studycase_id, '__wpgetsedbyptap', "2_WI_WSedInputs.csv", 'wsed_ton', 'BAU', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,studycase_id, '__wpgetnbyptap', "2_WI_WNInputs.csv", 'wn_kg', 'BAU', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,studycase_id, '__wpgetpbyptap', "2_WI_WPInputs.csv", 'wp_kg', 'BAU', path_data_wb_in)
    generateCsvQDisPTAP( "3_Water_Extraction.csv", path_data_wb_in)

# Genera los csv para la ejecución de WB en PTAP de dissagregation para el escenario NBS
def DataInNBSPTAP(id_ptap,study_case_id, path_data_wb_in):
    generateCsvTopology( id_ptap, '__wpgettopologybyptap', path_data_wb_in)
    generateCsvPerc( id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv", path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,study_case_id, '__wpgetawybyptap', "2_WI_AWYInputs.csv", 'awy', 'NBS', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,study_case_id, '__wpgetsedbyptap', "2_WI_WSedInputs.csv", 'wsed_ton', 'NBS', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,study_case_id, '__wpgetnbyptap', "2_WI_WNInputs.csv", 'wn_kg', 'NBS', path_data_wb_in)
    generateCsvDataDisPTAP( id_ptap,study_case_id, '__wpgetpbyptap', "2_WI_WPInputs.csv", 'wp_kg', 'NBS', path_data_wb_in)
    generateCsvQDisPTAP( "3_Water_Extraction.csv", path_data_wb_in)

