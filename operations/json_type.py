import json
import base64
from app.detections import regex
import re


def scan(input) -> dict:
    """
    This function will be used to scan the JSON content
    :param input: The Base64-encoded JSON data to scan
    :return: The results of the scan
    """

    try:
        parsed_json = json.loads(input)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")

    results = {}

    def recursive_scan(node):
        if isinstance(node, dict):
            for key, value in node.items():
                results.update(recursive_scan(value))
        elif isinstance(node, list):
            for item in node:
                results.update(recursive_scan(item))
        else:
            return scan_value(node)
        return results

    def scan_value(value):
        findings = {}
        if isinstance(value, str):
            for name, pattern in regex.patterns.items():
                matches = re.findall(pattern, value)
                if matches:
                    if name not in findings:
                        findings[name] = []
                    findings[name].extend(matches)
        return findings

    return recursive_scan(parsed_json)


def redact(input: str) -> dict:
    """
    This function will be used to redact sensitive information in the JSON content.
    :param input: The Base64-encoded JSON data to scan and redact
    :return: The redacted JSON data as a string
    """

    try:
        parsed_json = json.loads(input)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")

    def recursive_redact(node):
        if isinstance(node, dict):
            for key, value in node.items():
                node[key] = recursive_redact(value)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                node[index] = recursive_redact(item)
        else:
            return redact_value(node)
        return node

    def redact_value(value):
        if isinstance(value, str):
            for name, pattern in regex.patterns.items():
                if re.search(pattern, value):
                    value = re.sub(pattern, "[REDACTED]", value)
        return value

    redacted_json = recursive_redact(parsed_json)

    return redacted_json
