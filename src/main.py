#!/usr/bin/env python3
"""
Main script to run MF Dip Analysis and send email report

This script is designed to be run as a scheduled job (cron, etc.).
It analyzes funds and sends an email report.
"""

import importlib.util
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from mf.config import RECOMMENDATION_THRESHOLDS

# Import MF analysis modules (now from mf package)
from mf.dip_analyzer import analyze_all_funds
from mf.types import AnalysisMode, AnalysisResult, EmailFundData
from mf.utils import format_date_short

# Import email report generator using importlib to avoid conflict with built-in email module
email_report_path = (
    Path(__file__).parent / "email" / "template" / "email_report_generator.py"
)
spec_report = importlib.util.spec_from_file_location(
    "email_report_generator", email_report_path
)
email_report_module = importlib.util.module_from_spec(spec_report)
spec_report.loader.exec_module(email_report_module)
generate_mobile_responsive_html_report = (
    email_report_module.generate_mobile_responsive_html_report
)

# Import email sender using importlib to avoid conflict with built-in email module
email_sender_path = Path(__file__).parent / "email" / "email_sender.py"
spec_sender = importlib.util.spec_from_file_location("email_sender", email_sender_path)
email_sender_module = importlib.util.module_from_spec(spec_sender)
spec_sender.loader.exec_module(email_sender_module)
EmailSender = email_sender_module.EmailSender


def convert_analysis_to_email_format(
    results: List[AnalysisResult], mode: AnalysisMode
) -> List[EmailFundData]:
    """
    Convert dip analysis results to email report format

    Args:
        results: List of analysis results from analyze_all_funds
        mode: Analysis mode used

    Returns:
        List of dictionaries formatted for email report
    """
    email_data = []

    for result in results:
        if result.get("error"):
            continue

        curr = result["current_analysis"]
        hist = result["historical_analysis"]

        # Determine verdict based on score and threshold
        score = result["total_score"]
        threshold = RECOMMENDATION_THRESHOLDS[mode]

        if score >= 75:
            verdict = "STRONG BUY"
        elif score >= threshold:
            verdict = "BUY"
        else:
            verdict = "HOLD"

        # For recent: use current_analysis data (recent period)
        # For historical: use historical_analysis all-time data

        email_data.append(
            {
                "fund_name": result["fund_name"],
                "current_nav": curr["current_nav"],
                "dip_percentage": curr["dip_from_peak_percentage"],
                # Recent period (120-180 days) - from trend_analyzer (current_analysis)
                "recent_low_nav": curr["bottom_nav"],
                "recent_low_date": format_date_short(curr["bottom_date"]),
                "recent_high_nav": curr["peak_nav"],
                "recent_high_date": format_date_short(curr["peak_date"]),
                "recent_mean_nav": curr["mean_nav"],
                # Historical period (700+ days) - from history_analyzer (historical_analysis)
                # Now using consistent field names!
                "historical_low_nav": hist["bottom_nav"],
                "historical_low_date": format_date_short(hist["bottom_date"]),
                "historical_high_nav": hist["peak_nav"],
                "historical_high_date": format_date_short(hist["peak_date"]),
                "historical_mean_nav": hist["mean_nav"],
                "score": score,
                "verdict": verdict,
            }
        )

    return email_data


def run_analysis_and_send_email(
    mode: AnalysisMode = "conservative",
    to_email: str = None,
    from_name: str = "MF Analysis Bot",
) -> bool:
    """
    Main function to run analysis and send email report
    Designed to run as a scheduled job

    Args:
        mode: Risk mode (default: conservative)
        to_email: Recipient email address (from ENV if not provided)
        from_name: Display name for sender

    Returns:
        True if email sent successfully, False otherwise
    """
    print("\n" + "=" * 80)
    print("🚀 MF DIP ANALYSIS & EMAIL REPORT")
    print("=" * 80)

    # Step 1: Run analysis
    print(f"\n📊 Running analysis (Mode: {mode.upper()})...")
    results = analyze_all_funds(mode=mode)

    if not results:
        print("❌ No analysis results. Exiting.")
        return False

    print(f"✅ {len(results)} funds analyzed")

    # Step 2: Generate email report
    print("\n📧 Generating email report...")
    email_data = convert_analysis_to_email_format(results, mode)
    html_content = generate_mobile_responsive_html_report(email_data, mode=mode)
    print("✅ Report generated")

    # Step 3: Send email
    print("\n📨 Sending email...")

    # Get recipient email
    if not to_email:
        to_email = os.getenv("EMAIL_USERNAME")
        if not to_email:
            print("❌ EMAIL_USERNAME not set in .env")
            return False

    # Initialize email sender
    sender = EmailSender()

    if not sender.username or not sender.password:
        print("❌ Email credentials not set in .env")
        return False

    # Create subject
    timestamp = datetime.now().strftime("%d %B %Y")
    subject = f"📊 MF Dip Analysis Report - {timestamp}"

    # Send email
    success = sender.send_email(
        to_email=to_email,
        subject=subject,
        body=html_content,
        html=True,
        from_name=from_name,
    )

    if success:
        threshold = RECOMMENDATION_THRESHOLDS[mode]
        buy_signals = [r for r in results if r["triggers_buy"]]
        print("\n" + "=" * 80)
        print("✅ EMAIL SENT SUCCESSFULLY")
        print(f"   Funds: {len(results)} | Buy Signals: {len(buy_signals)}")
        print("=" * 80 + "\n")
        return True
    else:
        print("❌ Failed to send email")
        return False


if __name__ == "__main__":
    run_analysis_and_send_email(
        mode="conservative",
        to_email="talk2nandan5686@gmail.com",
        from_name="MF Analysis",
    )
