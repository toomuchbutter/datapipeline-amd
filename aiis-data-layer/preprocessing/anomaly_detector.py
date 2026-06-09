import pandas as pd
import numpy as np
import yaml

class AnomalyDetector:
    def __init__(self, config_path: str = "configs/metrics.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.z_cutoff = self.config['thresholds'].get('z_score_cutoff', 3.0)
        self.iqr_mult = self.config['thresholds'].get('iqr_multiplier', 1.5)

    def detect_z_score(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Flags outliers using Z-Score.
        """
        if column not in df.columns:
            return pd.Series([False] * len(df))
        
        mean = df[column].mean()
        std = df[column].std()
        if std == 0:
            return pd.Series([False] * len(df))
            
        z_scores = (df[column] - mean) / std
        return np.abs(z_scores) > self.z_cutoff

    def detect_iqr(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Flags outliers using IQR.
        """
        if column not in df.columns:
            return pd.Series([False] * len(df))
            
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - self.iqr_mult * IQR
        upper_bound = Q3 + self.iqr_mult * IQR
        
        return (df[column] < lower_bound) | (df[column] > upper_bound)

    def flag_anomalies(self, df: pd.DataFrame, columns: list = ['cpu', 'memory']) -> pd.DataFrame:
        """
        Adds anomaly flags to the dataframe.
        """
        for col in columns:
            if col in df.columns:
                z_flags = self.detect_z_score(df, col)
                iqr_flags = self.detect_iqr(df, col)
                df[f'{col}_anomaly'] = z_flags | iqr_flags
        return df

if __name__ == "__main__":
    detector = AnomalyDetector()
