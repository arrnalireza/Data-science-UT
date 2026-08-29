from common_utils import get_spark_session, order_schema
from pyspark.sql.functions import from_json, col, to_timestamp, window, expr, count, sum, lit, first, explode

spark = get_spark_session("Ashpaz-RealTime-Streaming")

kafka_stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "ashpaz.valid") \
    .load()

streaming_orders_df = kafka_stream_df \
    .select(from_json(col("value").cast("string"), order_schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp(col("order_time"))) \
    .withWatermark("timestamp", "10 minutes")

# Real-Time Fraud Detection

# Geographical Impossibility
stream_left = streaming_orders_df.alias("df1")
stream_right = streaming_orders_df.alias("df2")

geo_fraud_df = stream_left.join(
    stream_right,
    expr("""
        df1.user_id = df2.user_id AND
        df1.restaurant_city != df2.restaurant_city AND
        df2.timestamp > df1.timestamp AND
        df2.timestamp <= df1.timestamp + interval 30 minutes
    """)
).select(
    col("df2.order_id"),
    col("df2.user_id"),
    lit("GEOGRAPHIC_IMPOSSIBILITY").alias("error_type"),
    lit("User placed orders in multiple cities within 30 simulation minutes").alias("error_reason")
)

# Velocity Check (Order Spam)
velocity_fraud_df = streaming_orders_df \
    .groupBy(window(col("timestamp"), "60 minutes", "10 minutes"), col("user_id")) \
    .agg(count("order_id").alias("order_count"), first("order_id").alias("order_id")) \
    .filter(col("order_count") > 5) \
    .select(
        col("order_id"),
        col("user_id"),
        lit("VELOCITY_SPAM").alias("error_type"),
        lit("User exceeded 5 orders within a single hour window").alias("error_reason")
    )

alerts_df = geo_fraud_df.union(velocity_fraud_df)

# Real-Time Operational Analytics

cuisines_df = streaming_orders_df.select("order_price", "timestamp", explode(col("cuisines")).alias("cuisine"))

analytics_df = cuisines_df \
    .groupBy(window(col("timestamp"), "1 minute", "20 seconds"), col("cuisine")) \
    .agg(
        sum("order_price").alias("total_revenue"),
        (sum("order_price") / count("order_price")).alias("average_order_value")
    ).select(
        col("window.start").cast("string").alias("window_start"),
        col("window.end").cast("string").alias("window_end"),
        col("cuisine"),
        col("total_revenue"),
        col("average_order_value")
    )

# Starting Sinks & Checkpointing

# Publish detected fraud straight back out to Kafka alerts
fraud_query = alerts_df \
    .selectExpr("CAST(order_id AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "orders.fraud_alerts") \
    .option("checkpointLocation", "/tmp/spark-checkpoints/fraud_alerts") \
    .outputMode("append") \
    .start()

# Publish rolling operational aggregations to Kafka insights
analytics_query = analytics_df \
    .selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "ashpaz.operational_analytics") \
    .option("checkpointLocation", "/tmp/spark-checkpoints/operational_analytics") \
    .outputMode("update") \
    .start()


# # fraud query to print to the console terminal
# fraud_query = alerts_df \
#     .writeStream \
#     .format("console") \
#     .outputMode("append") \
#     .start()

# # operational analytics query to print  to the console terminal
# analytics_query = analytics_df \
#     .writeStream \
#     .format("console") \
#     .option("truncate", "false") \
#     .outputMode("update") \
#     .start()


fraud_query.awaitTermination()
analytics_query.awaitTermination()