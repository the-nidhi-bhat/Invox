/**
 * mockExtractor.js
 *
 * Isolated mock extraction service.
 * M2 uses this in place of the real API call.
 *
 * Contract:
 *   extractOrder(messageText: string) => Promise<ExtractionResult>
 *
 * When the real backend (API Gateway → Python Lambda → Bedrock) is ready
 * in M3, this file will be replaced or the call in OrderComposer will be
 * switched to the real API client — the UI components need no changes.
 *
 * ExtractionResult shape:
 * {
 *   source: 'mock' | 'bedrock',     // so the UI can label the source honestly
 *   customer: string,
 *   location: string,
 *   items: Array<{
 *     name: string,
 *     quantity: number,
 *     unitPrice: number,
 *   }>,
 *   statedGstRate: number,           // percentage as number, e.g. 5 means 5%
 * }
 */

// Simulated network latency so the loading state is visible during development.
const MOCK_DELAY_MS = 900

/**
 * Deterministic mock extractor.
 * Returns the canonical INVOX demo extraction for any non-empty message.
 * A message containing "fail" triggers the error path for testing error UI.
 *
 * NOTE: The returned statedGstRate is what the user said, NOT the authoritative
 * rate. GST validation is the backend's job (M5). Never treat this value as
 * the correct rate for financial calculations.
 *
 * @param {string} message
 * @returns {Promise<ExtractionResult>}
 */
export async function extractOrder(message) {
  if (!message || !message.trim()) {
    throw new Error('Order message must not be empty.')
  }

  await new Promise(resolve => setTimeout(resolve, MOCK_DELAY_MS))

  // Trigger error state for testing.
  if (message.toLowerCase().includes('fail')) {
    throw new Error(
      'Mock extraction failed. (Type a message without "fail" to see the success flow.)'
    )
  }

  // Return the canonical INVOX demo extraction.
  // In a real run this data comes from Bedrock via Lambda.
  return {
    source: 'mock',
    customer: 'Acme',
    location: 'Pune',
    items: [
      {
        name: 'Mouse',
        quantity: 50,
        unitPrice: 450,
      },
    ],
    statedGstRate: 5,
  }
}
