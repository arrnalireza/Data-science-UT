from common_utils import get_spark_session, order_schema
from pyspark.sql.functions import col, explode, sum, count, desc, when, hour, to_timestamp, rank
from pyspark.sql.window import Window

spark = get_spark_session("Ashpaz-Batch-Analysis")
batch_df = spark.read.schema(order_schema).json("historical_data.json")

# Revenue and Menu Analysis
print("Running Revenue and Menu Analysis\n")

# Top Ordered Items
top_items_df = batch_df.select(explode(col("items")).alias("item")) \
    .groupBy("item.food_item") \
    .agg(sum("item.quantity").alias("total_quantity_ordered")) \
    .orderBy(desc("total_quantity_ordered"))

print("Top Ordered Items")
top_items_df.show()

# Highest Revenue Restaurants
top_restaurants_df = batch_df.groupBy("restaurant_id", "restaurant_name") \
    .agg(sum("order_price").alias("total_earnings")) \
    .orderBy(desc("total_earnings"))

print("Highest Revenue Restaurants")
top_restaurants_df.show()

# Order Channel Leaders (Online vs. Dine-In)
channel_leaders_df = batch_df.groupBy("restaurant_id", "restaurant_name") \
    .agg(
        sum(when(col("request_online") == True, 1).otherwise(0)).alias("online_orders"),
        sum(when(col("request_table") == True, 1).otherwise(0)).alias("dine_in_orders")
    )

print("Online Order Leaders")
channel_leaders_df.orderBy(desc("online_orders")).show(10)

print("Dine-In Order Leaders")
channel_leaders_df.orderBy(desc("dine_in_orders")).show(10)

# Order Time & Peak Hour Analysis
print("Running Order Time & Peak Hour Analysis\n")

time_df = batch_df.withColumn("parsed_time", to_timestamp(col("order_time"))) \
                  .withColumn("order_hour", hour(col("parsed_time")))

hourly_patterns_df = time_df.groupBy("order_hour") \
    .agg(count("order_id").alias("order_volume")) \
    .orderBy(desc("order_volume"))

print("Hourly Order Patterns and Peak Identification")
hourly_patterns_df.show(24)

# Geographic & Location-Based Analysis
print("Running Geographic & Location-Based Analysis\n")

# Revenue Distribution by City
city_revenue_df = batch_df.groupBy("restaurant_city") \
    .agg(sum("order_price").alias("total_revenue")) \
    .orderBy(desc("total_revenue"))

print("Revenue Distribution by City")
city_revenue_df.show()

# Regional Favorite Foods
city_items_df = batch_df.select("restaurant_city", explode(col("items")).alias("item")) \
    .groupBy("restaurant_city", "item.food_item") \
    .agg(sum("item.quantity").alias("item_popularity"))

window_spec = Window.partitionBy("restaurant_city").orderBy(desc("item_popularity"))
regional_favorites_df = city_items_df.withColumn("rank", rank().over(window_spec)) \
    .filter(col("rank") == 1) \
    .drop("rank")

print("Regional Favorite Foods")
regional_favorites_df.show()