# Funcion para calcular balances en un sistema de captacion con conexiones topologicas
import os
import numpy as np
import csv
from os import environ

ruta = environ["PATH_FILES"]

def execWB(path_data_wb_in, path_data_wb_out):
    print ("path_data_wb_in: ", path_data_wb_in)
    print ("path_data_wb_out: ", path_data_wb_out)
    # Leer archivos base CSV
    # Los archivos CSV deberán ser construidos desde la interfaz WEB con la estructura propuesta

    # Leer archivo de topologia (Col1: From , Col2: To)
    # Archivo topologico basico que indica conexiones Desde (From) a (To)
    Topology    = np.loadtxt(open(os.path.join(path_data_wb_in,'0_WI_Topology.csv')), delimiter=",", skiprows=1)

    # Leer archivo de parametros (Col1: Elemento, Col2: Porcentaje de agua transportada (%),
    # Col 3: Porcentaje de retencion de sedimentos (%) Col 4: Porcentaje de retencion de Nitrogeno (%),
    # Col 5: Porcentaje de retencion de fosforo (%))
    Parameters  = np.loadtxt(open(os.path.join(path_data_wb_in,"1_WI_Elements_Param.csv")), delimiter=",", skiprows=1)
    PWater      = Parameters[:, 1] #Porcentaje de agua que transporta el elemento
    RetSed      = Parameters[:, 2] #Porcentaje de retencion de Sedimentos en el elemento
    RetN        = Parameters[:, 3] #Porcentaje de retencion de Nitrogeno en el elemento
    RetP        = Parameters[:, 4] #Porcentaje de retencion de Fosforo en el elemento

    # Leer archivo de series de entrada de (1) Annual Water Yield (AWY) (m3), (2) Carga de sedimentos (Ton)(3)
    # (3) Carga de Nitrogeno (Kg), (4) Carga de Fosforo (Kg),
    # Col1: Anho, Cada columna de la 2 en adelante representa la serie de tiempo para cada elemento de captacion
    # La Fila 1 indica el ID del elemento de captacion al cual se asigna la serie de tiempo
    # La posicion 1,1 corresponde a un cero que no tiene significado dentro del analisis
    AWYInputs   = np.loadtxt(open(os.path.join(path_data_wb_in,"2_WI_AWYInputs.csv")),  delimiter=",")
    WSedInputs  = np.loadtxt(open(os.path.join(path_data_wb_in,"2_WI_WSedInputs.csv")), delimiter=",")
    WNInputs    = np.loadtxt(open(os.path.join(path_data_wb_in,"2_WI_WNInputs.csv")),   delimiter=",")
    WPInputs    = np.loadtxt(open(os.path.join(path_data_wb_in,"2_WI_WPInputs.csv")),   delimiter=",")

    # Check AWY = 0  -> 0.0031536 m3 = 0.1 l/s
    if np.shape(AWYInputs)[0] == 2:
        AWYInputs[1,1:] = 0.0031536

    # Leer archivo de serie de tiempo de caudal extraido (l/s)
    # Col1: Anho Col 2: QExtract
    QExtract    = np.loadtxt(open(os.path.join(path_data_wb_in,"3_Water_Extraction.csv"), "rb"), delimiter=",")

    ## Correct
    PoPo  = AWYInputs.shape[0]
    PoPis = QExtract.shape[0]
    if PoPo > PoPis:
        Tmp = np.zeros((PoPo, 2))
        Tmp[0:PoPis,:] = QExtract
        for i in range(PoPis,PoPo):
            Tmp[i,0] = i - 1
            Tmp[i,1] = QExtract[PoPis-1,1]

        QExtract = Tmp
    elif PoPo < PoPis:
        QExtract = QExtract[0:PoPo,:]

    '''
    ------------------------------------------------------------------------------------------------------------------------
    '''
    # Leer elemento dondo se realiza la extraccion
    Extract_Element = QExtract[0, 1]

    # Leer archivo para elementos de captacion
    Elements = Parameters[:, 0]
    # Numero de Elementos
    Num_Elements = Elements.shape[0]

    # Matrices de Resultados Inicializadas en Columna [0] con Ceros - Numero de Filas igual a numero de años en archivo
    # de Inputs
    Num_Annos = AWYInputs.shape
    Num_Annos = Num_Annos[0]

    # Vector Fila para almacenar orden de solucion de red topologica inicializado en posicion [0] con Cero
    Order_Solution = 0

    # ALGORITMO PARA ORDEN DE SOLUCION DE RED TOPOLOGICA

    # Busqueda de Elementos Iniciales (Sin Conexiones Aguas Arriba)
    for i in Elements:
        To_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
        if not To_Elements_Pos.size > 0:  # Nodo Inicial!!
            Order_Solution = np.append(Order_Solution, i)

    Initial_Elements = Order_Solution[1:]

    # Variable de control para recorrer la red topologica
    CheckVar = 0
    Temp_Initial_Elements = 0
    k = 0   # Contador para casos de division de red
    Divisiones_Faltantes = 0

    # Orden de solucion de red topologica!!

    while CheckVar == 0:
        CheckVar2 = 0   # Variable de control de 2 o mas entradas en un elemento para escritura

        for i in Initial_Elements:
            From_Elements_Pos = np.asarray(np.where(Topology[:, 0] == i))
            To_Elements = Topology[From_Elements_Pos, 1]
            # El To_Element recibe mas de una entrada?
            Num_To_Elements = To_Elements.shape[1]

            # Chequeo de red topologica dividida
            if Num_To_Elements == 1:    # Sin division en Elemento
                Inputs_To_Element = np.asarray(np.where(Topology[:, 1] == To_Elements))
                Num_Inputs_To_Elements = Inputs_To_Element.shape[1]
                CheckVar3 = 0
            else:   # Division en Elemento
                CheckVar3 = 1   # Division en Elemento
                for j in To_Elements[0]:
                    Inputs_To_Element = np.asarray(np.where(Topology[:, 1] == j))
                    Num_Inputs_To_Elements = Inputs_To_Element.shape[1]
                    if not Num_Inputs_To_Elements == 1:
                        Num_Inputs_To_Elements = 1
                        break
            if Divisiones_Faltantes == 0:
                Division = 0
                k = 0

            # Elementos con solo una conexion aguas arriba!!
            if Num_Inputs_To_Elements == 1:

                if CheckVar3 == 0:
                    Order_Solution = np.append(Order_Solution, To_Elements)
                    Temp_Initial_Elements = np.append(Temp_Initial_Elements, To_Elements)
                    Initial_Elements = Temp_Initial_Elements
                if CheckVar3 == 1:
                    Division = i
                    To_Nodes_Divided_Pos = np.asarray(np.where(Topology[:, 0] == Division))
                    To_Nodes_Divided = Topology[To_Nodes_Divided_Pos, 1]
                    Temp_Initial_Elements = np.append(Temp_Initial_Elements, To_Nodes_Divided)
                    Initial_Elements = Temp_Initial_Elements[1:]
                    for j in Initial_Elements:
                        Order_Solution = np.append(Order_Solution, j)

            # Elementos con varias conexiones aguas arriba!!
            if Num_Inputs_To_Elements > 1:
                CheckVar1 = 0
                # Nodos a los que se conecta aguas arriba el elemento
                From_Elements_Connected = Topology[Inputs_To_Element[1], 0]
                x = np.asarray(np.where(Order_Solution == From_Elements_Connected[0]))
                for j in From_Elements_Connected:
                    x = np.asarray(np.where(Order_Solution == j))
                    if not x.size:
                        CheckVar1 = CheckVar1 + 1
                        Temp_Initial_Elements = np.append(Temp_Initial_Elements, j)
                if CheckVar1 == 0:
                    Temp_Initial_Elements = np.append(Temp_Initial_Elements, To_Elements)

                    if CheckVar2 == 0:
                        Order_Solution = np.append(Order_Solution, To_Elements[0])
                        CheckVar2 = 1

        if not isinstance(Temp_Initial_Elements, int):
            if Temp_Initial_Elements.shape[0] > 1:
                if (np.sum(Temp_Initial_Elements[1:])) / (Temp_Initial_Elements.shape[0]-1) == Temp_Initial_Elements[1]:
                    Initial_Elements = np.reshape(Temp_Initial_Elements[1], 1)
                else:
                    Initial_Elements = Temp_Initial_Elements[1:]
            if np.sum(Temp_Initial_Elements) == 0:
                CheckVar = 2
        else:
            CheckVar = 1

        Temp_Initial_Elements = 0

    # LIMPIAR VECTOR ORDER SOLUTION PARA SOLO PRESENTAR UNA VEZ CADA ELEMENTO
    Pos_for_Delete = 0

    for i in Elements:
        Order_Solution_Pos = np.asarray(np.where(Order_Solution == i))
        if Order_Solution_Pos[0].shape[0] > 1: # Obtener posiciones de elementos que se requieren eliminar
            Pos_for_Delete = np.append(Pos_for_Delete, Order_Solution_Pos[0, 1:])

    Final_Order_Solution = np.delete(Order_Solution, Pos_for_Delete)
    Last_Column = Elements.shape[0]

    if CheckVar == 2:
        Final_Order_Solution = Final_Order_Solution[:Last_Column]

    # CALCULO DE BALANCES EN RED TOPOLOGICA

    # Esquema de calculo conociendo la solucion obtenida de secuencia en el vector Final_Order_Solution

    # (1) Annual Water Yield (AWY)
    AWY_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados con ceros en la fila 1

    for i in Final_Order_Solution:

        # ELEMENTOS INICIALES
        if (np.asarray(np.where(Topology[:, 1] == i))).size == 0:   # Identifica si el elemento es un elemento inicial (Sin conexiones aguas arriba)
            # Posiciones de elementos requeridos para el calculo
            AWYInputs_Pos = np.asarray(np.where(AWYInputs[0, :] == i))  # Posicion en la matriz AWYInputs
            Pwater_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje Agua Trasnporta en Elemento
            # Calculo de AWY
            AWY_Calc = AWYInputs[:, AWYInputs_Pos[0]] * ((PWater[Pwater_Pos[0]]) / 100)
            AWY_Results = np.append(AWY_Results, AWY_Calc, axis=1)

        # ELEMENTO DE EXTRACCION
        if i == Extract_Element:
            # Posiciones de elementos requeridos para el calculo
            Pwater_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje Agua Trasnporta en Elemento
            # Calculo de AWY
            AWY_Calc = QExtract[:, 1] * ((60 * 60 * 24 * 365) / 1000) * ((PWater[Pwater_Pos[0]]) / 100)
            AWY_Calc = np.reshape(AWY_Calc, (Num_Annos, 1))
            AWY_Results = np.append(AWY_Results, AWY_Calc, axis=1)

        # ELEMENTOS COMUNES QUE INTEGRAN EL SISTEMA (ELEMENTOS CON FROM NODES QUE NO SON DE EXTRACCION)
        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                AWYInputs_Pos = np.asarray(np.where(AWYInputs[0, :] == i))  # Posicion en la matriz AWYInputs
                Pwater_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje Agua Trasnporta en Elemento
                # Calculo de AWY
                # Identificar todos los elementos aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Elements = Topology[Upstream_Elements_Pos, 0]
                AWY_Calc = 0    # Inicializa variable para acumular

                for j in Upstream_Elements[0]:
                    AWY_Results_Pos = np.asarray(np.where(Final_Order_Solution == j)) + 1
                    AWY_Calc = (AWY_Calc + AWY_Results[:, AWY_Results_Pos[0]])

                AWY_Calc = AWY_Calc * ((PWater[Pwater_Pos[0]]) / 100)   # Multiplica por porcentaje de transporte de Q
                AWY_Results = np.append(AWY_Results, AWY_Calc, axis=1)

    # (2) Sedimentos (Sed) (Carga de Sedimentos = WSed y Concentracion de Sedimentos CSed)
    WSed_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Carga de Sedimentos a la entrada del elemento
    WSed_Ret_Results = np.zeros((Num_Annos, 1)) # Iniicaliza matriz de resultados Carga de Sedimentos retenida en el elemento
    CSed_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Concentracion Sedimentos
    Divided_Elements = np.zeros(1)   # Inicializa vector que contiene nodos de division

    for i in Final_Order_Solution:
        Check_Division = 0  # Inicializa variable de chequeo de division
        # ELEMENTOS INICIALES
        if (np.asarray(np.where(Topology[:, 1] == i))).size == 0:   # Identifica si el elemento es un elemento inicial (Sin conexiones aguas arriba)
            # Posiciones de elementos requeridos para el calculo
            WSedInputs_Pos = np.asarray(np.where(WSedInputs[0, :] == i))  # Posicion en la matriz WSedInputs
            RetSed_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Retencion de Sedimentos en Elemento
            # Calculo de Carga de sedimentos a la entrada del elemento
            WSed_Calc = WSedInputs[:, WSedInputs_Pos[0]]
            WSed_Results = np.append(WSed_Results, WSed_Calc, axis=1)

            # Calculo de carga de sedimentos retenida en el elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            WSed_Ret_Calc = WSed_Results[:, Results_Pos[0]] * ((RetSed[RetSed_Pos[0]]) / 100)
            WSed_Ret_Results = np.append(WSed_Ret_Results, WSed_Ret_Calc, axis=1)
            # Calculo de Concentracion de Sedimentos
            AWY = AWY_Results[:, Results_Pos[0]]
            WSed = WSed_Results[:, Results_Pos[0]]
            CSed_Calc = (WSed / AWY) * (1000 * 1000) # Concentracion en miligramos por litro (1000 * 1000) Factor de conversion
            CSed_Results = np.append(CSed_Results, CSed_Calc, axis=1)

        # ELEMENTO DE EXTRACCION
        if i == Extract_Element:
            # Posiciones de elementos requeridos para el calculo
            RetSed_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Sedimentos retenidos en Elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            # Identificar el elemento aguas arriba del elemento de analisis
            Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
            Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
            Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
            # Calculo de Concentracion de sedimentos (La Concentracion Aguas Arriba y Aguas Abajo se Iguala
            CSed_Calc = CSed_Results[:, Upstream_Pos[0]]
            CSed_Results = np.append(CSed_Results, CSed_Calc, axis=1)
            # Calculo de Carga de Sedimentos (La carga se calcula considerando el caudal de extraccion)
            QExtract = QExtract[:, 1]
            QExtract = np.reshape(QExtract, (Num_Annos, 1))
            WSed_Calc = ((CSed_Calc * QExtract) * ((60 * 60 * 24 * 365) / 1000000000) * ((PWater[Pwater_Pos[0]]) / 100))  # Carga en Toneladas
            WSed_Results = np.append(WSed_Results, WSed_Calc, axis=1)
            # Calculo de carga de sedimentos retenida en el elemento
            WSed_Ret_Calc = WSed_Results[:, Results_Pos[0]] * ((RetSed[RetSed_Pos[0]]) / 100)
            WSed_Ret_Results = np.append(WSed_Ret_Results, WSed_Ret_Calc, axis=1)

        # IDENTIFICAR SI EL ELEMENTO ES UN ELEMENTO DE DIVISION
        Element_Pos = np.asarray(np.where(Topology[:, 0] == i))
        Divided_Elements_ID = Topology[Element_Pos, 1]
        if (Divided_Elements_ID[0].shape[0]) > 1:
            Divided_Elements = np.append(Divided_Elements, Divided_Elements_ID)

        Divided = np.asarray(np.where(Divided_Elements == i))

        if Divided.shape[1]:
            Check_Division = 1

        # ELEMENTOS COMUNES QUE INTEGRAN EL SISTEMA (ELEMENTOS CON FROM NODES QUE NO SON DE EXTRACCION) Y QUE NO ESTAN AGUAS ABAJO DE UNA DIVISION

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 0:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetSed_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Sedimentos Retenidos en Elemento

                # Identificar todos los elementos aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Elements = Topology[Upstream_Elements_Pos, 0]
                WSed_Calc = 0    # Inicializa variable para acumular

                # Calcular carga de sedimentos a la entrada del elemento
                for j in Upstream_Elements[0]:
                    Results_Pos = np.asarray(np.where(Final_Order_Solution == j)) + 1
                    WSed_Calc = (WSed_Calc + (WSed_Results[:, Results_Pos[0]]-WSed_Ret_Results[:, Results_Pos[0]]))

                WSed_Results = np.append(WSed_Results, WSed_Calc, axis=1)

                # Calcular Concentracion de Sedimentos
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                AWY = AWY_Results[:, Results_Pos[0]]
                WSed = WSed_Results[:, Results_Pos[0]]
                CSed_Calc = (WSed / AWY) * (1000 * 1000)  # Concentracion en miligramos por litro (1000 * 1000) Factor de conversion
                CSed_Results = np.append(CSed_Results, CSed_Calc, axis=1)

                # Calculo de carga de sedimentos retenida en el elemento
                WSed_Ret_Calc = WSed_Results[:, Results_Pos[0]] * ((RetSed[RetSed_Pos[0]]) / 100)
                WSed_Ret_Results = np.append(WSed_Ret_Results, WSed_Ret_Calc, axis=1)

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 1:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetSed_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Sedimentos retenidos en Elemento
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                # Identificar el elemento aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
                Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
                # Calculo de Concentracion de sedimentos (La Concentracion Aguas Arriba y Aguas Abajo se Iguala
                CSed_Calc = CSed_Results[:, Upstream_Pos[0]]
                CSed_Results = np.append(CSed_Results, CSed_Calc, axis=1)
                # Calculo de Carga de Sedimentos
                AWY = AWY_Results[:, Results_Pos[0]]
                WSed_Calc = (CSed_Calc * AWY) / (1000 * 1000)  # Carga en Toneladas
                WSed_Results = np.append(WSed_Results, WSed_Calc, axis=1)
                # Calculo de carga de sedimentos retenida en el elemento
                WSed_Ret_Calc = WSed_Results[:, Results_Pos[0]] * ((RetSed[RetSed_Pos[0]]) / 100)
                WSed_Ret_Results = np.append(WSed_Ret_Results, WSed_Ret_Calc, axis=1)

    # (3) Nitrogeno (N) (Carga de Nitrogeno = WN y Concentracion de Nitrogeno CN)
    WN_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Carga de Nitrogeno a la entrada del elemento
    WN_Ret_Results = np.zeros((Num_Annos, 1)) # Iniicaliza matriz de resultados Carga de Nitrogeno retenida en el elemento
    CN_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Concentracion Nitrogeno
    Divided_Elements = np.zeros(1)   # Inicializa vector que contiene nodos de division

    for i in Final_Order_Solution:
        Check_Division = 0  # Inicializa variable de chequeo de division
        # ELEMENTOS INICIALES
        if (np.asarray(np.where(Topology[:, 1] == i))).size == 0:   # Identifica si el elemento es un elemento inicial (Sin conexiones aguas arriba)
            # Posiciones de elementos requeridos para el calculo
            WNInputs_Pos = np.asarray(np.where(WNInputs[0, :] == i))  # Posicion en la matriz WNInputs
            RetN_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Retencion de Nitrogeno en Elemento
            # Calculo de Carga de nitrogeno a la entrada del elemento
            WN_Calc = WNInputs[:, WNInputs_Pos[0]]
            WN_Results = np.append(WN_Results, WN_Calc, axis=1)

            # Calculo de Carga de Nitrogeno retenida en el elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            WN_Ret_Calc = WN_Results[:, Results_Pos[0]] * ((RetN[RetN_Pos[0]]) / 100)
            WN_Ret_Results = np.append(WN_Ret_Results, WN_Ret_Calc, axis=1)
            # Calculo de Concentracion de Nitrogeno
            AWY = AWY_Results[:, Results_Pos[0]]
            WN = WN_Results[:, Results_Pos[0]]
            CN_Calc = (WN / AWY) * (1000) # Concentracion en miligramos por litro (1000) Factor de conversion
            CN_Results = np.append(CN_Results, CN_Calc, axis=1)

        # ELEMENTO DE EXTRACCION
        if i == Extract_Element:
            # Posiciones de elementos requeridos para el calculo
            RetN_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Sedimentos retenidos en Elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            # Identificar el elemento aguas arriba del elemento de analisis
            Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
            Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
            Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
            # Calculo de Concentracion de Nitrogeno (La Concentracion Aguas Arriba y Aguas Abajo se Iguala
            CN_Calc = CN_Results[:, Upstream_Pos[0]]
            CN_Results = np.append(CN_Results, CN_Calc, axis=1)
            # Calculo de Carga de Nitrogeno (La carga se calcula considerando el caudal de extraccion)
            #QExtract = QExtract[:, 1]
            #QExtract = np.reshape(QExtract, (Num_Annos, 1))
            WN_Calc = ((CN_Calc * QExtract) * ((60 * 60 * 24 * 365) / 1000000) * ((PWater[Pwater_Pos[0]]) / 100))  # Carga en Kilogramos
            WN_Results = np.append(WN_Results, WN_Calc, axis=1)
            # Calculo de carga de nitrogeno retenido en el elemento
            WN_Ret_Calc = WN_Results[:, Results_Pos[0]] * ((RetN[RetN_Pos[0]]) / 100)
            WN_Ret_Results = np.append(WN_Ret_Results, WN_Ret_Calc, axis=1)

        # IDENTIFICAR SI EL ELEMENTO ES UN ELEMENTO DE DIVISION
        Element_Pos = np.asarray(np.where(Topology[:, 0] == i))
        Divided_Elements_ID = Topology[Element_Pos, 1]
        if (Divided_Elements_ID[0].shape[0]) > 1:
            Divided_Elements = np.append(Divided_Elements, Divided_Elements_ID)

        Divided = np.asarray(np.where(Divided_Elements == i))

        if Divided.shape[1]:
            Check_Division = 1

        # ELEMENTOS COMUNES QUE INTEGRAN EL SISTEMA (ELEMENTOS CON FROM NODES QUE NO SON DE EXTRACCION) Y QUE NO ESTAN AGUAS ABAJO DE UNA DIVISION

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 0:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetN_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Nitrogeno Retenido en Elemento

                # Identificar todos los elementos aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Elements = Topology[Upstream_Elements_Pos, 0]
                WN_Calc = 0    # Inicializa variable para acumular

                # Calcular carga de nitrogeno a la entrada del elemento
                for j in Upstream_Elements[0]:
                    Results_Pos = np.asarray(np.where(Final_Order_Solution == j)) + 1
                    WN_Calc = (WN_Calc + (WN_Results[:, Results_Pos[0]]-WN_Ret_Results[:, Results_Pos[0]]))

                WN_Results = np.append(WN_Results, WN_Calc, axis=1)

                # Calcular Concentracion de nitrogeno
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                AWY = AWY_Results[:, Results_Pos[0]]
                WN = WN_Results[:, Results_Pos[0]]
                CN_Calc = (WN / AWY) * (1000)  # Concentracion en miligramos por litro (1000) Factor de conversion
                CN_Results = np.append(CN_Results, CN_Calc, axis=1)

                # Calculo de carga de nitrogeno retenido en el elemento
                WN_Ret_Calc = WN_Results[:, Results_Pos[0]] * ((RetN[RetN_Pos[0]]) / 100)
                WN_Ret_Results = np.append(WN_Ret_Results, WN_Ret_Calc, axis=1)

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 1:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetN_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Nitrogeno retenidos en Elemento
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                # Identificar el elemento aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
                Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
                # Calculo de Concentracion de Nitrogeno (La Concentracion Aguas Arriba y Aguas Abajo se Igualan)
                CN_Calc = CN_Results[:, Upstream_Pos[0]]
                CN_Results = np.append(CN_Results, CN_Calc, axis=1)
                # Calculo de Carga de Nitrogeno
                AWY = AWY_Results[:, Results_Pos[0]]
                WN_Calc = (CN_Calc * AWY) / (1000)  # Carga en Kilogramos
                WN_Results = np.append(WN_Results, WN_Calc, axis=1)
                # Calculo de carga de sedimentos retenida en el elemento
                WN_Ret_Calc = WN_Results[:, Results_Pos[0]] * ((RetN[RetN_Pos[0]]) / 100)
                WN_Ret_Results = np.append(WN_Ret_Results, WN_Ret_Calc, axis=1)

    # (4) Fosforo (P) (Carga de Fosforo = WP y Concentracion de Fosforo (CP)
    WP_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Carga de Fosforo a la entrada del elemento
    WP_Ret_Results = np.zeros((Num_Annos, 1)) # Iniicaliza matriz de resultados Carga de Fosforo retenida en el elemento
    CP_Results = np.zeros((Num_Annos, 1))  # Inicializa matriz de resultados Concentracion Fosforo
    Divided_Elements = np.zeros(1)   # Inicializa vector que contiene nodos de division

    for i in Final_Order_Solution:
        Check_Division = 0  # Inicializa variable de chequeo de division
        # ELEMENTOS INICIALES
        if (np.asarray(np.where(Topology[:, 1] == i))).size == 0:   # Identifica si el elemento es un elemento inicial (Sin conexiones aguas arriba)
            # Posiciones de elementos requeridos para el calculo
            WPInputs_Pos = np.asarray(np.where(WPInputs[0, :] == i))  # Posicion en la matriz WNInputs
            RetP_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Retencion de Fosforo en Elemento
            # Calculo de Carga de fosforo a la entrada del elemento
            WP_Calc = WPInputs[:, WPInputs_Pos[0]]
            WP_Results = np.append(WP_Results, WP_Calc, axis=1)

            # Calculo de Carga de Fosforo retenida en el elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            WP_Ret_Calc = WP_Results[:, Results_Pos[0]] * ((RetP[RetP_Pos[0]]) / 100)
            WP_Ret_Results = np.append(WP_Ret_Results, WP_Ret_Calc, axis=1)
            # Calculo de Concentracion de Fosforo
            AWY = AWY_Results[:, Results_Pos[0]]
            WP = WP_Results[:, Results_Pos[0]]
            CP_Calc = (WP / AWY) * (1000) # Concentracion en miligramos por litro (1000) Factor de conversion
            CP_Results = np.append(CP_Results, CP_Calc, axis=1)

        # ELEMENTO DE EXTRACCION
        if i == Extract_Element:
            # Posiciones de elementos requeridos para el calculo
            RetP_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Sedimentos retenidos en Elemento
            Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
            # Identificar el elemento aguas arriba del elemento de analisis
            Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
            Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
            Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
            # Calculo de Concentracion de Nitrogeno (La Concentracion Aguas Arriba y Aguas Abajo se Iguala
            CP_Calc = CP_Results[:, Upstream_Pos[0]]
            CP_Results = np.append(CP_Results, CP_Calc, axis=1)
            # Calculo de Carga de Nitrogeno (La carga se calcula considerando el caudal de extraccion)
            #QExtract = QExtract[:, 1]
            #QExtract = np.reshape(QExtract, (Num_Annos, 1))
            WP_Calc = ((CP_Calc * QExtract) * ((60 * 60 * 24 * 365) / 1000000) * ((PWater[Pwater_Pos[0]]) / 100))  # Carga en Kilogramos
            WP_Results = np.append(WP_Results, WP_Calc, axis=1)
            # Calculo de carga de fosforo retenido en el elemento
            WP_Ret_Calc = WP_Results[:, Results_Pos[0]] * ((RetP[RetP_Pos[0]]) / 100)
            WP_Ret_Results = np.append(WP_Ret_Results, WP_Ret_Calc, axis=1)

        # IDENTIFICAR SI EL ELEMENTO ES UN ELEMENTO DE DIVISION
        Element_Pos = np.asarray(np.where(Topology[:, 0] == i))
        Divided_Elements_ID = Topology[Element_Pos, 1]
        if (Divided_Elements_ID[0].shape[0]) > 1:
            Divided_Elements = np.append(Divided_Elements, Divided_Elements_ID)

        Divided = np.asarray(np.where(Divided_Elements == i))

        if Divided.shape[1]:
            Check_Division = 1

        # ELEMENTOS COMUNES QUE INTEGRAN EL SISTEMA (ELEMENTOS CON FROM NODES QUE NO SON DE EXTRACCION) Y QUE NO ESTAN AGUAS ABAJO DE UNA DIVISION

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 0:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetP_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Fosforo Retenido en Elemento

                # Identificar todos los elementos aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Elements = Topology[Upstream_Elements_Pos, 0]
                WP_Calc = 0    # Inicializa variable para acumular

                # Calcular carga de nitrogeno a la entrada del elemento
                for j in Upstream_Elements[0]:
                    Results_Pos = np.asarray(np.where(Final_Order_Solution == j)) + 1
                    WP_Calc = (WP_Calc + (WP_Results[:, Results_Pos[0]]-WP_Ret_Results[:, Results_Pos[0]]))

                WP_Results = np.append(WP_Results, WP_Calc, axis=1)

                # Calcular Concentracion de nitrogeno
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                AWY = AWY_Results[:, Results_Pos[0]]
                WP = WP_Results[:, Results_Pos[0]]
                CP_Calc = (WP / AWY) * (1000)  # Concentracion en miligramos por litro (1000) Factor de conversion
                CP_Results = np.append(CP_Results, CP_Calc, axis=1)

                # Calculo de carga de fosforo retenido en el elemento
                WP_Ret_Calc = WP_Results[:, Results_Pos[0]] * ((RetP[RetP_Pos[0]]) / 100)
                WP_Ret_Results = np.append(WP_Ret_Results, WP_Ret_Calc, axis=1)

        if (np.asarray(np.where(Topology[:, 1] == i))).size > 0 and Check_Division == 1:
            if not i == Extract_Element:
                # Posiciones de elementos requeridos para el calculo
                RetP_Pos = np.asarray(np.where(Parameters[:, 0] == i))  # Buscar Porcentaje de Fosforo retenido en Elemento
                Results_Pos = np.asarray(np.where(Final_Order_Solution == i)) + 1
                # Identificar el elemento aguas arriba del elemento de analisis
                Upstream_Elements_Pos = np.asarray(np.where(Topology[:, 1] == i))
                Upstream_Element = Topology[Upstream_Elements_Pos[0], 0]
                Upstream_Pos = np.asarray(np.where(Final_Order_Solution == Upstream_Element)) + 1
                # Calculo de Concentracion de Fosforo (La Concentracion Aguas Arriba y Aguas Abajo se Igualan)
                CP_Calc = CP_Results[:, Upstream_Pos[0]]
                CP_Results = np.append(CP_Results, CP_Calc, axis=1)
                # Calculo de Carga de Nitrogeno
                AWY = AWY_Results[:, Results_Pos[0]]
                WP_Calc = (CP_Calc * AWY) / (1000)  # Carga en Kilogramos
                WP_Results = np.append(WN_Results, WP_Calc, axis=1)
                # Calculo de carga de Fosforo retenido en el elemento
                WP_Ret_Calc = WP_Results[:, Results_Pos[0]] * ((RetP[RetP_Pos[0]]) / 100)
                WP_Ret_Results = np.append(WP_Ret_Results, WP_Ret_Calc, axis=1)

    # Limpiar matrices de resultados (No considerar Columna 1 (Posicion [0]) ni Fila 1 [Posicion [0] de matrices)
    AWY_Results = AWY_Results[1:, 1:]
    CSed_Results = CSed_Results[1:, 1:]
    WSed_Results = WSed_Results[1:, 1:]
    WSed_Ret_Results = WSed_Ret_Results[1:, 1:]
    CN_Results = CN_Results[1:, 1:]
    WN_Results = WN_Results[1:, 1:]
    WN_Ret_Results = WN_Ret_Results[1:, 1:]
    CP_Results = CP_Results[1:, 1:]
    WP_Results = WP_Results[1:, 1:]
    WP_Ret_Results = WP_Ret_Results[1:, 1:]


    """
    Check para verificar volumen de extracción de agua ingresado por el usuario
    """
    # AWY elemento de captación
    Posi  = np.where(Final_Order_Solution == Extract_Element)
    if np.sum((Final_Order_Solution == Extract_Element)) == 0:
        # Caso Particular - PTAP
        myFile = open(os.path.join(path_data_wb_out, 'SystemErrors.txt'), 'w', newline='')
        with myFile:
            Choco = "0"
            myFile.writelines(Choco)
            myFile.close()

    else: 
        # Casp Particular - Captación
        Data1 = AWY_Results[:,Posi[0][0]]

        # AWY Elemento conectado a la captación
        Posi  = np.where(Topology[:,1] == Extract_Element)
        Posi  = np.where(Final_Order_Solution == Topology[Posi[0],0])
        Data2 = AWY_Results[:,Posi[0][0]]
        for i in range(1,len(Posi)):
            Data2 = Data2 + AWY_Results[:,Posi[0][i]]

        Check = []
        for i in range(0,len(Data1)):
            Check.append(Data2[i] < Data1[i])

        Check = np.sum(Check)

        myFile = open(os.path.join(path_data_wb_out, 'SystemErrors.txt'), 'w', newline='')
        with myFile:
            if Check > 0:
                Choco = "1"
            else:
                Choco = "0"

            myFile.writelines(Choco)
            myFile.close()


    # Annual Water Yield (AWY) / Caudales Trasportados en cada Elemento
    myFile = open(os.path.join(path_data_wb_out,'Q_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(AWY_Results)

    # Concentracion de sedimentos
    myFile = open(os.path.join(path_data_wb_out,'CSed_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(CSed_Results)

    # Carga de sedimentos
    myFile = open(os.path.join(path_data_wb_out,'WSed_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WSed_Results)

    # Carga de sedimentos retenidos
    myFile = open(os.path.join(path_data_wb_out,'WSed_Ret_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WSed_Ret_Results)

    # Concentracion de nitrogeno
    myFile = open(os.path.join(path_data_wb_out,'CN_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(CN_Results)

    # Carga de nitrogeno
    myFile = open(os.path.join(path_data_wb_out,'WN_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WN_Results)

    # Carga de nitrogeno retenido
    myFile = open(os.path.join(path_data_wb_out,'WN_Ret_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WN_Ret_Results)

    # Concentracion de fosforo
    myFile = open(os.path.join(path_data_wb_out,'CP_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(CP_Results)

    # Carga de fosforo
    myFile = open(os.path.join(path_data_wb_out,'WP_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WP_Results)

    # Carga de fosforo retenido
    myFile = open(os.path.join(path_data_wb_out,'WP_Ret_Results.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(WP_Ret_Results)

    # RESULTS ORDER
    #Order_Solution = Order_Solution[1:Last_Column]
    Order_Results = np.reshape(Final_Order_Solution, (1, Elements.shape[0]))
    myFile = open(os.path.join(path_data_wb_out,'Results_Order.csv'), 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(Order_Results)

    print('Proceso WI_Balance finalizado con exito...')
    print('Se han creado los CSV de resultados!!')
