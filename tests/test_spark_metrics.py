import os
from decimal import Decimal
import pytest

@pytest.mark.skipif(os.getenv('DF_TEST_SPARK')!='1',reason='Set DF_TEST_SPARK=1 with Java/PySpark installed')
def test_spark_candles_and_gap_policy():
    from pyspark.sql import SparkSession,functions as F
    from app.pipelines.gold import frames
    spark=(SparkSession.builder.master('local[2]').appName('forge-test')
           .config('spark.ui.enabled','false').config('spark.sql.shuffle.partitions','2')
           .config('spark.sql.session.timeZone','UTC').getOrCreate())
    try:
        rows=[('a','EURUSD','2026-09-15 12:00:00.000',0,'1.1000','1.1002'),
              ('b','EURUSD','2026-09-15 12:00:00.000',1,'1.1002','1.1004'),
              ('c','EURUSD','2026-09-15 12:00:59.999',2,'1.0998','1.1000'),
              ('d','EURUSD','2026-09-15 12:01:00.000',3,'1.1000','1.1002'),
              ('e','EURUSD','2026-09-15 12:03:00.000',4,'1.1002','1.1004')]
        df=spark.createDataFrame(rows,'event_id string,instrument string,event_ts string,source_order long,bid string,ask string')
        df=(df.withColumn('event_ts',F.to_timestamp('event_ts'))
              .withColumn('bid',F.col('bid').cast('decimal(20,10)'))
              .withColumn('ask',F.col('ask').cast('decimal(20,10)'))
              .withColumn('mid',(F.col('bid')+F.col('ask'))/2)
              .withColumn('spread_abs',F.col('ask')-F.col('bid')))
        tables=frames(df)
        bars=tables['gold_candles'].filter("price_basis='mid' and interval_seconds=60").orderBy('window_start').collect()
        assert [bars[0][k] for k in ['open','high','low','close']]==list(map(Decimal,['1.1001','1.1003','1.0999','1.0999']))
        assert bars[0].tick_count==3
        returns=tables['gold_returns'].orderBy('sample_end').collect()
        assert returns[0].simple_return is None and returns[1].simple_return is not None
        assert returns[2].simple_return is None
        assert all(r.rolling_log_vol_60m is None for r in tables['gold_volatility'].collect())
        assert tables['gold_daily_summary'].collect()[0].complete_day is False
    finally:spark.stop()
