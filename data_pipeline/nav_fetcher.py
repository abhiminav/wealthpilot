from pathlib import Path

import pandas as pd
import requests


MFAPI_BASE_URL = "https://api.mfapi.in/mf"


def fetch_latest_nav(
    scheme_code: str | None = None,
) -> pd.DataFrame:
    """
    Fetch latest NAV data.

    If scheme_code is provided, fetch that scheme from MFapi.
    Otherwise, fetch the complete latest NAV universe from AMFI.
    """

    # Complete AMFI universe
    if scheme_code is None:
        response = requests.get(
            "https://www.amfiindia.com/spages/NAVAll.txt",
            timeout=30,
        )
        response.raise_for_status()

        records = []

        for line in response.text.splitlines():
            parts = line.split(";")

            if len(parts) != 6:
                continue

            records.append(parts)

        columns = [
            "scheme_code",
            "isin_growth",
            "isin_div_payout",
            "scheme_name",
            "net_asset_value",
            "nav_date",
        ]

        df = pd.DataFrame(
            records,
            columns=columns,
        )

        df["net_asset_value"] = pd.to_numeric(
            df["net_asset_value"],
            errors="coerce",
        )

        df["nav_date"] = pd.to_datetime(
            df["nav_date"],
            format="%d-%b-%Y",
            errors="coerce",
        )

        return df.dropna(
            subset=[
                "scheme_code",
                "scheme_name",
                "net_asset_value",
            ]
        )

    # Single scheme from MFapi
    url = f"{MFAPI_BASE_URL}/{scheme_code}/latest"

    response = requests.get(
        url,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "SUCCESS":
        raise ValueError(
            f"MFapi request failed: {payload}"
        )

    data = payload.get("data", [])

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(
        df["date"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    df["nav"] = pd.to_numeric(
        df["nav"],
        errors="coerce",
    )

    df["scheme_code"] = scheme_code
    df["scheme_name"] = payload["meta"]["scheme_name"]

    return df[
        [
            "scheme_code",
            "scheme_name",
            "date",
            "nav",
        ]
    ]


def fetch_historical_nav(
    scheme_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Fetch historical NAV data for a mutual fund.

    Dates must use YYYY-MM-DD format.
    """

    url = f"{MFAPI_BASE_URL}/{scheme_code}"

    params = {}

    if start_date:
        params["startDate"] = start_date

    if end_date:
        params["endDate"] = end_date

    response = requests.get(
        url,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "SUCCESS":
        raise ValueError(f"MFapi request failed: {payload}")

    data = payload.get("data", [])

    if not data:
        return pd.DataFrame(
            columns=[
                "scheme_code",
                "scheme_name",
                "date",
                "nav",
            ]
        )

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(
        df["date"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    df["nav"] = pd.to_numeric(
        df["nav"],
        errors="coerce",
    )

    df["scheme_code"] = str(
        payload["meta"]["scheme_code"]
    )

    df["scheme_name"] = payload["meta"]["scheme_name"]

    df = df.dropna(
        subset=["date", "nav"]
    )

    df = df.sort_values("date")

    return df[
        [
            "scheme_code",
            "scheme_name",
            "date",
            "nav",
        ]
    ].reset_index(drop=True)


def save_nav_data(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save NAV data to CSV."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        index=False,
    )


def fetch_scheme_metadata(scheme_code: str) -> dict:
    """Fetch scheme metadata from MFapi."""

    url = f"{MFAPI_BASE_URL}/{scheme_code}/latest"

    response = requests.get(
        url,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "SUCCESS":
        raise ValueError(
            f"MFapi request failed: {payload}"
        )

    meta = payload.get("meta", {})

    return {
        "amfi_code": str(meta.get("scheme_code", scheme_code)),
        "scheme_name": meta.get("scheme_name"),
        "fund_house": meta.get("fund_house"),
        "scheme_type": meta.get("scheme_type"),
        "scheme_category": meta.get("scheme_category"),
        "isin_growth": meta.get("isin_growth"),
    }


def fetch_and_cache_historical_nav(
    scheme_code: str,
    cache_dir: Path,
) -> pd.DataFrame:
    """Fetch historical NAV and cache it locally."""

    cache_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_file = (
        cache_dir /
        f"{scheme_code}.csv"
    )

    if cache_file.exists():
        return pd.read_csv(
            cache_file,
            parse_dates=["date"],
        )

    df = fetch_historical_nav(
        scheme_code
    )

    if not df.empty:
        df.to_csv(
            cache_file,
            index=False,
        )

    return df