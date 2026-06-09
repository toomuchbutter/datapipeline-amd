import pandas as pd
import numpy as np
import datetime
from main import DataLayerPipeline
import os

def test_pipeline():
    # Since we don't have a real Prometheus, we'll mock the collector's collect_all
    pipeline = DataLayerPipeline()
    
    # Generate dummy raw data
    dummy_data = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for i in range(100):
        ts = (now - datetime.timedelta(minutes=i)).isoformat()
        dummy_data.append({
            "timestamp": ts,
            "cluster_id": "test-cluster",
            "pod": "pod-1",
            "namespace": "default",
            "cpu": 50 + np.random.normal(0, 5),
            "memory": 200 + np.random.normal(0, 10),
            "replicas": 3
        })
    
    # Inject dummy data into a mock run
    df = pd.DataFrame(dummy_data)
    print("\nColumns in DataFrame:")
    print(df.columns.tolist())

    print("\nSample Data:")
    print(df.head())
    print("Running pipeline on dummy data...")
    # Step-by-step for verification visibility
    df = pipeline.cleaner.remove_duplicates(df)
    df = pipeline.cleaner.fill_missing_values(df)
    df = pipeline.detector.flag_anomalies(df)
    df_aligned = pipeline.cleaner.align_time_series(df)
    
    df_features = pipeline.builder.build_resource_features(df_aligned)
    df_features = pipeline.builder.build_scaling_features(df_features)
    df_features = pipeline.builder.build_pattern_features(df_features)
    df_features = pipeline.builder.build_cost_carbon_features(df_features)
    df_features = pipeline.builder.build_forecast_dataset(df_features)
    
    pipeline.writer.write(df_features, "test_dataset")
    
    # Test API
    latest = pipeline.get_latest_inference_data("test_dataset")
    print(f"Latest inference data columns: {latest.columns.tolist()}")
    print(f"Sample row:\n{latest.head(1)}")
    
    assert not latest.empty
    print("Pipeline verification SUCCESSful!")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/processed", exist_ok=True)
    test_pipeline()
