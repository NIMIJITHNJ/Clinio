from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_referral_pdf(consultation, type="lab"):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    patient = consultation.appointment.patient
    doctor = consultation.appointment.doctor

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 50, "CareWell Multispeciality Hospital")

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 65, "Plot No. 24, Sector 12, New Ashok Nagar, Delhi - 110096")
    p.drawCentredString(width / 2, height - 80, "Phone: +91 123 456 7890 | Email: carewellmsh@gmail.com")

    # Title
    referral_title = "Lab Referral" if type == "lab" else "X-Ray / Scan Referral"
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 120, referral_title)

    # Info
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 160, f"Patient Name: {patient.user.get_full_name()}")
    p.drawString(50, height - 175, f"Gender: {patient.gender}")
    p.drawString(50, height - 190, f"Doctor: Dr. {doctor.name} ({doctor.specialization})")
    p.drawString(50, height - 205, f"Date: {consultation.appointment.date.strftime('%d-%m-%Y')}")

    # Diagnosis
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 235, "Diagnosis / Reason for Referral:")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 250, consultation.diagnosis or "N/A")

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 40, "This is a system-generated referral. Please carry it to the lab/x-ray center.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
