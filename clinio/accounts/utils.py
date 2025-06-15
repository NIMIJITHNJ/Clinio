from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO
from datetime import datetime
import random

def generate_invoice_pdf(appointment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "CareWell Multispeciality Hospital")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 65, "Plot No. 24, Sector 12, New Ashok Nagar,")
    p.drawString(50, height - 80, "Delhi - 110096, India")
    p.drawString(50, height - 95, "Phone: +91 123 456 7890 | Email: carewellmsh@gmail.com")

    # Invoice Info
    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, height - 50, "INVOICE")

    invoice_number = appointment.invoice_number or f"INV{appointment.id:05d}"
    p.setFont("Helvetica", 10)
    p.drawString(400, height - 65, f"Invoice No: {invoice_number}")
    p.drawString(400, height - 80, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

    # Patient & Appointment Details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 120, "BILL TO:")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 135, f"Name: {appointment.patient.user.get_full_name()}")
    p.drawString(50, height - 150, f"Doctor: {appointment.doctor.user.get_full_name()}")
    p.drawString(50, height - 165, f"Appointment Date: {appointment.date}")
    p.drawString(50, height - 180, f"Appointment Time: {appointment.time}")
    p.drawString(50, height - 195, f"Payment Method: {appointment.payment_method.title()}")

    # Bill Details Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 230, "Description")
    p.drawString(400, height - 230, "Amount (Rs.)")

    # Line under table header
    p.setStrokeColor(colors.grey)
    p.line(50, height - 235, 550, height - 235)

    # Itemized Bill
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 255, "Consultation Fee")
    p.drawString(400, height - 255, f"Amount Paid: Rs.{appointment.amount}.00")

    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 295, "Total")
    p.drawString(400, height - 295, f"Rs.{appointment.amount}.00")

    # Line under total
    p.line(50, height - 300, 550, height - 300)

    
    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 40, "Thank you for choosing CareWell. Wishing you good health!")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
