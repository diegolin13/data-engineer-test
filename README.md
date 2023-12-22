# Prueba técnica data engineer

Se desarrolló un proceso ETL para un archivo que simula el historial de transacciones de una empresa ficticia.
El proceso se divide en dos partes:

A.- El primer proceso se encarga de hacer una limpieza a la data cruda y depositar el resultado en una capa intermedia de nombre curated. Para saber qué mejoras hacer, se realizó un pre-análisis en un Notebook (https://colab.research.google.com/drive/14BWRFPJmJ0HBjSm9DjT5ov2glDgkFq3X?usp=sharing).

    Como resultado de este pre-análisis se decidió lo siguiente:

    1.- A las columnas que contienen strings se quitaron espacios al principio y al final
    2.- Las columnas id, name y company_id que contengan valores nulos, se separaron a un csv de excepciones para su posterior analisis y reportarlo con el área correspondiente, ya que podrían afectar en el resultado final. (Estas excepciones se mandaron a la capa curada con el nombre de data_prueba_tecnica_err.csv)
    3.- Para la columna amount se evalua que su contenido realmente sea un número, en caso contrario se coloca un valor 0.
    4.- La columna status solo puede contener estos valores, 'refunded', 'charged_back', 'pre_authorized', 'paid', 'partially_refunded', 'pending_payment', 'expired', 'voided', de lo contrario se coloca la leyenda 'not_valid_status'.
    5.- Se asegura que todos los valores de las columnas created_at y paid_at cuenten con un mismo formato, en caso de que no se corrige la fecha al formato dsdeado.


B.- El segundo proceso toma la data limpia de la capa curada y realiza funciones de agrupación y agregación para conocer las ventas por día y por nombre de empresa. El resultado de estas agregaciones fue depositado en la capa augmented.
Nota: Se consideró como venta aquellas transacciones con status paid.

# Instrucciones para ejecutar el ETL

Requisitos: Tener Docker instalado y clonar este repositorio.

1.- Posicinoarse en la carpeta ejercicio1  
2.- Generar la imagen a partir del Dockerfile docker build -t <NOMBRE_IMAGEN> .  
3.- Generar un contenedor a partir de esta imagen y ejecutarlo docker run -it --rm <NOMBRE_IMAGEN:etiqueta>  
4.- Al finalizar el proceso, dentro del contenedor en la carpeta /app debió haberse generado dos directorios nuevos curated y augmented  

![Alt text](https://private-user-images.githubusercontent.com/63220767/292305373-24566294-1b7a-4f4e-a93d-01d11d1b9195.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTEiLCJleHAiOjE3MDMxODg0MTMsIm5iZiI6MTcwMzE4ODExMywicGF0aCI6Ii82MzIyMDc2Ny8yOTIzMDUzNzMtMjQ1NjYyOTQtMWI3YS00ZjRlLWE5M2QtMDFkMTFkMWI5MTk1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFJV05KWUFYNENTVkVINTNBJTJGMjAyMzEyMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjMxMjIxVDE5NDgzM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQ2N2VjN2NlNjYzMGMzOWFhZWRlYzkzZTU2MjVmNDFlZjIwMzlhMzZjZDY3MjE5OGQ2MWVjMGIzZDA1NDc2YTkmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.NTeE1S8AioYCf7WhpcRCungzKl1JJjHziKUw1ASHJsE)

## Preguntas y respuestas del ejercicio 1

1.- Para los ids nulos ¿Qué sugieres hacer con ellos ?

R: Las columnas que contengan id nulos son con considerados registros corruptos que pueden afectar el resultado del reporte, por lo tanto se decidió separarlos en un csv diferente para analizarlo y reportar esta anomalía de ingesta, ya que cada transaccion debería ser única.  

2.- Considerando las columnas name y company_id ¿Qué inconsistencias notas y como las mitigas?  

R: Analizando estas columnas se detectó que hay algunos valores Nulos y otros que parecen tener algun "error de dedo" tanto para company_id  con valores como '********' como para la columna name con valores como: 'MiPas0xFFFF'.  

Se decidió que los valores nulos sean considerados como registros corruptos y fueron separados en la carpeta de errores en capa curada.
Para los valores con "error de dedo", al no contar con una regla de negocio, se dejaron tal cual lo que provoca que sean consideradas como empresas diferentes. Se puede considerar este punto como una deuda técnica para definir una regla y saber qué hacer con estos registros.  

3.- Para el resto de los campos ¿Encuentras valores atípicos y de ser así cómo procedes?  

R: La columna de created_at cuenta con una fecha que tiene un formato yyyMMdd (sin guiones) a diferencia del resto que cuentan con un formato yyyy-MM-dd. Para corregirlo, en el proceso de limpieza esta columna evalua que las fechas cuenten con este formato yyyy-MM-dd en caso de que no se pasa del formato yyyMMdd al formato yyyy-MM-dd.  

Por otro lado la columna de amount es de tipo Double, pero existen valores que se consideran como Infinity (Probablemente cuentan con demasiados decimales) y podría afectar al proceso. Entonces en esta columna se valida que su valor sea realmente un numero en caso contrario se le coloca un valor 0 para que no afecten los resultados.  

4.- ¿Qué mejoras propondrías a tu proceso ETL para siguientes versiones?

R: Tener una correcta definición por parte de negocio de cómo se considera una venta, que criterios debe cumplir la transacción para poder ser tomado en cuenta como una venta. Por otro lado sería ideal ejecutar el proceso desde un orquestador como Airflow para que primero se corra el ETL de limpieza y al terminar se ejecute el ETL de reportes. Se hizo el intento pero tuve problemas con la instalación de pyspark dentro del contenedor de AirFLow (Sigo investigando como solucionarlo)

# Ejercicio 2

En el directorio de ejercicio2 se encontrará el desarrollo de la segunda parte de la prueba.