"""
Enhanced Mobile-Responsive Email Report Visualizer
Better mobile experience with card-based layout on small screens
"""

import webbrowser
import tempfile
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import sys

# Add mf module to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mf.config import RECOMMENDATION_THRESHOLDS


def generate_mobile_responsive_html_report(funds_analysis: List[Dict], mode: str = 'conservative') -> str:
    """
    Generate HTML email report with ENHANCED mobile responsiveness
    
    Args:
        funds_analysis: List of fund analysis dictionaries
        mode: Risk mode used (conservative, moderate, etc.)
    
    Returns:
        HTML string ready for email with mobile support
    """
    threshold = RECOMMENDATION_THRESHOLDS[mode]
    buy_funds = [f for f in funds_analysis if f['score'] >= threshold]
    strong_buy_funds = [f for f in buy_funds if f['score'] >= 75]
    regular_buy_funds = [f for f in buy_funds if 60 <= f['score'] < 75]
    
    # Calculate summary stats
    avg_dip = sum(f['dip_percentage'] for f in buy_funds) / len(buy_funds) if buy_funds else 0
    win_rate = (len(buy_funds) / len(funds_analysis) * 100) if funds_analysis else 0
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MF Dip Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 5px 0;
            font-size: 14px;
            opacity: 0.95;
        }}
        
        /* Summary Bar */
        .summary-bar {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 2px solid #e9ecef;
            text-align: center;
            font-size: 15px;
            color: #495057;
        }}
        .summary-bar strong {{
            color: #212529;
            font-weight: 600;
        }}
        
        /* Table Container */
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        .table-container h2 {{
            margin: 0 0 20px 0;
            color: #212529;
            font-size: 20px;
        }}
        
        /* Table Styles - DESKTOP */
        table {{
            width: 100%;
            border-collapse: collapse;
            border: 2px solid #dee2e6;
            background-color: white;
            font-size: 13px;
        }}
        
        thead {{
            background-color: #343a40;
            color: white;
        }}
        
        th {{
            padding: 12px 10px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #495057;
        }}
        
        th small {{
            font-size: 10px;
            font-weight: 400;
            text-transform: none;
            opacity: 0.9;
        }}
        
        td {{
            padding: 10px;
            border: 1px solid #dee2e6;
            vertical-align: top;
            font-size: 13px;
            line-height: 1.6;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        /* Column-specific styling */
        .fund-cell {{
            min-width: 220px;
        }}
        .fund-name {{
            font-weight: 600;
            color: #212529;
            margin-bottom: 3px;
            line-height: 1.3;
        }}
        .fund-nav {{
            color: #6c757d;
            font-size: 13px;
        }}
        
        .dip-cell {{
            text-align: center;
            font-weight: 700;
            font-size: 16px;
            min-width: 80px;
        }}
        .dip-high {{ color: #dc3545; }}      /* Deep red for big dips (15%+) */
        .dip-medium {{ color: #fd7e14; }}    /* Orange for medium dips (10-15%) */
        .dip-low {{ color: #e67e22; }}       /* Light orange for small dips (<10%) */
        
        .peak-cell {{
            min-width: 180px;
            line-height: 1.7;
            font-size: 12px;
        }}
        .peak-label {{
            font-weight: 700;
            color: #495057;
            display: inline-block;
            min-width: 45px;
            font-size: 11px;
        }}
        .peak-value {{
            color: #212529;
            font-size: 12px;
        }}
        
        .score-cell {{
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            min-width: 70px;
        }}
        .score-high {{ color: #28a745; }}
        .score-medium {{ color: #ffc107; }}
        .score-low {{ color: #6c757d; }}
        
        .verdict-cell {{
            text-align: center;
            min-width: 90px;
        }}
        .verdict-badge {{
            display: inline-block;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .verdict-strong-buy {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .verdict-buy {{
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        .verdict-hold {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        /* Recommendations Box */
        .recommendations {{
            margin: 30px;
            padding: 25px;
            background-color: #fffbf0;
            border: 1px solid #ffc107;
            border-radius: 5px;
        }}
        .recommendations h3 {{
            margin: 0 0 15px 0;
            font-size: 18px;
            font-weight: 600;
            color: #212529;
        }}
        .rec-section {{
            margin: 20px 0;
        }}
        .rec-section-title {{
            font-weight: 700;
            font-size: 14px;
            color: #495057;
            margin-bottom: 8px;
        }}
        .rec-fund {{
            padding: 8px 0;
            padding-left: 20px;
            font-size: 14px;
            color: #212529;
            line-height: 1.6;
            border-bottom: 1px solid #f8f9fa;
        }}
        .rec-fund:last-child {{
            border-bottom: none;
        }}
        .rec-total {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 2px solid #ffc107;
            font-size: 15px;
            font-weight: 600;
            color: #212529;
        }}
        
        /* Footer */
        .footer {{
            background-color: #f8f9fa;
            padding: 15px 20px;
            text-align: center;
            color: #6c757d;
            font-size: 11px;
            border-top: 1px solid #e9ecef;
        }}
        .footer p {{
            margin: 0;
        }}
        
        /* ============================================ */
        /* ENHANCED MOBILE RESPONSIVE (768px and below) */
        /* ============================================ */
        @media (max-width: 768px) {{
            body {{
                padding: 0;
                background-color: white;
            }}
            
            .container {{
                border-radius: 0;
            }}
            
            .header {{
                padding: 20px 16px;
            }}
            .header h1 {{
                font-size: 20px;
            }}
            .header p {{
                font-size: 12px;
            }}
            
            .summary-bar {{
                padding: 16px;
                font-size: 13px;
                line-height: 1.8;
            }}
            
            .table-container {{
                padding: 16px;
            }}
            
            .table-container h2 {{
                font-size: 18px;
                margin-bottom: 16px;
            }}
            
            /* Hide table on mobile, show cards instead */
            table {{
                display: none;
            }}
            
            /* Mobile card layout */
            .mobile-cards {{
                display: block !important;
            }}
            
            .recommendations {{
                margin: 16px;
                padding: 16px;
            }}
            .recommendations h3 {{
                font-size: 16px;
            }}
            .rec-fund {{
                font-size: 13px;
                padding: 6px 0 6px 15px;
            }}
        }}
        
        /* Mobile Cards - Hidden on desktop */
        .mobile-cards {{
            display: none;
        }}
        
        .mobile-card {{
            background: white;
            border-bottom: 2px solid #e9ecef;
            padding: 20px 0;
            margin-bottom: 0;
        }}
        
        .mobile-card:last-child {{
            border-bottom: none;
        }}
        
        .mobile-fund-name {{
            font-size: 15px;
            font-weight: 600;
            color: #212529;
            line-height: 1.4;
            margin-bottom: 12px;
        }}
        
        .mobile-verdict {{
            display: inline-block;
            margin-left: 8px;
        }}
        
        .mobile-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f8f9fa;
        }}
        
        .mobile-row:last-child {{
            border-bottom: none;
        }}
        
        .mobile-label {{
            font-size: 13px;
            color: #6c757d;
            font-weight: 500;
        }}
        
        .mobile-value {{
            font-size: 14px;
            font-weight: 600;
            color: #212529;
            text-align: right;
        }}
        
        .mobile-score-row {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .mobile-score-label {{
            font-size: 14px;
            color: #495057;
            font-weight: 600;
        }}
        
        .mobile-score-value {{
            font-size: 32px;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Mutual Fund Dip Analysis Report</h1>
            <p>Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
            <p>Mode: <strong>{mode.upper()}</strong> | Threshold: <strong>{threshold} points</strong></p>
        </div>
        
        <!-- Summary Bar -->
        <div class="summary-bar">
            <strong>{len(funds_analysis)}</strong> Funds  |  
            <strong style="color: #28a745;">{len(buy_funds)}</strong> BUY  |  
            <strong>{win_rate:.0f}%</strong> Win  |  
            <strong>{avg_dip:.1f}%</strong> Avg Dip
        </div>
        
        <!-- Table Container -->
        <div class="table-container">
            <h2>Detailed Analysis</h2>
            
            <!-- DESKTOP TABLE -->
            <table>
                <thead>
                    <tr>
                        <th style="text-align: center;">Fund Name<br><small>Current NAV</small></th>
                        <th style="text-align: center;">Change%</th>
                        <th style="text-align: center;">Recent</th>
                        <th style="text-align: center;">Historical</th>
                        <th style="text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Sort by score descending
    sorted_funds = sorted(funds_analysis, key=lambda x: x['score'], reverse=True)
    
    # Generate desktop table rows
    for fund in sorted_funds:
        # Determine verdict
        if fund['score'] >= 75:
            verdict_class = "verdict-strong-buy"
            verdict_text = "STRONG<br>BUY"
            score_class = "score-high"
        elif fund['score'] >= threshold:
            verdict_class = "verdict-buy"
            verdict_text = "BUY"
            score_class = "score-medium"
        else:
            verdict_class = "verdict-hold"
            verdict_text = "HOLD"
            score_class = "score-low"
        
        # Dip color
        if fund['dip_percentage'] >= 15:
            dip_class = "dip-high"
        elif fund['dip_percentage'] >= 10:
            dip_class = "dip-medium"
        else:
            dip_class = "dip-low"
        
        html += f"""                    <tr>
                        <td class="fund-cell" style="min-width: 200px;">
                            <div class="fund-name">{fund['fund_name']}</div>
                            <div class="fund-nav">Current: ₹{fund['current_nav']:.2f}</div>
                        </td>
                        <td class="dip-cell {dip_class}" style="text-align: center; min-width: 70px;">
                            {fund['dip_percentage']:.1f}%
                        </td>
                        <td class="peak-cell">
                            <div style="margin-bottom: 3px;">
                                <span class="peak-label">Low:</span>
                                <span class="peak-value">₹{fund['recent_low_nav']:.2f} ({fund['recent_low_date']})</span>
                            </div>
                            <div style="margin-bottom: 3px;">
                                <span class="peak-label">High:</span>
                                <span class="peak-value">₹{fund['recent_high_nav']:.2f} ({fund['recent_high_date']})</span>
                            </div>
                            <div>
                                <span class="peak-label">Mean:</span>
                                <span class="peak-value">₹{fund['recent_mean_nav']:.2f}</span>
                            </div>
                        </td>
                        <td class="peak-cell">
                            <div style="margin-bottom: 3px;">
                                <span class="peak-label">Low:</span>
                                <span class="peak-value">₹{fund['historical_low_nav']:.2f} ({fund['historical_low_date']})</span>
                            </div>
                            <div style="margin-bottom: 3px;">
                                <span class="peak-label">High:</span>
                                <span class="peak-value">₹{fund['historical_high_nav']:.2f} ({fund['historical_high_date']})</span>
                            </div>
                            <div>
                                <span class="peak-label">Mean:</span>
                                <span class="peak-value">₹{fund['historical_mean_nav']:.2f}</span>
                            </div>
                        </td>
                        <td style="text-align: center; min-width: 100px; padding: 8px;">
                            <div class="score-cell {score_class}" style="margin-bottom: 10px; font-size: 28px;">
                                {fund['score']:.0f}
                            </div>
                            <span class="verdict-badge {verdict_class}">{verdict_text}</span>
                        </td>
                    </tr>
"""
    
    html += """                </tbody>
            </table>
            
            <!-- MOBILE CARDS -->
            <div class="mobile-cards">
"""
    
    # Generate mobile cards
    for fund in sorted_funds:
        # Determine verdict
        if fund['score'] >= 75:
            verdict_class = "verdict-strong-buy"
            verdict_text = "STRONG BUY"
            score_class = "score-high"
        elif fund['score'] >= threshold:
            verdict_class = "verdict-buy"
            verdict_text = "BUY"
            score_class = "score-medium"
        else:
            verdict_class = "verdict-hold"
            verdict_text = "HOLD"
            score_class = "score-low"
        
        # Dip color
        if fund['dip_percentage'] >= 15:
            dip_class = "dip-high"
        elif fund['dip_percentage'] >= 10:
            dip_class = "dip-medium"
        else:
            dip_class = "dip-low"
        
        html += f"""                <div class="mobile-card">
                    <div class="mobile-fund-name">
                        {fund['fund_name']}
                        <span class="verdict-badge {verdict_class} mobile-verdict">{verdict_text}</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Current NAV</span>
                        <span class="mobile-value">₹{fund['current_nav']:.2f}</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Change%</span>
                        <span class="mobile-value {dip_class}">{fund['dip_percentage']:.1f}%</span>
                    </div>
                    
                    <div class="mobile-row" style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #dee2e6;">
                        <span class="mobile-label" style="font-weight: 700; color: #212529; font-size: 14px;">RECENT PERIOD</span>
                        <span></span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Low</span>
                        <span class="mobile-value" style="font-size: 12px;">₹{fund['recent_low_nav']:.2f} ({fund['recent_low_date']})</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">High</span>
                        <span class="mobile-value" style="font-size: 12px;">₹{fund['recent_high_nav']:.2f} ({fund['recent_high_date']})</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Mean</span>
                        <span class="mobile-value">₹{fund['recent_mean_nav']:.2f}</span>
                    </div>
                    
                    <div class="mobile-row" style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #dee2e6;">
                        <span class="mobile-label" style="font-weight: 700; color: #212529; font-size: 14px;">HISTORICAL PERIOD</span>
                        <span></span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Low</span>
                        <span class="mobile-value" style="font-size: 12px;">₹{fund['historical_low_nav']:.2f} ({fund['historical_low_date']})</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">High</span>
                        <span class="mobile-value" style="font-size: 12px;">₹{fund['historical_high_nav']:.2f} ({fund['historical_high_date']})</span>
                    </div>
                    
                    <div class="mobile-row">
                        <span class="mobile-label">Mean</span>
                        <span class="mobile-value">₹{fund['historical_mean_nav']:.2f}</span>
                    </div>
                    
                    <div class="mobile-score-row">
                        <span class="mobile-score-label">Score</span>
                        <span class="mobile-score-value {score_class}">{fund['score']:.0f}</span>
                    </div>
                </div>
"""
    
    html += """            </div>
        </div>
"""
    
    # Summary section - ALWAYS show
    html += """        <div class="recommendations" style="margin-top: 20px;">
            <h3 style="font-size: 20px; margin-bottom: 20px;">📊 Investment Summary</h3>
"""
    
    if buy_funds:
        html += """            <div class="rec-section">
"""
        if strong_buy_funds:
            html += f"""                <div class="rec-section-title" style="font-size: 15px; margin-bottom: 10px;">🎯 STRONG BUY ({len(strong_buy_funds)}):</div>
"""
            for fund in strong_buy_funds:
                html += f"""                <div class="rec-fund" style="padding: 10px 0 10px 20px; font-size: 14px;">• {fund['fund_name']} <strong>(Score: {fund['score']:.0f}, Dip: {fund['dip_percentage']:.1f}%)</strong></div>
"""
        
        if regular_buy_funds:
            html += f"""                <div class="rec-section-title" style="margin-top: 20px; font-size: 15px; margin-bottom: 10px;">✅ BUY ({len(regular_buy_funds)}):</div>
"""
            for fund in regular_buy_funds:
                html += f"""                <div class="rec-fund" style="padding: 10px 0 10px 20px; font-size: 14px;">• {fund['fund_name']} <strong>(Score: {fund['score']:.0f}, Dip: {fund['dip_percentage']:.1f}%)</strong></div>
"""
        
        html += """            </div>
"""
        
        total_investment = len(buy_funds) * 10000
        html += f"""            <div class="rec-total" style="margin-top: 25px; padding: 20px; background-color: #d4edda; border-left: 4px solid #28a745; font-size: 16px;">
                💰 <strong>Recommended Investment: ₹{total_investment:,}</strong> ({len(buy_funds)} funds × ₹10,000)
            </div>
"""
    else:
        # No buy signals
        html += f"""            <div style="padding: 30px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #dee2e6;">
                <p style="margin: 0; font-size: 18px; color: #495057; font-weight: 600;">⏳ No Buy Signals Currently</p>
                <p style="margin: 15px 0 0 0; font-size: 15px; color: #6c757d;">All {len(funds_analysis)} funds are rated as <strong>HOLD</strong></p>
                <p style="margin: 10px 0 0 0; font-size: 14px; color: #868e96;">Threshold for {mode.upper()} mode: {threshold} points</p>
            </div>
"""
    
    html += """        </div>
"""
    
    # Footer
    html += f"""        <div class="footer">
            <p>📊 Auto-generated Report | Please do your own research before investing</p>
        </div>
    </div>
</body>
</html>"""
    
    return html


def get_sample_data() -> List[Dict]:
    """Generate sample fund data for visualization"""
    return [
        {
            'fund_name': 'Quant Small Cap Fund Direct Growth',
            'current_nav': 281.43,
            'dip_percentage': 14.2,
            'peak_nav': 306.84,
            'peak_date': '08-10-2024',
            'recent_peak_nav': 306.84,
            'recent_peak_date': '08-10-2024',
            'score': 86.0,
            'verdict': 'STRONG BUY'
        },
        {
            'fund_name': 'Nippon India Small Cap Fund Direct Growth',
            'current_nav': 189.77,
            'dip_percentage': 12.4,
            'peak_nav': 204.30,
            'peak_date': '10-11-2024',
            'recent_peak_nav': 204.30,
            'recent_peak_date': '10-11-2024',
            'score': 79.0,
            'verdict': 'BUY'
        },
        {
            'fund_name': 'HDFC Mid-Cap Opportunities Direct Plan Growth',
            'current_nav': 222.34,
            'dip_percentage': 12.0,
            'peak_nav': 242.10,
            'peak_date': '05-11-2024',
            'recent_peak_nav': 242.10,
            'recent_peak_date': '05-11-2024',
            'score': 77.0,
            'verdict': 'STRONG BUY'
        },
        {
            'fund_name': 'Quant Flexi Cap Fund Direct Growth',
            'current_nav': 109.53,
            'dip_percentage': 11.1,
            'peak_nav': 123.23,
            'peak_date': '15-09-2024',
            'recent_peak_nav': 123.23,
            'recent_peak_date': '15-09-2024',
            'score': 76.3,
            'verdict': 'STRONG BUY'
        },
        {
            'fund_name': 'Nippon India Large Cap Fund Direct Growth',
            'current_nav': 102.72,
            'dip_percentage': 10.5,
            'peak_nav': 114.80,
            'peak_date': '27-09-2024',
            'recent_peak_nav': 114.80,
            'recent_peak_date': '27-09-2024',
            'score': 70.9,
            'verdict': 'BUY'
        },
        {
            'fund_name': 'Parag Parekh Flexi Cap Fund Direct Growth',
            'current_nav': 82.45,
            'dip_percentage': 5.2,
            'peak_nav': 87.26,
            'peak_date': '26-09-2024',
            'recent_peak_nav': 87.26,
            'recent_peak_date': '26-09-2024',
            'score': 42.0,
            'verdict': 'HOLD'
        },
        {
            'fund_name': 'Axis Bluechip Fund Direct Growth',
            'current_nav': 85.67,
            'dip_percentage': 18.5,
            'peak_nav': 105.20,
            'peak_date': '20-09-2024',
            'recent_peak_nav': 105.20,
            'recent_peak_date': '20-09-2024',
            'score': 92.0,
            'verdict': 'STRONG BUY'
        },
        {
            'fund_name': 'Mirae Asset Large Cap Fund Direct Growth',
            'current_nav': 145.30,
            'dip_percentage': 8.7,
            'peak_nav': 159.20,
            'peak_date': '25-10-2024',
            'recent_peak_nav': 159.20,
            'recent_peak_date': '25-10-2024',
            'score': 58.0,
            'verdict': 'MODERATE BUY'
        },
    ]


def visualize_mobile_responsive_report(mode: str = 'conservative', save_file: bool = True):
    """
    Generate MOBILE-RESPONSIVE HTML report and open in browser
    
    Args:
        mode: Risk mode (conservative, moderate, aggressive)
        save_file: Whether to save the HTML file permanently
    """
    print("\n" + "="*80)
    print("📱 MOBILE-RESPONSIVE EMAIL REPORT VISUALIZER")
    print("="*80)
    
    # Generate sample data
    print("\n1️⃣ Generating sample fund data...")
    sample_funds = get_sample_data()
    print(f"   ✅ Generated {len(sample_funds)} sample funds")
    
    # Generate HTML report
    print("\n2️⃣ Generating mobile-responsive HTML report...")
    html_content = generate_mobile_responsive_html_report(sample_funds, mode=mode)
    print(f"   ✅ HTML report generated (Mode: {mode.upper()})")
    
    # Save or create temporary file
    if save_file:
        output_dir = Path(__file__).parent / "reports"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = output_dir / f"email_preview_mobile_{timestamp}.html"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n3️⃣ Saved HTML file:")
        print(f"   📄 {filepath}")
        
        file_url = f"file://{filepath.absolute()}"
    else:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(html_content)
        temp_file.close()
        
        print(f"\n3️⃣ Created temporary preview file")
        
        file_url = f"file://{temp_file.name}"
    
    # Open in browser
    print("\n4️⃣ Opening in default browser...")
    webbrowser.open(file_url)
    print("   ✅ Browser opened!")
    
    print("\n" + "="*80)
    print("✅ MOBILE-RESPONSIVE VISUALIZATION COMPLETE!")
    print("="*80)
    print("\n💡 Tips for Testing:")
    print("   Desktop View (>768px):")
    print("   - Shows compact table with 5 columns")
    print("   - Hover effects on rows")
    print("")
    print("   Mobile View (≤768px):")
    print("   - Table switches to card-based layout")
    print("   - Each fund is a separate card")
    print("   - 2-column grid for information")
    print("   - Touch-friendly buttons")
    print("")
    print("   Test by:")
    print("   1. Resize browser window to narrow (< 768px)")
    print("   2. Use browser DevTools (F12) → Mobile view")
    print("   3. Open on actual phone/tablet")
    print("\n" + "="*80 + "\n")


def main():
    """Main function with CLI arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualize Mobile-Responsive MF Dip Analysis Email Report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python email_report_generator.py                    # Default
  python email_report_generator.py --mode aggressive  # Aggressive mode
  python email_report_generator.py --no-save          # Don't save file
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['ultra_conservative', 'conservative', 'moderate', 'aggressive'],
        default='conservative',
        help='Risk mode to use (default: conservative)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Use temporary file instead of saving permanently'
    )
    
    args = parser.parse_args()
    
    # Visualize report
    visualize_mobile_responsive_report(
        mode=args.mode,
        save_file=not args.no_save
    )


if __name__ == "__main__":
    main()


