from pyspark.sql.functions import floor, count
from pyspark.sql.functions import split
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define the schema for the Kafka message value
schema = StructType([
    StructField("age_group", IntegerType()),
    StructField("count", IntegerType())
])

# Create a Spark session
spark = SparkSession.builder \
    .appName("Kafka-Cassandra") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0") \
    .getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "fresh_topic") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

df \
    .writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "project_keyspace") \
    .option("table", "my_table") \
    .option("checkpointLocation", "/tmp") \
    .start()

# Start the streaming query
spark.streams.awaitAnyTermination()

# Print the processed data to the console
# df \
#     .writeStream \
#     .outputMode("complete") \
#     .format("console") \
#     .start() \
#     .awaitTermination()

# df = df.selectExpr("CAST(value AS STRING)")
#
# # # Split the message into separate columns
# df = df.select(split(df.value, ',').alias('data'))
#
# # # Explode the DataFrame to create a new row for each message
# df = df.selectExpr("explode(data) as message")
#
# query = df \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()
#
# # Wait for the streaming query to finish
# query.awaitTermination()

