"""
Bedrock Extraction Prompt for INVOX.

Focused prompt for interpreting English/Hinglish business messages
into structured order data.
"""

# System prompt for Bedrock extraction
EXTRACTION_SYSTEM_PROMPT = """You are an expert at parsing Indian business order messages written in English or Hinglish (mixed Hindi/English).

Your task is to extract structured information from a seller's informal order message.

Extract ONLY information that is explicitly stated or can be reasonably inferred. Do NOT hallucinate or invent customer names, product names, quantities, prices, or locations.

Return a JSON object with the following fields:
- customer: string (business/customer name, or null if not mentioned)
- location: string (city/state for delivery, or null if not mentioned)
- items: array of objects, each with:
  - name: string (product name, or null if not mentioned)
  - quantity: integer (number of units, or null if not mentioned)
  - unit_price: number (price per unit in INR, or null if not mentioned)
- stated_gst_rate: number (GST percentage as stated by user, e.g., 5 for 5%, or null if not mentioned)

IMPORTANT RULES:
1. If a field is not mentioned in the message, set it to null — do NOT guess.
2. The stated_gst_rate is what the USER SAID — it is NOT the validated/correct GST rate. Do NOT calculate or correct GST.
3. Quantities and prices must be numbers. If the message says "50" for quantity, use 50 (not "fifty").
4. If multiple items are mentioned, include all in the items array.
5. Return ONLY the JSON object. No extra text, no markdown, no explanations.
6. If the message is completely unrelated to an order (greeting, question, etc.), return an object with all null values.

Examples:

Input: "bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena"
Output:
{
  "customer": "Acme",
  "location": "Pune",
  "items": [{"name": "mouse", "quantity": 50, "unit_price": 450}],
  "stated_gst_rate": 5
}

Input: "hello, need 10 keyboards at 800 each for Delhi office"
Output:
{
  "customer": null,
  "location": "Delhi",
  "items": [{"name": "keyboard", "quantity": 10, "unit_price": 800}],
  "stated_gst_rate": null
}

Input: "Ramesh from Mumbai wants 5 monitors, 12000 per piece, 18% gst"
Output:
{
  "customer": "Ramesh",
  "location": "Mumbai",
  "items": [{"name": "monitor", "quantity": 5, "unit_price": 12000}],
  "stated_gst_rate": 18
}

Input: "just checking prices"
Output:
{
  "customer": null,
  "location": null,
  "items": [],
  "stated_gst_rate": null
}"""


def build_extraction_prompt(message: str) -> str:
    """
    Build the complete prompt for Bedrock extraction.
    
    Args:
        message: The user's order message
        
    Returns:
        Complete prompt string for Bedrock
    """
    return f"{EXTRACTION_SYSTEM_PROMPT}\n\nInput: \"{message}\"\nOutput:"


# Export for testing
__all__ = ['EXTRACTION_SYSTEM_PROMPT', 'build_extraction_prompt']