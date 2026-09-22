
# Analysis of the Supplied Online Retail II Dataset

This document is based on the exact `online_retail_II.csv` supplied for the project.

## Dataset shape

- Rows: 1,067,371
- Columns: 8

## Columns

| Original field | Project role |
|---|---|
| Invoice | Invoice/transaction identifier |
| StockCode | Product identifier |
| Description | Product description |
| Quantity | Units purchased |
| InvoiceDate | Transaction date and time |
| Price | Unit price |
| Customer ID | Customer identifier |
| Country | Customer country |

## Quality observations

- Missing Customer ID: 243,007 rows
- Missing Description: 4,382 rows
- Exact duplicate rows: 34,335
- Cancellation invoice rows: 19,494
- Negative quantity rows: 22,950
- Non-positive price rows: 6,207
- Unique invoices: 53,628
- Unique stock codes: 5,305
- Identifiable customers: 5,942
- Countries: 43
- Date range: 2009-12-01 07:45:00 through 2011-12-09 12:50:00

## Cleaning rules

### Customer ID
Converted to a nullable string representation so IDs do not appear as floating-point values.

Rows without customer IDs are retained for sales analysis but excluded from customer behaviour metrics.

### Description
Missing descriptions are replaced with:

```text
Unknown Product
```

### Cancellation detection
A row is marked as cancellation activity when:

```text
Invoice starts with C
OR Quantity < 0
```

### Valid sale
A row is included in sales KPIs when:

```text
not a cancellation
AND Quantity > 0
AND Price > 0
```

### Revenue

```text
Revenue = Quantity × Price
```

## Why customer IDs are handled separately

The supplied file contains 243,007 rows without a customer ID. These rows cannot support customer-level analysis, but they can still represent genuine revenue.

Therefore:

- Overall sales analytics use all valid sales.
- Customer analytics use only valid sales with a known customer ID.

This avoids understating overall revenue while keeping customer metrics logically correct.

## Profile calculated from the supplied file

### Identified-customer sales population

- Rows: 805,549
- Invoices: 36,969
- Customers: 5,878
- Repeat customers with more than one order: 4,255
- One-time customers: 1,623
- Revenue: 17,743,429.18

### Overall valid-sales population

- Rows: 1,041,670
- Invoices: 40,077
- Revenue: 20,972,594.57

The difference is valid sales from transactions with missing customer IDs.

## Customer segmentation

Project-defined segments:

- One-time Customer: exactly 1 order
- Repeat Customer: 2–5 orders
- Frequent Customer: more than 5 orders

These are analytical rules created for this project, not labels supplied by the dataset.

## Main BDA questions

The Spark SQL layer answers:

1. How does revenue change over time?
2. Which products generate the most revenue?
3. Which countries generate the most sales?
4. How often do customers purchase?
5. Which customers contribute the most revenue?
6. What proportion of customers are repeat purchasers?
7. How does cancellation activity change over time?
