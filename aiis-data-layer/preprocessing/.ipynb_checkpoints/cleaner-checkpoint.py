import pandas as pd
import numpy as np
import yaml
from typing import List, Optional


class DataCleaner:

    def __init__(self, config_path: str = "configs/metrics.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.alignment_window = (
            self.config["pipeline"]
            .get("alignment_window", "1min")
        )

    def remove_duplicates(
        self,
        df: pd.DataFrame,
        key_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Removes duplicate records while adapting
        to available columns.
        """

        if df.empty:
            return df

        if key_columns is None:

            candidate_columns = [
                "timestamp",
                "cluster_id",
                "namespace",
                "pod"
            ]

            key_columns = [
                col
                for col in candidate_columns
                if col in df.columns
            ]

        if not key_columns:
            return df

        if "timestamp" in df.columns:
            df = df.sort_values(by="timestamp")

        return df.drop_duplicates(
            subset=key_columns,
            keep="last"
        )

    def fill_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "linear"
    ) -> pd.DataFrame:
        """
        Fills missing values only for numeric columns.
        Avoids interpolation errors on string columns.
        """

        if df.empty:
            return df

        df = df.copy()

        numeric_cols = df.select_dtypes(
            include=[np.number]
        ).columns

        if len(numeric_cols) == 0:
            return df

        if method == "ffill":

            df[numeric_cols] = (
                df[numeric_cols]
                .ffill()
            )

        elif method == "bfill":

            df[numeric_cols] = (
                df[numeric_cols]
                .bfill()
            )

        elif method == "linear":

            df[numeric_cols] = (
                df[numeric_cols]
                .interpolate(method="linear")
                .ffill()
                .bfill()
            )

        return df

    def align_time_series(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aligns telemetry into fixed windows.
        Generates statistical summaries.
        """

        if df.empty:
            return df

        if "timestamp" not in df.columns:
            return df

        df = df.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        df = df.set_index("timestamp")

        group_cols = [
            c
            for c in [
                "pod",
                "namespace",
                "cluster_id"
            ]
            if c in df.columns
        ]

        metric_columns = [
            c
            for c in [
                "cpu",
                "memory",
                "replicas"
            ]
            if c in df.columns
        ]

        if not metric_columns:
            return df.reset_index()

        def q95(x):
            return x.quantile(0.95)

        def q99(x):
            return x.quantile(0.99)

        agg_dict = {}

        for metric in metric_columns:
            agg_dict[metric] = [
                "mean",
                "max",
                "min",
                q95,
                q99
            ]

        if group_cols:

            resampled = (
                df.groupby(group_cols)
                .resample(self.alignment_window)
                .agg(agg_dict)
            )

        else:

            resampled = (
                df.resample(self.alignment_window)
                .agg(agg_dict)
            )

        resampled.columns = [
            f"{col}_{agg}"
            for col, agg in resampled.columns
        ]

        return resampled.reset_index()


if __name__ == "__main__":

    cleaner = DataCleaner()

    sample_df = pd.DataFrame({
        "timestamp": pd.date_range(
            "2025-01-01",
            periods=5,
            freq="min"
        ),
        "cluster_id": ["cluster-1"] * 5,
        "pod": ["pod-1"] * 5,
        "namespace": ["default"] * 5,
        "cpu": [50, np.nan, 55, 60, 58],
        "memory": [200, 205, np.nan, 210, 215],
        "replicas": [3, 3, 3, 4, 4]
    })

    cleaned = cleaner.remove_duplicates(sample_df)

    cleaned = cleaner.fill_missing_values(
        cleaned,
        method="linear"
    )

    aligned = cleaner.align_time_series(
        cleaned
    )

    print(aligned.head())