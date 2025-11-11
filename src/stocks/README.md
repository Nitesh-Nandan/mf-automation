# Blue-Chip Stock Dip Analyzer

**8-factor algorithm for identifying stock dip-buying opportunities**

---

## 🚀 Quick Start

```bash
# Run the analyzer
uv run python src/stocks/stock_dip_analyzer.py
```

**Output:**
```
🚀 BLUE-CHIP STOCK DIP ANALYZER
8-factor analysis for quality stock opportunities

🎯 Analyzing Blue-Chip Stocks - CONSERVATIVE MODE

Analyzing Reliance Industries (RELIANCE)...
  ✅ Score: 68.5 | BUY

📊 STOCK ANALYSIS SUMMARY
Threshold: 65 points
Buy signals triggered: 2

✅ STOCKS TO BUY:
TCS        ₹3,250   12%    68.5   15%
Infosys    ₹1,530   10%    65.2   10%
```

---

## 📊 The 8 Factors

### Original 6 Factors (from MF analyzer)

1. **Dip Depth (0-25 pts)** - How far from peak
2. **Historical Context (0-20 pts)** - Compared to past dips
3. **Mean Reversion (0-15 pts)** - Below average price
4. **Volatility (0-15 pts)** - Risk/reward balance
5. **Recovery Speed (0-15 pts)** - Historical resilience
6. **Market Cap (0-5 pts)** - Size adjustment

### Stock-Specific Factors

7. **Fundamentals (0-20 pts)** ⭐ ENHANCED
   - P/E Ratio (valuation) - 4 pts
   - Debt-to-Equity (financial health) - 3 pts
   - ROE (profitability) - 3 pts
   - Revenue Growth (top-line) - 3 pts
   - **Profit Growth (bottom-line) - 4 pts** 🆕
   - **Profit Margin (efficiency) - 3 pts** 🆕

8. **Technicals (0-10 pts)** ⭐ NEW
   - RSI (oversold?)
   - Volume spike
   - Near support level

**Total:** 0-125 points (normalized to 100)

---

## 📋 Files

| File | Purpose |
|------|---------|
| `stock_dip_analyzer.py` | Main analyzer (run this) |
| `stock_data_fetcher.py` | Fetches price & fundamental data |
| `fundamental_analyzer.py` | Quality checks & scoring |
| `stocks_watchlist.csv` | Your blue-chip stocks |

---

## 🎯 How It Works

### Step 1: Quality Filter

**Only analyzes stocks that pass ALL these checks:**

```python
✅ Debt-to-Equity < 1.0  (Low debt)
✅ ROE > 12%              (Good returns)
✅ P/E Ratio < 50         (Not overvalued)
✅ Fundamental Score >= 8 (Quality company)
```

### Step 2: Dip Analysis

**Calculates 8-factor score (0-100):**

- Technical dip factors (6 factors)
- Fundamental quality (1 factor)
- Technical indicators (1 factor)

### Step 3: Recommendation

| Score | Recommendation | Allocation |
|-------|----------------|------------|
| 80-100 | STRONG BUY | 20% of reserve |
| 70-79 | BUY | 15% |
| 60-69 | MODERATE BUY | 10% |
| 50-59 | WEAK BUY | 5% |
| < 50 | HOLD | 0% |

---

## ⚙️ Configuration

### Edit Your Watchlist

`stocks_watchlist.csv`:

```csv
symbol,name,sector,market_cap,exchange,min_score
RELIANCE,Reliance Industries,Energy,large,NSE,65
INFY,Infosys,IT,large,NSE,60
TCS,TCS,IT,large,NSE,60
```

**Fields:**
- `symbol`: Stock symbol
- `name`: Company name
- `sector`: Industry sector
- `market_cap`: large/mid/small
- `exchange`: NSE or BSE
- `min_score`: Minimum score to consider (recommended: 60-65)

### Choose Mode

```python
# In stock_dip_analyzer.py, line ~570:

mode = 'conservative'  # Threshold 65 (recommended)
# mode = 'moderate'    # Threshold 55
# mode = 'aggressive'  # Threshold 45
```

---

## 💡 Usage Strategy

### Your Complete Setup

```
MONTHLY INVESTMENT: ₹100,000

1. Mutual Funds (₹70,000)
   ├─ ₹60,000 → Regular MF SIP
   └─ ₹10,000 → MF Dip Reserve

2. Stocks (₹30,000)
   ├─ ₹15,000 → Index Fund/ETF SIP
   └─ ₹15,000 → Stock Dip Reserve ← THIS ANALYZER

Stock Dip Reserve Rules:
├─ Max 20% per stock (₹3,000 max)
├─ Max 5-7 stocks total
├─ Max 40% per sector
└─ Deploy only when score >= 65
```

### Weekly Routine

```bash
# Every Monday
uv run python src/stocks/stock_dip_analyzer.py

# If buy signals:
# - Review fundamentals
# - Check sector allocation
# - Deploy up to 20% per stock
# - Max ₹3,000 per stock (if ₹15,000 reserve)

# If no signals:
# - Keep building reserve
# - Index fund SIP continues as usual
```

---

## 📊 Example Output

```
🎯 Analyzing Blue-Chip Stocks - CONSERVATIVE MODE

Analyzing Reliance Industries (RELIANCE)...
  Fetching data for RELIANCE.NS...
  ✅ Score: 68.5 | BUY

SCORE BREAKDOWN:
├─ Dip Depth:         18/25  (12% dip)
├─ Historical:        18/20  (Good vs historical)
├─ Mean Reversion:    10/15  (Below mean)
├─ Volatility:        12/15  (Moderate)
├─ Recovery:          10/15  (45-day avg)
├─ Market Cap:        5/5    (Large cap)
├─ Fundamentals:      12/15  ✅ (P/E: 24, ROE: 18%)
└─ Technicals:        7/10   ✅ (RSI: 38, Volume up)

TOTAL: 68.5/100 → BUY
```

---

## 🔧 Dependencies

Required:
- `yfinance` - Stock data API

Install:
```bash
uv sync
```

---

## ⚠️ Important Differences from MF Analyzer

### 1. Stricter Quality Filter

Stocks must pass fundamental checks before analysis:
- MF: Always analyzed (fund manager handles quality)
- Stocks: Quality filter first, then dip analysis

### 2. Smaller Position Sizes

- MF: 30-40% of reserve per opportunity
- Stocks: 10-20% of reserve per stock (higher risk)

### 3. More Diversification Needed

- MF: 2-3 funds can be enough
- Stocks: Need 5-7 stocks minimum

### 4. Higher Threshold

- MF: Conservative mode = 60
- Stocks: Conservative mode = 65 (need higher confidence)

---

## 📈 Understanding the Quality Filter

### Why Many Stocks Fail

```
Current Market (Example):

10 stocks analyzed
├─ 4 failed: P/E too high (overvalued)
├─ 2 failed: ROE too low (poor returns)
├─ 1 failed: High debt
└─ 3 passed: Quality stocks ✅

Of 3 quality stocks:
├─ 2 scored 40-50 (not dipping enough)
└─ 1 scored 68 (BUY signal!) ✅
```

**This is correct behavior!**
- Most stocks are expensive in bull markets
- Algorithm waits for quality stocks at good prices
- Better to hold cash than buy mediocre stocks

---

## 🎓 Tips

### 1. Start Conservative

```python
mode = 'conservative'  # 65 threshold
```

Only buy highest conviction opportunities

### 2. Position Sizing

```python
# If you have ₹15,000 stock reserve:

Score 80: Deploy ₹3,000 (20%)  # Max per stock
Score 70: Deploy ₹2,250 (15%)
Score 65: Deploy ₹1,500 (10%)

# Never more than ₹3,000 per stock
# Never more than 5-7 stocks total
```

### 3. Sector Limits

```python
# Don't put >40% in one sector

If you have ₹15,000:
- Max IT stocks: ₹6,000 (2 stocks × ₹3,000)
- Max Banking: ₹6,000
- Max Energy: ₹6,000
```

### 4. Rebuild Reserve

After deploying:
```
Month 1: Deploy ₹6,000 (2 stocks)
Month 2: Add ₹15,000, now ₹24,000
Month 3: Wait for next dip
Month 4: Deploy another ₹6,000...
```

---

## 📝 Current Test Results

**Test Date:** November 11, 2025

```
Stocks Analyzed: 10
Passed Quality Filter: 4
Buy Signals (65 threshold): 0

Top Scores:
- TCS: 56.8 (below threshold)
- Wipro: 44.9
- Infosys: 40.8

Why no buys?
- Market is bullish
- Stocks not dipping significantly
- Some expensive (high P/E)
- Algorithm correctly holding cash
```

**This is good!**
- Preserving capital for better opportunities
- Your index fund SIP is handling the bull run
- Reserve ready for next correction

---

## 🚀 Next Steps

1. ✅ **Review watchlist** - Add/remove stocks in `stocks_watchlist.csv`
2. ✅ **Build reserve** - Accumulate ₹15-20k for stock dips
3. ✅ **Run weekly** - Check every Monday
4. ✅ **Start conservative** - Use 65 threshold initially
5. ✅ **Track results** - Log all buys and outcomes

---

**Created:** November 11, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅

