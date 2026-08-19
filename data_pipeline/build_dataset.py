import pandas as pd

from config.settings import PROCESSED_DATA_DIR
from data_pipeline.metrics import build_metrics_dataset


def main():
    metadata_path = (
        PROCESSED_DATA_DIR /
        "fund_metadata.csv"
    )

    output_path = (
        PROCESSED_DATA_DIR /
        "fund_metrics.csv"
    )

    funds = pd.read_csv(metadata_path)

    print(f"Funds to process: {len(funds)}")

    metrics = build_metrics_dataset(funds)

    metrics.to_csv(
        output_path,
        index=False,
    )

    print()
    print(f"Successfully processed: {len(metrics)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()