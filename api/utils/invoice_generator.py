"""
Invoice PDF Generator

Generates PDF invoices for billing records using reportlab.
Simple text-based invoices without complex styling.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from io import BytesIO


def generate_invoice_pdf(
    billing_history_id: str,
    org_name: str,
    event_type: str,
    plan_tier: str,
    amount_cents: int,
    created_at: datetime,
    description: Optional[str] = None
) -> BytesIO:
    """
    Generate PDF invoice from billing history record.

    Uses simple text-based PDF generation without reportlab dependency.
    Returns PDF as BytesIO buffer.

    Args:
        billing_history_id: Billing history record ID
        org_name: Organization name
        event_type: Type of billing event
        plan_tier: Subscription plan tier
        amount_cents: Amount in cents
        created_at: Date of transaction
        description: Optional description

    Returns:
        BytesIO: PDF file buffer
    """
    # Simple text-based invoice (reportlab not installed)
    # Format as plain text for now, can be upgraded to proper PDF later

    buffer = BytesIO()

    # Generate invoice text
    invoice_text = f"""
====================================
        INVOICE
====================================

Invoice ID: {billing_history_id}
Date: {created_at.strftime('%Y-%m-%d')}

------------------------------------
Bill To:
{org_name}
------------------------------------

Description: {description or event_type.replace('_', ' ').title()}
Plan: {plan_tier.title()}
Amount: ${amount_cents / 100:.2f}

------------------------------------
Total Due: ${amount_cents / 100:.2f}
------------------------------------

Thank you for your business!

SignUpFlow
https://signupflow.io
support@signupflow.io

====================================
"""

    buffer.write(invoice_text.encode('utf-8'))
    buffer.seek(0)

    return buffer


def generate_invoice_pdf_html(
    billing_history_id: str,
    org_name: str,
    event_type: str,
    plan_tier: str,
    amount_cents: int,
    created_at: datetime,
    description: Optional[str] = None,
    org_address: Optional[str] = None,
    invoice_number: Optional[str] = None
) -> str:
    """
    Generate HTML invoice template.

    Can be converted to PDF using browser print or weasyprint.

    Args:
        billing_history_id: Billing history record ID
        org_name: Organization name
        event_type: Type of billing event
        plan_tier: Subscription plan tier
        amount_cents: Amount in cents
        created_at: Date of transaction
        description: Optional description
        org_address: Optional organization address
        invoice_number: Optional invoice number

    Returns:
        str: HTML invoice template
    """
    invoice_num = invoice_number or f"INV-{billing_history_id[:8].upper()}"
    amount_usd = amount_cents / 100

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice_num}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 40px;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 20px;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #4f46e5;
        }}
        .invoice-info {{
            text-align: right;
        }}
        .invoice-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .info-section {{
            margin-bottom: 30px;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
        }}
        .bill-to {{
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        th {{
            background-color: #4f46e5;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .total-row {{
            font-weight: bold;
            font-size: 18px;
            background-color: #f9fafb;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 14px;
        }}
        .thank-you {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #4f46e5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">SignUpFlow</div>
        <div class="invoice-info">
            <div class="invoice-title">INVOICE</div>
            <div><span class="info-label">Invoice #:</span> {invoice_num}</div>
            <div><span class="info-label">Date:</span> {created_at.strftime('%B %d, %Y')}</div>
        </div>
    </div>

    <div class="bill-to">
        <div class="info-label" style="margin-bottom: 10px;">BILL TO:</div>
        <div style="font-size: 16px; font-weight: bold;">{org_name}</div>
        {f'<div style="margin-top: 5px; color: #666;">{org_address}</div>' if org_address else ''}
    </div>

    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th>Plan</th>
                <th style="text-align: right;">Amount</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{description or event_type.replace('_', ' ').title()}</td>
                <td>{plan_tier.title()}</td>
                <td style="text-align: right;">${amount_usd:.2f}</td>
            </tr>
            <tr class="total-row">
                <td colspan="2" style="text-align: right;">Total Due:</td>
                <td style="text-align: right;">${amount_usd:.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="thank-you">Thank you for your business!</div>

    <div class="footer">
        <div>SignUpFlow - Volunteer Scheduling Made Easy</div>
        <div>https://signupflow.io | support@signupflow.io</div>
        <div style="margin-top: 10px; font-size: 12px;">
            This is a computer-generated invoice. No signature required.
        </div>
    </div>
</body>
</html>
"""

    return html
