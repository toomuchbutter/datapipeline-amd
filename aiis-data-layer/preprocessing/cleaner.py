import pandas as pd
import numpy as np
import yaml
from typing import List, Optional

class DataCleaner:
    def __init__(self, config_path: str = "configs/metrics.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.alignment_window = self.config['pipeline'].get('alignment_window', '1min')

    def remove_duplicates(
        self,
        df: pd.DataFrame,
        key_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Removes duplicates while adapting to available columns.
        """

        if df.empty:
            return df

        if key_columns is None:
            candidate_columns = [
                'timestamp',
                'cluster_id',
                'namespace',
                'pod'
            ]

            key_columns = [
                col for col in candidate_columns
                if col in df.columns
            ]

        df = df.sort_values(by='timestamp')

        return df.drop_duplicates(
            subset=key_columns,
            keep='last'
        )

    def fill_missing_values(self, df: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
        """
        Fills missing values using forward fill, backward fill, or linear interpolation.
        """
        if method == 'ffill':
            return df.ffill()
        elif method == 'bfill':
            return df.bfill()
        elif method == 'linear':
            return df.interpolate(method='linear')
        else:
            return df

    def align_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts metrics into 1-minute windows and aggregates.
        Expects a 'timestamp' column as datetime.
        """
        if df.empty:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Group by pod/namespace and resample
        group_cols = [c for c in ['pod', 'namespace', 'cluster_id'] if c in df.columns]
        
        if not group_cols:
            return df.resample(self.alignment_window).agg(['mean', 'max', 'min', 'std'])

        def q95(x): return x.quantile(0.95)
        def q99(x): return x.quantile(0.99)
        
        resampled = df.groupby(group_cols).resample(self.alignment_window).agg({
            'cpu': ['mean', 'max', 'min', q95, q99],
            'memory': ['mean', 'max', 'min', q95, q99]
        })
        
        # Flatten columns
        resampled.columns = [f"{col}_{agg}" for col, agg in resampled.columns]
        return resampled.reset_index()

if __name__ == "__main__":
    cleaner = DataCleaner()
    # df = pd.DataFrame(...)
    # df_clean = cleaner.remove_duplicates(df)
    # df_aligned = cleaner.align_time_series(df_clean)
