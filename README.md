# DataFix Pipeline Generator

[![CI](https://github.com/Assilzt/datafix-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Assilzt/datafix-pipeline/actions) [![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org) [![Data Engineering](https://img.shields.io/badge/Data%20Engineering-code%20generation-orange)](LICENSE)

DataFix Pipeline Generator is the engineer-facing MVP of DataFix: profile a CSV/Excel source, propose declarative operations, execute them on a sample, and generate reviewable pandas and dbt code. It keeps the operation list as the source of truth for previews and exports.

## MVP flow
`Source → Profile → Plan → Review JSON operations → Execute sample → Generate code`

## Supported operations
`fill_null`, `dedupe`, `filter`, `cast_numeric`, and `select`.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://localhost:8000/docs`.

## API example
```bash
curl -F 'file=@sample/vendor_feed.csv' http://localhost:8000/inspect
curl -X POST http://localhost:8000/generate -H 'Content-Type: application/json' \
  -d '{"operations":[{"op":"dedupe","keys":["invoice_id"]}]}'
```

## Architecture
The FastAPI boundary is intentionally thin. `app/core.py` contains the deterministic profiling, planner, executor, and code generators, enabling future targets such as Polars, Airflow, Great Expectations, and GitHub pull requests without coupling them to the UI.

## Docker
```bash
docker build -t datafix-pipeline . && docker run --rm -p 8000:8000 datafix-pipeline
```

## Roadmap
Add persistent job metadata, S3/GCS connectors, schema contracts, drift detection, dbt test generation, Airflow DAG generation, and a React review UI.

## License
MIT
