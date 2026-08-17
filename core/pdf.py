"""PDF generation for /pricing/ quote downloads.

Uses ReportLab to render a clean, branded quote. No external template
files — everything is drawn programmatically so the output looks
consistent across runs.
"""
from io import BytesIO
from datetime import datetime, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)


# Brand colors
INDIGO = colors.HexColor('#6366F1')
TEAL   = colors.HexColor('#22D3EE')
INK    = colors.HexColor('#0B1020')
INK2   = colors.HexColor('#334155')
MUTED  = colors.HexColor('#64748B')
LINE   = colors.HexColor('#E2E8F0')
SUCCESS = colors.HexColor('#10B981')


def _fmt_money(usd, currency, rate):
    n = int(round(usd))
    if currency == 'BDT':
        return f"BDT {int(round(usd * float(rate))):,}"
    return f"USD {n:,}"


def _unit_price_display(unit_price_usd, unit, qty, currency, rate):
    if unit == 'flat':
        return _fmt_money(unit_price_usd, currency, rate)
    n = int(round(unit_price_usd))
    if currency == 'BDT':
        amt = int(round(unit_price_usd * float(rate)))
    else:
        amt = n
    label = {'page':'page','hour':'hr','module':'module','session':'session','month':'month'}.get(unit, unit)
    if unit == 'flat':
        return f"{_fmt_money(unit_price_usd, currency, rate)} flat"
    return f"{amt:,} / {label}"


def render_quote_pdf(lead) -> bytes:
    """Render a QuoteLead instance as a PDF and return the bytes."""

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title=f"Quote #{lead.id} — {lead.name}",
        author="Odoo & ERP Quote",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=styles['Heading1'], fontName='Helvetica-Bold',
                        fontSize=22, leading=26, textColor=INK, spaceAfter=4)
    h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontName='Helvetica-Bold',
                        fontSize=12, leading=16, textColor=INK, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle('body', parent=styles['BodyText'], fontName='Helvetica',
                          fontSize=10, leading=14, textColor=INK2)
    small = ParagraphStyle('small', parent=styles['BodyText'], fontName='Helvetica',
                           fontSize=8.5, leading=11, textColor=MUTED)
    label = ParagraphStyle('label', parent=styles['BodyText'], fontName='Helvetica-Bold',
                           fontSize=8, leading=10, textColor=MUTED)

    story = []

    # ----- Header band -----
    quote_number = f"#{lead.id:05d}" if lead.id else "DRAFT"
    header_data = [[
        Paragraph('<font color="#0B1020"><b>Odoo &amp; ERP Implementation</b></font>'
                  '<br/><font size="9" color="#64748B">'
                  'Functional · Technical · Deployment · Data Migration</font>', body),
        Paragraph(f'<para align="right"><font size="9" color="#64748B">QUOTE</font><br/>'
                  f'<font size="18" color="#0B1020"><b>{quote_number}</b></font><br/>'
                  f'<font size="9" color="#64748B">{lead.created_at.strftime("%b %d, %Y")}</font></para>', body),
    ]]
    header_tbl = Table(header_data, colWidths=[110*mm, 60*mm])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(header_tbl)
    story.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceBefore=0, spaceAfter=10))

    # ----- Two-column: customer / quote meta -----
    customer_html = (
        f'<font size="8" color="#64748B"><b>PREPARED FOR</b></font><br/>'
        f'<font size="12" color="#0B1020"><b>{lead.name}</b></font><br/>'
        f'<font size="10" color="#334155">{lead.email}'
        + (f'<br/>{lead.phone}' if lead.phone else '')
        + (f'<br/>{lead.company}' if lead.company else '')
        + '</font>'
    )
    valid_until = (lead.created_at + timedelta(days=14)).strftime('%b %d, %Y')
    meta_html = (
        f'<para align="right">'
        f'<font size="8" color="#64748B"><b>VALID UNTIL</b></font><br/>'
        f'<font size="11" color="#0B1020"><b>{valid_until}</b></font><br/><br/>'
        f'<font size="8" color="#64748B"><b>CURRENCY</b></font><br/>'
        f'<font size="11" color="#0B1020"><b>{lead.currency}</b></font>'
        f'</para>'
    )
    two_col = Table([[Paragraph(customer_html, body), Paragraph(meta_html, body)]],
                    colWidths=[110*mm, 60*mm])
    two_col.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(two_col)
    story.append(Spacer(1, 6*mm))

    # ----- Project title -----
    story.append(Paragraph(f'<font color="#6366F1"><b>ERP / Odoo Implementation Quote</b></font>', h2))
    story.append(Paragraph(
        'This quote covers the items selected in the online pricing calculator. '
        'Final scope, timeline, and price are confirmed after a 15-minute discovery call. '
        'All prices exclude applicable taxes.',
        body
    ))
    story.append(Spacer(1, 4*mm))

    # ----- Items table -----
    rows = [['#', 'Item', 'Unit', 'Qty', 'Unit price', 'Line total']]
    for i, item in enumerate(lead.items or [], start=1):
        rows.append([
            str(i),
            item.get('name', ''),
            item.get('unit', 'flat'),
            str(item.get('qty', 1) if item.get('unit') != 'flat' else '—'),
            _unit_price_display(
                float(item.get('unit_price_usd', 0)),
                item.get('unit', 'flat'),
                item.get('qty', 1),
                lead.currency,
                lead.usd_to_bdt,
            ),
            _fmt_money(float(item.get('line_total_usd', 0)), lead.currency, lead.usd_to_bdt),
        ])

    if len(rows) == 1:
        rows.append(['—', 'No items selected', '', '', '', ''])

    tbl = Table(rows, colWidths=[10*mm, 70*mm, 22*mm, 14*mm, 28*mm, 26*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), INDIGO),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 9),
        ('ALIGN',      (0,0), (-1,0), 'LEFT'),
        ('ALIGN',      (3,1), (5,-1), 'RIGHT'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',   (0,1), (-1,-1), 9.5),
        ('TEXTCOLOR',  (0,1), (-1,-1), INK),
        ('FONTNAME',   (5,1), (5,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('LINEBELOW',  (0,0), (-1,0), 0.5, INDIGO),
        ('LINEBELOW',  (0,-1), (-1,-1), 0.5, LINE),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 4*mm))

    # ----- Totals -----
    totals_data = [
        ['Subtotal', _fmt_money(float(lead.subtotal_usd), lead.currency, lead.usd_to_bdt)],
    ]
    if lead.discount_percent and float(lead.discount_usd) > 0:
        totals_data.append([
            f'Bundle discount ({lead.discount_percent}%)',
            f'- {_fmt_money(float(lead.discount_usd), lead.currency, lead.usd_to_bdt)}',
        ])
    totals_data.append(['TOTAL', _fmt_money(float(lead.total_usd), lead.currency, lead.usd_to_bdt)])

    totals = Table(totals_data, colWidths=[40*mm, 30*mm], hAlign='RIGHT')
    totals_style = [
        ('FONTNAME', (0,0), (-1,-2), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-2), 10),
        ('TEXTCOLOR', (0,0), (-1,-2), INK2),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        # TOTAL row
        ('LINEABOVE', (0,-1), (-1,-1), 0.8, INDIGO),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 13),
        ('TEXTCOLOR', (0,-1), (-1,-1), INK),
        ('TOPPADDING', (0,-1), (-1,-1), 8),
    ]
    if lead.discount_percent and float(lead.discount_usd) > 0:
        totals_style.append(('TEXTCOLOR', (1,1), (1,1), SUCCESS))
    totals.setStyle(TableStyle(totals_style))
    story.append(totals)
    story.append(Spacer(1, 8*mm))

    # ----- Next steps -----
    story.append(Paragraph('<font color="#6366F1"><b>Next steps</b></font>', h2))
    story.append(Paragraph(
        '1. Reply to this quote or click "Send this estimate →" on the calculator to schedule the 15-minute discovery call.<br/>'
        '2. We confirm scope, timeline, and milestones.<br/>'
        '3. You receive a fixed-price contract. Implementation begins on signed agreement.',
        body
    ))
    story.append(Spacer(1, 6*mm))

    # ----- Footer -----
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceBefore=0, spaceAfter=4))
    contact = (
        'This quote is valid for 14 days from the issue date. '
        'Final scope and pricing are confirmed after a 15-minute discovery call.'
    )
    story.append(Paragraph(
        f'<para align="center"><font size="8" color="#64748B">{contact}</font></para>',
        small
    ))

    doc.build(story)
    return buf.getvalue()
