import pandas as pd

from value_check.app.services.history import compare_against_history


def test_history_percentile_for_multiple_metric_marks_expensive() -> None:
    history_df = pd.DataFrame(
        {
            "ticker": ["AAA"] * 5,
            "date": pd.to_datetime(["2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31", "2024-12-31"]),
            "pe_ratio": [10.0, 12.0, 14.0, 18.0, 22.0],
            "ev_ebitda": [8.0, 9.0, 10.0, 11.0, 12.0],
            "ps_ratio": [2.0, 2.5, 3.0, 3.2, 3.5],
            "pb_ratio": [4.0, 4.5, 5.0, 5.5, 6.0],
            "fcf_yield": [0.050, 0.048, 0.045, 0.040, 0.038],
        }
    )
    rows = compare_against_history(
        {
            "pe_ratio": 24.0,
            "ev_ebitda": 12.5,
            "ps_ratio": 3.6,
            "pb_ratio": 6.2,
            "fcf_yield": 0.030,
        },
        history_df,
        lookback_years=10,
    )
    pe_row = next(row for row in rows if row["metric"] == "pe_ratio")
    assert pe_row["percentile_rank"] == 100.0
    assert pe_row["metric_interpretation"] == "expensive"


def test_fcf_yield_percentile_uses_cheaper_direction_correctly() -> None:
    history_df = pd.DataFrame(
        {
            "ticker": ["AAA"] * 4,
            "date": pd.to_datetime(["2021-12-31", "2022-12-31", "2023-12-31", "2024-12-31"]),
            "fcf_yield": [0.02, 0.03, 0.04, 0.05],
        }
    )
    rows = compare_against_history({"fcf_yield": 0.05}, history_df, lookback_years=10)
    fcf_row = next(row for row in rows if row["metric"] == "fcf_yield")
    assert fcf_row["percentile_rank"] == 25.0
    assert fcf_row["metric_interpretation"] == "slightly cheap"


def test_history_parser_handles_non_numeric_placeholders() -> None:
    history_df = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2022-12-31", "2023-12-31", "2024-12-31"]),
            "pe_ratio": ["neg", "18.0", "22.0"],
        }
    )
    rows = compare_against_history({"pe_ratio": 20.0}, history_df, lookback_years=10)
    pe_row = next(row for row in rows if row["metric"] == "pe_ratio")
    assert pe_row["historical_average"] == 20.0
