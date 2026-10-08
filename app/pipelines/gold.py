from pyspark.sql import functions as F, Window

TABLES=['gold_candles','gold_spreads','gold_returns','gold_volatility','gold_daily_summary']

def frames(quotes):
    """All aggregates are event-time; no processing-order first()/last()."""
    order=F.struct('event_ts','source_order','event_id')
    all_candles=None
    for seconds in [1,60,3600]:
        for basis in ['bid','ask','mid']:
            c=(quotes.groupBy('instrument',F.window('event_ts',f'{seconds} seconds'))
               .agg(F.min_by(F.col(basis),order).alias('open'),F.max(basis).alias('high'),
                    F.min(basis).alias('low'),F.max_by(F.col(basis),order).alias('close'),
                    F.count('*').alias('tick_count'),F.max('event_ts').alias('last_event_ts'),
                    F.min_by('event_id',order).alias('first_event_id'),
                    F.max_by('event_id',order).alias('last_event_id'))
               .select('instrument',F.col('window.start').alias('window_start'),F.col('window.end').alias('window_end'),
                   'open','high','low','close','tick_count','last_event_ts','first_event_id','last_event_id')
               .withColumn('interval_seconds',F.lit(seconds)).withColumn('price_basis',F.lit(basis)))
            all_candles=c if all_candles is None else all_candles.unionByName(c)
    pips=F.when(F.col('instrument').endswith('JPY'),F.lit(.01)).otherwise(F.lit(.0001))
    q=(quotes.withColumn('spread_pips',F.col('spread_abs').cast('double')/pips)
        .withColumn('spread_bps',10000*F.col('spread_abs').cast('double')/F.col('mid').cast('double')))
    spreads=(q.groupBy('instrument',F.window('event_ts','60 seconds')).agg(
        F.count('*').alias('tick_count'),F.sum('spread_abs').alias('spread_abs_sum'),
        F.avg('spread_abs').alias('mean_spread_abs'),F.avg('spread_pips').alias('mean_spread_pips'),
        F.avg('spread_bps').alias('mean_spread_bps'),F.min('spread_abs').alias('min_spread_abs'),
        F.max('spread_abs').alias('max_spread_abs'))
        .select('instrument',F.col('window.start').alias('window_start'),F.col('window.end').alias('window_end'),
                'tick_count','spread_abs_sum','mean_spread_abs','mean_spread_pips','mean_spread_bps','min_spread_abs','max_spread_abs'))
    minute=all_candles.filter((F.col('interval_seconds')==60)&(F.col('price_basis')=='mid'))
    ordered=Window.partitionBy('instrument',F.to_date('window_start')).orderBy('window_start')
    returns=(minute.withColumn('prev_close',F.lag('close').over(ordered))
        .withColumn('previous_sample_end',F.lag('window_end').over(ordered))
        .withColumn('sample_age_ms',(F.col('window_end').cast('double')-F.col('last_event_ts').cast('double'))*1000)
        .withColumn('gap_flag',F.coalesce((F.col('window_end').cast('long')-F.col('previous_sample_end').cast('long')!=60),F.lit(True))))
    eligible=(~F.col('gap_flag'))&(F.col('sample_age_ms')<=60000)
    returns=(returns.withColumn('simple_return',F.when(eligible,F.col('close').cast('double')/F.col('prev_close').cast('double')-1))
        .withColumn('log_return',F.when(eligible,F.log(F.col('close').cast('double')/F.col('prev_close').cast('double'))))
        .select('instrument',F.col('window_end').alias('sample_end'),F.col('close').alias('mid_close'),
                'simple_return','log_return','previous_sample_end','gap_flag','sample_age_ms'))
    trailing=Window.partitionBy('instrument',F.to_date(F.col('sample_end')-F.expr('INTERVAL 1 SECOND'))).orderBy('sample_end').rowsBetween(-59,0)
    vol=(returns.withColumn('valid_return_count',F.count('log_return').over(trailing))
        .withColumn('oldest',F.min('sample_end').over(trailing))
        .withColumn('rolling_log_vol_60m',F.when((F.col('valid_return_count')==60)&
            (F.col('sample_end').cast('long')-F.col('oldest').cast('long')==59*60),F.stddev_samp('log_return').over(trailing)))
        .withColumn('expected_return_count',F.lit(60))
        .withColumn('coverage_ratio',F.col('valid_return_count')/60)
        .select('instrument','sample_end','rolling_log_vol_60m','valid_return_count','expected_return_count','coverage_ratio'))
    day=(q.withColumn('event_date',F.to_date('event_ts')).groupBy('instrument','event_date').agg(
        F.min_by('mid',order).alias('mid_open'),F.max('mid').alias('mid_high'),F.min('mid').alias('mid_low'),
        F.max_by('mid',order).alias('mid_close'),F.count('*').alias('tick_count'),
        F.avg('spread_pips').alias('mean_spread_pips'),F.avg('spread_bps').alias('mean_spread_bps'))
        .withColumn('open_close_return',F.col('mid_close').cast('double')/F.col('mid_open').cast('double')-1))
    daily_vol=(returns.withColumn('event_date',F.to_date(F.col('sample_end')-F.expr('INTERVAL 1 SECOND')))
        .groupBy('instrument','event_date').agg(F.sqrt(F.sum(F.pow('log_return',2))).alias('realized_vol_daily'),
                F.count('log_return').alias('valid_return_count')))
    day=(day.join(daily_vol,['instrument','event_date'],'left')
        .withColumn('return_coverage',F.col('valid_return_count')/1439)
        .withColumn('complete_day',F.lit(False))) # Acquisition calendar not certified in v1.
    return dict(zip(TABLES,[all_candles,spreads,returns,vol,day]))

def build(spark,store,root):
    quotes=spark.read.format('delta').load(store.uri(root+'/silver')).cache()
    try:
        for name,df in frames(quotes).items():
            df.write.format('delta').mode('overwrite').option('overwriteSchema','true').save(store.uri(root+'/'+name))
    finally: quotes.unpersist()
