## **1\. SparkSession & Configuration**

These define the entry point to Spark SQL functionality and manage configurations.

[ ] - `pyspark.sql.SparkSession.builder.getOrCreate` – Initializes or retrieves the Spark session.  
[ ] - `pyspark.sql.SparkSession.sql` – Executes SQL queries.  
[x] - `pyspark.sql.SparkSession.read` – Entry point for reading data.  
[ ] - `pyspark.sql.SparkSession.createDataFrame` – Converts various data sources into DataFrame.  
[ ] - `pyspark.sql.SparkSession.conf` – Manages runtime configurations.

### **pyspark.sql.SparkSession.read**

Annoyingly, the documentation for the option method is in the docs for the  **`DataFrameReader`** method.

## **2\. DataFrames & Transformations**

DataFrame operations form the core of data manipulation in Spark.

#### **Top 5 to Study:**

[ ] - `pyspark.sql.DataFrame.select` – Selects specific columns.  
[ ] - `pyspark.sql.DataFrame.filter` – Filters rows based on conditions.  
[ ] - `pyspark.sql.DataFrame.groupBy` – Groups data for aggregations.  
[ ] - `pyspark.sql.DataFrame.withColumn` – Adds or modifies columns.  
[ ] - `pyspark.sql.DataFrame.join` – Performs SQL-style joins between DataFrames

## **3\. Input/Output Operations**

These functions handle data ingestion and persistence.

#### **Top 5 to Study:**

[ ] - `pyspark.sql.DataFrameReader.load` – Generic data loading method.  
[ ] - `pyspark.sql.DataFrameReader.json` – Reads JSON data.  
[ ] - `pyspark.sql.DataFrameWriter.parquet` – Writes data to Parquet format.  
[ ] - `pyspark.sql.DataFrameWriter.saveAsTable` – Saves DataFrame as a table.  
[ ] - `pyspark.sql.DataFrameReader.jdbc` – Connects to relational databases.

## **4\. Functions (Built-in & UDFs)**

Functions are used for data transformation, computation, and aggregation.

#### **Top 5 to Study:**

[ ] - `pyspark.sql.functions.col` – References a column.  
[ ] - `pyspark.sql.functions.when` – Conditional expressions.  
[ ] - `pyspark.sql.functions.udf` – Registers a user-defined function.  
[ ] - `pyspark.sql.functions.window` – Defines time-based windowing.  
[ ] - `pyspark.sql.functions.agg` – Applies aggregate functions.

## **5\. Window & Grouping Operations**

Essential for advanced analytics, ranking, and aggregations.

#### **Top 5 to Study:**

[ ] - `pyspark.sql.Window.partitionBy` – Defines partitions for windowing.  
[ ] - `pyspark.sql.Window.orderBy` – Orders data within a window.  
[ ] - `pyspark.sql.GroupedData.agg` – Performs aggregation after grouping.  
[ ] - `pyspark.sql.DataFrame.rollup` – Hierarchical aggregations.  
[ ] - `pyspark.sql.DataFrame.cube` – Multi-dimensional aggregations.