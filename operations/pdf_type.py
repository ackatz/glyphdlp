import base64
import re
import pdfplumber
from io import BytesIO
from app.detections import regex
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def scan(input) -> dict:
    """
    Scan a PDF document for sensitive information.
    :param input: The PDF document in bytes.
    :return: The results of the scan.
    """

    with pdfplumber.open(BytesIO(input)) as pdf:
        text_chunks = [page.extract_text() or "" for page in pdf.pages]
        text = " ".join(
            text_chunk.strip().replace("\n", " ") for text_chunk in text_chunks
        )

    results = {}

    for name, pattern in regex.patterns.items():
        matches = re.findall(pattern, text)
        # Strip each match to remove leading/trailing spaces
        matches = [match.strip() for match in matches]
        if matches:
            if name not in results:
                results[name] = []
            results[name].extend(matches)

    return results


def redact(input) -> str:
    """
    Redact sensitive information in a PDF document.
    :param input: The PDF document in bytes.
    :return: The redacted PDF document as a Base64-encoded string.
    """
    output_stream = BytesIO()
    c = canvas.Canvas(output_stream, pagesize=letter)

    with pdfplumber.open(BytesIO(input)) as pdf:
        for page in pdf.pages:
            text_content = page.extract_text() or ""

            # Redact the content
            for name, pattern in regex.patterns.items():
                text_content = re.sub(pattern, "[REDACTED]", text_content)

            y_position = 770  # Adjusted starting position from the top of the page
            for line in text_content.split("\n"):
                c.drawString(72, y_position, line)
                y_position -= 16  # Adjusted line height

            c.showPage()

    c.save()

    # Get the redacted PDF bytes and encode to Base64
    redacted_pdf_base64 = base64.b64encode(output_stream.getvalue()).decode("utf-8")
    return redacted_pdf_base64
