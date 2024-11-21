from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import calendar
from datetime import datetime
from io import BytesIO

def generate_dtr_pdf(buffer, user_full_name, period):
    # Create document with landscape orientation
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='DTRTitle',
        fontName='Times-Roman',  # Using built-in Times-Roman font
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=0.2*cm,
        spaceBefore=0.2*cm,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='DTRNormal',
        fontName='Times-Roman',  # Using built-in Times-Roman font
        fontSize=10,
        alignment=TA_LEFT,
        leading=12
    ))

    styles.add(ParagraphStyle(
        name='DTRCenter',
        fontName='Times-Roman',  # Using built-in Times-Roman font
        fontSize=10,
        alignment=TA_CENTER,
        leading=12
    ))

    # Content elements
    elements = []

    # Title
    title = Paragraph("Civil Service Form No. 48", styles['DTRNormal'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*cm))
    
    subtitle = Paragraph("DAILY TIME RECORD", styles['DTRTitle'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2*cm))

    # Header info with underlines
    header_data = [
        [Paragraph("Name:", styles['DTRNormal']), 
         Paragraph(f"<u>{user_full_name}</u>", styles['DTRNormal']), 
         "", "", ""],
        [Paragraph("For the month of:", styles['DTRNormal']), 
         Paragraph(f"<u>{period}</u>", styles['DTRNormal']),
         "", 
         Paragraph("Official hours for arrival", styles['DTRNormal']),
         Paragraph("Regular days: ________________", styles['DTRNormal'])],
        ["", "", "",
         Paragraph("and departure:", styles['DTRNormal']),
         Paragraph("Saturdays: ________________", styles['DTRNormal'])]
    ]
    
    header_table = Table(header_data, colWidths=[2.5*cm, 7*cm, 2*cm, 4*cm, 6*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Using built-in Times-Roman font
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('SPAN', (1, 0), (4, 0)),  # Span name across columns
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))

    # Create main table headers
    table_headers = [
        ['DAY',
         Paragraph('A.M.<br/>ARRIVAL', styles['DTRCenter']),
         Paragraph('A.M.<br/>DEPARTURE', styles['DTRCenter']),
         Paragraph('P.M.<br/>ARRIVAL', styles['DTRCenter']),
         Paragraph('P.M.<br/>DEPARTURE', styles['DTRCenter']),
         Paragraph('UNDERTIME<br/>Hours Minutes', styles['DTRCenter'])
        ]
    ]
    
    # Table data for days
    for i in range(1, 32):
        table_data = [str(i), '', '', '', '', '']
        table_headers.append(table_data)

    # Create main table
    main_table = Table(
        table_headers,
        colWidths=[1.5*cm, 4*cm, 4*cm, 4*cm, 4*cm, 4*cm],
        rowHeights=[0.8*cm] + [0.6*cm] * 31
    )

    # Table style
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Using built-in Times-Roman font
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
    ])
    main_table.setStyle(table_style)
    elements.append(main_table)
    elements.append(Spacer(1, 0.5*cm))

    # Total undertime
    total_data = [
        ['', '', '', '', Paragraph('TOTAL', styles['DTRNormal']), '_____________'],
    ]
    total_table = Table(total_data, colWidths=[1.5*cm, 4*cm, 4*cm, 4*cm, 4*cm, 4*cm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (-2, -1), (-2, -1), 'RIGHT'),
        ('ALIGN', (-1, -1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Using built-in Times-Roman font
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 1*cm))

    # Certification
    cert_text = "I CERTIFY on my honor that the above is a true and correct report of the hours of work performed, record of which was made daily at the time of arrival and departure from office."
    cert = Paragraph(cert_text, ParagraphStyle(
        'Certification',
        parent=styles['DTRNormal'],
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=20,
    ))
    elements.append(cert)
    elements.append(Spacer(1, 1*cm))

    # Signature lines
    sig_data = [
        ['', '', Paragraph('Verified as to the prescribed office hours:', styles['DTRCenter'])],
        ['_' * 30, '', '_' * 30],
        [Paragraph('Signature', styles['DTRCenter']), '', 
         Paragraph('In Charge', styles['DTRCenter'])]
    ]
    sig_table = Table(sig_data, colWidths=[7*cm, 3*cm, 7*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Using built-in Times-Roman font
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)

    # Build PDF
    doc.build(elements)

# Example usage
if __name__ == "__main__":
    buffer = BytesIO()
    generate_dtr_pdf(
        buffer,
        "JUAN DELA CRUZ",
        "January 1-31, 2024"
    )
    with open("dtr_form.pdf", "wb") as f:
        f.write(buffer.getvalue())
