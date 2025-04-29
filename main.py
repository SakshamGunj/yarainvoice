# main.py (Final Version - with /view-pdf endpoint)

import os
import datetime
from io import BytesIO
from typing import List, Optional, Dict, Any

# --- Pydantic Models for Request Data Validation ---
from pydantic import BaseModel, Field

# --- FastAPI Imports ---
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware # Import CORS middleware

# --- ReportLab Imports (Keep as before) ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors

# --- Constants, Colors, Image Paths (Keep as before) ---
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 0.75 * inch
RIGHT_MARGIN = 0.75 * inch
TOP_MARGIN = 0.5 * inch
BOTTOM_MARGIN = 0.5 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
HEADER_RED = colors.Color(0.8, 0.2, 0.2)
TABLE_HEADER_RED = colors.Color(0.75, 0.25, 0.25)
DARK_RED = colors.Color(0.6, 0, 0)
GREY_TEXT = colors.gray
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
QRCODE_PATH = os.path.join(BASE_DIR, "qr-code.png")
SIGNATURE_PATH = os.path.join(BASE_DIR, "signature.png")

# --- ReportLab Helper Function (Keep as before) ---
def draw_logo(c, path, x, y, width, height):
    # (Code is identical to previous version)
    if os.path.exists(path):
        try:
            img = Image(path, width=width, height=height)
            img.drawOn(c, x, y)
        except Exception as e:
            print(f"Warning: Could not draw image {path}. Error: {e}")
            c.setFont("Helvetica", 8); c.setFillColor(colors.red)
            c.drawCentredString(x + width / 2, y + height / 2, f"Image Error: {os.path.basename(path)}")
            c.setFillColor(colors.black)
    else:
        print(f"Warning: Image file not found at {path}")
        c.setFont("Helvetica", 8); c.setFillColor(colors.darkgrey)
        c.drawCentredString(x + width / 2, y + height / 2, f"[{os.path.basename(path)} not found]")
        c.setFillColor(colors.black)

# --- PDF Generation Function (Keep as before) ---
def create_invoice_pdf(invoice_data: Dict[str, Any]) -> BytesIO:
    """
    Generates the invoice PDF based on the provided data dictionary.
    (Code is identical to the previous final version)
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    # --- Custom Styles (Keep as before) ---
    style_normal = styles['Normal']; style_normal.fontSize = 9; style_normal.leading = 11
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold')
    style_h1 = ParagraphStyle(name='H1', parent=style_bold, fontSize=22, alignment=TA_RIGHT)
    style_h2 = ParagraphStyle(name='H2', parent=style_bold, fontSize=10)
    style_right = ParagraphStyle(name='Right', parent=style_normal, alignment=TA_RIGHT)
    style_right_bold = ParagraphStyle(name='RightBold', parent=style_bold, alignment=TA_RIGHT)
    style_center = ParagraphStyle(name='Center', parent=style_normal, alignment=TA_CENTER)
    style_footer = ParagraphStyle(name='Footer', parent=style_normal, fontSize=8, alignment=TA_LEFT)
    style_grey = ParagraphStyle(name='Grey', parent=style_normal, textColor=GREY_TEXT)
    style_table_header = ParagraphStyle(name='TableHeader', parent=style_bold, textColor=colors.white, alignment=TA_CENTER, fontSize=9)
    style_table_cell = ParagraphStyle(name='TableCell', parent=style_normal, alignment=TA_LEFT, fontSize=9, leading=12)
    style_table_cell_center = ParagraphStyle(name='TableCellCenter', parent=style_table_cell, alignment=TA_CENTER)
    style_table_cell_right = ParagraphStyle(name='TableCellRight', parent=style_table_cell, alignment=TA_RIGHT)
    style_upi = ParagraphStyle(name='UPI', parent=style_bold, fontSize=9, alignment=TA_RIGHT)
    style_bank_label = ParagraphStyle(name='BankLabel', parent=style_normal, fontName='Helvetica-Bold')
    style_bank_value = ParagraphStyle(name='BankValue', parent=style_normal, leftIndent=0.8*inch)
    # --- Get data from dictionary ---
    inv_no = invoice_data.get('invoice_no', 'N/A')
    inv_date_str = invoice_data.get('invoice_date', datetime.date.today().strftime('%d.%m.%y'))
    due_date_str = invoice_data.get('due_date', 'N/A')
    client_name = invoice_data.get('client_name', '')
    client_phone = invoice_data.get('client_phone', '')
    client_email = invoice_data.get('client_email', '')
    client_address_lines = invoice_data.get('client_address', '').split('\n') if invoice_data.get('client_address') else []
    items = invoice_data.get('items', [])
    discount_amount = invoice_data.get('discount', 0.0)
    advance_payment = invoice_data.get('advance_payment', 0.0)
    gst_rate = invoice_data.get('gst_rate', 5.0)
    # --- PDF Drawing Logic (Keep entire drawing logic from previous final version) ---
    y_pos = PAGE_HEIGHT - TOP_MARGIN
    # === Header Section ===
    header_y_start = y_pos - 0.4 * inch; logo_size = 1.5 * inch
    draw_logo(c, LOGO_PATH, LEFT_MARGIN, header_y_start - logo_size, logo_size, logo_size)
    y_pos_left = header_y_start - logo_size - (0.1 * inch + 0.2 * inch)
    right_column_start_x = PAGE_WIDTH / 2 + 0.5 * inch; right_column_width = PAGE_WIDTH - RIGHT_MARGIN - right_column_start_x
    c.setFont("Helvetica", 8); c.setFillColor(HEADER_RED)
    c.drawRightString(right_column_start_x + right_column_width, header_y_start + 0.1 * inch, f"INVOICE NO: {inv_no} | INVOICE DATE: {inv_date_str}")
    c.setFillColor(colors.black); y_pos_right = header_y_start
    p = Paragraph("INVOICE", style_h1); p.wrapOn(c, right_column_width, 0.5*inch); p.drawOn(c, right_column_start_x, y_pos_right - 0.4 * inch)
    y_pos_right -= (0.4 * inch + p.height + 0.15 * inch)
    line_height_inv = 0.20 * inch; c.setFont("Helvetica", 9)
    c.drawRightString(right_column_start_x + right_column_width, y_pos_right, f"#{inv_no}"); c.drawString(right_column_start_x, y_pos_right, "Invoice No:")
    y_pos_right -= line_height_inv
    c.drawRightString(right_column_start_x + right_column_width, y_pos_right, due_date_str); c.drawString(right_column_start_x, y_pos_right, "Due Date:")
    y_pos_right -= line_height_inv
    c.drawRightString(right_column_start_x + right_column_width, y_pos_right, inv_date_str); c.drawString(right_column_start_x, y_pos_right, "Invoice Date:")
    y_pos_right -= (line_height_inv + 0.1*inch)
    upi_text = "UPI ID - TOURISM.NORTHSIKKIM@CNRB"
    p_upi = Paragraph(upi_text, style_upi); p_upi.wrapOn(c, right_column_width, 0.2*inch); p_upi.drawOn(c, right_column_start_x, y_pos_right)
    y_pos_right -= (p_upi.height + 0.1*inch)
    qr_size = 1.6 * inch; qr_x = right_column_start_x + (right_column_width - qr_size) / 2; qr_y = y_pos_right - qr_size
    draw_logo(c, QRCODE_PATH, qr_x, qr_y, qr_size, qr_size)
    pay_here_x = qr_x - 0.2 * inch
    c.saveState(); c.setFont("Helvetica-Bold", 10); c.setFillColor(HEADER_RED); c.translate(pay_here_x, qr_y + qr_size / 2); c.rotate(90); c.drawCentredString(0, 0, "PAY HERE"); c.restoreState()
    y_pos_right -= (qr_size + 0.2*inch)
    # === Static Company Info ===
    comp_x = LEFT_MARGIN; comp_width = 3 * inch
    p = Paragraph("Yara Escape Tours & Trek", style_h2); p.wrapOn(c, comp_width, 0.5*inch); p.drawOn(c, comp_x, y_pos_left); y_pos_left -= (p.height + 0.1*inch)
    p = Paragraph("Specialist in: Sikkim, Darjelling, Northeast", style_normal); p.wrapOn(c, comp_width, 0.2*inch); p.drawOn(c, comp_x, y_pos_left); y_pos_left -= (p.height + 0.2*inch)
    # === Dynamic Invoice To ===
    p = Paragraph("<u>INVOICE TO:</u>", ParagraphStyle(name='InvoiceTo', parent=style_bold, textColor=HEADER_RED)); p.wrapOn(c, comp_width, 0.2*inch); p.drawOn(c, comp_x, y_pos_left); y_pos_left -= (p.height + 0.1*inch)
    cust_info_dynamic = [(client_name, style_bold), (f"Phone: {client_phone}" if client_phone else "", style_normal), (f"Email: {client_email}" if client_email else "", style_normal)]
    if client_address_lines: cust_info_dynamic.append(("Address:", style_normal)); cust_info_dynamic.extend([(line, style_normal) for line in client_address_lines])
    for text, style in cust_info_dynamic:
        if text:
            is_address_line = any(line in text for line in client_address_lines if line) and "Address:" not in text
            p_style = ParagraphStyle(name=f'AddrDyn_{text[:10].replace(" ","_")}', parent=style, leftIndent=(0.3*inch if is_address_line else 0))
            p = Paragraph(text, p_style); p.wrapOn(c, comp_width + 1 * inch, 0.6 * inch)
            p.drawOn(c, comp_x, y_pos_left); y_pos_left -= p.height
    # === Dynamic Invoice Table ===
    table_start_y = min(y_pos_left, y_pos_right) - 0.3*inch; y_pos = table_start_y
    table_data = [[Paragraph('DESCRIPTION', style_table_header), Paragraph('PRICE', style_table_header), Paragraph('QTY', style_table_header), Paragraph('SUBTOTAL', style_table_header)]]
    sub_total_amount = 0.0
    for item in items:
        try:
            price = float(item.get('price', 0.0)); qty = float(item.get('qty', 0.0)); item_subtotal = price * qty; sub_total_amount += item_subtotal
            price_str = f"{price:,.2f}" if price else ''; qty_str = str(qty); item_subtotal_str = f"{item_subtotal:,.2f}"
            table_data.append([Paragraph(item.get('desc', ''), style_table_cell), Paragraph(price_str, style_table_cell_center), Paragraph(qty_str, style_table_cell_center), Paragraph(item_subtotal_str, style_table_cell_right)])
        except (ValueError, TypeError): table_data.append([Paragraph(f"{item.get('desc', '')} (Invalid Price/Qty)", style_table_cell), '', '', ''])
    col_widths = [CONTENT_WIDTH * 0.50, CONTENT_WIDTH * 0.15, CONTENT_WIDTH * 0.15, CONTENT_WIDTH * 0.20]
    table = Table(table_data, colWidths=col_widths)
    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_RED), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 9), ('BOTTOMPADDING', (0, 0), (-1, 0), 6), ('TOPPADDING', (0, 0), (-1, 0), 6), ('ALIGN', (1, 1), (1, -1), 'CENTER'), ('ALIGN', (2, 1), (2, -1), 'CENTER'), ('ALIGN', (3, 1), (3, -1), 'RIGHT'), ('VALIGN', (0, 1), (-1, -1), 'TOP'), ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), ('FONTSIZE', (0, 1), (-1, -1), 9), ('BOTTOMPADDING', (0, 1), (-1, -1), 4), ('TOPPADDING', (0, 1), (-1, -1), 4), ('LEFTPADDING', (0, 1), (0, -1), 5), ('RIGHTPADDING', (-1, 1), (-1, -1), 5), ('LINEBELOW', (0, 0), (-1, 0), 1, TABLE_HEADER_RED), *[('LINEBELOW', (0, i), (-1, i), 0.5, colors.lightgrey) for i in range(1, len(table_data) - 1)], ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)])
    table.setStyle(table_style); actual_width, table_height = table.wrapOn(c, CONTENT_WIDTH, PAGE_HEIGHT); table.drawOn(c, LEFT_MARGIN, y_pos - table_height); table_bottom_y = y_pos - table_height; y_pos = table_bottom_y - 0.2*inch
    # === Dynamic Summary ===
    gst_total = (sub_total_amount - discount_amount) * (gst_rate / 100.0); grand_total = sub_total_amount - discount_amount + gst_total; total_due = grand_total - advance_payment
    summary_x = PAGE_WIDTH / 2 + 0.5*inch; summary_width = PAGE_WIDTH - RIGHT_MARGIN - summary_x; summary_y_start = table_bottom_y - 0.3 * inch
    summary_items = [("Sub-total :", f"{sub_total_amount:,.2f}"), ("Discount :", f"- {discount_amount:,.2f}"), (f"GST ({gst_rate}%) :", f"+ {gst_total:,.2f}"), ("Advance Payment :", f"- {advance_payment:,.2f}")]
    c.setFont("Helvetica", 10); summary_line_height = 0.25 * inch; current_summary_y = summary_y_start
    for label, value in summary_items: c.drawString(summary_x, current_summary_y, label); c.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, current_summary_y, value); current_summary_y -= summary_line_height
    total_due_y = current_summary_y; total_due_height = 0.4 * inch; c.setFillColor(DARK_RED); c.roundRect(summary_x - 0.1*inch, total_due_y - total_due_height + 0.05*inch, summary_width + 0.1*inch, total_due_height, radius=3, stroke=0, fill=1); c.setFont("Helvetica-Bold", 12); c.setFillColor(colors.white); c.drawString(summary_x + 0.1*inch, total_due_y - 0.25*inch, "Total Due :"); c.drawRightString(PAGE_WIDTH - RIGHT_MARGIN - 0.1*inch, total_due_y - 0.25*inch, f"{total_due:,.2f}"); c.setFillColor(colors.black); summary_bottom_y = total_due_y - total_due_height
    # === Static Terms ===
    terms_x = LEFT_MARGIN; terms_width = CONTENT_WIDTH * 0.55; terms_y = table_bottom_y - 0.3 * inch
    p = Paragraph("<b>TERMS AND CONDITIONS</b>", style_h2); p.wrapOn(c, terms_width, 0.2*inch); p.drawOn(c, terms_x, terms_y); terms_y -= (p.height + 0.15 * inch)
    terms_text = "Please Pay 40% Advance payment within 12 Hours of receiving this invoice\nFor Instant Booking Confirmation.<br/><font color='green'>✔</font> 100% REFUND ON CANCELLATION<br/>(15 Days)"
    p = Paragraph(terms_text, style_normal); p.wrapOn(c, terms_width, 1.0*inch); p.drawOn(c, terms_x, terms_y - p.height); terms_y -= (p.height + 0.3*inch)
    # === Static Thank You & Contact ===
    contact_y = terms_y
    p = Paragraph("<b>THANK YOU FOR CHOOSING US!</b>", style_h2); p.wrapOn(c, terms_width, 0.2*inch); p.drawOn(c, terms_x, contact_y); contact_y -= (p.height + 0.2 * inch)
    contact_info_static = [("Phone:", "+91 8250133947 / +91 9883023091"), ("Website:", "www.yaraservice.com"), ("Address:", "Gangtok, Lumsey Sikkim - 737101")]
    for label, value in contact_info_static:
        line_start_y = contact_y; p_label = Paragraph(f"<b>{label}</b>", style_normal); label_width = 0.6 * inch; p_label.wrapOn(c, label_width, 0.5*inch); p_label.drawOn(c, terms_x, line_start_y - p_label.height)
        value_style = ParagraphStyle(name=f'ValueStatic_{label[:3]}', parent=style_normal, leftIndent=label_width + 0.1*inch); p_value = Paragraph(value, value_style); p_value.wrapOn(c, terms_width - (label_width + 0.1*inch), 0.6*inch); p_value.drawOn(c, terms_x , line_start_y - p_value.height); contact_y -= (max(p_label.height, p_value.height) + 0.1*inch)
    # === Bank Details ===
    bank_details_y = contact_y - 0.3*inch
    p_bank_heading = Paragraph("<b>Bank Details:</b>", style_h2); p_bank_heading.wrapOn(c, terms_width, 0.2*inch); p_bank_heading.drawOn(c, terms_x, bank_details_y); bank_details_y -= (p_bank_heading.height + 0.1 * inch)
    bank_info = [("Acc no:", "120033745630"), ("IFSC code:", "CNRB0003731"), ("Bank:", "Canara Bank"), ("Account Holder:", "Yara services")]
    for label, value in bank_info:
        p_label = Paragraph(f"<b>{label}</b>", style_normal); label_width = 1.0 * inch; p_label.wrapOn(c, label_width, 0.5*inch); p_label.drawOn(c, terms_x, bank_details_y)
        value_style = ParagraphStyle(name=f'BankValue_{label[:3]}', parent=style_normal, leftIndent=label_width + 0.05*inch); p_value = Paragraph(value, value_style); p_value.wrapOn(c, terms_width - (label_width + 0.05*inch), 0.6*inch); p_value.drawOn(c, terms_x , bank_details_y)
        bank_details_y -= (max(p_label.height, p_value.height) + 0.05*inch)
    bank_details_bottom_y = bank_details_y
    # === Static Signature ===
    sig_base_y = min(summary_bottom_y, bank_details_bottom_y) - 0.2*inch; sig_width = 1.5 * inch; sig_x = PAGE_WIDTH - RIGHT_MARGIN - sig_width; sig_img_width = 1.0 * inch; sig_img_height = 0.5 * inch
    draw_logo(c, SIGNATURE_PATH, sig_x + (sig_width - sig_img_width) / 2 , sig_base_y, sig_img_width, sig_img_height); sig_text_y = sig_base_y - 0.1*inch
    p = Paragraph("NORTH SIKKIM TOURS &<br/>TRAVELS PVT .LTD", style_center); p.wrapOn(c, sig_width, 0.4*inch); p.drawOn(c, sig_x, sig_text_y - p.height)
    # === Dynamic Footer ===
    footer_y = BOTTOM_MARGIN; c.setFillColor(HEADER_RED); c.line(LEFT_MARGIN, footer_y + 0.25*inch, PAGE_WIDTH - RIGHT_MARGIN, footer_y + 0.25*inch); c.setFillColor(colors.black)
    p_footer_left = Paragraph(f"INVOICE NO: {inv_no} | INVOICE DATE: {inv_date_str}", style_footer); p_footer_left.wrapOn(c, CONTENT_WIDTH / 2, 0.2*inch); p_footer_left.drawOn(c, LEFT_MARGIN, footer_y)
    # --- Finalize PDF ---
    c.save()
    buffer.seek(0)
    return buffer

# --- Pydantic Models (Keep as before) ---
class InvoiceItem(BaseModel):
    desc: str
    price: float = 0.0
    qty: float = 0.0

class InvoiceRequestData(BaseModel):
    invoice_no: str = Field(..., example="INV-20240101-001")
    invoice_date: str = Field(..., example="01.01.24")
    due_date: Optional[str] = Field(None, example="15.01.24")
    client_name: str = Field(..., example="Sourav Saha")
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    client_address: Optional[str] = Field(None, example="North Balurchar, Shashan Kali Rd,\nEnglish Bazar, Malda\nWest Bengal - 732101")
    items: List[InvoiceItem] = []
    discount: float = 0.0
    advance_payment: float = Field(default=0.0, alias="advancePayment")
    gst_rate: float = Field(default=5.0, alias="gstRate")
    class Config:
        populate_by_name = True

# --- FastAPI Application Setup (Keep as before) ---
app = FastAPI(title="Invoice PDF Generator API")

# --- CORS Configuration (Keep as before) ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.post("/generate-pdf")
async def generate_invoice_api(data: InvoiceRequestData = Body(...)):
    """
    Generates PDF and returns it for direct download.
    """
    try:
        invoice_data_dict = data.model_dump(by_alias=True)
        pdf_buffer = create_invoice_pdf(invoice_data_dict)

        # ++ Use correct invoice number for filename ++
        inv_no_filename = "".join(c for c in data.invoice_no if c.isalnum() or c in ('-', '_')).rstrip()
        filename = f"invoice_{inv_no_filename or 'generated'}.pdf"

        headers = {
            # Use 'attachment' for download
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

    except Exception as e:
        print(f"Error generating PDF for download: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# ++ NEW ENDPOINT for viewing PDF ++
@app.post("/view-pdf")
async def view_invoice_api(data: InvoiceRequestData = Body(...)):
    """
    Generates PDF and returns it for viewing inline in the browser.
    """
    try:
        invoice_data_dict = data.model_dump(by_alias=True)
        pdf_buffer = create_invoice_pdf(invoice_data_dict)

        # ++ Use correct invoice number for filename (optional but good practice) ++
        inv_no_filename = "".join(c for c in data.invoice_no if c.isalnum() or c in ('-', '_')).rstrip()
        filename = f"invoice_{inv_no_filename or 'generated'}.pdf"

        headers = {
            # Use 'inline' for viewing
            'Content-Disposition': f'inline; filename="{filename}"'
        }
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

    except Exception as e:
        print(f"Error generating PDF for viewing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

# --- Run instructions (Keep as before) ---
# uvicorn main:app --reload --host 0.0.0.0 --port 8000