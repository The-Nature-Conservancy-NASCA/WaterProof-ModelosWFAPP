
from getDataWB import generateCsvTopology, generateCsvPerc, generateCsvData, generateCsvDataDis, generateCsvQ, generateCsvQDisPTAP

def DataInWB( id_intake ):
    generateCsvTopology( id_intake, '__wpgettopologybycatchment', "0_WI_Topology.csv" )
    generateCsvPerc( id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv" )
    generateCsvData( id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv" )
    generateCsvData( id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv" )
    generateCsvData( id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv" )
    generateCsvData( id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv" )
    generateCsvQ( id_intake, '__wpgetqbycatchment', "3_Water_Extraction.csv" )

def DataInWBPTAP( id_ptap ):
    generateCsvTopology( id_ptap, '__wpgettopologybyptap', "0_WI_Topology.csv" )
    generateCsvPerc( id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv" )
    generateCsvData( id_ptap, '__wpgetawybyptap', "2_WI_AWYInputs.csv" )
    generateCsvData( id_ptap, '__wpgetsedbyptap', "2_WI_WSedInputs.csv" )
    generateCsvData( id_ptap, '__wpgetnbyptap', "2_WI_WNInputs.csv" )
    generateCsvData( id_ptap, '__wpgetpbyptap', "2_WI_WPInputs.csv" )
    generateCsvQ( id_ptap, '__wpgetqbyptap', "3_Water_Extraction.csv" )



def DataInBAU(id_intake):
    generateCsvTopology( id_intake, '__wpgettopologybycatchment', "0_WI_Topology.csv" )
    generateCsvPerc( id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv" )
    generateCsvDataDis( id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv", 1, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv", 2, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv", 3, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv", 4, '02-OUTPUTS_BaU.csv' )
    generateCsvQ( id_intake, '__wpgetqbycatchmentdis', "3_Water_Extraction.csv" )

def DataInNBS(id_intake):
    generateCsvTopology(id_intake, '__wpgettopologybycatchment', "0_WI_Topology.csv" )
    generateCsvPerc( id_intake, '__wpgetpercentagesbycatchment', "1_WI_Elements_Param.csv" )
    generateCsvDataDis( id_intake, '__wpgetawybycatchment', "2_WI_AWYInputs.csv", 1, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_intake, '__wpgetsedbycatchment', "2_WI_WSedInputs.csv", 2, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_intake, '__wpgetnbycatchment', "2_WI_WNInputs.csv", 3, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_intake, '__wpgetpbycatchment', "2_WI_WPInputs.csv", 4, '02-OUTPUTS_NBS.csv' )
    generateCsvQ( id_intake, '__wpgetqbycatchmentdis', "3_Water_Extraction.csv" )
    

def DataInBAUPTAP(id_ptap):
    generateCsvTopology( id_ptap, '__wpgettopologybyptap', "0_WI_Topology.csv" )
    generateCsvPerc( id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv" )
    generateCsvDataDis( id_ptap, '__wpgetawybyptap', "2_WI_AWYInputs.csv", 1, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_ptap, '__wpgetsedbyptap', "2_WI_WSedInputs.csv", 2, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_ptap, '__wpgetnbyptap', "2_WI_WNInputs.csv", 3, '02-OUTPUTS_BaU.csv' )
    generateCsvDataDis( id_ptap, '__wpgetpbyptap', "2_WI_WPInputs.csv", 4, '02-OUTPUTS_BaU.csv' )
    generateCsvQDisPTAP( "3_Water_Extraction.csv" )

def DataInNBSPTAP(id_ptap):
    generateCsvTopology(id_ptap, '__wpgettopologybyptap', "0_WI_Topology.csv" )
    generateCsvDataDis( id_ptap, '__wpgetpercentagesbyptap', "1_WI_Elements_Param.csv" )
    generateCsvDataDis( id_ptap, '__wpgetawybyptap', "2_WI_AWYInputs.csv", 1, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_ptap, '__wpgetsedbyptap', "2_WI_WSedInputs.csv", 2, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_ptap, '__wpgetnbyptap', "2_WI_WNInputs.csv", 3, '02-OUTPUTS_NBS.csv' )
    generateCsvDataDis( id_ptap, '__wpgetpbyptap', "2_WI_WPInputs.csv", 4, '02-OUTPUTS_NBS.csv' )
    generateCsvQDisPTAP( "3_Water_Extraction.csv" )

