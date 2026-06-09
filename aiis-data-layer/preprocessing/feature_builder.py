import pandas as pd
import numpy as np
from typing import Dict, List, Any

class FeatureBuilder:
    def __init__(self):
        # Constants for cost and carbon (could be moved to configs)
        self.cpu_rate = 0.05 # $/hour
        self.gpu_rate = 0.50 # $/hour
        self.carbon_intensity = 0.4 # kg CO2/kWh
        self.pue = 1.6 # Power Usage Effectiveness

    def build_resource_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates basic resource features.
        Expects aligned and aggregated metrics.
        """
        # Mapping aggregated names from cleaner.py to feature names
        # e.g. cpu_mean -> cpu_avg
        rename_map = {
            'cpu_mean': 'cpu_avg',
            'cpu_max': 'cpu_max',
            'cpu_q95': 'cpu_p95',
            'memory_mean': 'memory_avg',
            'memory_max': 'memory_max',
            'memory_q95': 'memory_p95'
        }
        df = df.rename(columns=rename_map)
        return df

    def build_scaling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        current_replicas, replica_growth_rate, pod_startup_time, scaling_frequency.
        """
        if 'replicas' in df.columns:
            df['replica_growth_rate'] = df['replicas'].diff().fillna(0)
            df['scaling_frequency'] = df['replicas'].diff().ne(0).rolling(window=60).sum().fillna(0)
        return df

    def build_pattern_features(self, df: pd.DataFrame, column: str = 'cpu_avg') -> pd.DataFrame:
        """
        rolling_mean_5m, rolling_mean_15m, rolling_std, trend_strength, seasonality_score, change_rate.
        """
        if column not in df.columns:
            return df
            
        df['rolling_mean_5m'] = df[column].rolling(window=5).mean()
        df['rolling_mean_15m'] = df[column].rolling(window=15).mean()
        df['rolling_std'] = df[column].rolling(window=15).std()
        
        # Simple trend strength: correlation with time index
        df['trend_strength'] = df[column].rolling(window=30).apply(lambda x: np.abs(np.corrcoef(x, np.arange(len(x)))[0, 1]) if len(x) > 1 else 0)
        
        # Change rate
        df['change_rate'] = df[column].pct_change().fillna(0)
        
        return df

    def build_forecast_dataset(self, df: pd.DataFrame, window_size: int = 60) -> pd.DataFrame:
        """
        Create sliding windows for forecasting.
        Input: Past 60 minutes
        Predict: Next 5, 15, 30 minutes
        """
        if len(df) < window_size + 30:
            return df
            
        df['future_cpu_5m'] = df['cpu_avg'].shift(-5)
        df['future_cpu_15m'] = df['cpu_avg'].shift(-15)
        df['future_cpu_30m'] = df['cpu_avg'].shift(-30)
        
        # Normally you'd flatten the 'history' into features, but for this layer
        # we'll provide the targets. Downstream agents will use the rolling features as history.
        return df

    def build_cost_carbon_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        estimated_compute_cost, estimated_gpu_cost, power_usage_kwh, co2_estimate.
        """
        # Simplified cost formula: cost = cpu_hours * cpu_rate
        # Since we have 1-minute windows, we divide by 60 for hourly rate
        if 'cpu_avg' in df.columns:
            df['estimated_compute_cost'] = (df['cpu_avg'] / 100) * (1/60) * self.cpu_rate # assuming cpu_avg is %
            
        # GPU features (dummy if not present)
        if 'gpu_utilization' not in df.columns:
            df['gpu_utilization'] = 0
            
        df['estimated_gpu_cost'] = (df['gpu_utilization'] / 100) * (1/60) * self.gpu_rate
        
        # Power usage estimtion (simplified)
        # Power = (CPU_Usage * Base_Power) * PUE
        df['power_usage_kwh'] = (df['cpu_avg'] * 0.2 + 50) * self.pue / 1000 # dummy formula
        df['co2_estimate'] = df['power_usage_kwh'] * self.carbon_intensity
        
        return df

if __name__ == "__main__":
    builder = FeatureBuilder()
