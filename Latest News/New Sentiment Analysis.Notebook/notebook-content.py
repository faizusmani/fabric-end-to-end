# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "beb4c7b0-75ff-4470-b1a6-43f196223b77",
# META       "default_lakehouse_name": "news_lake_db",
# META       "default_lakehouse_workspace_id": "03176b4b-e30b-41e1-beb0-6c46fa99320a"
# META     }
# META   }
# META }

# CELL ********************

df = spark.sql("SELECT * FROM news_lake_db.latest_news_tbl")
display(df)

# CELL ********************

import synapse.ml.core
from synapse.ml.services import AnalyzeText 

# CELL ********************

model = (AnalyzeText()
        .setTextCol("snippet")
        .setKind("SentimentAnalysis")
        .setOutputCol("sentimentResponse")
        .setErrorCol("sentimentError"))

# CELL ********************

result = model.transform(df)
display(result)

# MARKDOWN ********************

# #Change the cells from Markdown to Code once the Pre-trained models are available in your region.
# 
# from pyspark.sql.functions import col
# sentiment_df = result.withColumn('sentiment', col('sentimentResponse.documents.sentiment'))
# sentiment_df = sentiment_df.drop('sentimentResponse','sentimentError')

# MARKDOWN ********************

# 
# from pyspark.sql.utils import AnalysisException
# 
# try:
#     table_name = 'news_lake_db.sentiment_latest_news_tbl'
#     df_sentiment_final.write.format('delta').saveAsTable(table_name)
# 
# except AnalysisException:
# 
#     print('Table Already Exists')
#     df_sentiment_final.createOrReplaceTempView('vw_df_sentiment_final')
# 
#     spark.sql(f""" MERGE INTO {table_name} AS target_table
#                    USING vw_df_sentiment_final AS source_view
# 
#                    ON source_view.newsUrl = target_table.newsUrl
# 
#                    WHEN MATCHED AND
#                    source_view.publisher <> target_table.publisher OR
#                    source_view.title <> target_table.title OR
#                    source_view.snippet <> target_table.snippet OR
#                    source_view.thumbnail <> target_table.thumbnail OR
#                    source_view.datetimePublished <> target_table.datetimePublished 
# 
#                    THEN UPDATE SET *
# 
#                    WHEN NOT MATCHED THEN INSERT *
#     
#                  """)

