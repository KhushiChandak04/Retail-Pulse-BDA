# Pandas vs Spark Cross-Validation

This report independently compares the Pandas cleaning results with the
existing PySpark/Spark SQL views using the supplied Online Retail II dataset.
No project code or analytical definition was changed.

Revenue differences use a tolerance of `0.01` because Pandas and Spark may
accumulate IEEE floating-point values in a different order. Count metrics
require exact equality. Percentage difference is calculated as:

```text
abs(Spark result - Pandas result) / abs(Pandas result) * 100
```

| Metric | Pandas result | Spark result | Difference | Percentage difference | Status |
|---|---:|---:|---:|---:|---|
| Total input rows | 1,067,371 | 1,067,371 | 0 | 0.000000% | PASS |
| Valid sales rows | 1,041,670 | 1,041,670 | 0 | 0.000000% | PASS |
| Valid sales invoices | 40,077 | 40,077 | 0 | 0.000000% | PASS |
| Valid sales revenue | 20,972,594.568000 | 20,972,594.567999 | -0.000001 | 0.000000000006% | PASS |
| Identifiable customers | 5,878 | 5,878 | 0 | 0.000000% | PASS |
| Identifiable-customer invoices | 36,969 | 36,969 | 0 | 0.000000% | PASS |
| Identifiable-customer revenue | 17,743,429.178000 | 17,743,429.177999 | -0.000001 | 0.000000000008% | PASS |
| Repeat customers | 4,255 | 4,255 | 0 | 0.000000% | PASS |
| One-time customers | 1,623 | 1,623 | 0 | 0.000000% | PASS |
| Cancellation rows | 22,951 | 22,951 | 0 | 0.000000% | PASS |

## Population Definitions

- **Valid sales:** not a cancellation, quantity greater than zero, and price
  greater than zero.
- **Identifiable customers:** valid sales with a non-null customer ID.
- **Repeat customers:** known customers with more than one distinct invoice.
- **One-time customers:** known customers with exactly one distinct invoice.
- **Cancellation rows:** invoice begins with `C` or quantity is negative.

The repeat and one-time customer checks use distinct invoice counts on both
sides. Counting transaction rows instead would produce incorrect customer
segments because one invoice can contain multiple product rows.

## Conclusion

The Spark pipeline is consistent with the Pandas preprocessing. All requested
count metrics match exactly, and both revenue metrics differ only by negligible
floating-point accumulation noise, far below the cent-level tolerance. No
actual processing error was found and no code change was necessary.