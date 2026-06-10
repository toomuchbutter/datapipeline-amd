import os
import time
import datetime
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AegisScale-Pipeline")

class LiveDataPolishingPipeline:
    def __init__(self, base_path: str = "data/processed/prometheus"):
        self.base_path = base_path
        self.tick_count = 0
        os.makedirs(self.base_path, exist_ok=True)
        
    def collect_mock_prometheus_tick(self) -> pd.DataFrame:
        """Simulates raw, noisy incoming metrics from a server group."""
        self.tick_count += 1
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Force a major traffic surge pattern after tick #5 to verify agent triggers
        if self.tick_count < 6:
            base_cpu = 42.0
            base_rps = 1100
            pattern = "PERIODIC"
        else:
            base_cpu = 89.4
            base_rps = 4750
            pattern = "BURST"
            
        raw_row = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cluster_id": "amd-prod-cluster-01",
            "pod": "payment-processor-pod",
            "namespace": "production",
            "cpu": float(base_cpu + np.random.normal(0, 1.5)),
            "memory": float(210.0 + np.random.normal(0, 4.0)),
            "replicas": 3,
            "request_rate": int(base_rps + np.random.randint(-30, 30)),
            "pattern_archetype": pattern
        }
        return pd.DataFrame([raw_row])

    def clean_and_build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies anomaly filters and appends calculated resource metrics."""
        df_processed = df.copy()
        
        # 1. Resource renaming validation
        df_processed['cpu_avg'] = df_processed['cpu']
        df_processed['memory_avg'] = df_processed['memory']
        
        # 2. Simulate anomaly filter tracking flags
        df_processed['cpu_anomaly'] = df_processed['cpu_avg'] > 95.0
        
        # 3. Formulate predictive look-ahead values (The ML Forecaster Output)
        # If trend is shifting up, predict higher near-term resource strain
        if df_processed['pattern_archetype'].iloc[0] == "BURST":
            df_processed['future_cpu_15m'] = min(99.0, float(df_processed['cpu_avg'].iloc[0] * 1.12))
        else:
            df_processed['future_cpu_15m'] = max(10.0, float(df_processed['cpu_avg'].iloc[0] + np.random.uniform(-2, 2)))
            
        # 4. Integrate AMD Carbon Footprint & FinOps Logic
        # Calculate power consumption metrics based on processor load equations
        df_processed['amd_epyc_power_watts'] = 120.0 + (df_processed['cpu_avg'] * 2.5)
        df_processed['estimated_compute_cost'] = (df_processed['cpu_avg'] / 100) * 0.05
        df_processed['co2_estimate'] = (df_processed['amd_epyc_power_watts'] / 1000) * 0.4
        
        return df_processed

    def commit_to_parquet(self, df: pd.DataFrame):
        """Saves the record onto disk as an enterprise-grade Parquet file."""
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"metrics_{timestamp_str}.parquet"
        target_file_path = os.path.join(self.base_path, file_name)
        
        df.to_parquet(target_file_path, index=False)
        logger.info(f"💾 [Storage] Successfully saved polished log: {file_name}")

    def run_one_cycle(self):
        logger.info("Executing pipeline telemetry flow cycle...")
        raw_df = self.collect_mock_prometheus_tick()
        polished_df = self.clean_and_build_features(raw_df)
        self.commit_to_parquet(polished_df)

if __name__ == "__main__":
    engine = LiveDataPolishingPipeline()
    print("🚀 Data Pipeline online. Writing telemetry frames. Press Ctrl+C to stop.")
    try:
        while True:
            print("\n" + "="*60)
            engine.run_one_cycle()
            time.sleep(10) # Process a new telemetry slice every 10 seconds
    except KeyboardInterrupt:
        print("\n🛑 Telemetry ingestion loop halted safely.")
