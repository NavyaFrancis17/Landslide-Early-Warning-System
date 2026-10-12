# Chronological Evaluation Split Strategy Document

## 1. Split Allocation Rationale
To prevent temporal lookahead data leakage, random splitting is strictly forbidden. A chronological split is enforced based on event years:

* **Training Set (1988–2010)**: `5,712` samples (27.32%)
* **Validation Set (2011–2014)**: `8,186` samples (39.15%)
* **Test Set (2015–2017)**: `7,012` samples (33.53%)

## 2. Temporal Boundaries
* Train Period: `01-01-1997 00:00` to `12/31/2010 06:00:00 PM`
* Validation Period: `01-01-2011 00:00` to `12/31/2014 12:00:00 AM`
* Test Period: `01-01-2016 23:00` to `12/31/2016 04:08:00 PM`
