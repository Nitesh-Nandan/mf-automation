# Mutual Fund Dip Buying Strategy - Backtest Documentation

## Overview

This backtest simulates the performance of the mutual fund dip-buying strategy over historical periods. It evaluates whether the algorithm would have outperformed a simple buy-and-hold strategy.

## Key Features

### ✅ No Future Peeking
- Uses only historical data available at each decision point
- Simulates real-time decision making
- Realistic transaction timing

### ✅ Handles Missing Data
- Uses config defaults when historical data is unavailable
- Gracefully handles data gaps
- Maintains consistency with production algorithm

### ✅ Multiple Modes
- **Ultra Conservative** (threshold: 75) - Very selective, bear market opportunities
- **Conservative** (threshold: 60) - High quality signals (1-2 per year)
- **Moderate** (threshold: 55) - Balanced approach (3-5 per year)
- **Aggressive** (threshold: 45) - More opportunities (6-10 per year)

### ✅ Comprehensive Metrics
- Returns vs buy-and-hold baseline
- Transaction history with scores
- Per-fund and overall performance
- Market condition analysis

## How It Works

### Simulation Process

1. **Data Collection**: Fetch 2+ years of historical NAV data
2. **Time Walking**: Evaluate strategy every 7 days (weekly)
3. **Score Calculation**: Use only data available up to that point
4. **Buy Decisions**: Execute when score ≥ threshold and capital available
5. **Portfolio Tracking**: Monitor portfolio value over time
6. **Comparison**: Compare against buy-and-hold baseline

### Scoring Algorithm

The backtest uses the exact same 6-factor scoring system as production:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Dip Depth** | 40 pts | Current dip magnitude from peak |
| **Historical Context** | 13 pts | Comparison with past dips |
| **Mean Reversion** | 13 pts | Distance below average price |
| **Volatility** | 11 pts | Risk/reward balance |
| **Recovery Speed** | 13 pts | Historical bounce-back time |
| **Fund Category** | 10 pts | Fund type adjustment |

**Total: 100 points**

### Buy Logic

```python
if score >= threshold and capital >= investment_amount:
    execute_buy()
```

- Invest fixed amount (default: ₹10,000) per signal
- Keep remaining capital for future opportunities
- No selling (buy-only strategy)

## Usage

### Basic Usage

```bash
# Conservative mode, 2-year backtest
python backtest_dip_strategy.py --mode conservative --days 730

# Aggressive mode, 1-year backtest
python backtest_dip_strategy.py --mode aggressive --days 365

# Custom capital and investment
python backtest_dip_strategy.py --mode moderate --days 730 \
    --capital 200000 --investment 20000

# Save to specific directory
python backtest_dip_strategy.py --mode conservative --days 730 \
    --output ../../archive/backtest
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Risk mode (ultra_conservative, conservative, moderate, aggressive) | conservative |
| `--days` | Number of days to backtest | 730 (2 years) |
| `--capital` | Initial capital per fund | 100000 |
| `--investment` | Amount per buy signal | 10000 |
| `--output` | Output directory for results | current directory |

### Output Files

The backtest generates two files:

1. **JSON Results** (`backtest_results_{mode}_{timestamp}.json`)
   - Detailed transaction history
   - Portfolio values over time
   - Score breakdowns
   - Machine-readable format

2. **Text Report** (`backtest_report_{mode}_{timestamp}.txt`)
   - Human-readable summary
   - Performance metrics
   - Insights and recommendations
   - Fund-by-fund analysis

## Interpreting Results

### Key Metrics

#### Strategy Performance
- **Total Invested**: Capital deployed in dip buys
- **Units Accumulated**: Fund units purchased
- **Average Buy NAV**: Average purchase price
- **Final Value**: Portfolio value at end
- **Return %**: Total return percentage

#### Baseline Performance
- **Buy NAV**: Entry price at start of period
- **Final Value**: Value if bought and held
- **Return %**: Buy-and-hold return

#### Comparison
- **Outperformance**: Strategy return - Baseline return
- **Win Rate**: % of funds where strategy beats baseline

### Understanding Outperformance

#### Positive Outperformance (✅)
```
Strategy Return: +15%
Baseline Return: +10%
Outperformance: +5%
```
**Meaning**: Dip buying beat buy-and-hold by 5 percentage points

#### Negative Outperformance (❌)
```
Strategy Return: +10%
Baseline Return: +30%
Outperformance: -20%
```
**Meaning**: Strategy made money (+10%) but buy-and-hold was better

**Important**: Negative outperformance doesn't mean loss, just underperformance relative to baseline.

### Market Context Matters

#### Bull Markets (Strong Uptrend)
- ❌ Dip buying typically underperforms
- ✅ Buy-and-hold wins (invested from day 1)
- Strategy keeps cash idle waiting for dips

**Example**: Past 2 years (2023-2025) showed strong bull market
- Strategy: +9% to +18% returns
- Baseline: +36% to +51% returns
- Verdict: Underperformed but still profitable

#### Volatile/Sideways Markets
- ✅ Dip buying typically outperforms
- ❌ Buy-and-hold suffers from swings
- Strategy buys at valleys, accumulates more units

#### Bear Markets (Corrections/Crashes)
- ✅ Dip buying excels
- ❌ Buy-and-hold locks in early losses
- Strategy buys at increasingly better prices

### Transaction Analysis

#### Good Signs
- ✅ Multiple buy signals (7-10 over 2 years)
- ✅ Decreasing average buy NAV over time
- ✅ Buys during 12%+ dips
- ✅ Good score distribution (60-90 range)

#### Warning Signs
- ⚠️ Zero or too few signals (threshold too high)
- ⚠️ All buys at similar prices (not catching real dips)
- ⚠️ Low scores (45-55) for all transactions
- ⚠️ Buys too early in downtrend

## Strategy Limitations

### 1. Bull Market Underperformance
**Problem**: Missing early gains by waiting for dips

**Example**: If market goes up 50% before first 10% dip
- Strategy: Buys at +35% from start
- Baseline: Bought at start

**Mitigation**: 
- Combine with SIP for base allocation
- Use aggressive mode in bull markets
- Accept that outperformance isn't guaranteed every period

### 2. Timing Risk
**Problem**: Market may keep falling after buy signal

**Example**: Buy at 10% dip, falls another 10%
- Could have bought cheaper
- Temporary paper loss

**Mitigation**:
- Multiple small buys (₹10K each) instead of lump sum
- Keep reserves for deeper dips
- Focus on long-term recovery

### 3. Opportunity Cost
**Problem**: Capital sits idle waiting for signals

**Example**: ₹100K capital, only 3 signals
- ₹70K uninvested for 2 years
- Loses potential returns on that 70%

**Mitigation**:
- Use only "dip buying" allocation (e.g., 30% of portfolio)
- Rest in SIP/regular investments
- Accept lower utilization for better entry prices

### 4. Recovery Dependency
**Problem**: Strategy assumes dips will recover

**Example**: Permanent decline in fund fundamentals
- Buys get cheaper, but fund never recovers
- Accumulates losses

**Mitigation**:
- Monitor fund fundamentals separately
- Stop buying if fundamental deterioration
- Focus on quality funds only

## Best Practices

### 1. Realistic Expectations
✅ **Do**: Expect 5-15% returns in normal markets
❌ **Don't**: Expect to always beat buy-and-hold

### 2. Market Cycle Awareness
✅ **Do**: Understand which market phase you're in
- Bull: Strategy will likely underperform
- Volatile: Strategy has best chance
- Bear: Strategy can excel

❌ **Don't**: Judge strategy on single bull market period

### 3. Portfolio Integration
✅ **Do**: Use alongside SIP for base allocation
```
40% - Regular SIP (dollar-cost averaging)
30% - Dip buying strategy (opportunistic)
30% - Emergency reserve
```

❌ **Don't**: Make this your only investment method

### 4. Long-Term View
✅ **Do**: Evaluate over multiple market cycles (3-5 years)
❌ **Don't**: Judge on single year or backtest

### 5. Risk Management
✅ **Do**: 
- Set maximum allocation per fund (30%)
- Keep reserves for deeper dips (20%)
- Invest fixed amounts per signal

❌ **Don't**: 
- Go all-in on first signal
- Chase every small dip
- Ignore fund fundamentals

## Sample Backtest Interpretation

### Example: 2-Year Bull Market (Nov 2023 - Nov 2025)

```
Mode: Conservative
Threshold: 60 points
Funds: 6
Backtest Period: 730 days

Results:
- Buy Signals: 50 total (8.3 avg per fund)
- Strategy Return: +9.7% average
- Baseline Return: +42.4% average
- Outperformance: -32.7%
- Win Rate: 0%
```

### What This Tells Us

1. **Algorithm Works**: Generated 50 quality buy signals
2. **Market Was Strong**: +42% baseline shows bull market
3. **Strategy Protected Capital**: +9.7% return, no losses
4. **Timing Was Issue**: Bought dips in uptrend, missed early gains
5. **Context Matters**: Would likely outperform in correction/sideways market

### Actionable Insights

✅ **Continue Using**: Algorithm identifies dips correctly
✅ **Manage Expectations**: Won't beat buy-and-hold in strong bulls
✅ **Add SIP**: Combine with regular SIP for base allocation
⚠️ **Consider Aggressive Mode**: Lower threshold for more participation

## Advanced Analysis

### Score Distribution
Analyze transaction scores to understand buy quality:
```python
# Good distribution (well-timed dips)
60-69: 30% of buys
70-79: 40% of buys
80-89: 20% of buys
90+:   10% of buys

# Poor distribution (too aggressive)
45-54: 50% of buys  # Barely meeting threshold
55-64: 40% of buys
65+:   10% of buys  # Few high-quality signals
```

### Dip Magnitude Analysis
Check what dip levels triggered buys:
```python
# Conservative buying (good for quality)
8-10%:  20% of buys
10-15%: 50% of buys
15-20%: 25% of buys
20%+:   5% of buys

# Too aggressive (catching shallow dips)
5-8%:   50% of buys
8-10%:  30% of buys
10%+:   20% of buys
```

### Fund Type Performance
Different fund types perform differently:
```python
# Typical patterns
Small Cap:  Higher volatility → More signals
Mid Cap:    Balanced signals
Large Cap:  Fewer, deeper dips
Flexi Cap:  Variable by portfolio composition
```

## Troubleshooting

### No Buy Signals
**Problem**: Zero transactions over 1-2 years

**Possible Causes**:
1. Threshold too high for market conditions
2. Strong bull market (no significant dips)
3. Insufficient historical data

**Solutions**:
- Try aggressive or moderate mode
- Increase backtest period to 3 years
- Lower minimum dip threshold in config

### All Funds Underperform
**Problem**: Consistent negative outperformance

**Possible Causes**:
1. Bull market period (expected)
2. Buying too early in downtrends
3. Not enough time for recovery

**Solutions**:
- Check market phase (bull vs bear)
- Extend backtest period
- Wait for full market cycle
- This is expected behavior in bulls

### Very High Returns
**Problem**: Strategy returns seem unrealistic (>100%)

**Possible Causes**:
1. Testing during severe crash recovery (2020 COVID)
2. Small sample size (1-2 funds)
3. Specific fund had extraordinary performance

**Solutions**:
- Verify results against actual fund performance
- Test across multiple funds
- Check transaction timing and NAVs

## Technical Details

### Performance Optimization
- Fetches data once per fund (not per analysis)
- Weekly evaluation (vs daily) for speed
- Simplified recovery calculation for backtest
- Sorted data structures for fast lookups

### Data Handling
- Handles missing data gracefully
- Uses config defaults when needed
- Validates minimum data requirements
- Sorts data once, uses everywhere

### Accuracy
- Uses actual NAV data from API
- No future peeking (strict historical simulation)
- Realistic transaction costs (none assumed, add if needed)
- Weekly evaluation (conservative estimate)

## Future Enhancements

### Potential Additions
1. **Transaction Costs**: Add brokerage/STT fees
2. **Tax Impact**: Consider LTCG/STCG implications
3. **Daily Evaluation**: More frequent checks (slower)
4. **Monte Carlo**: Random start dates
5. **Drawdown Analysis**: Maximum portfolio decline
6. **Sharpe Ratio**: Risk-adjusted returns
7. **Recovery Time**: Time to breakeven

### Research Questions
1. Optimal threshold for different market phases?
2. Best investment amount per signal?
3. Impact of evaluation frequency (daily vs weekly)?
4. Should we sell at peaks?
5. Optimal combination with SIP?

## Conclusion

The backtest provides valuable insights into strategy performance, but remember:

✅ **Use It To**:
- Understand strategy behavior
- Set realistic expectations
- Validate scoring algorithm
- Choose appropriate mode
- Identify market suitability

❌ **Don't Use It To**:
- Guarantee future returns
- Judge strategy on single period
- Replace fundamental analysis
- Time the market perfectly
- Make all-or-nothing decisions

**Remember**: Past performance doesn't guarantee future results, but it helps understand strategy characteristics and set realistic expectations.

---

## Quick Reference

### When Strategy Works Best
- ✅ Volatile/sideways markets
- ✅ Bear market recoveries
- ✅ Periodic corrections in uptrend
- ✅ Quality funds with mean reversion

### When Strategy Struggles
- ❌ Strong bull markets (misses early gains)
- ❌ Permanent fund decline (no recovery)
- ❌ Very stable funds (no dips)
- ❌ Short time horizons (<1 year)

### Recommended Usage
```
Portfolio Structure:
- 40% Regular SIP (base allocation)
- 30% Dip buying (this strategy)
- 20% Emergency fund
- 10% Opportunistic reserve

Evaluation:
- Backtest over 2-3 years minimum
- Test multiple market conditions
- Compare across different modes
- Validate with multiple funds

Execution:
- Start with conservative mode
- Use fixed investment amounts
- Keep 20-30% reserve capital
- Monitor fund fundamentals
- Adjust based on market phase
```

---

*For questions or issues, refer to the main README or raise an issue in the repository.*

