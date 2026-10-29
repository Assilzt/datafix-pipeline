import pandas as pd
from app.core import execute, plan, generate_pandas

def test_plan_and_execute():
    df=pd.DataFrame({'a':[1,1,None]})
    ops=plan(df); out=execute(df,ops)
    assert len(out)==2 and out['a'].isna().sum()==0

def test_generate_rejects_unknown():
    try: generate_pandas([{'op':'nope'}])
    except ValueError as e: assert 'Unsupported' in str(e)
    else: assert False
