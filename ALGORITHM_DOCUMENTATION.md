# Mutual Fund Dip-Buying Algorithm - Complete Documentation

**Version:** 1.0  
**Last Updated:** November 11, 2025  
**Status:** Production Ready ✅

---

## Table of Contents

1. [Overview](#overview)
2. [The 6 Factors Explained](#the-6-factors-explained)
3. [Scoring System](#scoring-system)
4. [Modes & Thresholds](#modes--thresholds)
5. [How to Use](#how-to-use)
6. [Technical Details](#technical-details)
7. [Examples](#examples)

---

## Overview

This algorithm identifies optimal mutual fund buying opportunities during market dips using a **data-driven, multi-factor approach**. It scores each opportunity from **0-100** based on 6 independent factors, providing clear buy/hold recommendations with suggested capital allocation.

### Key Features

- ✅ **6-Factor Analysis** - Comprehensive, not reliant on single indicator
- ✅ **Adaptive Thresholds** - 4 modes for different market conditions
- ✅ **Risk-Aware** - Avoids "falling knives" and false signals
- ✅ **Transparent** - Clear breakdown of every decision
- ✅ **Actionable** - Provides specific allocation recommendations
- ✅ **Backtested** - Validated with historical data

### Philosophy

**"Buy the dip, not the crash"**

The algorithm is designed to identify **meaningful corrections** that represent buying opportunities, while avoiding:
- ❌ Minor fluctuations (noise)
- ❌ Falling knives (continued declines)
- ❌ Structural problems (fund issues)

---

## The 6 Factors Explained

### Factor 1: Dip Depth (0-25 points)

**What it measures:** How far the current NAV has dropped from its recent peak

**Timeframe:** Last 120 days

**Scoring Logic:**

| Dip Percentage | Score | Meaning |
|----------------|-------|---------|
| ≥ 20% | 25 pts | Exceptional discount |
| 15-20% | 22 pts | Significant dip |
| 12-15% | 18 pts | Good dip |
| 10-12% | 15 pts | Moderate dip |
| 7-10% | 10 pts | Small dip |
| 5-7% | 5 pts | Minor pullback |
| < 5% | 0 pts | No meaningful dip |

**Why it matters:**
- Deeper dips = bigger potential discount
- But uses diminishing returns to avoid over-weighting extremes
- 120-day window ensures recent, actionable peaks

**Example:**
```
Peak NAV (Oct 15): ₹300
Current NAV (Nov 11): ₹264
Dip: (300-264)/300 = 12%
Score: 18/25 points ✅
```

---

### Factor 2: Historical Context (0-20 points)

**What it measures:** How the current dip compares to the fund's worst historical dip

**Timeframe:** Last 730 days (2 years)

**Scoring Logic:**

| Dip Ratio (Current vs Historical Max) | Score | Meaning |
|---------------------------------------|-------|---------|
| 60-80% of max | 20 pts | ⭐ Sweet spot! |
| 80-90% of max | 18 pts | Near historical low |
| 50-60% of max | 15 pts | Significant |
| 40-50% of max | 10 pts | Moderate |
| > 90% of max | 12 pts | ⚠️ Caution - near extreme |
| < 40% of max | 5 pts | Not significant |

**Why it matters:**
- Prevents buying too early (if dip is small relative to history)
- Identifies the "sweet spot" (60-80% of max = significant but not unprecedented)
- Warns if near historical maximum (could indicate crisis)

**Example:**
```
Maximum historical dip (Mar 2020): 25%
Current dip: 15%
Ratio: 15/25 = 60%
Score: 20/20 points ✅ (Perfect entry point!)
```

**The Sweet Spot Explained:**
- **< 40%:** Dip is too small, not a great opportunity
- **60-80%:** Significant dip but not extreme - optimal range!
- **> 90%:** Near worst-case, could signal problems

---

### Factor 3: Mean Reversion (0-15 points)

**What it measures:** How far below the average NAV the current price is

**Timeframe:** Last 120 days

**Scoring Logic:**
- **Formula:** Score = (% below mean) × 2
- **Maximum:** 15 points (capped at 7.5% below mean)
- **If above mean:** 0 points

| Below Mean | Score | Meaning |
|------------|-------|---------|
| ≥ 7.5% | 15 pts | Far below average |
| 6% | 12 pts | Well below average |
| 4% | 8 pts | Below average |
| 2% | 4 pts | Slightly below |
| Above mean | 0 pts | No advantage |

**Why it matters:**
- **Statistical principle:** Prices tend to revert to their mean over time
- **Clear target:** Mean NAV acts as natural recovery target
- **Filters overvalued:** No points if price is above average

**Example:**
```
Mean NAV (120 days): ₹280
Current NAV: ₹260
Deviation: (280-260)/280 = 7.14% below mean
Score: 7.14 × 2 = 14.28/15 points ✅
```

**Visual Representation:**
```
Price Movement Over Time

High ₹300 ─────────────────────────────
                   ╲
Mean ₹280 ─────────────●────────────────  ← Statistical pull back
                        ╲
Current ₹260 ──────────────◉────────────  ← Current position
                            ╲
Low ₹240 ────────────────────╲──────────
```

---

### Factor 4: Volatility (0-15 points)

**What it measures:** Annualized volatility (price fluctuation) of the fund

**Timeframe:** Last 730 days (2 years)

**Formula:** 
```
Volatility = Standard Deviation of Daily Returns × √252 × 100
(252 = typical trading days per year)
```

**Scoring Logic:**

| Volatility Range | Score | Meaning |
|------------------|-------|---------|
| **15-25%** | **15 pts** | ⭐ **Goldilocks Zone** |
| 25-35% | 12 pts | High but manageable |
| 10-15% | 10 pts | Low but decent |
| > 35% | 5 pts | Too risky (falling knife risk) |
| < 10% | 3 pts | Too stable (limited upside) |

**Why it matters:**

1. **Recovery Potential** 🚀
   - Higher volatility = Bigger price swings = Faster recovery possible
   - 20% volatile fund can recover from 10% dip in weeks

2. **Attractive Entry Points** 🎯
   - Volatile funds create more dip opportunities
   - You're buying the "wave troughs"

3. **Risk is Manageable** ⚖️
   - 15-25% range: Good movement without extreme risk
   - 40%+ volatility suggests instability

4. **Higher Returns** 📈
   - Volatility = opportunity for gains
   - Stable funds (8% volatility) have limited upside

**The Risk/Reward Balance:**

```
Risk ←─────────────────────→ Reward

Low Vol (8%)     Moderate Vol (20%)     High Vol (40%)
   │                   │                      │
   │                   │                      │
Low Risk           Balanced            High Risk
Low Return      High Return          Uncertain Return
Score: 3/15      Score: 15/15         Score: 5/15
```

**Example:**
```
Fund: Quant Small Cap
Daily returns: [+2%, -1.5%, +3%, -2%, +1.8%, ...]
Std Dev: 1.2% daily
Annualized: 1.2% × √252 × 100 = 19.05%
Score: 15/15 points ✅ (In Goldilocks zone!)
```

---

### Factor 5: Recovery Track Record (0-15 points)

**What it measures:** How quickly the fund has historically recovered from dips

**Timeframe:** Last 730 days (2 years)

**Method:**
1. Identifies all 5%+ dips in historical data
2. Measures days from dip start to full recovery (return to peak)
3. Calculates average recovery time

**Scoring Logic:**

| Average Recovery Time | Score | Meaning |
|----------------------|-------|---------|
| ≤ 30 days | 15 pts | Excellent resilience |
| 31-60 days | 12 pts | Good recovery |
| 61-90 days | 8 pts | Moderate recovery |
| > 90 days | 4 pts | Slow recovery |
| No history | 8 pts | Neutral (unknown) |

**Why it matters:**
- **Opportunity Cost:** Faster recovery = less time money is locked
- **Fund Quality:** Consistent quick recoveries suggest strong fundamentals
- **Risk Mitigation:** Slow recoveries might indicate structural problems

**Example:**
```
Historical Dips & Recoveries:

Dip 1 (Mar 2024): 10% drop → Recovered in 35 days
Dip 2 (Jul 2024): 8% drop  → Recovered in 28 days
Dip 3 (Oct 2024): 12% drop → Recovered in 42 days

Average Recovery: (35 + 28 + 42) / 3 = 35 days
Score: 12/15 points ✅
```

**Visual Timeline:**
```
Dip → Recovery Cycle

Peak ₹300 ●──╲              ╱──● Peak Recovered
              ╲            ╱
               ╲          ╱  ← 35 days recovery
                ╲        ╱
Bottom ₹270      ●──────╯
```

---

### Factor 6: Fund Type Weighting (0-10 points)

**What it measures:** Risk/reward profile based on fund category

**Timeframe:** N/A (static property)

**Scoring Logic:**

| Fund Type | Score | Rationale |
|-----------|-------|-----------|
| **Small Cap** | 10 pts | Highest growth potential, high risk |
| **Mid Cap** | 8 pts | Good growth, moderate risk |
| **Flexi Cap** | 8 pts | Balanced approach |
| **Large Cap** | 6 pts | Lower volatility, lower opportunity |
| **Debt/Liquid** | 3 pts | Stable, minimal dip-buying benefit |
| **Unknown** | 7 pts | Default neutral score |

**Why it matters:**
- **Different dip meanings:** 10% dip in Small Cap is normal; in Large Cap it's significant
- **Growth potential:** Small/Mid caps have more room to grow post-dip
- **Risk appetite:** Adjusts expectations by category

**Example:**
```
Fund A: Quant Small Cap Fund
Type: Small Cap
Score: 10/10 points ✅

Fund B: Nippon Large Cap Fund
Type: Large Cap
Score: 6/10 points

Same 10% dip:
- Small Cap: Score includes 10 pts (volatile is expected)
- Large Cap: Score includes 6 pts (might signal trouble)
```

---

## Scoring System

### Total Score Calculation

**Formula:**
```
Total Score = Factor1 + Factor2 + Factor3 + Factor4 + Factor5 + Factor6
Maximum: 100 points
```

**Example Calculation:**

```
Fund: Quant Small Cap Direct Growth
Current Dip: 12%
Historical Max Dip: 18%

Factor 1 (Dip Depth):        18/25  (12% dip)
Factor 2 (Historical):       20/20  (67% of max - sweet spot!)
Factor 3 (Mean Reversion):   12/15  (6% below mean)
Factor 4 (Volatility):       15/15  (20% vol - perfect)
Factor 5 (Recovery):         12/15  (40-day avg recovery)
Factor 6 (Fund Type):        10/10  (Small Cap bonus)
────────────────────────────────────
TOTAL SCORE:                 87/100  ✅ STRONG BUY
```

### Recommendation Levels

Based on total score, the algorithm provides recommendations:

| Score Range | Recommendation | Allocation | Confidence | Action |
|-------------|----------------|------------|------------|--------|
| **80-100** | STRONG BUY | 50% | Very High | Deploy immediately |
| **75-79** | STRONG BUY | 40% | Very High | Excellent opportunity |
| **60-74** | BUY | 30% | High | Good entry point |
| **45-59** | MODERATE BUY | 20% | Medium | Consider buying |
| **30-44** | WEAK BUY | 10% | Low | Wait for better |
| **0-29** | HOLD | 0% | None | No opportunity |

### Allocation Guidance

**Example with ₹100,000 dip-buying reserve:**

```
Score 85 (STRONG BUY) → Invest ₹40,000 (40%)
Score 68 (BUY) → Invest ₹30,000 (30%)
Score 52 (MODERATE BUY) → Invest ₹20,000 (20%)
Score 38 (WEAK BUY) → Invest ₹10,000 (10%)
Score 25 (HOLD) → Invest ₹0 (0%)
```

---

## Modes & Thresholds

The algorithm supports 4 modes with different buy thresholds:

### Mode Comparison Table

| Mode | Threshold | When to Use | Buy Frequency | Risk Level |
|------|-----------|-------------|---------------|------------|
| **Ultra Conservative** | 70 | Bear markets, crashes | 1-2x/year | Very Low |
| **Conservative** ⭐ | 60 | Normal conditions | 3-5x/year | Low |
| **Moderate** | 50 | Bull markets with pullbacks | 6-10x/year | Medium |
| **Aggressive** | 40 | Strong bull markets | 10-15x/year | High |

⭐ = Recommended default

### Mode Details

#### 1. Ultra Conservative (Threshold: 70)
```
Use when: Bear market, market crash, high uncertainty
Buy only: Exceptional dips (15-20%+)
Example: COVID crash (March 2020)
Strategy: Wait for extreme opportunities
```

#### 2. Conservative (Threshold: 60) ⭐
```
Use when: Normal market conditions
Buy only: Significant dips (10-15%+)
Example: Standard corrections
Strategy: Patient, quality entries
```

#### 3. Moderate (Threshold: 50)
```
Use when: Bull market with occasional pullbacks
Buy: Moderate dips (7-10%+)
Example: Sideways choppy market
Strategy: More active, capture pullbacks
```

#### 4. Aggressive (Threshold: 40)
```
Use when: Strong bull run, fear of missing out
Buy: Any dip (5-7%+)
Example: Consistent uptrend
Strategy: Participate in uptrend
```

### Choosing the Right Mode

**Decision Tree:**

```
Is the market in a crash or severe bear market?
├─ YES → Ultra Conservative (70)
└─ NO
    └─ Is the market bullish with few dips?
        ├─ YES → Moderate (50) or Aggressive (40)
        └─ NO → Conservative (60) ⭐ Default
```

---

## How to Use

### Quick Start

```bash
# Run the analyzer
python src/mf/dip_analyzer.py
```

### In Your Code

```python
from src.mf.dip_analyzer import analyze_dip_opportunity

# Analyze a single fund
result = analyze_dip_opportunity(
    fund_name="Quant Small Cap Fund",
    code="120828",
    fund_type="Small Cap",
    mode="conservative"  # or 'moderate', 'aggressive', 'ultra_conservative'
)

# Check if it triggers a buy
if result['triggers_buy']:
    print(f"BUY SIGNAL!")
    print(f"Score: {result['total_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Allocate: {result['allocation_percentage'] * 100}%")
    
    # Get detailed breakdown
    breakdown = result['score_breakdown']
    print(f"\nFactor Breakdown:")
    print(f"  Dip Depth: {breakdown['dip_depth']['score']}/25")
    print(f"  Historical: {breakdown['historical_context']['score']}/20")
    print(f"  Mean Reversion: {breakdown['mean_reversion']['score']}/15")
    print(f"  Volatility: {breakdown['volatility']['score']}/15")
    print(f"  Recovery: {breakdown['recovery_track_record']['score']}/15")
    print(f"  Fund Type: {breakdown['fund_type']['score']}/10")
else:
    print(f"HOLD - Score: {result['total_score']} (below threshold)")
```

### Analyze All Funds

```python
from src.mf.dip_analyzer import analyze_all_funds, print_analysis_summary

# Analyze all funds in conservative mode
results = analyze_all_funds(mode='conservative')
print_analysis_summary(results, mode='conservative')

# Get funds that triggered buy signals
buy_opportunities = [r for r in results if r['triggers_buy']]

for fund in buy_opportunities:
    print(f"\n{fund['fund_name']}")
    print(f"  Score: {fund['total_score']}")
    print(f"  Recommendation: {fund['recommendation']}")
    print(f"  Suggested allocation: {fund['allocation_percentage']*100}%")
```

### Weekly Monitoring

Set up a weekly routine:

```bash
# Every Monday morning
cd /path/to/mf-automation
python src/mf/dip_analyzer.py

# Review the output
# If buy signals triggered → Execute trades
# If no signals → Wait for next week
```

---

## Technical Details

### Data Sources

- **API:** https://api.mfapi.in/mf/{code}
- **Data Format:** JSON with NAV history
- **Date Format:** DD-MM-YYYY
- **Update Frequency:** Daily

### Timeframes

| Analysis Type | Timeframe | Purpose |
|---------------|-----------|---------|
| **Short-term** | 120 days (~4 months) | Tactical decisions (current dips) |
| **Long-term** | 730 days (~2 years) | Strategic context (historical patterns) |

**Why these timeframes?**
- **120 days:** Recent enough to be actionable, long enough for meaningful peaks
- **730 days:** Captures 1-2 market cycles, includes major corrections

### Dependencies

```python
# Required packages
import requests      # API calls
import statistics    # Volatility calculations
from datetime import datetime, timedelta  # Date handling
from typing import Dict, List  # Type hints
```

Install via:
```bash
uv sync  # or pip install requests
```

### Performance

- **Analysis time per fund:** ~2-3 seconds
- **API timeout:** 10 seconds
- **Rate limiting:** No restrictions on mfapi.in
- **Caching:** None (fresh data each run)

---

## Examples

### Example 1: Perfect Buy Signal

```
Fund: Quant Small Cap Fund
Date: November 11, 2025

Current NAV: ₹264
Peak NAV (120 days): ₹300
Mean NAV (120 days): ₹282
Max Historical Dip (2 years): 24%
Volatility: 20%
Avg Recovery: 38 days

=== FACTOR BREAKDOWN ===

1. Dip Depth: (300-264)/300 = 12%
   Score: 18/25 ✅

2. Historical Context: 12%/24% = 50% of max
   Score: 15/20 ✅

3. Mean Reversion: (282-264)/282 = 6.4% below mean
   Score: 6.4 × 2 = 12.8/15 ✅

4. Volatility: 20% (in 15-25% range)
   Score: 15/15 ✅

5. Recovery: 38 days average
   Score: 12/15 ✅

6. Fund Type: Small Cap
   Score: 10/10 ✅

TOTAL SCORE: 82.8/100

=== RECOMMENDATION ===
STRONG BUY ✅
Confidence: Very High
Allocate: 40% of dip-buying reserve
```

**Action:** Invest ₹40,000 out of ₹100,000 reserve

---

### Example 2: Hold Signal (No Dip)

```
Fund: HDFC Mid-Cap Fund
Date: November 11, 2025

Current NAV: ₹222
Peak NAV (120 days): ₹223
Mean NAV (120 days): ₹218
Max Historical Dip (2 years): 17%
Volatility: 18%
Avg Recovery: 42 days

=== FACTOR BREAKDOWN ===

1. Dip Depth: (223-222)/223 = 0.45%
   Score: 0/25 ❌ (< 5% threshold)

2. Historical Context: 0.45%/17% = 2.6% of max
   Score: 5/20 ⚠️ (insignificant)

3. Mean Reversion: 222 > 218 (above mean)
   Score: 0/15 ❌ (price above average)

4. Volatility: 18% (in 15-25% range)
   Score: 15/15 ✅

5. Recovery: 42 days average
   Score: 12/15 ✅

6. Fund Type: Mid Cap
   Score: 8/10 ✅

TOTAL SCORE: 40/100

=== RECOMMENDATION ===
HOLD ❌
Confidence: None
Allocate: 0%
```

**Action:** Do not buy. Wait for a real dip (10%+).

---

### Example 3: Caution Signal (Too Risky)

```
Fund: Hypothetical High-Vol Fund
Date: November 11, 2025

Current NAV: ₹150
Peak NAV (120 days): ₹200
Mean NAV (120 days): ₹175
Max Historical Dip (2 years): 28%
Volatility: 42%
Avg Recovery: 120 days

=== FACTOR BREAKDOWN ===

1. Dip Depth: (200-150)/200 = 25%
   Score: 25/25 ✅ (deep dip)

2. Historical Context: 25%/28% = 89% of max
   Score: 18/20 ⚠️ (near worst-case)

3. Mean Reversion: (175-150)/175 = 14.3% below mean
   Score: 15/15 ✅ (capped)

4. Volatility: 42% (> 35%)
   Score: 5/15 ❌ (too risky!)

5. Recovery: 120 days average
   Score: 4/15 ❌ (very slow)

6. Fund Type: Small Cap
   Score: 10/10 ✅

TOTAL SCORE: 77/100

=== RECOMMENDATION ===
STRONG BUY (score-wise) but...
⚠️  RED FLAGS:
- Extreme volatility (42%)
- Near historical maximum dip (89%)
- Slow recovery history (120 days)

VERDICT: Potential falling knife. Proceed with caution!
```

**Action:** Despite high score, the volatility and recovery factors suggest this might not be a dip but a crash. Consider waiting or reducing allocation to 20% instead of 40%.

---

## Summary

### Algorithm Strengths

✅ **Multi-Factor** - Not reliant on single indicator  
✅ **Data-Driven** - Based on historical patterns  
✅ **Risk-Aware** - Filters out dangerous situations  
✅ **Transparent** - Clear reasoning for every decision  
✅ **Adaptive** - Works in different market conditions  
✅ **Actionable** - Provides specific recommendations  

### Best Practices

1. **Use Conservative Mode** as default (threshold 60)
2. **Check Weekly** - Mondays are ideal
3. **Combine with SIP** - 60% SIP + 40% Dip Buying
4. **Track Results** - Log all buys and outcomes
5. **Adjust Mode** - Switch based on market conditions
6. **Don't Chase** - If you miss a dip, wait for the next

### Recommended Investment Strategy

```
Total Capital: ₹100,000

├─ 60% (₹60,000) → Regular SIP
│   └─ Monthly investments regardless of market
│
├─ 30% (₹30,000) → Conservative Dip Buying
│   └─ Deploy when score >= 60
│
└─ 10% (₹10,000) → Aggressive Dip Buying
    └─ Deploy when score >= 45
```

---

**Document Version:** 1.0  
**Algorithm Version:** 1.0  
**Last Updated:** November 11, 2025  
**Status:** Production Ready ✅

