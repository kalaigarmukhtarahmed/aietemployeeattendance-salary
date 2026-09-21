"""
PDF Salary Slip Generator for AIET Employee Attendance & Salary Processing System.
Generates institutional-grade salary slips using ReportLab.
"""

import os
from datetime import datetime
from utils import get_salary_slips_dir, format_currency, get_month_name

def generate_salary_slip_pdf(salary_data, output_path=None):
    """
    Generate an official AIET Employee Salary Slip PDF.
    salary_data is a dict containing employee and salary breakdown fields.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return False, "ReportLab is not installed. Please run: pip install reportlab"

    emp_id = salary_data.get("employee_id", "EMP")
    month = salary_data.get("month", 1)
    year = salary_data.get("year", 2024)
    month_name = get_month_name(month)

    if not output_path:
        filename = f"SalarySlip_{emp_id}_{month_name}_{year}.pdf"
        output_path = os.path.join(get_salary_slips_dir(), filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    # Colors
    aiet_navy = colors.HexColor("#1e3a8a")
    aiet_accent = colors.HexColor("#0284c7")
    neutral_dark = colors.HexColor("#1e293b")
    neutral_light = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#cbd5e1")

    # Header Title
    title_style = ParagraphStyle(
        'AIETHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=22,
        alignment=1,  # Center
        textColor=aiet_navy
    )

    sub_style = ParagraphStyle(
        'AIETSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#475569")
    )

    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=aiet_accent
    )

    story.append(Paragraph("ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY", title_style))
    story.append(Paragraph("Shobhavana Campus, Mijar, Moodbidri, D.K., Karnataka - 574227", sub_style))
    story.append(Paragraph("Affiliated to VTU Belagavi &amp; Approved by AICTE New Delhi", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=aiet_navy, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph(f"EMPLOYEE SALARY SLIP — {month_name.upper()} {year}", doc_title_style))
    story.append(Spacer(1, 12))

    # Employee Identification Grid
    emp_meta = [
        [
            Paragraph("<b>Employee ID:</b>", styles['Normal']),
            Paragraph(str(salary_data.get("employee_id", "-")), styles['Normal']),
            Paragraph("<b>Department:</b>", styles['Normal']),
            Paragraph(str(salary_data.get("department", "-")), styles['Normal'])
        ],
        [
            Paragraph("<b>Employee Name:</b>", styles['Normal']),
            Paragraph(str(salary_data.get("name", "-")), styles['Normal']),
            Paragraph("<b>Designation:</b>", styles['Normal']),
            Paragraph(str(salary_data.get("designation", "-")), styles['Normal'])
        ],
        [
            Paragraph("<b>Pay Period:</b>", styles['Normal']),
            Paragraph(f"{month_name} {year}", styles['Normal']),
            Paragraph("<b>Generated On:</b>", styles['Normal']),
            Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles['Normal'])
        ],
        [
            Paragraph("<b>Total Working Days:</b>", styles['Normal']),
            Paragraph(str(salary_data.get("total_working_days", "-")), styles['Normal']),
            Paragraph("<b>Days Present / Leave:</b>", styles['Normal']),
            Paragraph(f"{salary_data.get('days_present', 0)} / {salary_data.get('leave_days', 0)}", styles['Normal'])
        ]
    ]

    emp_table = Table(emp_meta, colWidths=[110, 150, 110, 145])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), neutral_light),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 15))

    # Earnings and Deductions Table
    basic_val = float(salary_data.get("basic_salary", 0))
    att_sal_val = float(salary_data.get("attendance_salary", 0))
    ot_hrs = float(salary_data.get("overtime_hours", 0))
    ot_rate = float(salary_data.get("overtime_rate", 0))
    ot_pay_val = float(salary_data.get("overtime_pay", 0))
    allow_val = float(salary_data.get("allowances", 0))
    gross_val = float(salary_data.get("gross_salary", 0))
    deduct_val = float(salary_data.get("deductions", 0))
    net_val = float(salary_data.get("net_salary", 0))

    salary_breakdown = [
        # Table Header
        [
            Paragraph("<b>EARNINGS &amp; ALLOWANCES</b>", styles['Normal']),
            Paragraph("<b>AMOUNT (₹)</b>", styles['Normal']),
            Paragraph("<b>DEDUCTIONS</b>", styles['Normal']),
            Paragraph("<b>AMOUNT (₹)</b>", styles['Normal'])
        ],
        # Row 1
        [
            Paragraph("Basic Salary (Standard)", styles['Normal']),
            Paragraph(f"{basic_val:,.2f}", styles['Normal']),
            Paragraph("Standard Deductions (PF/Tax)", styles['Normal']),
            Paragraph(f"{deduct_val:,.2f}", styles['Normal'])
        ],
        # Row 2
        [
            Paragraph("Attendance Salary (Pro-rated)", styles['Normal']),
            Paragraph(f"{att_sal_val:,.2f}", styles['Normal']),
            Paragraph("Loss of Pay (Absences)", styles['Normal']),
            Paragraph("0.00", styles['Normal'])
        ],
        # Row 3
        [
            Paragraph(f"Overtime Pay ({ot_hrs} hrs @ ₹{ot_rate:,.2f})", styles['Normal']),
            Paragraph(f"{ot_pay_val:,.2f}", styles['Normal']),
            Paragraph("-", styles['Normal']),
            Paragraph("-", styles['Normal'])
        ],
        # Row 4
        [
            Paragraph("Special Allowances (DA/HRA/Other)", styles['Normal']),
            Paragraph(f"{allow_val:,.2f}", styles['Normal']),
            Paragraph("-", styles['Normal']),
            Paragraph("-", styles['Normal'])
        ],
        # Gross vs Deductions Totals
        [
            Paragraph("<b>Gross Earnings</b>", styles['Normal']),
            Paragraph(f"<b>₹ {gross_val:,.2f}</b>", styles['Normal']),
            Paragraph("<b>Total Deductions</b>", styles['Normal']),
            Paragraph(f"<b>₹ {deduct_val:,.2f}</b>", styles['Normal'])
        ]
    ]

    breakdown_table = Table(salary_breakdown, colWidths=[175, 85, 170, 85])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 15))

    # Net Salary Highlight Box
    net_box = [
        [
            Paragraph("<b>NET PAYABLE SALARY:</b>", ParagraphStyle('NetLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=aiet_navy)),
            Paragraph(f"<b>{format_currency(net_val)}</b>", ParagraphStyle('NetVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=2, textColor=colors.HexColor("#15803d")))
        ]
    ]
    net_table = Table(net_box, colWidths=[250, 265])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#10b981")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 40))

    # Signatures Table
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Prepared By (Accounts Staff)</b>", styles['Normal']),
            Paragraph("____________________________<br/><b>Principal / Director (AIET)</b>", ParagraphStyle('Ctr', parent=styles['Normal'], alignment=1)),
            Paragraph("____________________________<br/><b>Employee Signature</b>", ParagraphStyle('Rt', parent=styles['Normal'], alignment=2))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[170, 175, 170])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 20))

    # Footer note
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        alignment=1,
        textColor=colors.HexColor("#94a3b8")
    )
    story.append(Paragraph("This is a computer-generated salary slip from AIET Employee Attendance &amp; Salary Processing System.", footer_style))

    doc.build(story)
    return True, output_path
