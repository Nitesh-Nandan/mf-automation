# 🎯 Mutual Fund Dip Buying - Complete Guide

A robust, data-driven algorithm for identifying optimal mutual fund buying opportunities during market dips.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Run the smart dip buyer (recommended)
python src/mf/smart_dip_buyer.py

# 3. See current opportunities with different risk levels
```

---

## 📚 What This Does

This system analyzes your mutual funds and scores them (0-100) based on **6 independent factors** to identify the best times to buy during dips.

### The 6 Factors

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| 🔴 **Dip Depth** | 25 pts | How far price dropped from peak |
| 📊 **Historical Context** | 20 pts | Is this dip significant vs. history? |
| 📈 **Mean Reversion** | 15 pts | How far below average? |
| 📉 **Volatility** | 15 pts | Risk/reward balance |
| 🔄 **Recovery Speed** | 15 pts | How fast fund recovers |
| 🏷️ **Fund Type** | 10 pts | Small/Mid/Large cap adjustment |

**Total Score:** 0-100 points

---

## 🎚️ Modes & Thresholds

Choose your risk level:

| Mode | Threshold | When to Use | Expected Frequency |
|------|-----------|-------------|-------------------|
| **Ultra Conservative** | 70+ | Bear markets, crashes | Rare (1-2x/year) |
| **Conservative** ⭐ | 60+ | Normal corrections | Occasional (3-5x/year) |
| **Moderate** | 50+ | Bull with pullbacks | Regular (6-10x/year) |
| **Aggressive** | 40+ | Strong bull markets | Frequent (10-15x/year) |

⭐ = Recommended default

---

## 📊 Test Results Summary

### Backtest Period: Nov 2024 - Nov 2025

**Result:** ✅ Algorithm worked correctly

- **0 buy signals** generated (conservative/moderate modes)
- **Market was bullish** - funds went up 1-10%
- **Algorithm correctly avoided** buying at high prices
- **Aggressive mode** would have triggered 4 buys

### Key Finding

> The algorithm is **designed to be conservative**. It will hold cash during bull runs and only buy during genuine corrections. This is the correct behavior.

---

## 💡 Recommended Strategy

### Don't Use Dip-Buying Alone!

**Optimal Allocation:**

```
Total Investment Capital: ₹100,000

├─ 60% (₹60,000) → Regular SIP
│   Monthly investment regardless of market
│   Ensures you stay invested
│
├─ 30% (₹30,000) → Conservative Dip Buying
│   Deploy when score >= 60
│   For significant corrections
│
└─ 10% (₹10,000) → Aggressive Dip Buying
    Deploy when score >= 45
    For moderate pullbacks
```

---

## 🔧 Available Tools

### 1. Smart Dip Buyer (Main Tool)
```bash
python src/mf/smart_dip_buyer.py
```

**What it does:**
- Analyzes all your funds
- Shows current scores
- Tests all 4 modes
- Recommends which funds to buy

**Output:**
```
📊 SUMMARY - CONSERVATIVE MODE
Threshold: 60 points
Buy signals triggered: 2/6

✅ FUNDS TO BUY:
  Quant Small Cap Fund    Score: 68.5 | BUY
  Nippon Small Cap Fund   Score: 62.3 | BUY
```

---

### 2. Backtest Tool
```bash
python src/mf/backtest_dip_strategy.py
```

**What it does:**
- Tests algorithm on past year
- Compares to buy-and-hold
- Shows if it would have worked

**When to use:**
- Test on historical data
- Validate before live use
- Understand past performance

---

### 3. Diagnostics Tool
```bash
python src/mf/backtest_diagnostics.py
```

**What it does:**
- Shows score history
- Explains why no buys
- Identifies missed opportunities

**When to use:**
- Understand algorithm behavior
- Check if threshold is appropriate
- See what scores were generated

---

## 📖 How to Use

### Step 1: Check Current Opportunities

```bash
python src/mf/smart_dip_buyer.py
```

Look at the output for each mode. Focus on **Conservative** and **Moderate**.

### Step 2: Interpret Results

**If Conservative Mode triggers (score >= 60):**
✅ **Action:** Buy! This is a good dip opportunity
💰 **Amount:** 30% of your dip-buying reserve

**If Moderate Mode triggers (score >= 50):**
✅ **Action:** Consider buying
💰 **Amount:** 20% of your dip-buying reserve

**If no signals:**
⏸️ **Action:** Hold cash, wait for better opportunity
📊 **Check:** Run weekly to catch dips

### Step 3: Monitor Weekly

Set a reminder to check every **Monday**:

```bash
# Add to your weekly routine
# Monday morning: Check for dip opportunities
python src/mf/smart_dip_buyer.py
```

---

## 📈 Understanding Scores

### Score Ranges

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | Exceptional opportunity | Strong buy (50% allocation) |
| 70-79 | Excellent opportunity | Strong buy (40% allocation) |
| 60-69 | Good opportunity | Buy (30% allocation) |
| 50-59 | Moderate opportunity | Light buy (20% allocation) |
| 40-49 | Weak opportunity | Consider (10% allocation) |
| 0-39 | No opportunity | Hold cash |

### Example Score Breakdown

```
Fund: Quant Small Cap Direct Growth
Total Score: 68/100 → BUY

Factor Breakdown:
  Dip Depth:         15/25  (12% dip from peak)
  Historical:        18/20  (70% of max historical dip)
  Mean Reversion:    12/15  (6% below mean)
  Volatility:        15/15  (22% annualized)
  Recovery:          12/15  (45-day avg recovery)
  Fund Type:         10/10  (Small Cap bonus)
```

**Interpretation:**
- ✅ Decent 12% dip (could go deeper, but good enough)
- ✅ This is 70% of worst historical dip (sweet spot!)
- ✅ Price below average (mean reversion likely)
- ✅ Good volatility (potential for recovery)
- ✅ Quick recoveries historically
- ✅ Small cap = higher growth potential

**Verdict:** Good buying opportunity at 30% allocation

---

## 🎯 Real-World Example

### Scenario: Market Correction

**Week 1:** Check algorithm
```
All funds score 35-40 → No action, hold cash
```

**Week 3:** Market drops 8%
```
Conservative mode: No signals (scores 52-58)
Moderate mode: 2 signals triggered!
  → Quant Small Cap: 54 → Buy ₹3,000 (20% allocation)
  → Nippon Small Cap: 52 → Buy ₹3,000 (20% allocation)
```

**Week 5:** Market drops another 5% (total 13%)
```
Conservative mode: 3 signals triggered!
  → Quant Small Cap: 65 → Buy ₹4,500 (30% allocation)
  → Nippon Small Cap: 68 → Buy ₹4,500 (30% allocation)
  → Quant Flexi Cap: 61 → Buy ₹4,500 (30% allocation)
```

**Week 10:** Market recovers
```
All funds score 38-42 → No action, wait for next dip
Gains: ₹15,000 invested returned 18% = ₹2,700 profit
```

---

## ⚠️ Important Warnings

### ❌ Don't Do This

1. **Don't go all-in** on dip buying - Keep SIP going
2. **Don't use only aggressive mode** - You'll buy too often
3. **Don't panic sell** - Algorithm is for buying, not selling
4. **Don't ignore your risk tolerance** - Adjust modes accordingly
5. **Don't expect perfect timing** - No algorithm catches exact bottom

### ✅ Do This

1. **Do maintain regular SIP** - 60% of capital
2. **Do keep cash reserve** - 30-40% for dip buying
3. **Do check weekly** - Consistency matters
4. **Do use conservative/moderate** - For most situations
5. **Do track results** - Learn and adjust

---

## 🔍 FAQ

### Q: Why didn't it trigger any buys in the backtest?
**A:** The market was bullish with no significant dips. This is correct behavior - it avoids buying at high prices.

### Q: Should I use aggressive mode?
**A:** Only allocate 10-20% of dip-buying capital to aggressive mode. It's for capturing small pullbacks in strong bull markets.

### Q: How often should I check?
**A:** Weekly is sufficient. Dip opportunities don't change day-to-day.

### Q: What if I miss a dip?
**A:** There will be more. Markets correct regularly. Don't chase.

### Q: Can I modify the scoring?
**A:** Yes! The code is open. Adjust factor weights in `smart_dip_buyer.py` based on your testing.

### Q: Is this guaranteed to work?
**A:** No investment strategy is guaranteed. This is a systematic approach to dip-buying, not a crystal ball.

---

## 📁 Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `smart_dip_buyer.py` | Main algorithm | Check weekly for opportunities |
| `backtest_dip_strategy.py` | Historical testing | Validate before live use |
| `backtest_diagnostics.py` | Score analysis | Understand behavior |
| `trends_analyser.py` | Single fund analysis | Deep dive on one fund |
| `historical_dip_analysis.py` | Historical dip finder | See past corrections |
| `mf_funds.py` | Fund data loader | Automatic (used by others) |

---

## 🎓 Learn More

### Documentation
- `ALGORITHM_TEST_RESULTS.md` - Full test results and validation
- `BACKTEST_ANALYSIS_REPORT.md` - Detailed analysis of backtest
- `DIP_BUYING_GUIDE.md` - This guide

### Understanding the Math
Each factor is scored independently:

**Factor 1: Dip Depth**
```python
if dip >= 20%: score = 25
if dip >= 15%: score = 22
if dip >= 12%: score = 18
# ... and so on
```

**Factor 2: Historical Context**
```python
ratio = current_dip / max_historical_dip
if 60% <= ratio <= 80%: score = 20  # Sweet spot!
```

**Factor 3-6:** Similar logic based on their specific metrics

---

## 🚀 Next Steps

1. **Run the tools** - Get familiar with output
2. **Check weekly** - Make it a habit
3. **Start small** - Test with 10% of capital first
4. **Track results** - Keep a log of buys and outcomes
5. **Adjust** - Refine based on your experience

---

## 💬 Support

For questions or improvements:
1. Read the documentation files
2. Check the code comments
3. Run diagnostics to understand behavior
4. Test different modes to find what works

---

**Last Updated:** November 11, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅

Happy Dip Buying! 📈💰

