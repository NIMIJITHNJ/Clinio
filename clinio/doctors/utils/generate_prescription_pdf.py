from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_prescription_pdf(consultation):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header - Centered Hospital Info
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 50, "CareWell Multispeciality Hospital")

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 65, "Plot No. 24, Sector 12, New Ashok Nagar, Delhi - 110096")
    p.drawCentredString(width / 2, height - 78, "Phone: +91 123 456 7890 | Email: carewellmsh@gmail.com")

    # Divider
    p.setStrokeColor(colors.grey)
    p.line(40, height - 85, width - 40, height - 85)

    # Patient and Consultation Info
    patient = consultation.appointment.patient
    doctor = consultation.appointment.doctor
    appointment = consultation.appointment

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Patient Information:")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 125, f"Name: {patient.user.get_full_name()}")
    p.drawString(50, height - 140, f"Gender: {patient.gender}")
    p.drawString(50, height - 155, f"Date: {appointment.date} | Time: {appointment.time}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 185, "Doctor:")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 200, f"Dr. {doctor.name} ({doctor.specialization})")

    # Symptoms
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 235, "Symptoms / Complaints:")
    text = p.beginText(50, height - 250)
    text.setFont("Helvetica", 11)
    text.textLines(consultation.symptoms or "N/A")
    p.drawText(text)

    # Diagnosis
    offset = height - 250 - (15 * (consultation.symptoms.count('\n') + 1))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, offset, "Diagnosis:")
    text = p.beginText(50, offset - 15)
    text.setFont("Helvetica", 11)
    text.textLines(consultation.diagnosis or "N/A")
    p.drawText(text)

    # Prescription
    offset -= 15 * (consultation.diagnosis.count('\n') + 2)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, offset, "Prescription:")
    text = p.beginText(50, offset - 15)
    text.setFont("Helvetica", 11)
    text.textLines(consultation.prescription or "N/A")
    p.drawText(text)

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 40, "Note: Please follow the prescribed medication and contact the hospital in case of any issues.")
    p.drawString(50, 25, "Wishing you a speedy recovery. Thank you for visiting CareWell.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
