import test from 'node:test'
import assert from 'node:assert/strict'
import { calculateGstLocally } from '../src/services/gstCalculator.js'

test('calculates intra-state GST and flags a stated-rate mismatch', () => {
  const result = calculateGstLocally({
    customer_state: ' maharashtra ',
    items: [{ name: 'Mouse', quantity: 50, unit_price: 450, stated_gst_rate: 5 }],
  })

  assert.equal(result.tax_type, 'intra_state')
  assert.equal(result.items[0].gst_rate, 18)
  assert.equal(result.items[0].cgst_rate, 9)
  assert.equal(result.items[0].sgst_rate, 9)
  assert.equal(result.items[0].gst_amount, 4050)
  assert.equal(result.total_subtotal, 22500)
  assert.equal(result.grand_total, 26550)
  assert.equal(result.gst_mismatch, true)
  assert.deepEqual(result.mismatch_details, ["Item 'Mouse': stated 5%, rules determine 18%"])
})

test('uses IGST for a different state and matches product rule rates', () => {
  const result = calculateGstLocally({
    customer_state: 'Karnataka',
    items: [{ name: 'pen', quantity: 3, unit_price: 10, stated_gst_rate: 12 }],
  })

  assert.equal(result.tax_type, 'inter_state')
  assert.equal(result.items[0].gst_rate, 12)
  assert.equal(result.items[0].cgst_amount, 0)
  assert.equal(result.items[0].sgst_amount, 0)
  assert.equal(result.items[0].igst_amount, 3.6)
  assert.equal(result.grand_total, 33.6)
  assert.equal(result.gst_mismatch, false)
})

test('rounds line amounts half up and recalculates edited quantity and price', () => {
  const result = calculateGstLocally({
    customer_state: 'Maharashtra',
    items: [{ name: 'unknown item', quantity: 3, unit_price: 0.005 }],
  })

  assert.equal(result.items[0].subtotal, 0.02)
  assert.equal(result.items[0].gst_amount, 0)
  assert.equal(result.grand_total, 0.02)
})

test('applies the zero-rate salt rule', () => {
  const result = calculateGstLocally({
    customer_state: 'Maharashtra',
    items: [{ name: 'salt', quantity: 2, unit_price: 4.25, stated_gst_rate: 0 }],
  })

  assert.equal(result.items[0].gst_rate, 0)
  assert.equal(result.items[0].gst_amount, 0)
  assert.equal(result.gst_mismatch, false)
})

test('rejects invalid quantities, prices, rates, and empty item lists', () => {
  const valid = { customer_state: 'Maharashtra', items: [{ name: 'mouse', quantity: 1, unit_price: 1 }] }

  assert.throws(() => calculateGstLocally({ ...valid, items: [] }), /at least one item/i)
  assert.throws(() => calculateGstLocally({ ...valid, items: [{ ...valid.items[0], quantity: 0 }] }), /positive whole number/i)
  assert.throws(() => calculateGstLocally({ ...valid, items: [{ ...valid.items[0], unit_price: -1 }] }), /cannot be negative/i)
  assert.throws(() => calculateGstLocally({ ...valid, items: [{ ...valid.items[0], stated_gst_rate: 101 }] }), /between 0 and 100/i)
})
