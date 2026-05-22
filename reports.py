"""
Namara Water Risk Intelligence Platform — PDF Report Generator
Generates property-level risk assessment reports using reportlab.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics import renderPDF
import io
import os
from datetime import datetime


NAVY = HexColor("#1A234D")
BLUE = HexColor("#2E75B6")
TEAL = HexColor("#009688")
GREEN = HexColor("#22c55e")
YELLOW = HexColor("#f59e0b")
ORANGE = HexColor("#f97316")
RED = HexColor("#ef4444")
LIGHT_GRAY = HexColor("#F5F5F5")
MEDIUM_GRAY = HexColor("#666666")
DARK_GRAY = HexColor("#333333")


def risk_color(level):
    return {"Low": GREEN, "Moderate": YELLOW, "High": ORANGE, "Critical": RED}.get(level, MEDIUM_GRAY)


def generate_report(score_data):
    """Generate a PDF risk assessment report. Returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Title2', parent=styles['Title'], fontSize=24, textColor=NAVY, spaceAfter=6))
    styles.add(ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=14, textColor=BLUE, spaceAfter=12))
    styles.add(ParagraphStyle('SectionHead', parent=styles['Heading2'], fontSize=16, textColor=NAVY, spaceBefore=18, spaceAfter=8))
    styles.add(ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=DARK_GRAY, leading=14))
    styles.add(ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=MEDIUM_GRAY))
    styles.add(ParagraphStyle('ScoreLabel', parent=styles['Normal'], fontSize=10, textColor=white, alignment=TA_CENTER))

    elements = []

    # ─── Header ───
    elements.append(Paragraph("NAMARA", ParagraphStyle('Logo', parent=styles['Title'], fontSize=28, textColor=NAVY, spaceAfter=2)))
    elements.append(Paragraph("Water Risk Intelligence Report", styles['Subtitle']))
    elements.append(Spacer(1, 4))

    # ─── Property Info ───
    zip_code = score_data.get("zip_code", "Unknown")
    state = score_data.get("state", "")
    scored_at = score_data.get("scored_at", datetime.utcnow().isoformat())
    ts = scored_at[:10] if scored_at else datetime.utcnow().strftime("%Y-%m-%d")

    info_data = [
        ["Zip Code", zip_code, "State", state],
        ["Latitude", str(round(score_data.get("latitude", 0), 4)), "Longitude", str(round(score_data.get("longitude", 0), 4))],
        ["Report Date", ts, "Confidence", score_data.get("confidence", "Moderate")],
    ]
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), NAVY),
        ('TEXTCOLOR', (2, 0), (2, -1), NAVY),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
        ('TEXTCOLOR', (3, 0), (3, -1), DARK_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    # ─── Composite Score ───
    composite = score_data.get("composite_score", 0)
    level = score_data.get("risk_level", "Unknown")
    color = risk_color(level)

    score_box = Table(
        [[Paragraph(f'<font size="36" color="white"><b>{composite}</b></font>', styles['ScoreLabel']),
          Paragraph(f'<font size="18" color="{NAVY}"><b>Composite Risk Score</b></font><br/>'
                    f'<font size="14" color="{color}">{level} Risk</font>', styles['Body'])]],
        colWidths=[1.5*inch, 5.5*inch]
    )
    score_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), color),
        ('BACKGROUND', (1, 0), (1, 0), LIGHT_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 16),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    elements.append(score_box)
    elements.append(Spacer(1, 16))

    # ─── Layer Breakdown ───
    elements.append(Paragraph("Risk Score Breakdown", styles['SectionHead']))

    layers = score_data.get("layers", {})
    layer_names = {
        "climate": "Climate & Freeze Risk",
        "water_quality": "Water Quality",
        "infrastructure": "Infrastructure Aging",
        "builder_quality": "Builder Quality",
        "regulatory": "Regulatory & Mandate"
    }

    breakdown_data = [["Layer", "Score", "Weight", "Contribution"]]
    for key, label in layer_names.items():
        layer = layers.get(key, {})
        s = layer.get("score", 0)
        w = f"{int(layer.get('weight', 0) * 100)}%"
        c = layer.get("weighted_contribution", 0)
        breakdown_data.append([label, str(s), w, str(c)])

    breakdown_data.append(["COMPOSITE", str(composite), "100%", str(composite)])

    bt = Table(breakdown_data, colWidths=[2.8*inch, 1.2*inch, 1.2*inch, 1.8*inch])
    bt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor("#E8F4F8")),
        ('TEXTCOLOR', (0, -1), (-1, -1), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(bt)
    elements.append(Spacer(1, 16))

    # ─── Climate Detail ───
    climate = layers.get("climate", {}).get("data", {})
    if climate and not climate.get("error"):
        elements.append(Paragraph("Climate & Freeze Risk Detail", styles['SectionHead']))
        cd = [
            ["Freeze Days (<32°F)", str(climate.get("freeze_days", 0))],
            ["Extreme Heat Days (>95°F)", str(climate.get("heat_days", 0))],
            ["Total Precipitation", f'{climate.get("total_precip_inches", 0)}"'],
            ["Max Daily Precipitation", f'{climate.get("max_daily_precip_inches", 0)}"'],
            ["Data Points", str(climate.get("data_points", 0))],
            ["Source", climate.get("source", "Open-Meteo")],
        ]
        ct = Table(cd, colWidths=[3.5*inch, 3.5*inch])
        ct.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), NAVY),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT_GRAY, white]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(ct)
        elements.append(Spacer(1, 12))

    # ─── Namara Gap ───
    elements.append(Paragraph("The Namara Advantage", styles['SectionHead']))
    elements.append(Paragraph(
        "This report is based on public data sources. With a Namara device installed, "
        "the following additional signals would be available — dramatically increasing "
        "scoring accuracy and enabling real-time risk management:",
        styles['Body']
    ))
    elements.append(Spacer(1, 8))

    gap = score_data.get("namara_gap", [])
    for item in gap:
        elements.append(Paragraph(f"• {item}", styles['Body']))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        '<font color="#009688"><b>With Namara: Risk score accuracy improves from 60-65% to 85-90%</b></font>',
        styles['Body']
    ))
    elements.append(Spacer(1, 24))

    # ─── Footer ───
    elements.append(Paragraph(
        f'<font size="8" color="#999999">Namara Water Technologies, Inc. — Confidential<br/>'
        f'Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")} | Report ID: {hash(str(score_data))}</font>',
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
