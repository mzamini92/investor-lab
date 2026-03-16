from __future__ import annotations

from etf_catalog.fetcher import parse_nasdaq_traded_text, parse_other_listed_text


def test_parse_nasdaq_traded_text_filters_columns() -> None:
    raw_text = "\n".join(
        [
            "Nasdaq Traded|Symbol|Security Name|Listing Exchange|Market Category|ETF|Round Lot Size|Test Issue|Financial Status|CQS Symbol|NASDAQ Symbol|NextShares",
            "Y|QQQ|Invesco QQQ Trust, Series 1|Q|Q|Y|100|N|N||QQQ|N",
            "Y|AAPL|Apple Inc. - Common Stock|Q|Q|N|100|N|N||AAPL|N",
            "File Creation Time: 03152026",
        ]
    )
    df = parse_nasdaq_traded_text(raw_text)
    assert list(df.columns) == ["ticker", "security_name", "listing_exchange", "is_etf"]
    assert df.iloc[0]["ticker"] == "QQQ"


def test_parse_other_listed_text_filters_columns() -> None:
    raw_text = "\n".join(
        [
            "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
            "VOO|Vanguard S&P 500 ETF|P|VOO|Y|100|N|VOO",
            "BRK.B|Berkshire Hathaway Inc. Class B|N|BRK.B|N|100|N|BRK.B",
            "File Creation Time: 03152026",
        ]
    )
    df = parse_other_listed_text(raw_text)
    assert list(df.columns) == ["ticker", "security_name", "listing_exchange", "is_etf"]
    assert df.iloc[0]["ticker"] == "VOO"

