# 📊 Technical Stock Dip-Buying Algorithm (Price Action Only)

## Executive Summary

**6-Factor Price-Action Scoring System** for timing entries into pre-selected high-quality stocks.

**Philosophy:** "Human for Quality, Machine for Timing."
This algorithm assumes the user has **already filtered** for fundamental quality. Its sole purpose is to identify the **optimal technical entry point** during corrections.

**Target:** Investors who have a curated watchlist of "Forever Stocks" (e.g., Asian Paints, Bajaj Finance) and want a systematic signal to buy dips.

---

## 🎯 Algorithm Overview

### Core Principle

> **"The stock is good (Human Decision). Is the price right? (Machine Decision)"**

### Scoring Framework

**Total Score:** 0-100 points

**6 Independent Factors (Re-weighted for Price Action):**
```
1. Dip Depth            (0-20 pts)  - How cheap is it?
2. Historical Context   (0-25 pts)  - Is this a rare opportunity?
3. Mean Reversion       (0-15 pts)  - Is it below the 100 DMA? (Value Zone)
4. Volatility           (0-10 pts)  - Stock-specific risk check
5. Recovery Speed       (0-20 pts)  - Does it bounce back fast?
6. Technicals           (0-10 pts)  - RSI & Bull Market Support (Timing)
```

---

## 📈 Factor 1: Dip Depth (0-20 points)

### What It Measures
Current price relative to recent peak (90-day high).

### Why It Matters
Since we know the stock is quality, a deeper dip is purely a better bargain. We reward depth more aggressively here than in the fundamental version.

### Scoring Logic

```python
dip_percentage = ((peak_nav - current_nav) / peak_nav) * 100

if dip >= 20%:     20 pts  # Crash / Crisis Opportunity
elif dip >= 15%:   18 pts  # Excellent
elif dip >= 12%:   15 pts  # Very Good
elif dip >= 10%:   12 pts  # Good
elif dip >= 8%:    8 pts   # Moderate
elif dip >= 5%:    5 pts   # Minor
else:              0 pts
```

---

## 📊 Factor 2: Historical Context (0-25 points)

### What It Measures
Current dip relative to maximum historical dip over 2 years.

### Why It Matters
**The most important factor.** It answers: "Is this dip special for THIS stock?"
A 10% dip in HUL is rare (Score: 25). A 10% dip in Zomato is noise (Score: 5).

### Scoring Logic

```python
max_historical_dip = calculate_max_dip(2_years_data)
dip_ratio = current_dip / max_historical_dip

if dip_ratio >= 0.90:    25 pts  # Near historical worst (Rare!)
elif dip_ratio >= 0.75:  20 pts  # Significant
elif dip_ratio >= 0.60:  15 pts  # Above average
elif dip_ratio >= 0.40:  10 pts  # Average
elif dip_ratio >= 0.20:   5 pts  # Minor
else:                     0 pts
```

---

## 📉 Factor 3: Mean Reversion (0-15 points)

### What It Measures
**Deep Value Check:** How far the price is relative to the **100-Day Moving Average (DMA)**.

### Why It Matters
The 100 DMA represents the intermediate-term trend (3-4 months).
*   **Above 100 DMA:** Healthy uptrend
*   **Below 100 DMA:** Correction territory / Value opportunity

For quality stocks, dipping **below** the 100 DMA during corrections is a strong buying signal. This factor rewards you for buying when the stock is "statistically cheap" relative to its recent trend.

### Scoring Logic
```python
distance_from_100dma = ((price - dma_100) / dma_100) * 100

-6% ≤ distance < 0%:      15 pts  # Below 100 DMA (Sweet Spot!)
0% ≤ distance ≤ 3%:       12 pts  # At 100 DMA (Testing Support)
-12% ≤ distance < -6%:     8 pts  # Deep below (Caution: verify fundamentals)
3% < distance ≤ 6%:        5 pts  # Slight premium (Early dip)
6% < distance ≤ 10%:       2 pts  # Moderately above
else:                      0 pts  # Either too expensive or falling knife (< -12%)
```

### Key Insight
A stock 3% below its 100 DMA is in a **normal correction**.
A stock 15% below its 100 DMA might be a **falling knife** (score drops to 0 to protect you).

---

## 📊 Factor 4: Volatility (0-10 points)

### What It Measures
Current volatility relative to the stock's own historical average (not absolute thresholds).

### Why It Matters
**Stock-Specific Volatility Assessment.** Each stock has its own "normal" volatility:
- Asian Paints: ~15% is normal
- Zomato: ~40% is normal

We want to buy when the stock dips with **controlled volatility** (orderly correction), not during panic spikes (falling knife).

### Calculation Method
```python
# Baseline: Stock's typical volatility over 2 years
historical_avg_vol = annualized_volatility(2_year_data)

# Current: Recent volatility (90 days)
current_vol = annualized_volatility(90_day_data)

# Ratio: How volatile is it NOW vs its NORMAL?
vol_ratio = current_vol / historical_avg_vol
```

### Scoring Logic
```python
0.85 ≤ vol_ratio ≤ 1.15:    10 pts  # Normal range (healthy dip)
0.70 ≤ vol_ratio < 0.85:     8 pts  # Quieter than usual (controlled decline)
1.15 < vol_ratio ≤ 1.40:     6 pts  # Moderate spike
1.40 < vol_ratio ≤ 1.75:     3 pts  # High spike (caution)
vol_ratio > 1.75:            0 pts  # Extreme spike (falling knife)
vol_ratio < 0.70:            5 pts  # Too quiet (slow bleed)
```

### Interpretation
- **vol_ratio = 1.0** → Stock dipping with normal volatility (ideal)
- **vol_ratio = 1.5** → Stock dipping with 50% more volatility than usual (risky)
- **vol_ratio = 2.0** → Stock in panic mode (avoid)

---

## 🚀 Factor 5: Recovery Speed (0-20 points)

### What It Measures
How quickly the stock has recovered from past dips.

### Why It Matters
**Critical Quality Proxy.** Since we removed fundamental checks, this is our "Technical Quality Check". Good stocks bounce fast. Bad stocks stay down.

### Scoring Logic
```python
Avg Recovery Time:

< 20 days:    20 pts  # Rocket Recovery (High Demand)
20-40 days:   15 pts  # Fast
40-60 days:   10 pts  # Moderate
60-90 days:   5 pts   # Slow
> 90 days:    0 pts   # Sluggish / Dead money
```

---

## 📊 Factor 6: Technicals (0-10 points)

### What It Measures
**Timing Indicators** to fine-tune the exact entry point.

### Distinction from Factor 3
*   **Factor 3 (Mean Reversion)** asks: "Is it cheap?" (Below 100 DMA).
*   **Factor 6 (Technicals)** asks: "Is it bouncing?" (Support at 50/100 DMA with RSI).

### Scoring Logic

**1. RSI (0-5 pts)**
*Adjusted for Bull Market Behavior*
```python
< 40:     5 pts  # Oversold / Strong Support
40-50:    3 pts  # Accumulation Zone
50-60:    1 pt   # Neutral
> 60:     0 pts  # Momentum
```

**2. Volume Spike (0-3 pts)**
```python
> 2.0x Avg Vol: 3 pts  # Capitulation
> 1.5x Avg Vol: 2 pts
```

**3. Bull Market Support (0-2 pts)**
*Rewards bouncing off shorter-term trends*
```python
Near 50 DMA:      1 pt   # Trend Support
Near 100 DMA:     2 pts  # Correction Support
```

---

## 🎯 Final Scoring & Recommendations

### Total Score Calculation
```python
Total = Dip(20) + Historical(25) + Mean(15) + Volatility(10) + Recovery(20) + Technicals(10)
Maximum: 100 points
```

### Recommendation Thresholds

| Score | Recommendation | Position Size | Meaning |
| :--- | :--- | :--- | :--- |
| **85-100** | **STRONG BUY** | 1.0x standard | Rare, "Back up the truck" moment |
| **75-84** | **BUY** | 0.75x standard | Excellent entry |
| **60-74** | **ACCUMULATE** | 0.50x standard | Good standard dip |
| **50-59** | **NIBBLE** | 0.25x standard | Small starter position |
| **< 50** | **WAIT** | 0% | Not cheap enough |

**Note:** "Standard position" is your pre-defined position size per stock (e.g., 5% of portfolio). This multiplier approach maintains risk discipline while allowing flexibility.

---

## ⚠️ Crucial Warning: The "Blind Spot"

This algorithm **CANNOT** detect fundamental deterioration.

*   **Scenario:** A CEO resigns due to fraud. The stock crashes 30%.
*   **Algorithm View:** "Huge Dip (20 pts) + Oversold (5 pts) + High Volume (3 pts) = **STRONG BUY**"
*   **Reality:** The stock might go to zero.

**Rule:** ALWAYS check news before executing a buy signal from this algorithm.

---

**Version:** 2.0 (Technical Only - Optimized for Active Dip-Buying)
**Date:** November 2025
**Key Updates:**
- Switched to 100 DMA for more frequent signals
- Relative volatility (stock-specific calibration)
- Position size multipliers for risk management
