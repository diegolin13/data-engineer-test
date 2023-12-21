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
![Resultado del ETL](https://drive.google.com/file/d/1rwiH3cwqLH0h-nWLgQk49GpqR1gsS8H2/view?usp=sharing)

## Preguntas y respuestas del ejercicio 1

1.- Para los ids nulos ¿Qué sugieres hacer con ellos ?

R: Las columnas que contengan id nulos son con considerados registros corruptos que pueden afectar el resultado del reporte, por lo tanto se decidió separarlos en un csv diferente para analizarlo y reportar esta anomalía de ingesta, ya que cada transaccion debería ser única.