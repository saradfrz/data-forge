import math
from decimal import Decimal
from app.domain import validate,event_id,candles,return_pair,volatility,normalized_json
from app.reconcile import equal,compare_rows

def event(i=0,**kw):
    return dict(schema_version=1,event_id=event_id('fixture',i),source_order=i,
                instrument='EURUSD',event_ts='2026-09-15T12:00:00Z',bid='1.1000',ask='1.1002',**kw)

def test_ties_and_boundary():
    a=event();b=event(1);b.update(bid='1.1002',ask='1.1004')
    c=event(2);c.update(event_ts='2026-09-15T12:00:59.999Z',bid='1.0998',ask='1.1000')
    d=event(3);d['event_ts']='2026-09-15T12:01:00Z'
    rows=[validate(e)[0] for e in [d,c,b,a]]
    first=candles(rows,60)[0]
    assert first['tick_count']==3
    assert [first[x] for x in ['open','high','low','close']]==list(map(Decimal,['1.1001','1.1003','1.0999','1.0999']))

def test_invalid_and_locked():
    e=event();e['ask']='1';assert validate(e)[1]==['prices']
    e['ask']=e['bid'];assert not validate(e)[1]
    e['event_ts']='2026-09-15T12:00:00';assert 'timestamp' in validate(e)[1]
    e['bid']='NaN';assert 'prices' in validate(e)[1]

def test_returns_and_volatility():
    simple,log=return_pair(Decimal('1.1000'),Decimal('1.1011'))
    assert math.isclose(simple,.001);assert math.isclose(log,math.log(1.001))
    sd,rv=volatility([.001,-.002,.001])
    assert math.isclose(sd,.0017320508075688774)
    assert math.isclose(rv,.0024494897427831783)

def test_reconciliation_detects_mutation():
    assert equal(Decimal('1.1'),Decimal('1.10'))
    assert not equal(None,0)
    assert not equal(float('nan'),float('nan'))
    assert compare_rows([{'id':1,'x':2}],[{'id':1,'x':3}],['id'])
    assert compare_rows([{'id':1,'x':2}],[],['id'])
