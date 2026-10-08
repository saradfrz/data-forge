import os

def spark_session(config):
    from pyspark.sql import SparkSession
    packages=','.join(['io.delta:delta-spark_2.12:3.3.2',
        'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6',
        'org.apache.hadoop:hadoop-aws:3.3.4'])
    builder=(SparkSession.builder.appName('DataForge')
        .master(config.spark.master).config('spark.jars.packages',packages)
        .config('spark.sql.extensions','io.delta.sql.DeltaSparkSessionExtension')
        .config('spark.sql.catalog.spark_catalog','org.apache.spark.sql.delta.catalog.DeltaCatalog')
        .config('spark.sql.session.timeZone','UTC')
        .config('spark.sql.shuffle.partitions',str(config.spark.shuffle_partitions))
        .config('spark.sql.ansi.enabled','false')
        .config('spark.hadoop.fs.s3a.impl','org.apache.hadoop.fs.s3a.S3AFileSystem'))
    if not os.getenv('DF_LOCAL_STORE'):
        builder=(builder.config('spark.hadoop.fs.s3a.endpoint',os.environ['S3_ENDPOINT'])
            .config('spark.hadoop.fs.s3a.path.style.access','true')
            .config('spark.hadoop.fs.s3a.connection.ssl.enabled','false')
            .config('spark.hadoop.fs.s3a.access.key',os.environ['MINIO_ROOT_USER'])
            .config('spark.hadoop.fs.s3a.secret.key',os.environ['MINIO_ROOT_PASSWORD']))
    return builder.getOrCreate()
