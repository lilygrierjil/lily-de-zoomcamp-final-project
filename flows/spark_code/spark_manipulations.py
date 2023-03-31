from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.functions import to_date


# start a spark session
spark = SparkSession.builder \
    .appName('memphis-police-data') \
    .getOrCreate()

# read from big query
bucket = "dataproc-temp-bucket_de-zoomcamp-final-project"
spark.conf.set('temporaryGcsBucket', bucket)

mpd_schema = types.StructType([
    types.StructField("crime_id", types.StringType(), True),
    types.StructField("offense_date", types.StringType(), True),
    types.StructField("agency_crimetype_id", types.StringType(), True),
    types.StructField("city", types.StringType(), True),
    types.StructField("state", types.StringType(), True),
    types.StructField("masked_address", types.StringType(), True),
    types.StructField("category", types.StringType(), True),
    types.StructField("coord1", types.DoubleType(), True),
    types.StructField("coord2", types.DoubleType(), True),
    types.StructField("location", types.MapType(types.DoubleType(), types.DoubleType()), False),
    types.StructField("offense_date_datetime", types.TimestampType(), True),
])
df = spark.read.format('bigquery') \
  .schema(mpd_schema) \
  .option('table', 'memphis_police_data_all.memphis_police_data_partitioned_clustered') \
  .load()



df = df.withColumn('offense_day', to_date('offense_date_datetime'))

df.registerTempTable('memphis')



# daily_grouped = spark.sql('''
# SELECT agency_crimetype_id AS crime_type,
# offense_day,
# FIRST(category) AS crime_type_category,
# COUNT(crime_id) AS daily_crime_type_count
# FROM memphis
# GROUP BY 1, 2
# ''')
                      
# daily_grouped.write \
#   .mode('overwrite') \
#   .format('bigquery') \
#   .option('table', 'memphis_police_data_all.daily_crime_type_counts') \
#   .save()


monthly_grouped = spark.sql('''
SELECT agency_crimetype_id AS crime_type,
date_trunc('month', offense_day) AS offense_month, 
FIRST(category) AS crime_type_category,
COUNT(crime_id) AS monthly_crime_type_count
FROM memphis
GROUP BY 1, 2
''')
                      
monthly_grouped.write.format('bigquery') \
  .mode('overwrite') \
  .option('table', 'memphis_police_data_all.monthly_crime_type_counts') \
  .save()

