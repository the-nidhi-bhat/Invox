import { normalizeExtractionResponse, postJson } from './api.js'

/**
 * mockExtractor.js
 *
 * Deterministic extraction fixture when no API URL is configured.
 *
 * Contract:
 *   extractOrder(messageText: string) => Promise<ExtractionResult>
 *
 * API-configured builds use the existing /extract endpoint.
 *
 * ExtractionResult shape:
 * {
 *   source: 'mock' | 'bedrock',     // so the UI can label the source honestly
 *   customer: string,
 *   location: string,
 *   state?: string,                 // present in the canonical local fixture
 *   items: Array<{
 *     name: string,
 *     quantity: number,
 *     unitPrice: number,
 *   }>,
 *   statedGstRate: number,           // percentage as number, e.g. 5 means 5%
 * }
 */

// Simulated network latency so the local fixture is visible during development.
const MOCK_DELAY_MS = 900

/**
 * Use the demo fixture when no API base URL is configured.
 *
 * @param {string} message
 * @returns {Promise<ExtractionResult>}
 */
export async function extractOrder(message) {
  if (!message || !message.trim()) {
    throw new Error('Order message must not be empty.')
  }

  if (!import.meta.env.VITE_API_BASE_URL?.trim()) {
    return extractOrderMock(message)
  }

  const response = await postJson('/extract', { message }, 'Order extraction failed')
  return normalizeExtractionResponse(response)
}

/**
 * Deterministic demo extractor.
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
async function extractOrderMock(message) {
  await new Promise(resolve => setTimeout(resolve, MOCK_DELAY_MS))

  // Trigger error state for testing.
  if (message.toLowerCase().includes('fail')) {
    throw new Error(
      'Mock extraction failed. (Type a message without "fail" to see the success flow.)'
    )
  }

  // Return the canonical INVOX demo extraction.
  // Real extraction is handled by the configured API path above.
  return {
    source: 'mock',
    customer: 'Acme',
    location: 'Pune',
    state: 'Maharashtra',
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
