# Data Forge — Finance Theory and Visualization Guide

**As of:** 8 October 2026 · **Reviewed revision:** 2 · **Audience:** a data engineer familiar with Python and SQL, learning market-data analytics.

This guide defines the financial meaning of the datasets in `TickStream_Lakehouse_PM_Report.md`. It is an educational specification, not an investment strategy. All worked numbers are synthetic. Metric names below are the contract shared by the pipeline, tests, API, and dashboard.


## Revision 2 review and implementation boundary

The financial concepts remain applicable after adding Kubernetes, Airflow and MinIO. Orchestration and storage do not change the meaning of a quote or a return. Databricks and dbt are now outside this project; Spark owns the production metric transformations.

This review checked the worked spread, return and volatility calculations and reconciled names with the generated code. Important implementation boundaries:

| Topic | Data Forge v0.1 behavior | Guidance beyond v0.1 |
|---|---|---|
| Candles | Bid/ask/midpoint at 1s, 1m, 1h; UTC half-open windows; timestamp ties retained | Same semantics for future continuous aggregates |
| Precision | Input bid/ask DECIMAL(20,10), midpoint DECIMAL(21,11) | Preserve half of the smallest accepted input increment |
| Spreads | Observation-weighted means and absolute min/max | Exact p50/p95 and time weighting below are defined for later implementation |
| Returns | Consecutive observed minute closes, no cross-UTC-day or missing-minute bridges | Calendar-aware session alternatives remain optional |
| Volatility | 60 consecutive minute returns; daily observed realized volatility | No default annualization |
| Coverage | 1,439 as a full-24-hour within-day reference; `complete_day=false` | Provider-calendar certification required before asserting completeness |
| Streaming finality | Completed finite replay, consumed end-offset check, final Gold rebuild | Watermarks, provisional candles and late corrections described below are future design |
| Health | Captured publication time and reconciliation result | Live lag/latency telemetry is not yet implemented |
| Public preview | Synthetic reference calculations; reconciliation `not_run` | Only a completed cluster run can establish actual batch/Kafka agreement |

The 1,439 denominator is a convention for the included full-day reference, not proof a provider should produce quotes every minute. Sparse OHLC has no forward-filled intervals. Daily volatility with incomplete returns is labeled an observed subset, never a certified complete-day risk estimate.

## 1. FX market-data fundamentals

### Currency pairs and quotation direction

In **EUR/USD**, EUR is the **base currency** and USD is the **quote currency**. A price of 1.1000 means one euro is quoted at 1.1000 US dollars. A rising EUR/USD quote means the euro is becoming more expensive in dollars; it does not mean both currencies rose.

USD/JPY at 150.00 means 150 yen per dollar. Raw price levels of 150 and 1.10 are not comparable measures of strength, volatility, or liquidity. Pair direction matters: a rise in EUR/USD and a rise in USD/JPY have different implications for the dollar. Inversion also transforms bid and ask: for an inverse pair, bid is `1 / original_ask`, and ask is `1 / original_bid`, not merely reciprocal prices retaining their original sides.

Store `base_currency`, `quote_currency`, `pip_size`, and source precision explicitly. The project basket contains seven USD majors and selected crosses such as EUR/GBP. A cross does not contain USD; “ten major pairs” would be an imprecise label.

### Bid, ask, midpoint and spread

For a quote from a given provider:

- **Bid** is the quoted price at which the base currency can be sold to that quoting side.
- **Ask** is the quoted price at which the base currency can be bought from that side.
- **Midpoint** is the arithmetic average of bid and ask.
- **Spread** is ask minus bid.

At bid 1.10000 and ask 1.10020, midpoint is 1.10010 and spread is 0.00020 USD per EUR. Midpoint is useful for describing price movement but is not an executable price. Quoted availability does not guarantee an actual fill, size, or transaction cost: latency, slippage and fees are absent from this project.

### Pips, pipettes and source precision

A pip is a conventional price increment. For the selected non-JPY pairs use **0.0001**; for the selected JPY-quoted pairs use **0.01**. A pipette is one tenth of a pip. Thus a five-decimal EUR/USD quote can move by a pipette, and a three-decimal USD/JPY quote can do the same. These conventions are described in OANDA's pip education material [F1].

Do not confuse a pip with the smallest source increment, a binary price divisor, or a monetary profit. A 0.020 USD/JPY spread is 2 pips; a 0.00020 EUR/USD spread is also 2 pips, but the relative spread and currency value differ. Pip conventions belong in instrument metadata, not a global multiplier.

### Quote updates are not trades

The project processes **quote ticks**, observations of bid and ask. A new row may reflect a price change, a displayed-size change, or a repeated quote. It does not prove a buyer and seller transacted. Tick count is feed activity, not traded quantity, transaction count, or total FX market volume.

Dukascopy's ITick documentation describes bid/ask volume as the amount available at the best corresponding quote; historical records do not provide full historical market depth [F2]. Units depend on the chosen export and must be verified by the acquisition adapter. Retain unknown units as `unverified` rather than inventing them. Never sum these snapshots and label the result daily traded volume: the same displayed liquidity may appear repeatedly.

Consequently, this project does **not** propose trade VWAP, money flow, or volume-weighted trading indicators. A midpoint average weighted by quote count is an observation-weighted quote statistic, not VWAP.

### Sessions, weekends and clock time

FX trading is distributed across venues and time zones. Activity shifts through Asia-Pacific, European and American business hours; overlaps can have different quote-update rates. Weekend closures and holiday schedules depend on the provider and instrument. An empty interval can also indicate missing acquisition or a feed outage.

Use UTC storage and UTC reporting days `[00:00, next 00:00)` for reproducibility. A UTC day is an engineering convention, not a universal FX session. New York 17:00 rollovers are an optional alternative, requiring `America/New_York` calendar rules and daylight-saving awareness. Do not hardcode a constant UTC offset for London or New York. The PM sample panel does not itself test a DST transition; add synthetic/known transition cases to calendar tests.

Session overlays are descriptive context. They cannot prove why prices moved. A provider's market-hours calendar and documented acquisition coverage should distinguish `expected_closed` from `missing_source`; never infer closure solely from a missing file.

### One provider is one view

FX is substantially an over-the-counter market, with trading distributed across participants and locations [F3]. A provider's best bid/ask is not a consolidated global best quote. Its activity, liquidity fields, spread and outages may differ from another feed. The project can describe this source's observations; it cannot estimate total FX turnover from those observations.

## 2. Common metric conventions

### Notation and defaults

| Symbol / field | Meaning |
|---|---|
| `b_i`, `a_i` | Bid and ask at source observation i, in quote currency per base unit |
| `m_i` | Midpoint `(a_i + b_i) / 2` |
| `s_i` | Absolute spread `a_i - b_i` |
| `p` | Pip size from instrument metadata |
| `t_i` | Source event timestamp in UTC |
| `P_k` | Eligible midpoint close for one-minute interval k |
| `r_k`, `l_k` | Simple and logarithmic returns between eligible adjacent samples |
| `n` | Number of valid observations or returns, specified per metric |
| `Δ_i` | Valid covered duration for which a quote is held, in seconds |

**Project defaults:** midpoint price basis; sparse quote-based OHLC; one-minute close sampling for returns; 60 consecutive valid one-minute returns for rolling volatility; UTC daily summaries; no automatic annualization; no forward-filled returns. All three price bases are available for candles.

Every Gold dataset must be traceable to its instrument, source dataset/run/path and definitions. In v0.1, dataset/run are encoded in storage paths and snapshot metadata; per-row metric-version and revision columns are planned. The dashboard's percentage formatting multiplies decimal returns/volatility by 100. It does not change the stored units.

### Irregular ticks: observation weighting versus time weighting

An observation-weighted mean asks: **what did the average recorded quote look like?**

$$\bar{x}_{obs}=\frac{1}{n}\sum_{i=1}^{n}x_i$$

A time-weighted mean asks: **what did the quote look like over the covered passage of time?**

$$\bar{x}_{time}=\frac{\sum_i x_i\Delta_i}{\sum_i\Delta_i}$$

Example: a spread of 1 pip persists for 9 seconds; a spread of 3 pips persists for 1 second. With one observation at the start of each state, the observation mean is `(1+3)/2 = 2 pips`; the time mean is `(1×9+3×1)/10 = 1.2 pips`. Neither is universally superior: they answer different questions. Frequent quote updates cause observation weighting to emphasize busy periods.

MVP spread statistics are **observation-weighted**, explicitly labeled. Optional time-weighted spread statistics use previous-quote hold until the next update, window end or 60-second staleness cap, whichever comes first. Include the last quote before the window if still valid. Split durations at boundaries; exclude unknown/closed periods from the denominator and publish coverage seconds. At tied timestamps, earlier tied observations have zero subsequent duration; the last deterministic tie governs until the next timestamp.

Time weighting assumes a quote persisted between observations; it does not prove execution remained possible. Never carry a Friday quote across the weekend, nor divide by a full day when only part of it has valid coverage.

## 3. Metric definitions and worked examples

### 3.1 Bid-, ask- and midpoint-based OHLC

**Business question:** How did the observed quote evolve within an interval?

For a chosen basis `x_i` (bid, ask or midpoint), take all valid observations in `[T,T+h)`. Sort by `(event_ts, source_order, event_id)`. Then:

$$O=x_{first},\quad H=\max_i x_i,\quad L=\min_i x_i,\quad C=x_{last}$$

Synthetic observations in a single EUR/USD minute:

| Time / source row | Bid | Ask | Midpoint |
|---|---:|---:|---:|
| 12:00:00.000 / 1 | 1.10000 | 1.10020 | 1.10010 |
| 12:00:00.000 / 2 | 1.10020 | 1.10040 | 1.10030 |
| 12:00:59.999 / 3 | 1.09980 | 1.10000 | 1.09990 |

| Basis | Open | High | Low | Close |
|---|---:|---:|---:|---:|
| Bid | 1.10000 | 1.10020 | 1.09980 | 1.09980 |
| Ask | 1.10020 | 1.10040 | 1.10000 | 1.10000 |
| Midpoint | 1.10010 | 1.10030 | 1.09990 | 1.09990 |

The tick at exactly 12:01:00 belongs to the following minute. Two observations at the same timestamp remain separate. If a window has only one observation, O=H=L=C. If it has none, OHLC is null/absent, not zero.

**Required fields/aggregation:** pair, timestamp, stable ordering key and selected price; compute at 1s, 1m and 1h. `gold_candles` stores `price_basis`. Hourly OHLC can roll up complete minute OHLC using first open, maximum high, minimum low, last close and summed counts. Preserve boundary and coverage semantics.

**Units:** quote currency per base unit. **Default:** midpoint, because it reduces side-selection ambiguity for descriptive price analysis. Bid and ask remain useful to inspect the quote spread and explain execution-side differences.

**Interpretation and mistakes:** OHLC summarizes four values; it does not retain the full within-window path. Do not average high-bid and high-ask to derive high-midpoint: their extrema may occur at different times. Calculate midpoint per observation first. Midpoint candles do not imply midpoint fills.

**Quality limits:** ordering errors alter open/close; one bad tick can set high/low; late quotes revise any component. **Visualization:** candlesticks with UTC x-axis and selected basis/price y-axis, optional bid/ask close lines, and explicit missing intervals.

### 3.2 Absolute spread, pip spread and relative spread

**Business question:** How wide was this provider's two-sided quote, and how did it vary?

$$spread\_abs_i=a_i-b_i$$
$$spread\_pips_i=\frac{a_i-b_i}{p}$$
$$spread\_bps_i=10{,}000\frac{a_i-b_i}{m_i}$$

A basis point is 0.01%, or 0.0001 of a dimensionless ratio. For EUR/USD bid 1.10000, ask 1.10020 and midpoint 1.10010:

- `spread_abs = 0.00020` USD/EUR.
- `spread_pips = 0.00020 / 0.0001 = 2` pips.
- `spread_bps ≈ 1.81802` bps.

For USD/JPY bid 150.000 and ask 150.020, spread is 0.020 JPY/USD, or 2 pips, but only approximately 1.33324 bps. Pips standardize quotation convention; bps normalize relative to price.

**Required fields/aggregation:** bid, ask, midpoint and pip size. In `gold_spreads`, `mean_spread_abs`, `mean_spread_pips` and `mean_spread_bps` are arithmetic means of per-tick metrics. The mean of `spread_abs/mid` is generally different from mean spread divided by mean midpoint. Store sums/counts so daily means are weighted by observations, not by an equal average of minute means.

Example of correct rollup: one minute has 100 ticks averaging 1 pip and another has 10 ticks averaging 3 pips. The daily observation mean for these two minutes is `(100×1+10×3)/110 = 1.181818 pips`, not 2 pips.

Optional `p50_spread_pips` and `p95_spread_pips` use exact continuous interpolation at rank `(n-1)q` over sorted observations. For `[1,1,2,4]` pips, median is 1.5 and p95 is 3.7. Do not average minute p95s to obtain a daily p95; recompute from underlying observations or explicitly label a different statistic.

**Interpretation:** wider spreads describe worse quoted two-sided pricing in this feed. They may coincide with lower liquidity or uncertainty, but the chart alone establishes neither cause nor actual trading cost.

**Quality limits:** crossed quotes (`ask < bid`) are invalid for this contract; locked quotes have zero spread and are counted, not automatically rejected. Missing one side invalidates spread. Outliers may be real and should be flagged before exclusion. **Visualization:** mean/p95 line or band over time, a distribution plot, and later a session heatmap with sample counts. Never use raw absolute spread for a cross-pair ranking without units.

### 3.3 Simple returns

**Business question:** What proportional price change occurred between consecutive eligible minute samples?

$$simple\_return_k=r_k=\frac{P_k}{P_{k-1}}-1$$

If midpoint close rises from 1.1000 to 1.1011, the return is `0.001`, displayed as **0.1%**, or 10 basis points of return. This is a price change, not a leveraged account return.

**Required fields/aggregation:** eligible midpoint minute closes and their boundaries, in `gold_returns`. Use consecutive minute intervals in the same UTC day; require a last quote no more than 60 seconds old at each boundary. If a minute is missing, both the return into the gap and the return out of it are null. The first sample of a UTC day has no within-day predecessor.

Over a contiguous sequence, compound simple returns:

$$R=\prod_{k=1}^{n}(1+r_k)-1$$

For +1% followed by −1%, the cumulative return is `1.01×0.99−1 = −0.01%`, not zero. Do not sum simple returns except as an explicitly approximate small-return calculation.

**Units:** dimensionless stored ratio, percent displayed. **Interpretation:** a positive value means the base currency rose in quote-currency terms for this interval. It says nothing about future movement or net trading profit.

**Quality limits:** stale prices suppress measured changes; a gap bridged accidentally creates a multi-minute return mislabeled as one minute. **Visualization:** zero-centered return bars/line and a histogram, with missing returns omitted and counted.

### 3.4 Logarithmic returns

**Business question:** What additive measure describes proportional price changes through time?

$$log\_return_k=l_k=\ln\left(\frac{P_k}{P_{k-1}}\right)=\ln(1+r_k)$$

For 1.1000 → 1.1011, `l ≈ 0.0009995003`, displayed as approximately **0.0999500% log return**. It is close to, but not exactly, the 0.1% simple return.

For contiguous eligible samples, log returns add: `L = Σl_k`; convert to a cumulative simple return with `exp(L)-1`. With a missing interval, a sum of remaining log returns describes only the included segments. It is not the full start-to-end return.

**Fields/aggregation:** same samples and null policy as simple returns, in `gold_returns`. Prices must be strictly positive. **Units:** dimensionless; percent-scaled display must say log return. Use log returns as the volatility input for consistency.

**Mistakes and limits:** log returns are not cash profit and cannot be compared to simple returns without labeling. A positive-price validation rule is mathematically necessary. Outliers influence subsequent variance strongly. **Visualization:** line/bars or distribution with identical time filters to volatility.

### 3.5 Rolling volatility

**Business question:** How variable have recent one-minute price changes been?

The project defines `rolling_log_vol_60m` as the **sample standard deviation of the last 60 consecutive valid one-minute log returns**, ending at the displayed sample:

$$\bar{l}=\frac{1}{n}\sum_{j=1}^{n}l_j,\qquad
rolling\_log\_vol=\sqrt{\frac{\sum_{j=1}^{n}(l_j-\bar{l})^2}{n-1}}$$

Use `n=60`; this requires 61 eligible consecutive closes. A gap or new UTC day resets eligibility. The first valid 60-return window can therefore appear only after an hour of consecutive returns. Do not compute a “60m” metric over the last 60 available returns spread across several hours.

For a small illustrative three-return window `[0.001, -0.002, 0.001]`, mean is zero and sample standard deviation is `sqrt(0.000006/2) ≈ 0.00173205`, displayed as **0.173205% per one-minute return**. This illustrates the formula; it is not a valid production 60m window.

**Required fields/aggregation:** `gold_returns.log_return`, minute sample boundaries and eligibility. `gold_volatility` includes valid/expected counts and coverage. Use `STDDEV_SAMP`, not population standard deviation. Output null until the entire 60-return window is eligible.

**Units:** dimensionless dispersion of one-minute returns; percent per minute on charts. The 60-minute window is the estimation lookback, not the return horizon. A 0.1% per-minute standard deviation is not the same quantity as one-hour realized volatility.

**Interpretation:** a rise means recent sampled changes have become more variable. It does not provide direction, probability of loss, or a forecast by itself. Overlapping windows are highly related, not independent observations.

**Quality limits:** outliers can dominate; staleness can understate variability; one-second sampling can expose microstructure noise. Never compare volatility curves computed with different sampling intervals or missingness policies as if identical. **Visualization:** line beneath price, with units, sampling interval, lookback and null/coverage overlay.

### 3.6 Realized variance and realized volatility

**Business question:** How much sampled price variation accumulated over the reporting period?

$$RV=\sum_{k \in eligible}l_k^2,\qquad
realized\_vol=\sqrt{RV}$$

`RV` is realized **variance**, with squared-return units. `realized_vol_daily` is its square root for eligible one-minute log returns inside one UTC day, stored in `gold_daily_summary`.

Using `[0.001,-0.002,0.001]`, realized variance is `0.000006`; realized volatility is approximately `0.00244949`, or **0.244949% over those three intervals**. This differs from the sample standard deviation above: it accumulates squared changes without demeaning or dividing by `n-1`.

**Required fields/aggregation:** eligible one-minute log returns, day, expected intervals and coverage. For a fully covered 24-hour day with 1,440 minute closes, there are **1,439 within-day adjacent returns**, because the cross-day return is excluded. Provider closures can reduce the eligible calendar; if that calendar is unknown, do not assert full-day completeness.

**Interpretation:** more sampled movement produces a larger value. Missing returns produce an observed-subset estimate that typically omits variation; do not scale it up automatically. Retain coverage and label a partial result “observed intervals only.” Exclude partial days from default comparative rankings. Never sum hourly realized volatility to obtain daily volatility; sum squared returns/variances and then take the square root.

**Units:** variance is return²; volatility is a dimensionless period measure, displayed as percent. **Quality limits:** sampling frequency changes the estimate; gaps and noise matter. It is not a model-free guarantee of latent continuous-market volatility. **Visualization:** daily bars with coverage and sample count, optionally paired with return bars.

### 3.7 Tick count and quote-update activity

**Business question:** How active was the observed feed during an interval?

$$tick\_count=\#\{unique\ canonical\ source\ records\ in\ interval\}$$

$$quote\_activity\_hz=\frac{tick\_count}{window\_seconds}$$

If a fully observed 60-second interval contains 120 source records, tick count is 120 and activity is 2 observations/second. Redelivering 10 of them through Kafka does not change either analytical metric. Two distinct rows at the same timestamp remain two observations.

**Fields/aggregation:** event ID, pair, timestamp, source-order metadata and interval length. Use `gold_candles.tick_count` for a **single price basis**, or `gold_spreads.tick_count`. Do not sum counts across bid, ask and midpoint rows and triple the feed activity. Daily counts sum non-overlapping interval counts.

**Units:** observations and observations/second. Within a partially covered window, `tick_count/window_seconds` is the observed rate over the full interval, not a coverage-adjusted estimate. A separate `tick_count/covered_seconds` may be added later with a distinct name and only trustworthy coverage.

**Interpretation and limits:** more ticks indicate more source updates. They do not identify more trades, global liquidity or directional buying pressure. Timestamp granularity, feed throttling and repeated prices affect counts. Optional `price_change_count` counts changes in the bid/ask tuple; it is a different metric from all quote updates and requires a deterministic predecessor.

**Visualization:** activity bars beneath price, or pair/hour heatmap. Show count/coverage on hover and do not interpret a missing file as zero demand.

### 3.8 Daily price, spread and volatility summaries

**Business question:** What happened in this pair's observed UTC day, and is the summary comparable to another day?

`gold_daily_summary` combines metrics with their own aggregation rules:

| Daily field | Definition | Example | Units / caution |
|---|---|---|---|
| `mid_open/high/low/close` | First/max/min/last valid midpoint across the day | O 1.1000; H 1.1020; L 1.0990; C 1.1011 | USD/EUR; observed range, not executed trade range |
| `open_close_return` | `mid_close / mid_open - 1` | `1.1011/1.1000−1 = 0.1%` | Dimensionless; differs from previous-day-close return |
| `tick_count` | Distinct source records in day | 200,000 accepted records | Feed observations, not contracts traded |
| `mean_spread_pips` | Sum of per-tick pip spread / accepted count | 100 ticks at 1 pip and 10 at 3 → 1.181818 | Pips, observation weighted |
| `mean_spread_bps` | Mean of per-tick relative spread | One constant EUR/USD quote from section 3.2 → 1.81802 | Bps; normalize before averaging |
| `realized_vol_daily` | Square root of sum of eligible minute log returns squared | Three-return example → 0.244949% for those intervals only | Period %, requires coverage label |
| `return_coverage` | Eligible one-minute returns / expected within-day return slots | 1,400 / 1,439 ≈ 97.29% | Ratio; calendar must be explicit |
| `complete_day` | Acquisition and calendar checks pass, with no unresolved missing required intervals | Missing expected source file → false | Completeness is not inferred from a positive tick count |

Open-to-close return may still be computable with interior gaps; that does not validate realized volatility or spread coverage. Daily OHLC can use all valid quotes while volatility uses only eligible consecutive samples. Preserve those different denominators.

**Visualization:** sortable pair/day table with units and coverage, plus small daily bars. Use relative spread/returns for cross-pair comparison. Do not rank raw quote price or raw spread across currency units. Always expose partial-day and correction status.

### 3.9 Annualization is optional and model-dependent

Do not annualize in the default dashboard. If a later educational view annualizes sampled volatility, publish the assumptions next to it:

$$\sigma_{annual}=\sigma_{minute}\sqrt{M D}$$

Here `M` is assumed eligible minute returns per trading day and `D` assumed trading days per year. A common illustrative model uses 1,440 and 252; this project's within-UTC-day return convention would instead require reconciling its excluded boundary returns, for example explicitly using 1,439 for a fully covered day. Neither choice makes FX calendar/holiday effects disappear.

For a synthetic `σ_minute=0.0001`, an explicitly chosen `M=1439`, `D=252` gives approximately **6.02% annualized**. This square-root-time scaling assumes a stable variance process and sufficiently uncorrelated increments; it is not a forecast. Missing returns cannot be repaired simply by using 1,439 in the multiplier. Likewise, converting daily realized volatility to an annual scale with `sqrt(252)` describes a convention, not a guaranteed future risk.

## 4. Chart interpretation guide

### Price and OHLC panel

The x-axis is event time, not replay arrival time; the y-axis is the selected quote price. The candle body joins open and close and the wick spans low to high. Colors indicate close relative to open, not trade flow. Show basis, interval, tick count, revision and completeness in the tooltip.

A one-second chart exposes local detail and irregular updates; one-hour candles hide sequence and short-lived extremes. A long wick can result from a real quote, one bad record, or a corrected late tick. Inspect lineage before explaining it economically. Leave missing intervals blank; a flat carried-forward candle would imply observations that did not occur. Cross-pair raw-price overlays need indexing or returns, not a shared raw-price scale.

### Spread panel

The x-axis is window time and the y-axis is pips or bps. Lines/bands distinguish mean and p95; do not imply a confidence interval when a band is a quantile range. Widening indicates a broader quoted gap in this feed. It does not identify a cause or an achievable execution cost.

Longer aggregation intervals can hide brief spread spikes. P95 depends on the observation population and activity rate. Gaps, stale quotes and missing ask/bid fields reduce evidence; late quotes revise distributions. Compare pairs with bps for relative normalization, or pips with explicit instrument conventions.

### Returns and volatility panel

The return chart has event/sample time on x, percent return on y, and a meaningful zero line. A separate volatility chart uses percent dispersion per one-minute return; a second axis is acceptable only with very clear labels, so two aligned panels are preferable.

Large positive/negative returns reveal sampled changes; rising volatility reveals larger recent variability, not trend direction. Longer sampling may hide reversals and change measured volatility. Missing minute samples should break the return line; stale prices create artificial calm followed by jumps. Outliers and late corrections propagate through the 60-return lookback. Dimensionless returns help pair comparisons, but sampling, orientation, source and coverage must still match.

### Daily summary and activity panel

Rows represent pair/day; daily bars represent a named summary. Activity bars count observations per interval. A busy period is a feed phenomenon, not evidence of buying, selling or total turnover. Day-length/session definitions and excluded boundaries affect comparison.

Longer aggregation smooths intraday activity; a low daily total can mean acquisition failure. Use coverage badges, pair-normalized bps, percent returns and a consistent volatility horizon. Revisions should be visible when late data changes rankings. Do not compare a half day to a full day without qualification.

### Freshness and pipeline health

Display two clocks: **source event-time progress** and **processing/publication time**. A September replay viewed in October is intentionally historical. Old event timestamps are not evidence of broken ingestion. Offset lag, last successful publish, quarantine rate and captured delivery latency describe engineering health.

The x-axis in an operational history chart is wall-clock processing time; label it differently from financial charts. Aggregating latency by a minute changes how spikes are visible; show p95 and count rather than only a mean. Outliers in latency may reflect a restart, not market activity. An offline static page shows captured metrics, not live monitoring. Pair normalization is unnecessary for seconds/offset lag, but different replay speeds make throughput comparisons conditional.

### Reconciliation panel

Rows or a heatmap represent pair/window/metric; values show batch-stream difference and pass/fail status. Exact-zero OHLC differences are meaningful only when input manifests, metric versions and cutoffs match. Display missing/extra keys separately from numerical differences.

Provisional mismatches may follow expected lateness; reconciled mismatches are defects or explicitly changed input versions. Larger intervals can mask a wrong second candle, so test all three intervals. Compare decimal prices exactly and floating returns/volatility within the PM tolerances. Normalize displayed price differences to pips when helpful, but retain raw values and the actual comparison criterion. This panel validates processing consistency, not provider truth or financial predictive power.

### Business question mapping

| Business question | Metric | Gold dataset | Chart | Interpretation caveat |
|---|---|---|---|---|
| How did the quoted price move? | Midpoint OHLC | `gold_candles` | Candlesticks | Midpoint is not an executable trade price |
| How do quote sides differ? | Bid/ask close and OHLC | `gold_candles` | Aligned lines or basis selector | Extrema across sides may occur at different times |
| How wide was the quote? | Mean/p95 spread pips | `gold_spreads` | Line and quantile band | Observation weighted; p95 is not uncertainty |
| Which pair had wider relative spreads? | `mean_spread_bps` | `gold_spreads`, `gold_daily_summary` | Comparable bars | Same source period/coverage required |
| What changed since the prior minute? | `simple_return`, `log_return` | `gold_returns` | Zero-centered bars | Gaps cannot be bridged as one-minute returns |
| How variable were recent changes? | `rolling_log_vol_60m` | `gold_volatility` | Line | Lookback is 60m; units describe one-minute dispersion |
| How much variation accumulated today? | `realized_vol_daily` | `gold_daily_summary` | Daily bars | Sampling and coverage affect magnitude |
| How active was the feed? | `tick_count`, derived activity Hz | One basis of `gold_candles` | Bars/heatmap | Quote updates are not trade volume |
| Is this day complete enough to compare? | Coverage and `complete_day` | `gold_daily_summary` | Summary table | A calculable close does not establish completeness |
| Is the pipeline progressing? | Offset lag, delivery lag, last publish | `ops_runs` and manifest | Status/operational lines | Historical event age is not pipeline latency |
| Do both processing paths agree? | Metric differences and missing keys | `gold_reconciliation` | Status table/heatmap | Agreement does not prove source accuracy |

## 5. How financial definitions determine engineering choices

| Financial requirement | Engineering consequence | Test / audit evidence |
|---|---|---|
| A quote can share a timestamp with another | Identity includes canonical source row, not only time or prices | Two tied observations survive and retain deterministic order |
| OHLC needs first and last | Stable source ordering is part of the contract | Restart/repartition cannot change open/close |
| Windows must not overlap at boundaries | Use `[start,end)` in UTC at every interval | Boundary quote appears exactly once |
| Midpoint can lie between source increments | Preserve sufficient decimal scale; do not round to pip size | Half-increment midpoint fixture |
| Quote spread needs two contemporaneous sides | Validate bid/ask together from the same source observation | No asynchronous cross-row side pairing |
| A missing minute is not zero movement | Calendar spine plus nulls; no default forward-fill | Return across gap is null |
| Volatility needs equal sampling intervals | Compute from eligible one-minute closes, not irregular raw ticks | 60 valid returns must also be consecutive |
| Stale data is not proof of calm | Record last quote age and apply stated freshness threshold | Stale sample invalidates return eligibility |
| Extreme moves can be real | Separate hard validity rules from soft outlier flags | Original retained; reviewed view versioned |
| A UTC day is a convention | Store/report the boundary policy and calendar version | No implicit local-time grouping |
| Late quotes can change extrema and successors | Retain valid late data, rebuild dependent windows and returns | Correct next-minute return, rolling horizon and daily summary |
| Stream closure is not market completeness | Separate provisional, watermark-closed and reconciled status | Compare after explicit source/offset cutoff |
| Daily means need correct denominators | Roll up sums and counts, not means of means | Unequal-count spread example passes |
| Raw data does not establish market-wide activity | Name counts and volumes accurately in schema and UI | No “global volume,” VWAP or trade-count labels |

For reconciliation, apply the exact same price basis, calendar, ordering, sample eligibility and rounding in both paths. Keep their output namespaces independent. A corrected final comparison includes all accepted records in the frozen manifest; a two-minute watermark is a resource/latency policy, not a financial reason to erase later-arriving history.

Use the code tests and the PM acceptance fixture to connect semantics to implementation: tied timestamps, boundary placement, duplicate delivery, missing minutes, invalid prices and late correction. A visually smooth chart is not evidence these cases work.

## 6. Glossary

| Term | Meaning in this project |
|---|---|
| Base / quote currency | The unit being priced / currency used to express that price |
| Bid / ask | Two sides of the provider's quoted market |
| Midpoint | Arithmetic mean of bid and ask |
| Spread | Ask minus bid; may be expressed in price units, pips or bps |
| Pip / pipette | Conventional FX increment / one tenth of it |
| Basis point | One hundredth of a percentage point |
| Quote tick | A recorded quote observation, not necessarily a transaction |
| OHLC | Open, high, low and close for a specified basis and interval |
| Event time | Time assigned to the source observation |
| Ingestion time | Time the pipeline records receipt |
| Replay | Delivery of historical events on a controlled simulated schedule |
| Watermark | Event-time progress threshold used to bound streaming state |
| Stale quote | Last observation older than the chosen freshness threshold |
| Simple return | Proportional price change |
| Log return | Logarithm of the price ratio |
| Rolling volatility | Dispersion of sampled returns in a moving lookback |
| Realized variance / volatility | Sum of squared sampled log returns / its square root |
| Observation weighting | Each recorded observation contributes equally |
| Time weighting | Contribution reflects duration under a stated holding rule |
| Coverage | How much expected data/time is represented, with a stated denominator |
| Reconciliation | Comparison of outputs under the same inputs and definitions |
| Quarantine | Retained data that failed a specified acceptance rule |

## 7. Learning sequence tied to delivery

1. **Phase A — Synthetic cluster validation:** read the hand-calculated candle tests, identify tied timestamps and explain the static preview's not-run reconciliation status.
2. **Phase B — Real source slice:** inspect bid/ask, base/quote, UTC timezone, decimal precision and source-volume units before importing a CSV.
3. **Phase C — Recovery:** replay the same source at different speeds, retry deliveries and confirm final financial results do not change.
4. **Phase D — Scale:** measure actual provider observation counts, sampled time coverage and storage rather than equating target load with market activity.
5. **Phase E — Continuous processing:** learn watermark closure, provisional aggregates and late corrections; these are later capabilities, not the current bounded replay implementation.
6. **Phase F — Financial completeness:** validate session calendars, time weighting and quantiles with manual examples; test DST transitions and incomplete days.
7. **Phase G — Portfolio delivery:** label axes, source period, units, gaps and comparison status; distinguish implemented output from illustrative preview.

## Sources and verification boundaries

Checked **2026-10-08**. The formulas, numerical examples, sampling rules and acceptance policies are project definitions using standard arithmetic/statistics, not vendor-specific promises. This guide deliberately makes no recommendation to trade or forecast returns.

- **F1:** [OANDA: What is a pip?](https://www.oanda.com/us-en/skills-and-insights/education/introduction-trading/basics/what-is-a-pip/) — quotation conventions and pip context.
- **F2:** [Dukascopy ITick API](https://www.dukascopy.com/client/javadoc/com/dukascopy/api/ITick.html) — best-quote volume semantics and historical depth limits. The precise CSV representation still requires sample verification.
- **F3:** [BIS: The internationalisation of EME currency trading](https://www.bis.org/publications/qr-202212/internationalisation-eme-currency-trading) — context for OTC FX trading across locations; this project does not derive turnover estimates from tick counts.
- [Dukascopy Historical Data Export](https://www.dukascopy.com/swiss/english/marketwatch/historical/) — source availability. Download permissions and public redistribution are different questions.
- [Dukascopy terms of use](https://www.dukascopy.com/swiss/english/legal-pages/terms-of-use/) — review the applicable rights before publishing real-data artifacts. Use labeled synthetic examples until rights are established.
- The companion PM report contains the complete dated technology/source feasibility register, schema definitions, roadmap and operational acceptance criteria.
