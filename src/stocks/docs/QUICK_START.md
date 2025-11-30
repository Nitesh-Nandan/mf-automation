# 🚀 Quick Start

## Run Analysis

```bash
python src/stocks/run_analysis.py
```

## Basic Usage

```python
from stocks import TechnicalAnalysis

analyzer = TechnicalAnalysis(
    stock_name="Asian Paints",
    stock_symbol="ASIANPAINT",
    instrument_key="NSE_EQ|INE021A01026"
)

result = analyzer.analyze()
print(f"Score: {result['final_score']}/100 - {result['recommendation']}")
```

## Output

```
Asian Paints (ASIANPAINT)
──────────────────────────────────────────────────
Price: ₹2874.40  |  RSI: 80.0  |  100 DMA: ₹2519.18
Peak (90d): ₹2926.90  |  Change: -1.79%

🎯 Score: 25/100  |  WAIT  (0.0x)
──────────────────────────────────────────────────

Factors: Dip:0 | Hist:0 | Mean:0 | Vol:10 | Rec:15 | Tech:0
```

## Score Meaning

| Score | Action | Meaning |
|-------|--------|---------|
| 85+ | STRONG BUY | Rare opportunity |
| 75-84 | BUY | Excellent entry |
| 60-74 | ACCUMULATE | Good dip |
| 50-59 | NIBBLE | Small position |
| <50 | WAIT | Not cheap enough |

## Configuration

Edit thresholds in `TechnicalScore.py`

## Docs

Full details: `README.md` | Algorithm: `docs/TECHNICAL_ALGORITHM_DOCUMENTATION.md`
