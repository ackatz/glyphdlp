from app.detections import regex
import re


def scan(input) -> dict:
    """
    This function will be used to scan the text file
    :param input: The text file to scan
    :return: The results of the scan
    """

    results = {}

    for name, pattern in regex.patterns.items():
        matches = re.findall(pattern, input)
        if matches:
            if name not in results:
                results[name] = []
            results[name].extend(matches)

    return results


def redact(input_text) -> str:
    """
    This function will be used to redact sensitive information in the text.
    :param input_text: The text to scan and redact
    :return: The redacted text
    """

    redacted_text = input_text

    for name, pattern in regex.patterns.items():
        if re.search(pattern, redacted_text):
            redacted_text = re.sub(pattern, "[REDACTED]", redacted_text)

    return redacted_text
