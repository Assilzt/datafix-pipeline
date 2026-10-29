from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from .core import read_table, profile, plan, execute, generate_pandas, generate_dbt
app=FastAPI(title='DataFix Pipeline Generator', version='0.1.0')
class Operations(BaseModel): operations:list[dict]
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/inspect')
async def inspect(file: UploadFile=File(...)):
    df=read_table(await file.read(),file.filename or 'input.csv'); return {'profile':profile(df),'plan':plan(df)}
@app.post('/generate')
def generate(body: Operations):
    try: return {'pandas':generate_pandas(body.operations),'dbt':generate_dbt(body.operations)}
    except ValueError as e: raise HTTPException(400,str(e))
@app.post('/execute')
async def run(body: Operations, file: UploadFile=File(...)):
    try: df=read_table(await file.read(),file.filename or 'input.csv'); out=execute(df,body.operations)
    except (ValueError,KeyError) as e: raise HTTPException(400,str(e))
    return {'rows':len(out),'columns':list(out.columns),'preview':out.head(20).where(out.notna(),None).to_dict(orient='records')}
