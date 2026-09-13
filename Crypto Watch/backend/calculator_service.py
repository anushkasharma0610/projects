def _round(value):
    return round(value, 2)


def calculate_lumpsum(investment: float, annual_return: float, years: float):
    rate = annual_return / 100
    estimated_value = investment * (1 + rate) ** years
    points = [{"year": 0, "invested": _round(investment), "value": _round(investment)}]
    whole_years = int(years)
    for year in range(1, whole_years + 1):
        points.append({"year": year, "invested": _round(investment), "value": _round(investment * (1 + rate) ** year)})
    if years != whole_years:
        points.append({"year": years, "invested": _round(investment), "value": _round(estimated_value)})
    return {"total_invested": _round(investment), "estimated_value": _round(estimated_value),
            "estimated_gain": _round(estimated_value - investment), "yearly_values": points}


def calculate_sip(monthly_investment: float, annual_return: float, years: int):
    monthly_rate = annual_return / 100 / 12
    months = years * 12
    value = 0.0
    points = [{"year": 0, "invested": 0, "value": 0}]
    for month in range(1, months + 1):
        value = (value + monthly_investment) * (1 + monthly_rate)
        if month % 12 == 0:
            points.append({"year": month // 12, "invested": _round(monthly_investment * month), "value": _round(value)})
    invested = monthly_investment * months
    return {"total_invested": _round(invested), "estimated_value": _round(value),
            "estimated_gain": _round(value - invested), "yearly_values": points}
