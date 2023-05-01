# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC This notebook will show you how to create and query a table or DataFrame that you uploaded to DBFS. [DBFS](https://docs.databricks.com/user-guide/dbfs-databricks-file-system.html) is a Databricks File System that allows you to store data for querying inside of Databricks. This notebook assumes that you have a file already inside of DBFS that you would like to read from.
# MAGIC
# MAGIC This notebook is written in **Python** so the default cell type is Python. However, you can use different languages by using the `%LANGUAGE` syntax. Python, Scala, SQL, and R are all supported.

# COMMAND ----------

# File location and type
file_location = "/FileStore/tables/Car_data-1.csv"
file_type = "csv"

df=spark.read.csv(file_location,header=True,inferSchema=True)
df.show()

# COMMAND ----------

df.printSchema()

# COMMAND ----------

# handling categorical features
from pyspark.ml.feature import StringIndexer
indexer=StringIndexer(inputCols=["name","fuel","seller_type","transmission","owner"],outputCols=["name_indexed","fuel_indexed","seller_type_indexed","transmission_indexed","owner_indexed"])
df_indexed=indexer.fit(df).transform(df)
df_indexed.show()

# COMMAND ----------

# grouping all features in a vector
from pyspark.ml.feature import VectorAssembler
featureAssembler=VectorAssembler(inputCols=["name_indexed","fuel_indexed","seller_type_indexed","transmission_indexed","owner_indexed","year","km_driven"],outputCol="Independent feature")
output_df=featureAssembler.transform(df_indexed)
output_df.show()

# COMMAND ----------

finalized_df=output_df.select("Independent feature","selling_price")
finalized_df.show()

# COMMAND ----------

# apply linear regression
from pyspark.ml.regression import LinearRegression
train_data,test_data=finalized_df.randomSplit([0.75,0.25])
regressor=LinearRegression(featuresCol="Independent feature",labelCol="selling_price")
regressor=regressor.fit(train_data)

# COMMAND ----------

regressor.coefficients

# COMMAND ----------

pred_resulta=regressor.evaluate(test_data)
pred_resulta.predictions.show()

# COMMAND ----------

pred_resulta.meanAbsoluteError,pred_resulta.meanSquaredError

# COMMAND ----------


