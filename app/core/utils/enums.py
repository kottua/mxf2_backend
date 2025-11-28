from enum import StrEnum


class PropertyClassEnum(StrEnum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    PREMIUM = "premium"


class CurrencyEnum(StrEnum):
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
