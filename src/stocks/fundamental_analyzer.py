"""
Fundamental Analyzer for Stocks
Evaluates company fundamentals for quality assessment
"""

from typing import Dict


def calculate_fundamental_score(fundamentals: Dict) -> Dict:
    """
    Calculate fundamental quality score (0-20 points) - ENHANCED
    
    Evaluates:
    - P/E Ratio (valuation) - 4 pts
    - Debt-to-Equity (financial health) - 3 pts
    - ROE (profitability) - 3 pts
    - Revenue Growth (top-line growth) - 3 pts
    - Profit Growth (bottom-line growth) - 4 pts ⭐ NEW
    - Profit Margin (profitability efficiency) - 3 pts ⭐ NEW
    
    Args:
        fundamentals: Dictionary with fundamental metrics
    
    Returns:
        Dictionary with score and breakdown
    """
    score = 0
    breakdown = {}
    
    # 1. P/E Ratio (0-4 points)
    pe_ratio = fundamentals.get('pe_ratio', 0)
    if pe_ratio > 0:
        if pe_ratio < 15:
            pe_score = 4  # Undervalued
            pe_assessment = "Undervalued"
        elif pe_ratio < 25:
            pe_score = 3  # Fair value
            pe_assessment = "Fair"
        elif pe_ratio < 35:
            pe_score = 2  # Slightly expensive
            pe_assessment = "Slightly Expensive"
        else:
            pe_score = 1  # Expensive
            pe_assessment = "Expensive"
    else:
        pe_score = 2  # Neutral if no data
        pe_assessment = "No Data"
    
    score += pe_score
    breakdown['pe_ratio'] = {
        'score': pe_score,
        'value': pe_ratio,
        'assessment': pe_assessment,
        'max': 4
    }
    
    # 2. Debt-to-Equity (0-3 points)
    debt_equity = fundamentals.get('debt_to_equity', 100)
    if debt_equity == 0:
        de_score = 3  # Zero debt is best
        de_assessment = "Debt-free"
    elif debt_equity < 50:
        de_score = 3  # Very low debt
        de_assessment = "Very Low"
    elif debt_equity < 100:
        de_score = 2  # Moderate debt
        de_assessment = "Moderate"
    elif debt_equity < 200:
        de_score = 1  # High debt
        de_assessment = "High"
    else:
        de_score = 0  # Very high debt
        de_assessment = "Very High"
    
    score += de_score
    breakdown['debt_to_equity'] = {
        'score': de_score,
        'value': debt_equity,
        'assessment': de_assessment,
        'max': 3
    }
    
    # 3. ROE - Return on Equity (0-3 points)
    roe = fundamentals.get('roe', 0)
    if roe > 20:
        roe_score = 3  # Excellent
        roe_assessment = "Excellent"
    elif roe > 15:
        roe_score = 2  # Very Good
        roe_assessment = "Very Good"
    elif roe > 10:
        roe_score = 1  # Good
        roe_assessment = "Good"
    else:
        roe_score = 0  # Poor/Fair
        roe_assessment = "Below Average"
    
    score += roe_score
    breakdown['roe'] = {
        'score': roe_score,
        'value': roe,
        'assessment': roe_assessment,
        'max': 3
    }
    
    # 4. Revenue Growth (0-3 points)
    revenue_growth = fundamentals.get('revenue_growth', 0)
    if revenue_growth > 20:
        growth_score = 3  # Excellent growth
        growth_assessment = "Excellent"
    elif revenue_growth > 12:
        growth_score = 2  # Good growth
        growth_assessment = "Good"
    elif revenue_growth > 5:
        growth_score = 1  # Moderate growth
        growth_assessment = "Moderate"
    else:
        growth_score = 0  # Slow/declining
        growth_assessment = "Slow/Declining"
    
    score += growth_score
    breakdown['revenue_growth'] = {
        'score': growth_score,
        'value': revenue_growth,
        'assessment': growth_assessment,
        'max': 3
    }
    
    # 5. Profit Growth (0-4 points) ⭐ NEW & CRITICAL
    profit_growth = fundamentals.get('profit_growth', 0)
    if profit_growth > 25:
        profit_growth_score = 4  # Excellent profit growth
        profit_growth_assessment = "Excellent"
    elif profit_growth > 15:
        profit_growth_score = 3  # Very good profit growth
        profit_growth_assessment = "Very Good"
    elif profit_growth > 8:
        profit_growth_score = 2  # Good profit growth
        profit_growth_assessment = "Good"
    elif profit_growth > 0:
        profit_growth_score = 1  # Slow profit growth
        profit_growth_assessment = "Slow"
    else:
        profit_growth_score = 0  # Negative profit growth
        profit_growth_assessment = "Negative/Declining"
    
    score += profit_growth_score
    breakdown['profit_growth'] = {
        'score': profit_growth_score,
        'value': profit_growth,
        'assessment': profit_growth_assessment,
        'max': 4
    }
    
    # 6. Profit Margin (0-3 points) ⭐ NEW
    profit_margin = fundamentals.get('profit_margin', 0)
    if profit_margin > 15:
        margin_score = 3  # Excellent margins
        margin_assessment = "Excellent"
    elif profit_margin > 10:
        margin_score = 2  # Good margins
        margin_assessment = "Good"
    elif profit_margin > 5:
        margin_score = 1  # Fair margins
        margin_assessment = "Fair"
    else:
        margin_score = 0  # Poor margins
        margin_assessment = "Poor"
    
    score += margin_score
    breakdown['profit_margin'] = {
        'score': margin_score,
        'value': profit_margin,
        'assessment': margin_assessment,
        'max': 3
    }
    
    return {
        'total_score': min(score, 20),
        'breakdown': breakdown,
        'max_score': 20
    }


def is_quality_stock(fundamentals: Dict, min_score: int = 10) -> Dict:
    """
    Check if stock passes quality criteria (Updated for 20-point scale)
    
    Args:
        fundamentals: Dictionary with fundamental metrics
        min_score: Minimum fundamental score required (default 10/20 = 50%)
    
    Returns:
        Dictionary with pass/fail and reasons
    """
    result = calculate_fundamental_score(fundamentals)
    score = result['total_score']
    
    # Strict quality filters
    checks = []
    
    # Check 1: Debt Level
    debt_equity = fundamentals.get('debt_to_equity', 1000)
    debt_ok = debt_equity < 100  # Debt-to-Equity < 1.0
    checks.append({
        'name': 'Debt Level',
        'pass': debt_ok,
        'value': debt_equity,
        'criteria': '< 100'
    })
    
    # Check 2: ROE
    roe = fundamentals.get('roe', 0)
    roe_ok = roe > 12
    checks.append({
        'name': 'ROE',
        'pass': roe_ok,
        'value': f"{roe:.1f}%",
        'criteria': '> 12%'
    })
    
    # Check 3: P/E Ratio (not too expensive)
    pe_ratio = fundamentals.get('pe_ratio', 0)
    pe_ok = 0 < pe_ratio < 50 if pe_ratio > 0 else False
    checks.append({
        'name': 'P/E Ratio',
        'pass': pe_ok,
        'value': pe_ratio,
        'criteria': '< 50'
    })
    
    # Check 4: Profit Growth ⭐ NEW
    profit_growth = fundamentals.get('profit_growth', -100)
    profit_growth_ok = profit_growth > 0  # At least positive profit growth
    checks.append({
        'name': 'Profit Growth',
        'pass': profit_growth_ok,
        'value': f"{profit_growth:.1f}%",
        'criteria': '> 0%'
    })
    
    # Check 5: Profit Margin ⭐ NEW
    profit_margin = fundamentals.get('profit_margin', 0)
    profit_margin_ok = profit_margin > 5  # At least 5% profit margin
    checks.append({
        'name': 'Profit Margin',
        'pass': profit_margin_ok,
        'value': f"{profit_margin:.1f}%",
        'criteria': '> 5%'
    })
    
    # Check 6: Overall fundamental score
    score_ok = score >= min_score
    checks.append({
        'name': 'Fundamental Score',
        'pass': score_ok,
        'value': f"{score}/20",
        'criteria': f'>= {min_score}'
    })
    
    all_pass = all(check['pass'] for check in checks)
    
    return {
        'is_quality': all_pass,
        'fundamental_score': score,
        'checks': checks,
        'summary': 'PASS' if all_pass else 'FAIL'
    }


def print_fundamental_analysis(fundamentals: Dict, stock_name: str):
    """Pretty print fundamental analysis"""
    print(f"\n{'='*80}")
    print(f"📊 FUNDAMENTAL ANALYSIS: {stock_name}")
    print(f"{'='*80}")
    
    if not fundamentals:
        print("❌ No fundamental data available")
        return
    
    result = calculate_fundamental_score(fundamentals)
    quality = is_quality_stock(fundamentals)
    
    print(f"\nFUNDAMENTAL SCORE: {result['total_score']}/15")
    print(f"Quality Status: {'✅ PASS' if quality['is_quality'] else '❌ FAIL'}")
    
    print(f"\nKEY METRICS:")
    breakdown = result['breakdown']
    
    print(f"  P/E Ratio:        {breakdown['pe_ratio']['value']:.2f} "
          f"({breakdown['pe_ratio']['assessment']}) - {breakdown['pe_ratio']['score']}/4")
    
    print(f"  Debt-to-Equity:   {breakdown['debt_to_equity']['value']:.2f} "
          f"({breakdown['debt_to_equity']['assessment']}) - {breakdown['debt_to_equity']['score']}/3")
    
    print(f"  ROE:              {breakdown['roe']['value']:.1f}% "
          f"({breakdown['roe']['assessment']}) - {breakdown['roe']['score']}/4")
    
    print(f"  Revenue Growth:   {breakdown['revenue_growth']['value']:.1f}% "
          f"({breakdown['revenue_growth']['assessment']}) - {breakdown['revenue_growth']['score']}/4")
    
    print(f"\nQUALITY CHECKS:")
    for check in quality['checks']:
        status = "✅" if check['pass'] else "❌"
        print(f"  {status} {check['name']}: {check['value']} (need {check['criteria']})")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    # Test with sample data
    print("🧪 Testing Fundamental Analyzer\n")
    
    # Test Case 1: Good Stock
    good_stock = {
        'pe_ratio': 22,
        'debt_to_equity': 45,
        'roe': 18.5,
        'revenue_growth': 12.3
    }
    
    print("Test Case 1: Good Quality Stock")
    result1 = calculate_fundamental_score(good_stock)
    quality1 = is_quality_stock(good_stock)
    
    print(f"Score: {result1['total_score']}/15")
    print(f"Quality: {'✅ PASS' if quality1['is_quality'] else '❌ FAIL'}")
    
    # Test Case 2: Poor Stock
    poor_stock = {
        'pe_ratio': 55,
        'debt_to_equity': 180,
        'roe': 8.2,
        'revenue_growth': -2.5
    }
    
    print("\nTest Case 2: Poor Quality Stock")
    result2 = calculate_fundamental_score(poor_stock)
    quality2 = is_quality_stock(poor_stock)
    
    print(f"Score: {result2['total_score']}/15")
    print(f"Quality: {'✅ PASS' if quality2['is_quality'] else '❌ FAIL'}")

