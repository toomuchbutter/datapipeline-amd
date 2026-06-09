import pandas as pd
import os
import datetime
from typing import Optional

class ParquetWriter:
    def __init__(self, base_path: str = "data/processed/"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def write(self, df: pd.DataFrame, dataset_name: str):
        """
        Writes dataframe to Parquet, partitioned by year/month/day.
        """
        if df.empty:
            return
            
        now = datetime.datetime.now()
        partition_path = os.path.join(
            self.base_path,
            dataset_name,
            now.strftime("%Y"),
            now.strftime("%m"),
            now.strftime("%d")
        )
        os.makedirs(partition_path, exist_ok=True)
        
        file_name = f"data_{now.strftime('%H%M%S')}.parquet"
        full_path = os.path.join(partition_path, file_name)
        
        try:
            df.to_parquet(full_path, index=False)
            print(f"Successfully wrote data to {full_path}")
        except Exception as e:
            print(f"Error writing Parquet: {e}")

if __name__ == "__main__":
    writer = ParquetWriter()
    # writer.write(pd.DataFrame({'a': [1]}), "prometheus")
