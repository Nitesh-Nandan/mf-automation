# 📊 Mutual Fund Dip Analyzer - Scoring Reference

Quick reference guide for understanding how the 6-factor scoring system works.

---

## 🎯 Total Score: 0-100 Points

| Factor | Max Points | What It Measures |
|--------|-----------|------------------|
| 1. Dip Depth | 25 | How far from peak |
| 2. Historical Context | 20 | Compared to past dips |
| 3. Mean Reversion | 15 | Below average price |
| 4. Volatility | 15 | Risk/reward balance |
| 5. Recovery Speed | 15 | Past resilience |
| 6. Fund Category | 10 | Type adjustment |
| **TOTAL** | **100** | **Overall Score** |

---

## Factor 1: Dip Depth (0-25 points)

How much the NAV has dropped from its peak.

| Dip Percentage | Score | Assessment |
|----------------|-------|------------|
| ≥ 20% | 25 pts | Exceptional opportunity |
| ≥ 15% | 22 pts | Very strong dip |
| ≥ 12% | 18 pts | Strong dip |
| ≥ 10% | 15 pts | Significant dip |
| ≥ 7% | 10 pts | Moderate dip |
| ≥ 5% | 5 pts | Small dip |
| < 5% | 0 pts | No meaningful dip |

**Example:** If current NAV is down 12% from peak → **18 points**

---

## Factor 2: Historical Context (0-20 points)

Current dip as a percentage of the worst historical dip.

| Current vs Max Historical | Score | Assessment |
|---------------------------|-------|------------|
| 60-80% of max | 20 pts | ⭐ Sweet spot |
| 80-90% of max | 18 pts | Near historical low |
| 50-60% of max | 15 pts | Moderate relative dip |
| 40-50% of max | 10 pts | Small relative dip |
| 90%+ of max | 12 pts | Extreme (proceed with caution) |
| < 40% of max | 5 pts | Insignificant vs history |
| No historical data | 10 pts | Neutral (unknown) |

**Example:** Current dip 12%, max historical dip 18% → Ratio 67% → **20 points**

---

## Factor 3: Mean Reversion (0-15 points)

How far below the mean NAV the current price is.

**Formula:** Score = (% below mean) × 2, capped at 15 points

| Below Mean % | Score | Assessment |
|--------------|-------|------------|
| 7.5%+ below | 15 pts | Far below average |
| 6% below | 12 pts | Well below average |
| 4% below | 8 pts | Moderately below average |
| 2% below | 4 pts | Slightly below average |
| 0% (at mean) | 0 pts | At average |
| Above mean | 0 pts | No points |

**Example:** Current NAV ₹270, Mean NAV ₹285 → 5.3% below → **10.6 points**

---

## Factor 4: Volatility (0-15 points)

Annualized volatility (standard deviation of returns).

| Volatility Range | Score | Assessment |
|------------------|-------|------------|
| 8-15% | 15 pts | ⭐ Ideal risk/reward |
| 15-25% | 12 pts | Acceptable volatility |
| < 8% | 10 pts | Low volatility (stable but less upside) |
| > 25% | 5 pts | High volatility (risky) |

**Example:** Fund with 18% annualized volatility → **12 points**

---

## Factor 5: Recovery Speed (0-15 points)

Average days to recover from past 5%+ dips.

| Average Recovery Time | Score | Assessment |
|----------------------|-------|------------|
| ≤ 30 days | 15 pts | Excellent resilience |
| 31-60 days | 12 pts | Good recovery |
| 61-90 days | 8 pts | Moderate recovery |
| > 90 days | 4 pts | Slow recovery |
| No history | 8 pts | Neutral (unknown) |

**Example:** Fund recovered from past dips in avg 45 days → **12 points**

---

## Factor 6: Fund Category (0-10 points)

Bonus/adjustment based on fund type.

| Fund Type | Score | Rationale |
|-----------|-------|-----------|
| Small Cap | 10 pts | Highest growth potential |
| Mid Cap | 8 pts | Good growth potential |
| Flexi Cap | 8 pts | Flexible allocation advantage |
| Sectoral | 7 pts | Sector-specific opportunities |
| Thematic | 7 pts | Theme-based opportunities |
| Large Cap | 6 pts | Stable but lower upside |
| Debt/Liquid | 3 pts | Minimal dip-buying benefit |
| Unknown | 7 pts | Neutral default |

**Example:** Small Cap fund → **10 points**

---

## 🎯 Recommendation Thresholds

Based on total score, the algorithm recommends action:

| Mode | Threshold | When to Use |
|------|-----------|-------------|
| **Ultra Conservative** | 70 | Bear markets, crashes |
| **Conservative** ⭐ | 60 | Normal conditions (default) |
| **Moderate** | 50 | Bull markets with pullbacks |
| **Aggressive** | 40 | Strong bull runs |

---

## 💰 Allocation Guidance

How much of your dip-buying reserve to deploy:

| Score Range | Recommendation | Allocation | Confidence |
|-------------|----------------|------------|------------|
| 80-100 | STRONG BUY | 50% | Very High |
| 75-79 | STRONG BUY | 40% | Very High |
| 60-74 | BUY | 30% | High |
| 45-59 | MODERATE BUY | 20% | Medium |
| 30-44 | WEAK BUY | 10% | Low |
| 0-29 | HOLD | 0% | None |

**Example with ₹100,000 reserve:**
- Score 85 → Invest **₹50,000** (50%)
- Score 65 → Invest **₹30,000** (30%)
- Score 40 → Invest **₹10,000** (10%)

---

## 📊 Complete Scoring Example

**Fund:** Quant Small Cap Direct Growth

```
Current NAV:     ₹270
Peak NAV:        ₹300 (30 days ago)
Mean NAV:        ₹285
Max Historical:  18% dip
Volatility:      20% annualized
Avg Recovery:    40 days
Fund Type:       Small Cap

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Factor Breakdown:

1. Dip Depth
   Current: ₹270, Peak: ₹300
   Dip: 10%
   Score: 15/25 ✅

2. Historical Context
   Current dip: 10%, Max historical: 18%
   Ratio: 56% of max
   Score: 15/20 ✅

3. Mean Reversion
   Current: ₹270, Mean: ₹285
   Below mean: 5.3%
   Score: 10.6/15 ✅

4. Volatility
   Annualized: 20%
   Range: 15-25% (acceptable)
   Score: 12/15 ✅

5. Recovery Speed
   Avg recovery: 40 days
   Range: 31-60 days (good)
   Score: 12/15 ✅

6. Fund Category
   Type: Small Cap
   Score: 10/10 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL SCORE: 74.6/100

Recommendation: BUY
Allocation: 30% of dip-buying reserve
Confidence: High
```

---

## 🔍 Score Interpretation

| Score Range | Meaning |
|-------------|---------|
| **90-100** | Once in a blue moon opportunity |
| **80-89** | Exceptional opportunity |
| **70-79** | Very good opportunity |
| **60-69** | Good opportunity |
| **50-59** | Decent opportunity |
| **40-49** | Marginal opportunity |
| **30-39** | Weak signal |
| **0-29** | No opportunity |

---

## ⚙️ Time Windows

| Analysis | Timeframe | Purpose |
|----------|-----------|---------|
| Current Analysis | 120 days (~4 months) | Recent dip detection |
| Historical Context | 730 days (~2 years) | Long-term patterns |
| Volatility | 730 days (~2 years) | Risk assessment |
| Recovery Speed | 730 days (~2 years) | Resilience tracking |

---

## 💡 Key Principles

1. **Multiple Factors**: No single factor dominates - balanced approach
2. **Context Matters**: Same dip means different things for different funds
3. **Historical Perspective**: Past behavior predicts future resilience
4. **Risk-Adjusted**: Volatility and recovery speed account for risk
5. **Category-Aware**: Small cap 10% dip ≠ Large cap 10% dip

---

## 📝 Notes

- **Minimum Dip:** Algorithm only considers dips ≥5%
- **Fresh Data:** NAV data fetched in real-time from API
- **No Predictions:** Algorithm doesn't predict future, only identifies current opportunities
- **Complement to SIP:** Dip buying is for extra capital, not replacing regular SIP

---

## 🚀 Quick Usage

```bash
# Run analyzer
cd src/mf
uv run python dip_analyzer.py

# Change mode by editing dip_analyzer.py:
mode = 'conservative'  # or 'moderate', 'aggressive', 'ultra_conservative'
```

---

For complete algorithm details, see `ALGORITHM_DOCUMENTATION.md`

