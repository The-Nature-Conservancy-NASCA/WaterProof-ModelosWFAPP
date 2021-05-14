# Modelos de geoprocesamiento WFAPP

Modelos desarrollados dentro del marco del proyecto entre TNC y Skaphe para el an�lisis, desarrollo e implementaci�n de la Water Funds App.

## Instalaci�n

Use el administrador de paquetes [pip](https://pip.pypa.io/en/stable/) para instalar las dependencias del proyecto.

```bash
pip install -r requirements.txt
```

## Uso
### Snap (linear referencing) al punto de acumulaci�n m�s cercano
A partir de un conjunto de coordenadas (longitud, latitud) se determinan las coordenadas del punto corregido


```bash
python delineate.py -s x y
```
El argumento -s indica que se utiliza snap, los parametros xy indican la latitud y longitud, respectivamente.
### Delimitar cuenca a partir de  coordenadas
A partir de un conjunto de coordenadas (longitud, latitud) se halla el trazado de la cuenca en formato shapefile


```bash
python delineate.py -d x y
```
El argumento -d indica que se utiliza la delimitaci�n, los parametros xy indican la latitud y longitud, respectivamente. Como salida se obtiene un archivo en formato shapefile llamado catchment.shp.

Se pueden ejecutar dichos procedimientos, tambi�n mediante un llamado a un API REST implementada utilizando la dependencia FastAPI. 

### Ejecuci�n mediante API REST

Para iniciar el API REST se debe escribir el siguiente comando:

```bash
python startup.py
```

Inmediatamente sube el API; y genera dos endpoint desde los cuales se pueden ejecutar los procedimientos de snap y delimitar cuenca. Los dos procedmientios se realizan mediante peticiones tipo GET:

-  /snapPoint?x=?&y=?, donde los signos de interrogaci�n se refieren a las coordenadas longitud y latitud, respectivamente. Esta url ejecuta el procdimiento de snap, y devuelve un fichero json con las coordenadas corregidas (x_snap,y_snap)
- /delineateCatchment?x=?&y=?, donde los signos de interrogaci�n se refieren a las coordenadas longitud y latitud, respectivamente. Esta url ejecuta el procedimiento para delimiat una cuenca a partir de unas coordenadas corregidas; se retorna un geojson que puede ser abierto en cualquier software SIG de escritorio en navegadores web, con el poligono de la cuenca delimitada.


### Init submodules (first time)

```bash
git submodule update --init
```

### Enable Debug

install in local interpreter libraries in rev_requirements.txt

## Licencia
[MIT](https://choosealicense.com/licenses/mit/)