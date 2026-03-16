MOAT_SCORE_WEIGHTS = {
    "gross_margin_trajectory": 0.20,
    "roic_spread": 0.20,
    "pricing_power": 0.18,
    "market_share": 0.15,
    "innovation_reinvestment": 0.12,
    "sales_efficiency": 0.08,
    "commentary_pressure": 0.07,
}

MOAT_LABEL_BANDS = [
    (35, "Red"),
    (50, "Orange"),
    (65, "Yellow"),
    (80, "Green"),
    (101, "Strong Green"),
]

COMMENTARY_KEYWORDS = {
    "negative": {
        "pricing_pressure": ["pricing pressure", "price sensitivity", "value-seeking", "softer demand"],
        "competition": ["competitive", "competition intensified", "share loss", "churn"],
        "promotions": ["promotions", "discounting", "couponing"],
        "cost_pressure": ["cost pressure", "margin pressure", "inflation", "headwind"],
        "customer_weakness": ["customer weakness", "cautious consumer", "slowing traffic"],
    },
    "positive": {
        "share_gains": ["market share gains", "share gains", "outgrew the category"],
        "innovation": ["innovation strength", "product cycle", "new launches", "AI demand"],
        "pricing_discipline": ["pricing power", "pricing remained strong", "limited promotional activity"],
        "brand_strength": ["brand strength", "loyalty", "retention remained strong"],
    },
}
