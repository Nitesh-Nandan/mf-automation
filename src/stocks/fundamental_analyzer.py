"""
Fundamental Analyzer for Stocks
Evaluates company fundamentals for quality assessment
"""

from typing import Dict

from config import (
    get_pe_score, 
    QUALITY_THRESHOLDS,
    adjust_threshold_for_estimates,
    DATA_QUALITY
)


def calculate_fundamental_score(fundamentals: Dict) -> Dict:
    """
    Calculate fundamental quality score (0-25 points) - ENHANCED v3.0
    
    Evaluates:
    - Relative P/E Ratio (valuation) - 4 pts (or Absolute P/E fallback)
    - PEG Ratio (growth valuation) - 3 pts ⭐ NEW
    - Debt-to-Equity (financial health) - 3 pts
    - ROE (profitability) - 3 pts
    - Revenue Growth (top-line growth) - 5 pts
    - Profit Growth (bottom-line growth) - 4 pts
    - Profit Margin (profitability efficiency) - 3 pts
    
    Args:
        fundamentals: Dictionary with fundamental metrics
    
    Returns:
        Dictionary with score and breakdown
    """
    score = 0
    breakdown = {}
    
    # 1. Relative P/E Ratio (0-4 points)
    pe_ratio = fundamentals.get('pe_ratio', 0)
    median_pe = fundamentals.get('median_pe', 0)
    
    if median_pe > 0:
        # Relative Valuation Logic
        ratio = pe_ratio / median_pe
        if ratio < 0.8:
            pe_score = 4
            pe_assessment = "Historically Cheap"
        elif ratio < 1.0:
            pe_score = 3
            pe_assessment = "Below Median"
        elif ratio < 1.2:
            pe_score = 2
            pe_assessment = "Fair Value"
        elif ratio < 1.5:
            pe_score = 1
            pe_assessment = "Expensive"
        else:
            pe_score = 0
            pe_assessment = "Very Expensive"
    else:
        # Fallback to Absolute Valuation Logic (from config)
        pe_score, pe_assessment = get_pe_score(pe_ratio)
        pe_assessment += " (Absolute)"
    
    score += pe_score
    breakdown['pe_ratio'] = {
        'score': pe_score,
        'value': pe_ratio,
        'assessment': pe_assessment,
        'max': 4
    }

    # 2. PEG Ratio (0-3 points) ⭐ NEW
    peg_ratio = fundamentals.get('peg_ratio', 0)
    # If PEG is missing but we have P/E and Profit Growth, calculate it
    if peg_ratio == 0 and pe_ratio > 0 and fundamentals.get('profit_growth', 0) > 0:
        peg_ratio = pe_ratio / fundamentals.get('profit_growth')

    if peg_ratio > 0:
        if peg_ratio < 1.0:
            peg_score = 3
            peg_assessment = "Undervalued Growth"
        elif peg_ratio < 1.5:
            peg_score = 2
            peg_assessment = "Fair Price"
        elif peg_ratio < 2.0:
            peg_score = 1
            peg_assessment = "Expensive"
        else:
            peg_score = 0
            peg_assessment = "Overvalued"
    else:
        peg_score = 0
        peg_assessment = "N/A"

    score += peg_score
    breakdown['peg_ratio'] = {
        'score': peg_score,
        'value': peg_ratio,
        'assessment': peg_assessment,
        'max': 3
    }
    
    # 3. Debt-to-Equity (0-3 points)
    debt_equity = fundamentals.get('debt_to_equity', 100)
    if debt_equity == 0:
        de_score = 3
        de_assessment = "Debt-free"
    elif debt_equity < 50:
        de_score = 3
        de_assessment = "Very Low"
    elif debt_equity < 100:
        de_score = 2
        de_assessment = "Moderate"
    elif debt_equity < 200:
        de_score = 1
        de_assessment = "High"
    else:
        de_score = 0
        de_assessment = "Very High"
    
    score += de_score
    breakdown['debt_to_equity'] = {
        'score': de_score,
        'value': debt_equity,
        'assessment': de_assessment,
        'max': 3
    }
    
    # 4. ROE - Return on Equity (0-3 points)
    roe = fundamentals.get('roe', 0)
    if roe > 20:
        roe_score = 3
        roe_assessment = "Excellent"
    elif roe > 15:
        roe_score = 2
        roe_assessment = "Very Good"
    elif roe > 10:
        roe_score = 1
        roe_assessment = "Good"
    else:
        roe_score = 0
        roe_assessment = "Below Average"
    
    score += roe_score
    breakdown['roe'] = {
        'score': roe_score,
        'value': roe,
        'assessment': roe_assessment,
        'max': 3
    }
    
    # 5. Revenue Growth (0-5 points)
    revenue_growth = fundamentals.get('revenue_growth', 0)
    if revenue_growth > 15:
        growth_score = 5
        growth_assessment = "Excellent"
    elif revenue_growth > 10:
        growth_score = 3
        growth_assessment = "Good"
    elif revenue_growth > 5:
        growth_score = 1
        growth_assessment = "Moderate"
    else:
        growth_score = 0
        growth_assessment = "Slow/Declining"
    
    score += growth_score
    breakdown['revenue_growth'] = {
        'score': growth_score,
        'value': revenue_growth,
        'assessment': growth_assessment,
        'max': 5
    }
    
    # 6. Profit Growth (0-4 points)
    profit_growth = fundamentals.get('profit_growth', 0)
    if profit_growth > 25:
        profit_growth_score = 4
        profit_growth_assessment = "Excellent"
    elif profit_growth > 15:
        profit_growth_score = 3
        profit_growth_assessment = "Very Good"
    elif profit_growth > 8:
        profit_growth_score = 2
        profit_growth_assessment = "Good"
    elif profit_growth > 0:
        profit_growth_score = 1
        profit_growth_assessment = "Slow"
    else:
        profit_growth_score = 0
        profit_growth_assessment = "Negative/Declining"
    
    score += profit_growth_score
    breakdown['profit_growth'] = {
        'score': profit_growth_score,
        'value': profit_growth,
        'assessment': profit_growth_assessment,
        'max': 4
    }
    
    # 7. Profit Margin (0-3 points)
    profit_margin = fundamentals.get('profit_margin', 0)
    if profit_margin > 15:
        margin_score = 3
        margin_assessment = "Excellent"
    elif profit_margin > 10:
        margin_score = 2
        margin_assessment = "Good"
    elif profit_margin > 5:
        margin_score = 1
        margin_assessment = "Fair"
    else:
        margin_score = 0
        margin_assessment = "Poor"
    
    score += margin_score
    breakdown['profit_margin'] = {
        'score': margin_score,
        'value': profit_margin,
        'assessment': margin_assessment,
        'max': 3
    }
    
    return {
        'total_score': min(score, 25),
        'breakdown': breakdown,
        'max_score': 25
    }


def is_quality_stock(fundamentals: Dict, min_score: int = None) -> Dict:
    """
    Check if stock passes quality criteria (Updated for 25-point scale)
    
    Args:
        fundamentals: Dictionary with fundamental metrics
        min_score: Minimum fundamental score required (default from config)
    
    Returns:
        Dictionary with pass/fail and reasons
    """
    result = calculate_fundamental_score(fundamentals)
    score = result['total_score']
    
    # Use config default if not provided (Default 12/25)
    if min_score is None:
        min_score = 12 
    
    # Check if data is estimated
    data_quality = fundamentals.get('_data_quality', 'actual')
    estimated_fields = fundamentals.get('_estimated_fields', [])
    
    # Adjust min_score if many fields are estimated (from config)
    if DATA_QUALITY['adjust_score_for_estimates']:
        min_score = adjust_threshold_for_estimates(min_score, len(estimated_fields))
    
    # Strict quality filters
    checks = []
    
    # Check 1: Debt Level
    debt_equity = fundamentals.get('debt_to_equity', 1000)
    debt_ok = debt_equity < 200 # < 2.0
    checks.append({
        'name': 'Debt Level',
        'pass': debt_ok,
        'value': debt_equity,
        'criteria': "< 200"
    })
    
    # Check 2: ROE
    roe = fundamentals.get('roe', 0)
    roe_ok = roe > 10
    checks.append({
        'name': 'ROE',
        'pass': roe_ok,
        'value': f"{roe:.1f}%",
        'criteria': "> 10%"
    })
    
    # Check 3: Profit Growth
    profit_growth = fundamentals.get('profit_growth', -100)
    profit_growth_ok = profit_growth > 0
    checks.append({
        'name': 'Profit Growth',
        'pass': profit_growth_ok,
        'value': f"{profit_growth:.1f}%",
        'criteria': "> 0%"
    })
    
    # Check 4: Promoter Pledging ⭐ NEW
    pledged_shares = fundamentals.get('pledged_shares', 0)
    pledging_ok = pledged_shares < 5
    checks.append({
        'name': 'Promoter Pledging',
        'pass': pledging_ok,
        'value': f"{pledged_shares:.1f}%",
        'criteria': "< 5%"
    })
    
    # Check 5: Overall fundamental score
    score_ok = score >= min_score
    checks.append({
        'name': 'Fundamental Score',
        'pass': score_ok,
        'value': f"{score}/25",
        'criteria': f'>= {min_score}'
    })
    
    all_pass = all(check['pass'] for check in checks)
    
    return {
        'is_quality': all_pass,
        'fundamental_score': score,
        'checks': checks,
        'summary': 'PASS' if all_pass else 'FAIL',
        'data_quality': data_quality,
        'estimated_fields': estimated_fields
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
    print("🧪 Testing Enhanced Fundamental Analyzer (20-point system)\n")
    print("=" * 70)
    
    # Test Case 1: Excellent Blue-Chip Stock
    excellent_stock = {
        'pe_ratio': 22,
        'debt_to_equity': 45,
        'roe': 18.5,
        'revenue_growth': 15.3,
        'profit_growth': 20.5,      # ⭐ Strong profit growth
        'profit_margin': 16.2        # ⭐ Excellent margins
    }
    
    print("\n📊 Test Case 1: Excellent Blue-Chip Stock")
    print("-" * 70)
    result1 = calculate_fundamental_score(excellent_stock)
    quality1 = is_quality_stock(excellent_stock)
    
    print(f"Score: {result1['total_score']}/20 ({result1['total_score']/20*100:.1f}%)")
    print(f"Quality: {'✅ PASS' if quality1['is_quality'] else '❌ FAIL'}")
    print("\nBreakdown:")
    for factor, data in result1['breakdown'].items():
        print(f"  • {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} pts - {data['assessment']} (Value: {data['value']})")
    
    # Test Case 2: High Revenue, Low Profit (Growth Stock Warning)
    growth_warning = {
        'pe_ratio': 45,
        'debt_to_equity': 85,
        'roe': 14.2,
        'revenue_growth': 35.0,      # High revenue growth
        'profit_growth': -3.5,       # ⚠️ Negative profit growth
        'profit_margin': 4.2         # ⚠️ Low margins
    }
    
    print("\n📊 Test Case 2: High Revenue Growth, BUT Low Profitability")
    print("-" * 70)
    result2 = calculate_fundamental_score(growth_warning)
    quality2 = is_quality_stock(growth_warning)
    
    print(f"Score: {result2['total_score']}/20 ({result2['total_score']/20*100:.1f}%)")
    print(f"Quality: {'✅ PASS' if quality2['is_quality'] else '❌ FAIL'}")
    print("\nBreakdown:")
    for factor, data in result2['breakdown'].items():
        print(f"  • {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} pts - {data['assessment']} (Value: {data['value']})")
    
    # Test Case 3: Poor Quality Stock
    poor_stock = {
        'pe_ratio': 65,
        'debt_to_equity': 220,
        'roe': 7.8,
        'revenue_growth': -2.5,
        'profit_growth': -8.3,       # Declining profits
        'profit_margin': 2.1         # Very low margins
    }
    
    print("\n📊 Test Case 3: Poor Quality Stock")
    print("-" * 70)
    result3 = calculate_fundamental_score(poor_stock)
    quality3 = is_quality_stock(poor_stock)
    
    print(f"Score: {result3['total_score']}/20 ({result3['total_score']/20*100:.1f}%)")
    print(f"Quality: {'✅ PASS' if quality3['is_quality'] else '❌ FAIL'}")
    print("\nBreakdown:")
    for factor, data in result3['breakdown'].items():
        print(f"  • {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} pts - {data['assessment']} (Value: {data['value']})")
    
    # Test Case 4: Balanced Mid-Cap
    balanced_stock = {
        'pe_ratio': 28,
        'debt_to_equity': 75,
        'roe': 16.5,
        'revenue_growth': 14.0,
        'profit_growth': 18.2,       # Good profit growth
        'profit_margin': 11.5        # Solid margins
    }
    
    print("\n📊 Test Case 4: Balanced Mid-Cap Stock")
    print("-" * 70)
    result4 = calculate_fundamental_score(balanced_stock)
    quality4 = is_quality_stock(balanced_stock)
    
    print(f"Score: {result4['total_score']}/20 ({result4['total_score']/20*100:.1f}%)")
    print(f"Quality: {'✅ PASS' if quality4['is_quality'] else '❌ FAIL'}")
    print("\nBreakdown:")
    for factor, data in result4['breakdown'].items():
        print(f"  • {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} pts - {data['assessment']} (Value: {data['value']})")
    
    # Summary
    print("\n" + "=" * 70)
    print("📈 SUMMARY")
    print("=" * 70)
    print(f"Case 1 (Excellent): {result1['total_score']}/20 - {'✅ QUALITY' if quality1['is_quality'] else '❌ NOT QUALITY'}")
    print(f"Case 2 (High Rev, Low Profit): {result2['total_score']}/20 - {'✅ QUALITY' if quality2['is_quality'] else '❌ NOT QUALITY'}")
    print(f"Case 3 (Poor): {result3['total_score']}/20 - {'✅ QUALITY' if quality3['is_quality'] else '❌ NOT QUALITY'}")
    print(f"Case 4 (Balanced): {result4['total_score']}/20 - {'✅ QUALITY' if quality4['is_quality'] else '❌ NOT QUALITY'}")
    print("\n💡 Key Insight: Case 2 shows why profit growth matters more than revenue growth!")

