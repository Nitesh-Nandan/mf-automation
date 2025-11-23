# 📊 Stock Dip-Buying Algorithm - Complete Documentation

## Executive Summary

**8-Factor Multi-Dimensional Scoring System** for identifying high-conviction dip-buying opportunities in blue-chip Indian stocks.

**Philosophy:** Quality stocks at temporary discounts present the best risk-adjusted returns. This algorithm combines price action, fundamentals, and technicals to identify when quality meets opportunity.

**Target:** Long-term investors seeking to enhance returns by opportunistically buying quality during market corrections.

---

## 🎯 Algorithm Overview

### Core Principle

> **"Never catch a falling knife, but always pick up quality when it's on sale."**

The algorithm answers three critical questions:
1. **Is it quality?** → Fundamental scoring (Quality Gate)
2. **Is it cheap?** → Price dip & Valuation analysis
3. **Is it the right time?** → Technical confirmation

### Scoring Framework

**Total Score:** 0-125 points (normalized to 100)

**8 Independent Factors:**
```
1. Dip Depth            (0-15 pts)  - How far from peak
2. Historical Context   (0-20 pts)  - vs past dips
3. Mean Reversion       (0-15 pts)  - Below average
4. Volatility           (0-15 pts)  - Risk/reward
5. Recovery Speed       (0-15 pts)  - Historical resilience
6. Market Cap           (0-5 pts)   - Size bonus
7. Fundamentals         (0-25 pts)  - Quality & Valuation ⭐ (Enhanced v3.0)
8. Technicals           (0-10 pts)  - Entry timing (Enhanced v3.0)
```

---

## 📈 Factor 1: Dip Depth (0-15 points)

### What It Measures
Current price relative to recent peak (90-day high).

### Why It Matters
**Conviction:** Deeper dips offer better value IF fundamentals remain intact. A 15% dip in a quality stock often represents temporary mispricing rather than permanent impairment.

### Scoring Logic

```python
dip_percentage = ((peak_nav - current_nav) / peak_nav) * 100

if dip >= 15%:     15 pts  # Significant opportunity
elif dip >= 12%:   12 pts  # Strong dip
elif dip >= 10%:   10 pts  # Meaningful dip
elif dip >= 8%:    8 pts   # Moderate dip
elif dip >= 5%:    5 pts   # Small dip
else:              0 pts   # Not a dip
```

### Rationale
- **15%+ dips** are rare in quality stocks → highest conviction
- **10-15%** dips happen 1-2x per year → good opportunities
- **5-10%** dips are common noise → lower priority
- **<5%** is not a meaningful dip

### Time Window
**90 days (3 months)** - Balances recency with meaningful peak detection

---

## 📊 Factor 2: Historical Context (0-20 points)

### What It Measures
Current dip relative to maximum historical dip over 2 years.

### Why It Matters
**Conviction:** Understanding historical pain points prevents buying too early. If this is a 10% dip but the stock has seen 25% dips before, we may be early.

### Scoring Logic

```python
max_historical_dip = calculate_max_dip(2_years_data)
dip_ratio = current_dip / max_historical_dip

if dip_ratio >= 0.80:    20 pts  # Near historical worst
elif dip_ratio >= 0.60:  15 pts  # Significant in context
elif dip_ratio >= 0.40:  10 pts  # Moderate in context
elif dip_ratio >= 0.20:   5 pts  # Small in context
else:                     0 pts  # Negligible
```

### Example
```
Stock: TCS
Current dip: 12%
Max historical dip (2yr): 15%
Ratio: 12/15 = 0.80 → 20 points ✅

Interpretation: This is near the worst dip we've seen in 2 years.
Very attractive relative to history.
```

---

## 📉 Factor 3: Mean Reversion (0-15 points)

### What It Measures
How far below the historical mean price (120-day average).

### Why It Matters
**Conviction:** Stock prices oscillate around their mean. When significantly below mean, probability of reversion is high (statistical edge).

### Scoring Logic

```python
mean_price = average(120_day_prices)
deviation = ((mean - current) / mean) * 100

score = min(deviation * 2, 15)  # 2 pts per % below mean
```

### Examples
```
7.5% below mean → 15 pts (max) ✅
5.0% below mean → 10 pts
2.5% below mean → 5 pts
At or above mean → 0 pts
```

---

## 📊 Factor 4: Volatility (0-15 points)

### What It Measures
Annualized volatility (standard deviation of returns) over 90 days.

### Why It Matters
**Conviction:** Moderate volatility = healthy. Too low = missed opportunity. Too high = excessive risk.

### Scoring Logic

```python
daily_returns = calculate_returns(90_days)
volatility = stdev(daily_returns) * sqrt(252)  # Annualized

if 15% ≤ vol ≤ 25%:    15 pts  # Sweet spot for stocks
elif 10% ≤ vol < 15%:  12 pts  # Low but acceptable
elif 25% < vol ≤ 35%:  12 pts  # High but manageable
elif 35% < vol ≤ 50%:   8 pts  # Very high - caution
else:                    5 pts  # Extreme - high risk
```

### Rationale

**The Goldilocks Zone (15-25%):**
- Enough volatility to create opportunities
- Not so much that risk is unmanageable
- Typical for healthy Indian large-caps

---

## 🚀 Factor 5: Recovery Speed (0-15 points)

### What It Measures
Historical speed of recovery from past dips (number of dips fully recovered).

### Why It Matters
**Conviction:** Past behavior predicts future behavior. Stocks that recover quickly have strong underlying demand and quality.

### Scoring Logic

```python
dips_found = identify_all_dips(2_years)
dips_recovered = count_full_recoveries(dips_found)
recovery_rate = dips_recovered / total_dips

Fast recovery: All recovered in <30 days    → 15 pts
Good recovery: 80%+ recovered              → 12 pts  
Moderate: 60%+ recovered                   → 8 pts
Slow: 40%+ recovered                       → 5 pts
Poor: <40% recovered                       → 0 pts
```

---

## 🏢 Factor 6: Market Cap (0-5 points)

### What It Measures
Stock size category (large/mid/small cap).

### Why It Matters
**Conviction:** Larger companies = more stable, lower risk, better for opportunistic buying.

### Scoring Logic

```python
if market_cap ≥ ₹50,000 Cr:    5 pts  # Large cap
elif market_cap ≥ ₹10,000 Cr:  3 pts  # Mid cap
else:                           0 pts  # Small cap
```

---

## 💎 Factor 7: Fundamentals (0-25 points) ⭐ ENHANCED v3.0

### What It Measures
**7 Key Financial Metrics** - The quality gate and valuation check.

### Why It Matters
**Conviction:** This factor has been overhauled in v3.0 to be **sector-agnostic** and focus on **relative value** and **governance**.

### The 7 Metrics

#### 7.1 Relative P/E Ratio (0-4 points) ⭐ NEW
*Replaces absolute P/E to handle high-P/E sectors like FMCG.*

```python
Ratio = Current P/E / 5-Year Median P/E

< 0.8x Median:    4 pts  # Historically Cheap
0.8x - 1.0x:      3 pts  # Below Median
1.0x - 1.2x:      2 pts  # Fair Value
1.2x - 1.5x:      1 pt   # Expensive
> 1.5x Median:    0 pts  # Very Expensive
```
**Why:** A P/E of 60 is cheap for Nestle (Median 80) but expensive for Tata Steel (Median 10).

#### 7.2 PEG Ratio (0-3 points) ⭐ NEW
*Price/Earnings to Growth Ratio. Contextualizes valuation with growth.*

```python
PEG = P/E Ratio / Profit Growth Rate

< 1.0:      3 pts  # Undervalued Growth
1.0 - 1.5:  2 pts  # Fair Price for Growth
1.5 - 2.0:  1 pt   # Expensive for Growth
> 2.0:      0 pts  # Overvalued
```
**Why:** High P/E is justified if growth is high. PEG captures this.

#### 7.3 Profit Growth (0-4 points)
```python
> 25%:    4 pts  # Excellent
15-25%:   3 pts  # Very good
8-15%:    2 pts  # Good
0-8%:     1 pt   # Slow
< 0%:     0 pts  # Declining
```

#### 7.4 Profit Margin (0-3 points)
```python
> 15%:    3 pts  # Excellent
10-15%:   2 pts  # Good
5-10%:    1 pt   # Fair
< 5%:     0 pts  # Low
```

#### 7.5 ROE (0-3 points)
```python
> 20%:    3 pts  # Excellent
15-20%:   2 pts  # Very good
10-15%:   1 pt   # Good
< 10%:    0 pts  # Below average
```

#### 7.6 Debt-to-Equity (0-3 points)
```python
< 0.5:    3 pts  # Low Debt
0.5-1.0:  2 pts  # Moderate
1.0-2.0:  1 pt   # High
> 2.0:    0 pts  # Very High
```

#### 7.7 Revenue Growth (0-5 points)
*Remaining points allocated here.*
```python
> 15%:    5 pts
10-15%:   3 pts
5-10%:    1 pt
< 5%:     0 pts
```

### Quality Gate (Must Pass All Checks)

**Fail any check = Stock REJECTED regardless of price dip.**

```python
1. Debt/Equity < 2.0          ✅
2. ROE > 10%                  ✅
3. Profit Growth > 0%         ✅ (No declining profits)
4. Promoter Pledging < 5%     ✅ (NEW: Governance Check)
5. Fundamental Score ≥ 12/25  ✅ (Approx 50% threshold)
```

---

## 📊 Factor 8: Technicals (0-10 points) ⭐ ENHANCED v3.0

### What It Measures
**3 Technical Indicators** for timing entry.

### 8.1 RSI - Relative Strength Index (0-5 points)

**Updated for Bluechips:** Quality stocks rarely hit RSI 30 in bull markets. Threshold raised to 40.

```python
RSI = calculate_rsi(14_days)

< 40:     5 pts  # Oversold (Strong Buy Zone)
40-50:    3 pts  # Weakness (Accumulation Zone)
50-60:    1 pt   # Neutral
> 60:     0 pts  # Momentum/Overbought
```

### 8.2 Volume Spike (0-3 points)
```python
Current Vol / Avg Vol (20d)

≥ 2.0x:   3 pts  # Capitulation / Big Hands
1.5-2x:   2 pts  # Strong Interest
< 1.5x:   0 pts  # Normal
```

### 8.3 Near Support (0-2 points)
```python
Distance to 200 DMA or 52w Low

< 2%:     2 pts  # At Support
2-5%:     1 pt   # Near Support
> 5%:     0 pts
```

---

## 🎯 Final Scoring & Recommendations

### Total Score Calculation

```python
Total = Dip(15) + Historical(20) + Mean(15) + Volatility(15) 
        + Recovery(15) + MarketCap(5) + Fundamentals(25) 
        + Technicals(10)

Maximum: 120 points (approx)
Normalized: (Total / Max_Possible) * 100 = Final Score (0-100)
```

### Recommendation Thresholds

```python
≥ 80:  STRONG BUY    (Allocation: 20%)  # Rare, exceptional
≥ 70:  BUY           (Allocation: 15%)  # Strong conviction
≥ 60:  MODERATE BUY  (Allocation: 10%)  # Good opportunity
≥ 50:  WEAK BUY      (Allocation: 5%)   # Consider small position
< 50:  HOLD          (Allocation: 0%)   # Wait for better entry
```

---

## ⚠️ Limitations & Considerations

1.  **Data Dependency:** Relative P/E requires 5 years of historical data. If unavailable, the algorithm falls back to absolute P/E logic.
2.  **Sector Nuances:** While Relative P/E helps, some sectors (Banks) are better valued on P/B. This algorithm currently uses P/E as the primary valuation metric.
3.  **Promoter Pledging:** Data for pledging must be accurate. High pledging is a major risk factor (e.g., margin calls).

---

**Version:** 3.0  
**Last Updated:** November 2025  
**Calibrated For:** Indian Stock Market (NSE/BSE)
