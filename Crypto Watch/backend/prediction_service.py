"""Transparent statistical estimate: MA crossover, momentum, change and volatility are scored.
This is a repeatable educational estimate, not a forecast or financial advice."""
import statistics


def calculate_prediction(coin_id: str, current_price: float, prices: list[list[float]]):
    closes = [point[1] for point in prices if len(point) > 1 and point[1] is not None]
    if len(closes) < 15 or not current_price:
        raise ValueError("Not enough historical market data to calculate an estimate.")
    ma7, ma14 = sum(closes[-7:]) / 7, sum(closes[-14:]) / 14
    momentum = (closes[-1] / closes[-4] - 1) * 100 if closes[-4] else 0
    recent_change = (closes[-1] / closes[-8] - 1) * 100 if closes[-8] else 0
    returns = [(closes[i] / closes[i - 1] - 1) * 100 for i in range(-13, 0) if closes[i - 1]]
    volatility = statistics.pstdev(returns) if len(returns) > 1 else 0
    score = 0
    score += 1 if ma7 > ma14 else -1
    score += 1 if momentum > 0 else -1 if momentum < 0 else 0
    score += 1 if recent_change > 0 else -1 if recent_change < 0 else 0
    # Cap contribution to avoid presenting extreme estimates as meaningful.
    predicted_change = max(-5, min(5, 0.35 * score + 0.18 * momentum + 0.08 * recent_change))
    if volatility > 8:
        predicted_change *= 0.5
    direction = "Bullish" if score >= 2 else "Bearish" if score <= -2 else "Neutral"
    confidence = "Low" if volatility > 6 else "High" if abs(score) >= 3 and volatility < 3 else "Medium"
    return {"coin_id": coin_id, "current_price": round(current_price, 8),
            "predicted_price": round(current_price * (1 + predicted_change / 100), 8),
            "predicted_change_percent": round(predicted_change, 2), "direction": direction,
            "confidence": confidence}
