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
3. Mean Reversion       (0-15 pts)  - Is it below the 200 DMA? (Deep Value)
4. Volatility           (0-10 pts)  - Is risk manageable?
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
**Deep Value Check:** How far the price is relative to the **200-Day Moving Average (DMA)**.

### Why It Matters
The 200 DMA is the institutional "Line in the Sand".
*   **Above 200 DMA:** Bull Trend.
*   **Below 200 DMA:** Value Zone (or Bear Trend).

For Blue-Chip stocks, falling **below** the 200 DMA is a rare buying opportunity. This factor rewards you for buying when the stock is "statistically cheap."

### Scoring Logic
```python
Price vs 200 DMA:

< 0% (Below 200 DMA):   15 pts  # Deep Value (Rare!)
0-2% (At 200 DMA):      10 pts  # Great Value
2-5% (Near 200 DMA):    5 pts   # Good Value
> 5% (Far above):       0 pts   # Normal Pricing
```

---

## 📊 Factor 4: Volatility (0-10 points)

### What It Measures
Annualized volatility.

### Why It Matters
Slightly reduced weight (10 pts) because we assume the user has picked stable stocks. We still penalize extreme volatility as it suggests "falling knife" risk.

### Scoring Logic
```python
15% ≤ vol ≤ 30%:    10 pts  # Ideal
10% ≤ vol < 15%:    8 pts   # Low
30% < vol ≤ 45%:    5 pts   # High
> 45%:              0 pts   # Dangerous
```

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
*   **Factor 3 (Mean Reversion)** asks: "Is it cheap?" (Below 200 DMA).
*   **Factor 6 (Technicals)** asks: "Is it bouncing?" (Support at 50/100 DMA).

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

| Score | Recommendation | Allocation | Meaning |
| :--- | :--- | :--- | :--- |
| **85-100** | **STRONG BUY** | 20% | Rare, "Back up the truck" moment |
| **75-84** | **BUY** | 15% | Excellent entry |
| **60-74** | **ACCUMULATE** | 10% | Good standard dip |
| **50-59** | **NIBBLE** | 5% | Small starter position |
| **< 50** | **WAIT** | 0% | Not cheap enough |

---

## ⚠️ Crucial Warning: The "Blind Spot"

This algorithm **CANNOT** detect fundamental deterioration.

*   **Scenario:** A CEO resigns due to fraud. The stock crashes 30%.
*   **Algorithm View:** "Huge Dip (20 pts) + Oversold (5 pts) + High Volume (3 pts) = **STRONG BUY**"
*   **Reality:** The stock might go to zero.

**Rule:** ALWAYS check news before executing a buy signal from this algorithm.

---

**Version:** 1.1 (Technical Only - 200 DMA Enhanced)
**Date:** November 2025
