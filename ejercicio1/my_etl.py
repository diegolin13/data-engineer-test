"""
El objetivo de este pipeline es tomar un insumo de la capa raw, hacer una limpieza a este archivo
y depositarlo en una capa intermedia de nombre curada, para poder realizar operaciones de agrupación y agregación
en una capa superior de nombre Augmented.
"""

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, when, isnan, lit, to_date, date_format, sum


"""
En este método se excluyen las filas en donde la columna name y company_id contengan un valor NULL
mismas que serán separadas en un DF diferente que serán manejados como excepciones para su postrior 
análisis y correción.

Se retorna un DF ya sin valores NULL para estas columnas
"""
def drop_nulls(origin_df, spark):
    filter_expr = 'name is null or company_id is null'
    df_null = origin_df.filter(filter_expr)
    if df_null.count():
        df_null.coalesce(1).write.csv('./curated/data_prueba_tecnica_err.csv', header=True, mode="overwrite")
    origin_df = origin_df.dropna(how='any', subset=['name', 'company_id', 'id'])
    return origin_df


"""
Este método se encarga de quitar espacios al principio y al final en las columnas con tipo de dato string
y se retorna un DF con estas adecuaciones
"""
def fix_strings(origin_df):
    origin_df = origin_df.withColumn('id', trim(col('id')))
    origin_df = origin_df.withColumn('name', trim(col('name')))
    origin_df = origin_df.withColumn('company_id', trim(col('company_id')))
    origin_df = origin_df.withColumn('status', trim(col('status')))
    return origin_df



"""
Aquí se valida que la columna amount realmente contenga números.

En caso de encontrar un valor que no sea número, se reemplazará dicho valor por un 0.

Se retorna un DF con la columna amount corregida
"""
def fix_numbers(origin_df):
    origin_df = origin_df.withColumn('amount', when(isnan('amount') | (col('amount') == float('inf')), 0).otherwise(col('amount')))
    return origin_df


"""
Se hace una validación en donde se evalúa el valor de la columna de status para que solo contenga opciones válidas definidas por negocio.
En caso de encontrar alguna que no corresponda, se colocará la leyenda not_valid_status.
Se retorna un DF con estas correciones
"""
def fix_status(origin_df):
    valid_status = ['refunded', 'charged_back', 'pre_authorized', 'paid', 'partially_refunded', 'pending_payment', 'expired', 'voided']
    origin_df = origin_df.withColumn('status', when(col('status').isin(valid_status), col('status')).otherwise(lit('not_valid_status')))
    return origin_df


""""
Se corrigen los formatos de fechas.

"""
def fix_dates(origin_df, columna):
    formato_original = 'yyyyMMdd'
    formato_objetivo = 'yyyy-MM-dd'
    origin_df = origin_df.withColumn(
        columna,
        when(
            to_date(col(columna), formato_original).isNotNull(), 
            date_format(to_date(col(columna), formato_original), formato_objetivo) 
        ).otherwise(
            col(columna)
        )
    )
    return origin_df


"""
Se realizan funciones de agrupación y agregación para conocer las ventas por cliente y por día.

NOTA: Se consideró como venta aquellas transacciones con status paid.
"""
def agg_sales(curated_df):
    curated_df = curated_df.filter('status == "paid"')
    curated_df = curated_df.groupBy("name", "created_at").agg(sum("amount").alias('total'))
    curated_df = curated_df.withColumn('created_at', to_date('created_at'))
    return curated_df

    


"""
Punto de partida.

Se levanta una sesión de spark y se carga el insumo como un DataFrame
"""
def main():
    spark = SparkSession.builder.appName('test').getOrCreate()
    #=========================CURATED===================================================
    df = spark.read.csv('./raw/data_prueba_tecnica.csv', header=True, inferSchema=True)
    df = drop_nulls(df, spark)
    df = fix_strings(df)
    df = fix_numbers(df)
    df = fix_status(df)
    df = fix_dates(df, 'created_at')
    df = fix_dates(df, 'paid_at')
    df.coalesce(1).write.csv('./curated/c_data_prueba_tecnica.csv', header=True, mode="overwrite")
    #=========================CURATED===================================================

    #===========================Augmented=================================================
    df_curated = spark.read.csv('./curated/c_data_prueba_tecnica.csv', header=True, inferSchema=True)
    df_result = agg_sales(df_curated)
    df_result.coalesce(1).write.csv('./augmented/report.csv', header=True, mode="overwrite")
    #===========================Augmented=================================================
    print("End process")



if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print('Error')
        print(str(err))