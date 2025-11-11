# 📊 Mutual Fund Dip Analyzer - Scoring Reference

Quick reference guide for understanding how the 6-factor scoring system works.

Dip Depth is the DOMINANT signal (40% weight)

---

## 🎯 Total Score: 0-100 Points

| Factor | Max Points | % Weight | What It Measures |
|--------|-----------|----------|------------------|
| **1. Dip Depth** ⭐ | **40** | **40%** | **How far from peak (PRIMARY SIGNAL)** |
| 2. Historical Context | 13 | 13% | Compared to past dips |
| 3. Mean Reversion | 13 | 13% | Below average price |
| 4. Volatility | 11 | 11% | Risk/reward balance |
| 5. Recovery Speed | 13 | 13% | Past resilience |
| 6. Fund Category | 10 | 10% | Type adjustment |
| **TOTAL** | **100** | **100%** | **Overall Score** |

**Philosophy:** Dip Depth dominates (40%), other factors are quality filters (60%)

---

## Factor 1: Dip Depth (0-40 points) ⭐ PRIMARY SIGNAL

How much the NAV has dropped from its peak.

| Dip Percentage | Score | Assessment |
|----------------|-------|------------|
| ≥ 18% | 40 pts | 🔥 Maximum opportunity - almost guaranteed trigger |
| ≥ 15% | 30 pts | Excellent opportunity |
| ≥ 12% | 25 pts | Very good opportunity |
| ≥ 10% | 22 pts | Good opportunity |
| ≥ 8% | 20 pts | Significant dip (minimum threshold) |
| < 8% | 0 pts | No meaningful dip |

**Why 40%?** Dip depth is the PRIMARY signal. Deep dips will trigger even with suboptimal secondary factors.

**Example:** If current NAV is down 15% from peak → **30 points** (75% of max)

---

## Factor 2: Historical Context (0-13 points)

Current dip as a percentage of the worst historical dip.

| Current vs Max Historical | Score | Assessment |
|---------------------------|-------|------------|
| 50-80% of max | 13 pts | ⭐ Sweet spot (optimal entry) |
| 60-80% of max | 12 pts | Excellent timing |
| 80-90% of max | 12 pts | Near historical low |
| 50-60% of max | 10 pts | Good relative dip |
| 40-50% of max | 8 pts | Moderate relative dip |
| 30-40% of max | 6 pts | Small relative dip |
| 90-100% of max | 10 pts | New record or limited data |
| ≥ 100% of max | 10 pts | Record-breaking dip (generous default) |
| < 30% of max | 4 pts | Insignificant vs history |
| No historical data | 10 pts | Generous default (unknown) |

**Note:** When current dip equals or exceeds historical max, algorithm uses generous default (10/13 points) because this indicates limited historical data OR a new record-breaking dip.

**Example:** Current dip 15%, max historical dip 18% → Ratio 83% → **12 points**

---

## Factor 3: Mean Reversion (0-13 points)

How far below the mean NAV the current price is.

**Formula:** Score = (% below mean) × 2, capped at 13 points

| Below Mean % | Score | Assessment |
|--------------|-------|------------|
| 6.5%+ below | 13 pts | Maximum (far below average) |
| 5% below | 10 pts | Well below average |
| 3% below | 6 pts | Moderately below average |
| 1% below | 2 pts | Slightly below average |
| 0% (at mean) | 0 pts | At average |
| Above mean | 0 pts | No points |

**Example:** Current NAV ₹270, Mean NAV ₹285 → 5.3% below → **10.6 points**

---

## Factor 4: Volatility (0-11 points)

Annualized volatility (standard deviation of returns).

| Volatility Range | Score | Assessment |
|------------------|-------|------------|
| 8-25% | 11 pts | ⭐ Ideal for mutual funds |
| 25-35% | 9 pts | Acceptable volatility |
| < 8% | 7 pts | Low volatility (stable but less upside) |
| > 35% | 5 pts | High volatility (risky) |

**Note:** Range expanded to 8-25% to match typical mutual fund behavior (was too strict at 8-15%).

**Example:** Fund with 20% annualized volatility → **11 points** (ideal range)

---

## Factor 5: Recovery Speed (0-13 points)

Average days to recover from past 8%+ dips.

| Average Recovery Time | Score | Assessment |
|----------------------|-------|------------|
| ≤ 30 days | 13 pts | Excellent resilience |
| 31-60 days | 10 pts | Good recovery |
| 61-90 days | 7 pts | Moderate recovery |
| > 90 days | 4 pts | Slow recovery |
| No history | 8 pts | Neutral (generous default) |

**Note:** Tracks dips ≥8% (matches main threshold).

**Example:** Fund recovered from past dips in avg 45 days → **10 points**

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

| Mode | Threshold | Typical Signals/Year | When to Use |
|------|-----------|---------------------|-------------|
| **Ultra Conservative** | 75 | <1 | Bear markets, crashes (18%+ dips) |
| **Conservative** ⭐ | **60** | **1-2** | **Normal conditions (default)** |
| **Moderate** | 55 | 3-5 | Bull markets with pullbacks |
| **Aggressive** | 45 | 6-10 | Strong bull runs |

**Recommended:** Use **Conservative mode (60)** for 1-2 high-quality signals per year.

---

## 💰 Allocation Guidance

How much of your dip-buying reserve to deploy:

| Score Range | Recommendation | Allocation | Confidence |
|-------------|----------------|------------|------------|
| 85-100 | STRONG BUY | 50% | Very High |
| 75-84 | STRONG BUY | 40% | Very High |
| 60-74 | BUY | 30% | High |
| 55-59 | MODERATE BUY | 20% | Medium |
| 45-54 | WEAK BUY | 15% | Low |
| 0-44 | HOLD | 0% | None |

**Example with ₹100,000 reserve:**
- Score 90 → Invest **₹50,000** (50%)
- Score 65 → Invest **₹30,000** (30%)
- Score 50 → Invest **₹15,000** (15%)

---

## 📊 Complete Scoring Example

**Fund:** Quant Small Cap Direct Growth (September 2024 Correction)

```
Current NAV:     ₹232
Peak NAV:        ₹307 (27-Sep-2024)
Dip:             24.4%
Mean NAV:        ₹270
Max Historical:  24.4% (same - limited data)
Volatility:      18% annualized
Avg Recovery:    60 days
Fund Type:       Small Cap

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Factor Breakdown:

1. Dip Depth ⭐
   Current: ₹232, Peak: ₹307
   Dip: 24.4%
   Score: 40/40 ✅ (≥18% = maximum)

2. Historical Context
   Current dip: 24.4%, Max historical: 24.4%
   Ratio: 100% of max (record-breaking)
   Score: 10/13 ✅ (generous default)

3. Mean Reversion
   Current: ₹232, Mean: ₹270
   Below mean: 14.1%
   Score: 13/13 ✅ (capped at max)

4. Volatility
   Annualized: 18%
   Range: 8-25% (ideal)
   Score: 11/11 ✅

5. Recovery Speed
   Avg recovery: 60 days
   Range: 31-60 days (good)
   Score: 10/13 ✅

6. Fund Category
   Type: Small Cap
   Score: 10/10 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL SCORE: 94/100

Recommendation: STRONG BUY 🔥
Allocation: 50% of dip-buying reserve
Confidence: Very High
```

**Real Result:** This was an actual 24% correction in Sept 2024. Algorithm correctly scored it at 94/100!

---

## 🔍 Score Interpretation

| Score Range | Meaning | Typical Dip Size |
|-------------|---------|------------------|
| **90-100** | Once in a blue moon opportunity | 20%+ dips |
| **85-89** | Exceptional opportunity | 18-20% dips |
| **80-84** | Excellent opportunity | 15-18% dips |
| **75-79** | Very good opportunity | 15% dips |
| **70-74** | Good opportunity | 13-15% dips |
| **65-69** | Solid opportunity | 12-13% dips |
| **60-64** | Decent opportunity (conservative threshold) ⭐ | 12% dips |
| **55-59** | Moderate opportunity (moderate threshold) | 10-12% dips |
| **45-54** | Marginal opportunity (aggressive threshold) | 8-10% dips |
| **0-44** | No opportunity | <8% or weak factors |

---

## ⚙️ Time Windows

| Analysis | Timeframe | Purpose |
|----------|-----------|---------|
| Current Analysis | 180 days (~6 months) | Catches full depth of major dips |
| Historical Context | 730 days (~2 years) | Captures market cycles + price appreciation |
| Volatility | Full available data | Risk assessment |
| Recovery Speed | Full available data | Resilience tracking |

**Why 2 years?** Captures meaningful market cycles including both bull and bear phases, plus sufficient data for price appreciation patterns. APIs typically provide ~2.8 years of data.

---

## 💡 Key Principles

1. **Dip Depth Dominates (40%)**: The PRIMARY signal - deep dips trigger with minimal secondary support
2. **Quality Filters (60%)**: Other factors ensure high-quality opportunities
3. **Context Matters**: Same dip means different things for different funds
4. **Historical Perspective**: Past behavior predicts future resilience
5. **Risk-Adjusted**: Volatility and recovery speed account for risk
6. **Category-Aware**: Small cap 15% dip ≠ Large cap 15% dip
7. **Generous Defaults**: Limited data doesn't disqualify valid opportunities
8. **Data-Driven**: Validated against September 2024 correction (all funds scored 78-97)

---

## 📈 Expected Signal Frequency

With **Conservative Mode (60 threshold)**:

| Market Condition | Signals/Year | Typical Dip Size |
|-----------------|--------------|------------------|
| Bull Market | 0-1 | Rarely triggers (capital preserved) |
| Normal Market | 1-2 | 12-15% corrections |
| Bear Market | 3-5 | 15-20%+ corrections |

**Goal:** 1-2 high-quality signals per year in normal markets.

---

## 📝 Notes

- **Minimum Dip:** Algorithm only considers dips ≥8% (top 10% of all dips)
- **Fresh Data:** NAV data fetched in real-time from API
- **No Predictions:** Algorithm doesn't predict future, only identifies current opportunities
- **Complement to SIP:** Dip buying is EXTRA capital on corrections, NOT a replacement for regular SIP
- **Conservative by Design:** Preserves capital during bull runs, deploys during real corrections
- **Battle-Tested:** Validated against Sept 2024 correction (24% dips scored 78-97)

---

## 🚀 Quick Usage

```bash
# Run analyzer (conservative mode - recommended)
cd /Users/nn359v/workspace/nitesh/mf-automation
uv run python src/mf/dip_analyzer.py conservative

# Test configuration
uv run python src/mf/config.py

# Change modes
uv run python src/mf/dip_analyzer.py moderate      # 55 threshold
uv run python src/mf/dip_analyzer.py aggressive    # 45 threshold
```

---

## 🎯 What Makes a Good Buy Signal?

**Example 1: Strong Signal (Score 78-97)** ✅
- Dip: 15-24% (30-40 points) ⭐
- Historical: 50-100% of max (10-13 points)
- Mean Reversion: Good (10-13 points)
- Volatility: Ideal (11 points)
- Recovery: Good (7-13 points)
- Category: Small/Mid cap (8-10 points)

**Example 2: Weak Signal (Score 45-55)** ❌
- Dip: 8-10% (20-22 points)
- Historical: <40% of max (4-6 points)
- Mean Reversion: Moderate (5-8 points)
- Volatility: High (5 points)
- Recovery: Slow (4 points)
- Category: Large cap (6 points)

**Key Insight:** With 40% dip depth weight, a 15%+ correction almost guarantees a signal (30-40 base points + 20-30 from other factors = 50-70+ total).

---

For complete algorithm details and implementation, see `ALGORITHM_DOCUMENTATION.md`

**Last Updated:** November 2025
