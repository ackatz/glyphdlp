import csv
from io import StringIO
import re
from app.detections import regex
import base64


def scan(input) -> dict:
    """
    This function will be used to scan the CSV data
    :param input: The Base64encoded CSV data to scan
    :return: The results of the scan
    """

    results = {}

    reader = csv.reader(StringIO(input.decode("utf-8")), delimiter=",")
    for row in reader:
        for field in row:
            for name, pattern in regex.patterns.items():
                matches = re.findall(pattern, field)
                if matches:
                    if name not in results:
                        results[name] = []
                    results[name].extend(matches)

    return results


def redact(input) -> str:
    """
    This function will be used to redact sensitive information in the CSV.
    :param input: The CSV data to scan and redact
    :return: The redacted CSV
    """

    redacted_output = StringIO()
    writer = csv.writer(redacted_output, delimiter=",")

    reader = csv.reader(StringIO(input.decode("utf-8")), delimiter=",")
    for row in reader:
        redacted_row = []
        for field in row:
            redacted_field = field
            for name, pattern in regex.patterns.items():
                if re.search(pattern, redacted_field):
                    redacted_field = re.sub(pattern, "[REDACTED]", redacted_field)
            redacted_row.append(redacted_field)
        writer.writerow(redacted_row)

    # Get the redacted PDF bytes and encode to Base64
    redacted_csv_base64 = base64.b64encode(
        redacted_output.getvalue().encode("utf-8")
    ).decode("utf-8")

    return redacted_csv_base64
