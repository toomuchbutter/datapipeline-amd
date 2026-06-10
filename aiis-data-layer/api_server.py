import os
import pandas as pd
import numpy as np  
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AegisScale-API")

app = FastAPI(title="🛡️ AegisScale AI Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "data/processed/prometheus"

def locate_latest_parquet_record() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    all_parquet_files = [
        os.path.join(DATA_PATH, f) for f in os.listdir(DATA_PATH) if f.endswith(".parquet")
    ]
    if not all_parquet_files:
        return pd.DataFrame()
    target_file = max(all_parquet_files, key=os.path.getmtime)
    return pd.read_parquet(target_file)

@app.get("/health")
def api_health():
    return {"status": "ONLINE", "pipeline_storage_path_exists": os.path.exists(DATA_PATH)}

@app.get("/api/v1/metrics/latest")
def get_latest_polished_inference_metrics():
    try:
        df = locate_latest_parquet_record()
        if df.empty:
            raise HTTPException(status_code=404, detail="No active telemetry records found on disk.")
            
        latest_row_dict = df.iloc[-1].to_dict()
        
        # Converts specialized data types into formats standard JSON protocols can handle
        for key, value in latest_row_dict.items():
            if isinstance(value, (np.int64, np.int32)):
                latest_row_dict[key] = int(value)
            elif isinstance(value, (np.float64, np.float32)):
                latest_row_dict[key] = float(value)
            elif isinstance(value, np.bool_):
                latest_row_dict[key] = bool(value)
                
        return latest_row_dict
    except Exception as e:
        logger.error(f"💥 Endpoint crashed: {str(e)}")
        return {"error": "Internal Server Error Exception Caught", "real_reason": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
