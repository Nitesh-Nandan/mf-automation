# 🎯 Mutual Fund Dip Analyzer

Intelligent dip-buying algorithm for Indian mutual funds.

## 🚀 Quick Start

```bash
cd src/mf
uv run python dip_analyzer.py
```

## 📂 Files

| File | Purpose |
|------|---------|
| `dip_analyzer.py` | Main analyzer - run this |
| `mf_funds.py` | Load funds from CSV |
| `mf_funds.csv` | Your fund portfolio |
| `trends_analyser.py` | NAV analysis |
| `historical_dip_analysis.py` | Historical dip calculator |

## 📊 How It Works

6-factor robust scoring system:
1. **Dip Depth** (0-25 pts) - Current vs peak NAV
2. **Historical Context** (0-20 pts) - vs past dips
3. **Mean Reversion** (0-15 pts) - Below average
4. **Volatility** (0-15 pts) - Risk assessment
5. **Recovery Speed** (0-15 pts) - Past resilience
6. **Fund Category** (0-10 pts) - Type bonus

**Total:** 0-100 points

## 🎯 Modes

- **Conservative** - Score ≥ 70 (very selective)
- **Moderate** - Score ≥ 60 (balanced)
- **Aggressive** - Score ≥ 50 (more opportunities)

## 💡 Strategy

**SIP + Opportunistic Dip Buying**

- Continue regular SIP (discipline)
- Use extra capital when algorithm signals dip
- Position size based on score strength

## 📖 Documentation

See `docs/` folder for:
- Algorithm documentation
- Backtest results
- Strategy guide

## 📝 Adding Funds

Edit `mf_funds.csv`:
```csv
FundName,Type,API Code,Url
Your Fund Name,Fund Type,CODE,https://api.mfapi.in/mf/CODE
```

Get API codes from https://api.mfapi.in

