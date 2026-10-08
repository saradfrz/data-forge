"""Pure financial definitions; imported by Spark workers and unit tests."""
import hashlib
import json
import math
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from statistics import stdev
from models.quote import Quote

PIPS = {x: Decimal('0.0001') for x in
        ['EURUSD','GBPUSD','USDCHF','USDCAD','AUDUSD','NZDUSD','EURGBP']}
PIPS.update({x: Decimal('0.01') for x in ['USDJPY','EURJPY','GBPJPY']})

def digest(value):
    return hashlib.sha256(value).hexdigest()

def event_id(file_hash, row_index):
    return digest(json.dumps([file_hash, row_index], separators=(',', ':')).encode())

def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp must include UTC offset')
    return parsed.astimezone(timezone.utc)

def validate(event):
    errors = []
    if event.get('schema_version') != 1:
        errors.append('schema_version')
    pair = event.get('instrument')
    if pair not in PIPS:
        errors.append('instrument')
    try:
        ts = timestamp(event['event_ts'])
    except (ValueError, KeyError, TypeError, AttributeError):
        ts = None
        errors.append('timestamp')
    try:
        bid, ask = Decimal(event['bid']), Decimal(event['ask'])
        if not bid.is_finite() or not ask.is_finite() or not 0 < bid <= ask:
            raise ValueError()
        if max(abs(bid), abs(ask)) >= Decimal('10000000000'):
            raise ValueError()
        if any(x != x.quantize(Decimal('0.0000000001')) for x in [bid,ask]):
            raise ValueError()
    except (InvalidOperation, ValueError, KeyError, TypeError):
        bid = ask = None
        errors.append('prices')
    if not event.get('event_id') or not isinstance(event.get('source_order'), int):
        errors.append('identity')
    if errors:
        return None, errors
    return Quote(event['event_id'], pair, ts, event['source_order'], bid, ask), []

def normalized_json(raw):
    try:
        event = json.loads(raw)
        q, reasons = validate(event)
        volumes = {}
        flags = []
        for key in ['bid_volume_source','ask_volume_source']:
            value = event.get(key)
            try:
                value = float(value) if value not in [None,''] else None
                if value is not None and (not math.isfinite(value) or value < 0):
                    raise ValueError()
            except (ValueError, TypeError):
                value = None
                flags.append(key + '_invalid')
            volumes[key] = value
        return json.dumps(dict(event_id=event.get('event_id'),
            instrument=event.get('instrument'), event_ts=q.event_ts.isoformat() if q else None,
            source_order=event.get('source_order'), bid=str(q.bid) if q else None,
            ask=str(q.ask) if q else None, reasons=reasons, quality_flags=flags,
            volume_unit=event.get('volume_unit','unverified'), **volumes))
    except (ValueError, TypeError, AttributeError):
        return json.dumps({'reasons':['malformed_json']})

def candles(quotes, seconds, basis='mid'):
    """Independent small-fixture oracle; production aggregates in Spark."""
    bins = {}
    for q in quotes:
        start = int(q.event_ts.timestamp()) // seconds * seconds
        bins.setdefault((q.instrument,start),[]).append(q)
    output = []
    for (pair,start), rows in sorted(bins.items()):
        rows.sort(key=lambda q:(q.event_ts,q.source_order,q.event_id))
        prices=[getattr(q,basis) for q in rows]
        output.append(dict(instrument=pair,window_start=start,open=prices[0],
            high=max(prices),low=min(prices),close=prices[-1],tick_count=len(rows)))
    return output

def return_pair(previous, current):
    return float(current / previous - 1), math.log(float(current / previous))

def volatility(values):
    return stdev(values), math.sqrt(sum(x*x for x in values))
