from __future__ import annotations
import io
from typing import Any
import pandas as pd

def read_table(data: bytes, filename: str) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(data)) if filename.lower().endswith(('.xlsx','.xls')) else pd.read_csv(io.BytesIO(data))

def profile(df: pd.DataFrame) -> dict[str, Any]:
    return {'rows':len(df),'columns':len(df.columns),'schema':[{'name':str(c),'dtype':str(df[c].dtype),'nulls':int(df[c].isna().sum()),'unique':int(df[c].nunique(dropna=True))} for c in df.columns]}

def plan(df: pd.DataFrame) -> list[dict[str, Any]]:
    ops=[]
    for c in df.columns:
        if df[c].isna().any(): ops.append({'op':'fill_null','col':str(c),'value':''})
    if df.duplicated().any(): ops.append({'op':'dedupe','keys':[]})
    return ops

def validate_ops(ops: list[dict[str, Any]]) -> None:
    allowed={'fill_null','dedupe','filter','cast_numeric','select'}
    for op in ops:
        if op.get('op') not in allowed: raise ValueError(f"Unsupported operation: {op.get('op')}")

def execute(df: pd.DataFrame, ops: list[dict[str, Any]]) -> pd.DataFrame:
    validate_ops(ops); out=df.copy()
    for op in ops:
        kind=op['op']
        if kind=='fill_null': out[op['col']]=out[op['col']].fillna(op.get('value',''))
        elif kind=='dedupe': out=out.drop_duplicates(subset=op.get('keys') or None)
        elif kind=='filter': out=out.query(op['expression'])
        elif kind=='cast_numeric': out[op['col']]=pd.to_numeric(out[op['col']], errors='coerce')
        elif kind=='select': out=out[op['columns']]
    return out

def generate_pandas(ops: list[dict[str, Any]], source='input.csv') -> str:
    validate_ops(ops); lines=['import pandas as pd',f"df = pd.read_csv('{source}')"]
    for op in ops:
        k=op['op']
        if k=='fill_null': lines.append(f"df[{op['col']!r}] = df[{op['col']!r}].fillna({op.get('value','')!r})")
        elif k=='dedupe': lines.append('df = df.drop_duplicates()' if not op.get('keys') else f"df = df.drop_duplicates(subset={op['keys']!r})")
        elif k=='filter': lines.append(f"df = df.query({op['expression']!r})")
        elif k=='cast_numeric': lines.append(f"df[{op['col']!r}] = pd.to_numeric(df[{op['col']!r}], errors='coerce')")
        elif k=='select': lines.append(f"df = df[{op['columns']!r}]")
    lines.append("df.to_parquet('output.parquet', index=False)"); return '\n'.join(lines)+'\n'

def generate_dbt(ops: list[dict[str, Any]], source='raw.input') -> str:
    validate_ops(ops); lines=['select *']
    for op in ops:
        if op['op']=='dedupe': lines.append("-- add row_number() over the declared keys for warehouse deduplication")
        elif op['op']=='cast_numeric': lines.append(f", cast({op['col']} as numeric) as {op['col']}")
    lines.append(f"from {{{{ source('raw', 'input') }}}}"); return '\n'.join(lines)+'\n'
