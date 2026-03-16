from __future__ import annotations

import pycountry


def country_name_to_code(country_name: str) -> str:
    if not country_name:
        return ""
    try:
        result = pycountry.countries.lookup(country_name)
        return str(result.alpha_3)
    except LookupError:
        return ""

