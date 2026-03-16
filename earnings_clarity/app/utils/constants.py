from __future__ import annotations

SPEAKER_ROLE_KEYWORDS = {
    "chief executive officer": "ceo",
    "ceo": "ceo",
    "chief financial officer": "cfo",
    "cfo": "cfo",
    "analyst": "analyst",
    "operator": "operator",
    "president": "executive",
    "vice president": "executive",
}

SECTION_MARKERS = {
    "question-and-answer session": "analyst_qna",
    "question and answer session": "analyst_qna",
    "prepared remarks": "prepared_remarks",
    "closing remarks": "closing",
}

POSITIVE_GUIDANCE_PHRASES = {
    "improving": 1.0,
    "reaccelerating": 1.3,
    "raised outlook": 2.5,
    "strong demand": 1.2,
    "healthy demand": 1.0,
    "remain confident": 1.0,
    "durable growth": 1.3,
    "stabilizing": 0.8,
    "expanding margins": 1.5,
    "strong pipeline": 1.0,
    "better than expected": 1.0,
}

CAUTION_GUIDANCE_PHRASES = {
    "lowered outlook": 3.0,
    "remain cautious": 1.8,
    "visibility is limited": 2.0,
    "not assuming": 1.2,
    "headwinds": 1.4,
    "moderation": 1.0,
    "uncertain environment": 1.8,
    "pressure": 1.2,
    "softness": 1.2,
    "mixed demand": 1.0,
    "challenging": 1.2,
    "macro uncertainty": 1.5,
    "margin pressure": 1.8,
    "cautious on china": 2.0,
    "slower growth": 1.4,
    "visibility remains limited": 2.0,
}

DEFENSIVE_QA_PHRASES = {
    "premature to say": 1.2,
    "too early to call": 1.3,
    "we are not providing": 1.5,
    "we would not extrapolate": 1.4,
    "we are watching closely": 1.0,
    "hard to predict": 1.1,
}

POSITIVE_TONE_WORDS = {
    "strong",
    "confident",
    "durable",
    "accelerate",
    "improved",
    "record",
    "healthy",
    "expansion",
    "momentum",
    "opportunity",
}

CAUTIOUS_TONE_WORDS = {
    "cautious",
    "uncertain",
    "pressure",
    "softness",
    "volatile",
    "moderation",
    "headwinds",
    "challenging",
    "defensive",
    "limited",
}

TOPIC_KEYWORDS = {
    "ai": ["ai", "artificial intelligence", "gen ai", "inference"],
    "cloud": ["cloud", "azure", "aws", "workload"],
    "china": ["china", "greater china"],
    "margins": ["margin", "gross margin", "operating margin"],
    "services": ["services", "subscription", "installed base"],
    "enterprise demand": ["enterprise", "commercial", "seat growth"],
    "consumer weakness": ["consumer weakness", "soft consumer", "discretionary pressure"],
    "regulation": ["regulation", "regulatory", "antitrust", "compliance"],
    "capex": ["capex", "capital expenditure", "infrastructure spend", "data center"],
    "semiconductors": ["semiconductor", "gpu", "wafer", "foundry"],
    "pricing": ["pricing", "price increase", "mix"],
    "fx": ["fx", "foreign exchange", "currency"],
    "europe": ["europe", "emea"],
    "inventory": ["inventory", "channel inventory", "supply"],
    "guidance": ["guidance", "outlook", "forecast"],
    "profitability": ["profitability", "opex discipline", "cash flow"],
}

JARGON_EXPLANATIONS = {
    "installed base": "the number of active devices already in customers' hands",
    "gross margin": "how much profit remains after direct product and service costs",
    "opex": "operating expenses, such as payroll and marketing",
    "visibility": "management's confidence in what demand will look like soon",
    "capex": "capital spending on equipment, infrastructure, or facilities",
}
