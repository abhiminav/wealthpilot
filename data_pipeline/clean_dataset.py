import pandas as pd

from config.settings import PROCESSED_DATA_DIR
from data_pipeline.metrics import filter_quality_funds


def main():
    input_path = (
        PROCESSED_DATA_DIR /
        "fund_metrics.csv"
    )

    output_path = (
        PROCESSED_DATA_DIR /
        "fund_metrics_clean.csv"
    )

    df = pd.read_csv(input_path)

    print("Before:", len(df))

    cleaned = filter_quality_funds(df)

    cleaned.to_csv(
        output_path,
        index=False,
    )

    print("After:", len(cleaned))
    print(
        "Removed:",
        len(df) - len(cleaned),
    )


if __name__ == "__main__":
    main()