# Dip-Buying Algorithm Backtest Analysis Report

## Executive Summary

**Test Period:** Last 365 days (Nov 2024 - Nov 2025)  
**Funds Tested:** 6 mutual funds  
**Result:** Algorithm did NOT generate any buy signals

---

## Key Findings

### 1. **Algorithm Behavior: CONSERVATIVE (Correct)**

The algorithm scored all opportunities at **35-40 points** (out of 100), well below the **60-point buy threshold**.

| Fund | Avg Score | Max Score | Max Dip | Buy Signals |
|------|-----------|-----------|---------|-------------|
| Quant Small Cap | 40.0 | 40.0 | 1.23% | 0 |
| Nippon Small Cap | 40.0 | 40.0 | 2.19% | 0 |
| Nippon Large Cap | 35.0 | 35.0 | 1.22% | 0 |
| Quant Flexi Cap | 40.0 | 40.0 | 1.02% | 0 |
| HDFC Mid-Cap | 40.0 | 40.0 | 0.47% | 0 |

### 2. **Market Condition: BULLISH**

- **4 out of 6 funds** had positive returns (+1.59% to +9.88%)
- **No significant corrections** occurred in this period
- Maximum dips were only **0.5% to 2.2%** (very small)
- Historical maximum dips were **15-24%**, showing the current period was unusually stable

### 3. **Why No Buy Signals?**

**Factor Breakdown (Best Opportunity - Oct 31, 2025):**

| Factor | Score | Reason |
|--------|-------|--------|
| Dip Depth | 0/25 | Only 1-2% dips (need >5% for points) |
| Historical Context | 5/20 | Current dips were <10% of historical max |
| Mean Reversion | 0/15 | Price was above mean (bullish) |
| Volatility | 15/15 | Good volatility score |
| Recovery Track | 10/15 | Neutral |
| Fund Type | 10/10 | Full points |
| **TOTAL** | **40/100** | **Below 60 threshold** |

---

## Algorithm Validation

### ✅ **Positive Aspects**

1. **Conservative by design** - Didn't buy during a bull market (smart!)
2. **Avoided FOMO** - Prevented buying when prices were high
3. **Capital preservation** - In declining funds, holding cash outperformed
4. **Factor-based** - Clear reasons why scores were low

### ❌ **Limitations Identified**

1. **Too conservative for moderate volatility** - Missed 8-10% gains in bullish funds
2. **Fixed threshold** - 60-point threshold may be too high for stable markets
3. **Single timeframe tested** - This period had no corrections
4. **Need bearish period test** - Algorithm untested in actual dip conditions

---

## Recommendations

### 1. **Adaptive Thresholds**

Create mode-based thresholds based on market conditions:

```python
# Ultra Conservative (Bear Market)
threshold = 70  # Only buy extreme dips

# Conservative (Current)
threshold = 60  # Buy significant dips

# Moderate (Bull Market)
threshold = 50  # Buy moderate dips

# Aggressive (Strong Bull)
threshold = 40  # Buy any pullback
```

### 2. **Test with Historical Corrections**

To truly validate, backtest during periods with known corrections:
- **March 2020** - COVID crash (~30-40% correction)
- **2022** - Market correction (~15-20% correction)
- **2018** - NBFC crisis correction

### 3. **Hybrid Strategy**

Combine dip-buying with regular SIP:
- **70% SIP** - Regular monthly investment
- **30% Dip-buying** - Deploy using algorithm during corrections

### 4. **Score-Based Allocation**

Instead of binary buy/hold, use graduated allocation:

| Score Range | Recommendation | Allocation |
|-------------|----------------|------------|
| 80-100 | Strong Buy | 50% |
| 70-79 | Buy | 40% |
| 60-69 | Moderate Buy | 30% |
| 50-59 | Light Buy | 20% |
| 40-49 | Consider | 10% |
| <40 | Hold | 0% |

---

## Conclusion

### **Is the Algorithm Good?**

**YES**, but with caveats:

✅ **The algorithm is working as designed** - It correctly identified that the past year offered no compelling dip-buying opportunities.

✅ **Risk management is sound** - Better to miss gains than catch a "falling knife."

⚠️ **Needs real-world validation** - Must test during actual market corrections (2020, 2022) to see if it catches good entry points.

⚠️ **Consider adaptive thresholds** - Market conditions vary; threshold should too.

### **Next Steps**

1. ✅ **Backtest on 2020 data** - See if it caught COVID crash recovery
2. ✅ **Backtest on 2022 data** - Test on recent correction
3. ✅ **Implement adaptive thresholds** - Adjust based on market conditions
4. ✅ **Combine with SIP** - Don't rely solely on dip-buying

---

## Technical Notes

### Algorithm Components (6 Factors)

1. **Dip Depth (25 points)** - Current drop from peak
2. **Historical Context (20 points)** - Comparison to past dips
3. **Mean Reversion (15 points)** - Distance from average
4. **Volatility (15 points)** - Risk/reward profile
5. **Recovery Track (15 points)** - Historical recovery speed
6. **Fund Type (10 points)** - Category adjustment

### Timeframes Used

- **Short-term (120 days)** - Current conditions
- **Long-term (730 days)** - Historical context

### Buy Thresholds

- **Strong Buy:** Score ≥ 75 (40% allocation)
- **Buy:** Score ≥ 60 (30% allocation)
- **Moderate Buy:** Score ≥ 45 (20% allocation)
- **Hold:** Score < 45 (0% allocation)

---

*Report Generated: November 11, 2025*  
*Analysis Period: November 12, 2024 - November 10, 2025*

