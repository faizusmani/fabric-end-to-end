# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "beb4c7b0-75ff-4470-b1a6-43f196223b77",
# META       "default_lakehouse_name": "news_lake_db",
# META       "default_lakehouse_workspace_id": "03176b4b-e30b-41e1-beb0-6c46fa99320a",
# META       "known_lakehouses": [
# META         {
# META           "id": "beb4c7b0-75ff-4470-b1a6-43f196223b77"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

df = spark.read.option("multiline", "true").json("abfss://Project@onelake.dfs.fabric.microsoft.com/news_lake_db.Lakehouse/Files/google-latest-news.json")
# df now is a Spark DataFrame containing JSON data from "abfss://Project@onelake.dfs.fabric.microsoft.com/news_lake_db.Lakehouse/Files/google-latest-news.json".
display(df)

# CELL ********************

df = df.select("items")
display(df)

# CELL ********************

from pyspark.sql.functions import explode
df_exploded = df.select(explode(df["items"]).alias("json_object"))

# CELL ********************

display(df_exploded)

# CELL ********************

json_list = df_exploded.toJSON().collect()

# CELL ********************

print(json_list[2])

# CELL ********************

import json

news_json = json.loads(json_list[2])

# CELL ********************

print(news_json)

# CELL ********************

print(news_json['json_object']['publisher'])
print(news_json['json_object']['newsUrl'])
print(news_json['json_object']['timestamp'])
print(news_json['json_object']['title'])
print(news_json['json_object']['snippet'])
print(news_json['json_object']['images']['thumbnail'])

# CELL ********************

publisher = []
newsUrl = []
timestamp = []
title = []
snippet = []
thumbnail = []

for json_str in json_list:
    try:
        article = json.loads(json_str)

        if article['json_object'].get('images',{}).get('thumbnail'):

            publisher.append(article['json_object']['publisher'])
            newsUrl.append(article['json_object']['newsUrl'])
            timestamp.append(article['json_object']['timestamp'])
            title.append(article['json_object']['title'])
            snippet.append(article['json_object']['snippet'])
            thumbnail.append(article['json_object']['images']['thumbnail'])

    except Exception as e:
        print(f"Error processing the JSON object: {e}")

# CELL ********************

from pyspark.sql.types import StructType, StructField, StringType

data = list(zip(publisher, newsUrl, timestamp, title, snippet, thumbnail))

schema = StructType([
    StructField("publisher", StringType(), True),
    StructField("newsUrl", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("title", StringType(), True),
    StructField("snippet", StringType(), True),
    StructField("thumbnail", StringType(), True)
])

df_cleaned = spark.createDataFrame(data, schema=schema)

# CELL ********************

display(df_cleaned)

# CELL ********************

from pyspark.sql import functions as F

df_cleaned_final = df_cleaned.withColumn("datetimePublished", F.from_unixtime((F.col('timestamp')/1000)))
df_cleaned_final = df_cleaned_final.withColumn("date", F.to_date(F.col('datetimePublished')))

# CELL ********************

display(df_cleaned_final)

# CELL ********************

from pyspark.sql.utils import AnalysisException

try:
    table_name = 'news_lake_db.latest_news_tbl'
    df_cleaned_final.write.format('delta').saveAsTable(table_name)

except AnalysisException:

    print('Table Already Exists')
    df_cleaned_final.createOrReplaceTempView('vw_df_cleaned_final')

    spark.sql(f""" MERGE INTO {table_name} AS target_table
                   USING vw_df_cleaned_final AS source_view

                   ON source_view.newsUrl = target_table.newsUrl

                   WHEN MATCHED AND
                   source_view.publisher <> target_table.publisher OR
                   source_view.title <> target_table.title OR
                   source_view.snippet <> target_table.snippet OR
                   source_view.thumbnail <> target_table.thumbnail OR
                   source_view.datetimePublished <> target_table.datetimePublished 

                   THEN UPDATE SET *

                   WHEN NOT MATCHED THEN INSERT *
    
                 """)
