const SELLER_STATE = 'MAHARASHTRA'
const DEFAULT_GST_RATE = 18

const PRODUCT_GST_RATES = new Map([
  ...['mouse', 'keyboard', 'monitor', 'laptop', 'mobile', 'phone', 'headphones', 'charger', 'cable']
    .map(name => [name, 18]),
  ...['pen', 'notebook', 'paper', 'pencil', 'eraser'].map(name => [name, 12]),
  ...['rice', 'wheat', 'sugar', 'milk'].map(name => [name, 5]),
  ['salt', 0],
])

function decimalParts(value) {
  const match = String(value).match(/^(\d+)(?:\.(\d*))?(?:e([+-]?\d+))?$/i)
  if (!match) {
    throw new Error('Enter valid numeric values before calculating GST.')
  }

  const fraction = match[2] ?? ''
  const exponent = Number(match[3] ?? 0)
  return {
    coefficient: BigInt(`${match[1]}${fraction}`),
    scale: fraction.length - exponent,
  }
}

function roundRatioHalfUp(numerator, denominator) {
  return (numerator + denominator / 2n) / denominator
}

function currencyCents(value, multiplier = 1n) {
  const { coefficient, scale } = decimalParts(value)
  const numerator = coefficient * multiplier * 100n
  if (scale <= 0) return numerator * (10n ** BigInt(-scale))
  return roundRatioHalfUp(numerator, 10n ** BigInt(scale))
}

function centsToAmount(cents) {
  const amount = Number(cents) / 100
  if (!Number.isFinite(amount)) {
    throw new Error('The order total is too large to calculate safely.')
  }
  return amount
}

function numberValue(value, label) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${label} must be a valid number.`)
  }
  return value
}

export function calculateGstLocally(request) {
  if (!request || !Array.isArray(request.items) || request.items.length === 0) {
    throw new Error('At least one item is required for GST calculation.')
  }
  if (request.items.length > 20) {
    throw new Error('A maximum of 20 items can be included in one order.')
  }
  if (request.customer_state != null && typeof request.customer_state !== 'string') {
    throw new Error('Customer state must be text.')
  }

  const customerState = request.customer_state ?? null
  const taxType = customerState?.trim().toUpperCase() === SELLER_STATE
    ? 'intra_state'
    : 'inter_state'
  const mismatchDetails = []

  const items = request.items.map((item, index) => {
    if (!item || typeof item.name !== 'string' || !item.name.trim()) {
      throw new Error(`Item ${index + 1} must have a product name.`)
    }
    const quantity = numberValue(item.quantity, `Item ${index + 1} quantity`)
    if (!Number.isInteger(quantity) || quantity <= 0) {
      throw new Error(`Item ${index + 1} quantity must be a positive whole number.`)
    }
    const unitPrice = numberValue(item.unit_price, `Item ${index + 1} unit price`)
    if (unitPrice < 0) {
      throw new Error(`Item ${index + 1} unit price cannot be negative.`)
    }

    const statedRate = item.stated_gst_rate ?? null
    if (statedRate !== null) {
      numberValue(statedRate, `Item ${index + 1} stated GST rate`)
      if (statedRate < 0 || statedRate > 100) {
        throw new Error(`Item ${index + 1} stated GST rate must be between 0 and 100.`)
      }
    }

    const name = item.name
    const gstRate = PRODUCT_GST_RATES.get(name.trim().toLowerCase()) ?? DEFAULT_GST_RATE
    const subtotalCents = currencyCents(unitPrice, BigInt(quantity))
    const gstAmountCents = roundRatioHalfUp(subtotalCents * BigInt(gstRate), 100n)
    const cgstRateCents = taxType === 'intra_state'
      ? roundRatioHalfUp(BigInt(gstRate) * 100n, 2n)
      : 0n
    const cgstAmountCents = taxType === 'intra_state'
      ? roundRatioHalfUp(subtotalCents * cgstRateCents, 10000n)
      : 0n
    const sgstAmountCents = cgstAmountCents
    const igstAmountCents = taxType === 'inter_state' ? gstAmountCents : 0n
    const gstMismatch = statedRate !== null && statedRate !== gstRate

    if (gstMismatch) {
      mismatchDetails.push(`Item '${name}': stated ${statedRate}%, rules determine ${gstRate}%`)
    }

    return {
      name,
      quantity,
      unit_price: unitPrice,
      subtotal: centsToAmount(subtotalCents),
      gst_rate: gstRate,
      gst_amount: centsToAmount(gstAmountCents),
      cgst_rate: centsToAmount(cgstRateCents),
      cgst_amount: centsToAmount(cgstAmountCents),
      sgst_rate: centsToAmount(cgstRateCents),
      sgst_amount: centsToAmount(sgstAmountCents),
      igst_rate: taxType === 'inter_state' ? gstRate : 0,
      igst_amount: centsToAmount(igstAmountCents),
      stated_gst_rate: statedRate,
      gst_mismatch: gstMismatch,
      tax_type: taxType,
      subtotalCents,
      gstAmountCents,
      cgstAmountCents,
      sgstAmountCents,
      igstAmountCents,
    }
  })

  const total = field => items.reduce((sum, item) => sum + item[field], 0n)
  const statedRates = items.map(item => item.stated_gst_rate).filter(rate => rate !== null)
  const determinedRates = items.map(item => item.gst_rate)
  const publicItems = items.map(({ subtotalCents, gstAmountCents, cgstAmountCents, sgstAmountCents, igstAmountCents, ...item }) => item)

  return {
    items: publicItems,
    total_subtotal: centsToAmount(total('subtotalCents')),
    total_gst_amount: centsToAmount(total('gstAmountCents')),
    total_cgst: centsToAmount(total('cgstAmountCents')),
    total_sgst: centsToAmount(total('sgstAmountCents')),
    total_igst: centsToAmount(total('igstAmountCents')),
    grand_total: centsToAmount(total('subtotalCents') + total('gstAmountCents')),
    tax_type: taxType,
    seller_state: SELLER_STATE,
    customer_state: customerState,
    stated_gst_rate: statedRates.length > 0 && new Set(statedRates).size === 1 ? statedRates[0] : null,
    determined_gst_rate: determinedRates[0],
    gst_mismatch: mismatchDetails.length > 0,
    mismatch_details: mismatchDetails,
  }
}
