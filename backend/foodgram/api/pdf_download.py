from io import BytesIO

from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def pdf_download(ingredients):
    file_list = []
    [
        file_list.append("{} - {} {}.".format(*ingredient))
        for ingredient in ingredients
    ]
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    pdfmetrics.registerFont(
        TTFont("Arial", "./recipes/fonts/arial.ttf")
    )
    p.setFont("Arial", 12)
    p.drawString(100, 750, "Список покупок:")
    y = 730
    for ingredient in file_list:
        p.drawString(100, y, ingredient)
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    response = FileResponse(
        buffer, as_attachment=True, filename="purchases.pdf"
    )
    return response
