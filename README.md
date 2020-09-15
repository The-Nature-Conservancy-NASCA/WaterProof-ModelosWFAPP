# Modelos de geoprocesamiento WFAPP

Modelos desarrollados dentro del marco del proyecto entre TNC y Skaphe para el análisis, desarrollo e implementación de la Water Funds App.

## Instalación

Use el administrador de paquetes [pip](https://pip.pypa.io/en/stable/) para instalar las dependencias del proyecto.

```bash
pip install -r requirements.txt
```

## Uso
### Snap (linear referencing) al punto de acumulación más cercano
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
El argumento -d indica que se utiliza la delimitación, los parametros xy indican la latitud y longitud, respectivamente. Como salida se obtiene un archivo en formato shapefile llamado catchment.shp.

## Licencia
[MIT](https://choosealicense.com/licenses/mit/)