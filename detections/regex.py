patterns = {
    "ssn": r"(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}",  # Avoid non-valid SSNs
    "credit_card": r"(?:Credit\sCard\s#?|CC\s#?)?\b\d{4}-?\d{4}-?\d{4}-?\d{4}\b",
    "account_number": r"(?:bank\s+)?(?:account|acct|Account\sNumber)\s*#?\s*\b\d+\b",
    "routing_number": r"(?:routing|Routing\sNumber)[ \t]?#?[ \t]?\b\d{9}\b",
    "tax_id": r"(?:(?:TIN|Tax\sID\sNumber|taxpayer\s:)[ \t]?#?[ \t]?)?\b\d{2}-\d{7}\b",
    "email_address": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",  # Added word boundaries
    "date_of_birth": r"(?:(?:DOB|Date\sof\sBirth)\s?)?\b(?<!\w)\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",  # More strict day and month
    "medical_record_number": r"MRN[ \t]?#?[ \t]?\b\d{8,10}\b",
    "id_or_passport": r"(?:US\s)?Passport[ \t]?#?[ \t]?\b\d{7,10}\b|\b(?:(?:DL|[A-Z]{2}(?![\-]))|Drivers?\sLicense|Driver's?\sLicense|Driving\sLicense)\s*#?\s*[\d\-]{6,12}\b",
    "health_insurance": r"Health\sInsurance[ \t]?(?:#)?[ \t]?\b\d{3}-\d{2}-\d{4}\b",
    "medicare_number": r"Medicare(?:[ \t]|#)?[ \t]?\b\d{3}-\d{2}-\d{4}\b",
}
