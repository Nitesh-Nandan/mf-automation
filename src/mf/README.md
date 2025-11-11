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
| `fund_loader.py` | Load funds from CSV |
| `mf_funds.csv` | Your fund portfolio |
| `trend_analyzer.py` | NAV analysis |
| `history_analyzer.py` | Historical dip calculator |

## 📊 How It Works

6-factor robust scoring system:
1. **Dip Depth** (0-40 pts) - Current vs peak NAV
2. **Historical Context** (0-13 pts) - vs past dips
3. **Mean Reversion** (0-13 pts) - Below average
4. **Volatility** (0-11 pts) - Risk assessment
5. **Recovery Speed** (0-13 pts) - Past resilience
6. **Fund Category** (0-10 pts) - Type bonus

**Total:** 0-100 points

## 🎯 Modes

- **Ultra Conservative** - Score ≥ 75 (bear markets, crashes)
- **Conservative** ⭐ - Score ≥ 60 (normal conditions)
- **Moderate** - Score ≥ 55 (bull markets)
- **Aggressive** - Score ≥ 45 (strong uptrends)

## 💡 Strategy

**SIP + Opportunistic Dip Buying**

- Continue regular SIP (discipline)
- Use extra capital when algorithm signals dip
- Position size based on score strength

## 📖 Documentation

Essential docs in `docs/` folder:
- **`ALGORITHM_DOCUMENTATION.md`** - Complete algorithm explanation
- **`SCORING_REFERENCE.md`** - Quick scoring reference guide

## 📝 Adding Funds

Edit `mf_funds.csv`:
```csv
FundName,Type,API Code,Url
Your Fund Name,Fund Type,CODE,https://api.mfapi.in/mf/CODE
```

Get API codes from https://api.mfapi.in

