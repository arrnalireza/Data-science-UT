import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, DoubleType, IntegerType, ArrayType, LongType

def get_spark_session(app_name):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    jars_dir = os.path.join(current_dir, "jars")
    jar_files = [os.path.join(jars_dir, f)
        for f in os.listdir(jars_dir) if f.endswith('.jar')]
    jars_string = ",".join(jar_files)

    print(f"[LOG] Loading {len(jar_files)} JARs. Initializing Spark...")

    # Initialize Spark with the JARs included
    
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", jars_string) \
        .config("spark.driver.extraClassPath", jars_string) \
        .config("spark.executor.extraClassPath", jars_string) \
        .getOrCreate()

nested_item_schema = StructType([
    StructField("food_item", StringType(), True),
    StructField("category", StringType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("quantity", IntegerType(), True)
])

order_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("restaurant_id", LongType(), True),
    StructField("restaurant_name", StringType(), True),
    StructField("restaurant_city", StringType(), True),
    StructField("cuisines", ArrayType(StringType()), True),
    StructField("phone_number", StringType(), True),
    StructField("request_online", BooleanType(), True),
    StructField("request_table", BooleanType(), True),
    StructField("order_time", StringType(), True),
    StructField("items", ArrayType(nested_item_schema), True),
    StructField("order_price", DoubleType(), True)
])