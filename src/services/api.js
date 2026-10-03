const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/+$/, '')

export function hasConfiguredApi() {
  return Boolean(API_BASE_URL)
}

function apiUrl(path) {
  return `${API_BASE_URL ?? ''}${path}`
}

function requireObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`The ${label} response is incomplete. Please try again.`)
  }
  return value
}

function requireArray(value, label, allowEmpty = false) {
  if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) {
    throw new Error(`The ${label} response is invalid. Please try again.`)
  }
  return value
}

function requireString(record, key, label) {
  const value = record[key]
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`The ${label} response is missing ${key}. Please try again.`)
  }
  return value
}

function requireNumber(record, key, label) {
  const value = record[key]
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`The ${label} response contains an invalid ${key}. Please try again.`)
  }
  return value
}

function requireBoolean(record, key, label) {
  const value = record[key]
  if (typeof value !== 'boolean') {
    throw new Error(`The ${label} response contains an invalid ${key}. Please try again.`)
  }
  return value
}

function optionalNumber(record, key, label) {
  if (record[key] == null) return null
  return requireNumber(record, key, label)
}

function optionalString(record, key, label) {
  if (record[key] == null) return null
  if (typeof record[key] !== 'string') {
    throw new Error(`The ${label} response contains an invalid ${key}. Please try again.`)
  }
  return record[key]
}

function normalizeCalculatedItem(item, label) {
  const record = requireObject(item, label)
  const taxType = requireString(record, 'taxType', label)
  if (taxType !== 'intra_state' && taxType !== 'inter_state') {
    throw new Error(`The ${label} response contains an unknown tax type. Please try again.`)
  }
  return {
    name: requireString(record, 'name', label),
    quantity: requireNumber(record, 'quantity', label),
    unit_price: requireNumber(record, 'unitPrice', label),
    subtotal: requireNumber(record, 'subtotal', label),
    gst_rate: requireNumber(record, 'gstRate', label),
    gst_amount: requireNumber(record, 'gstAmount', label),
    cgst_rate: requireNumber(record, 'cgstRate', label),
    cgst_amount: requireNumber(record, 'cgstAmount', label),
    sgst_rate: requireNumber(record, 'sgstRate', label),
    sgst_amount: requireNumber(record, 'sgstAmount', label),
    igst_rate: requireNumber(record, 'igstRate', label),
    igst_amount: requireNumber(record, 'igstAmount', label),
    stated_gst_rate: optionalNumber(record, 'statedGstRate', label),
    gst_mismatch: requireBoolean(record, 'gstMismatch', label),
    tax_type: taxType,
  }
}

export async function postJson(path, payload, fallbackMessage) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 35_000)
  let response

  try {
    response = await fetch(apiUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
  } catch (error) {
    if (error?.name === 'AbortError') {
      throw new Error('The request timed out. Please try again.')
    }
    throw new Error('Could not connect to the INVOX API. Check the API URL or connection and try again.')
  } finally {
    clearTimeout(timeoutId)
  }

  let data
  try {
    data = await response.json()
  } catch {
    throw new Error(
      response.ok
        ? 'The INVOX API returned an invalid response. Please try again.'
        : `${fallbackMessage} (HTTP ${response.status})`
    )
  }

  if (!response.ok) {
    throw new Error(typeof data?.error === 'string' ? data.error : `${fallbackMessage} (HTTP ${response.status})`)
  }

  return requireObject(data, fallbackMessage)
}

export function normalizeExtractionResponse(value) {
  const data = requireObject(value, 'order extraction')
  const items = requireArray(data.items, 'order extraction')
  return {
    source: requireString(data, 'source', 'order extraction'),
    customer: requireTextValue(data, 'customer', 'order extraction'),
    location: requireTextValue(data, 'location', 'order extraction'),
    items: items.map((item, index) => {
      const record = requireObject(item, `extracted item ${index + 1}`)
      return {
        name: requireString(record, 'name', `extracted item ${index + 1}`),
        quantity: requireNumber(record, 'quantity', `extracted item ${index + 1}`),
        unitPrice: requireNumber(record, 'unitPrice', `extracted item ${index + 1}`),
      }
    }),
    statedGstRate: optionalNumber(data, 'statedGstRate', 'order extraction'),
  }
}

export function normalizeGstResponse(value) {
  const data = requireObject(value, 'GST calculation')
  const taxType = requireString(data, 'taxType', 'GST calculation')
  if (taxType !== 'intra_state' && taxType !== 'inter_state') {
    throw new Error('The GST calculation response contains an unknown tax type. Please try again.')
  }

  return {
    items: requireArray(data.items, 'GST calculation').map((item, index) =>
      normalizeCalculatedItem(item, `GST item ${index + 1}`)
    ),
    total_subtotal: requireNumber(data, 'totalSubtotal', 'GST calculation'),
    total_gst_amount: requireNumber(data, 'totalGstAmount', 'GST calculation'),
    total_cgst: requireNumber(data, 'totalCgst', 'GST calculation'),
    total_sgst: requireNumber(data, 'totalSgst', 'GST calculation'),
    total_igst: requireNumber(data, 'totalIgst', 'GST calculation'),
    grand_total: requireNumber(data, 'grandTotal', 'GST calculation'),
    tax_type: taxType,
    seller_state: requireString(data, 'sellerState', 'GST calculation'),
    customer_state: optionalString(data, 'customerState', 'GST calculation'),
    stated_gst_rate: optionalNumber(data, 'statedGstRate', 'GST calculation'),
    determined_gst_rate: requireNumber(data, 'determinedGstRate', 'GST calculation'),
    gst_mismatch: requireBoolean(data, 'gstMismatch', 'GST calculation'),
    mismatch_details: requireArray(data.mismatchDetails, 'GST mismatch details', true),
  }
}

export function normalizeInvoiceResponse(value) {
  const data = requireObject(value, 'invoice')
  const seller = requireObject(data.seller, 'invoice seller')
  const customer = requireObject(data.customer, 'invoice customer')
  const taxType = requireString(data, 'taxType', 'invoice')
  if (taxType !== 'intra_state' && taxType !== 'inter_state') {
    throw new Error('The invoice response contains an unknown tax type. Please try again.')
  }

  return {
    invoice_number: requireString(data, 'invoiceNumber', 'invoice'),
    invoice_date: requireString(data, 'invoiceDate', 'invoice'),
    status: requireString(data, 'status', 'invoice'),
    seller,
    customer,
    items: requireArray(data.items, 'invoice').map((item, index) =>
      normalizeCalculatedItem(item, `Invoice item ${index + 1}`)
    ),
    subtotal: requireNumber(data, 'totalSubtotal', 'invoice'),
    total_gst_amount: requireNumber(data, 'totalGstAmount', 'invoice'),
    total_cgst: requireNumber(data, 'totalCgst', 'invoice'),
    total_sgst: requireNumber(data, 'totalSgst', 'invoice'),
    total_igst: requireNumber(data, 'totalIgst', 'invoice'),
    grand_total: requireNumber(data, 'grandTotal', 'invoice'),
    tax_type: taxType,
    seller_state: requireString(data, 'sellerState', 'invoice'),
    customer_state: optionalString(data, 'customerState', 'invoice'),
    stated_gst_rate: optionalNumber(data, 'statedGstRate', 'invoice'),
    determined_gst_rate: requireNumber(data, 'determinedGstRate', 'invoice'),
    gst_mismatch: requireBoolean(data, 'gstMismatch', 'invoice'),
    mismatch_details: requireArray(data.mismatchDetails, 'invoice mismatch details', true),
  }
}

export function normalizeUpiResponse(value) {
  const data = requireObject(value, 'payment request')
  return {
    upi_request_id: requireString(data, 'upiRequestId', 'payment request'),
    upi_deep_link: requireString(data, 'upiDeepLink', 'payment request'),
    qr_code_data: requireString(data, 'qrCodeData', 'payment request'),
    amount: requireNumber(data, 'amount', 'payment request'),
    currency: requireString(data, 'currency', 'payment request'),
    merchant_name: requireString(data, 'merchantName', 'payment request'),
    merchant_vpa: requireString(data, 'merchantVpa', 'payment request'),
    transaction_note: optionalString(data, 'transactionNote', 'payment request'),
    status: requireString(data, 'status', 'payment request'),
    created_at: optionalString(data, 'createdAt', 'payment request'),
    expires_at: optionalString(data, 'expiresAt', 'payment request'),
  }
}

function requireTextValue(record, key, label) {
  const value = record[key]
  if (typeof value !== 'string') {
    throw new Error(`The ${label} response contains an invalid ${key}. Please try again.`)
  }
  return value
}
