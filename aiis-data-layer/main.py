import logging
import json
import os
import pandas as pd
from ingestion.prometheus_collector import PrometheusCollector
from preprocessing.cleaner import DataCleaner
from preprocessing.anomaly_detector import AnomalyDetector
from preprocessing.feature_builder import FeatureBuilder
from storage.parquet_writer import ParquetWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIIS-Pipeline")

class DataLayerPipeline:
    def __init__(self):
        self.collector = PrometheusCollector()
        self.cleaner = DataCleaner()
        self.detector = AnomalyDetector()
        self.builder = FeatureBuilder()
        self.writer = ParquetWriter()

    def run_prometheus_flow(self):
        logger.info("Starting Prometheus telemetry flow")
        
        # 1. Collect
        raw_data = self.collector.collect_all()
        if not raw_data:
            logger.warning("No data collected from Prometheus")
            return
        
        df = pd.DataFrame(raw_data)
        raw_count = len(df)
        
        # 2. Clean
        df = self.cleaner.remove_duplicates(df)
        duplicates_removed = raw_count - len(df)
        
        # Fill missing values
        df = self.cleaner.fill_missing_values(df)
        
        # 3. Anomaly Detection
        df = self.detector.flag_anomalies(df)
        outliers_count = df['cpu_anomaly'].sum() if 'cpu_anomaly' in df.columns else 0
        
        # 4. Time Alignment & aggregation
        df_aligned = self.cleaner.align_time_series(df)
        
        # 5. Feature Engineering
        df_features = self.builder.build_resource_features(df_aligned)
        df_features = self.builder.build_scaling_features(df_features)
        df_features = self.builder.build_pattern_features(df_features)
        df_features = self.builder.build_cost_carbon_features(df_features)
        df_features = self.builder.build_forecast_dataset(df_features)
        
        # 6. Store
        self.writer.write(df_features, "prometheus")
        
        # 7. Quality Validation Report
        report = {
            "records_processed": raw_count,
            "duplicates_removed": int(duplicates_removed),
            "outliers_detected": int(outliers_count),
            "features_generated": len(df_features.columns),
            "status": "success"
        }
        logger.info(f"Quality Report: {json.dumps(report, indent=2)}")
        return report

    def get_latest_inference_data(self, dataset_name: str = "prometheus") -> pd.DataFrame:
        """
        Loads the most recent parquet file for downstream agent inference.
        """
        dataset_path = os.path.join(self.writer.base_path, dataset_name)
        if not os.path.exists(dataset_path):
            return pd.DataFrame()
            
        # Find the latest file by walking the directory structure
        all_files = []
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(".parquet"):
                    all_files.append(os.path.join(root, file))
        
        if not all_files:
            return pd.DataFrame()
            
        latest_file = max(all_files, key=os.path.getmtime)
        return pd.read_parquet(latest_file)

    def get_training_dataset(self, dataset_name: str = "prometheus", days: int = 7) -> pd.DataFrame:
        """
        Loads data from the last N days for training.
        """
        # Simplified: just load all files for now
        dataset_path = os.path.join(self.writer.base_path, dataset_name)
        all_dfs = []
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(".parquet"):
                    all_dfs.append(pd.read_parquet(os.path.join(root, file)))
        
        if not all_dfs:
            return pd.DataFrame()
        return pd.concat(all_dfs).sort_values('timestamp')

if __name__ == "__main__":
    pipeline = DataLayerPipeline()
    pipeline.run_prometheus_flow()
