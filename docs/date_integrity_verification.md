# Phase 2 Data-Integrity Verification Report: Date Parsing Discrepancy Investigation

## 1. Executive Summary

This report presents an empirical investigation into the date parsing discrepancy observed between Phase 1 and Phase 2 reports for the NASA Global Landslide Catalog dataset (`data/raw/Global_Landslide_Catalog_Export.csv`).

* **Phase 1 Reported**: `4,395` / `11,033` parsed event dates (`39.84%`)
* **Phase 2 Reported**: `11,033` / `11,033` parsed event dates (`100.00%`)

---

## 2. Empirical Root-Cause Analysis

The discrepancy was caused by pandas' single-format inference behavior when executing `pd.to_datetime(s, errors="coerce")` without the `format="mixed"` parameter on a Series containing heterogeneous date formats.

### Dataset Date String Distribution
The raw `event_date` column contains **11,033 non-null string records** split into two distinct formatting patterns:

1. **Pattern A: Slash Format (`MM/DD/YYYY HH:MM:SS AM/PM`)**
   * **Row Count**: `6,638` (`60.16%`)
   * **Example Raw Value**: `'01/19/2007 12:00:00 AM'`, `'07/31/2009 12:00:00 AM'`, `'12/21/2014 08:10:00 AM'`
   * **Token Structure**: Token 1 (Month) $\in [1, 12]$, Token 2 (Day) $\in [13, 31]$ (100% of these 6,638 rows have Token 2 $> 12$, making them unambiguously US `MM/DD/YYYY` format).

2. **Pattern B: Hyphen Format (`MM-DD-YYYY HH:MM`)**
   * **Row Count**: `4,395` (`39.84%`)
   * **Example Raw Value**: `'08-01-2008 00:00'`, `'01-02-2009 02:00'`, `'09-05-2007 00:00'`
   * **Token Structure**: Token 1 $\in [1, 12]$, Token 2 $\in [1, 12]$, Token 3 (Year) $\in [1988, 2017]$.

---

## 3. Explanation of Parser Discrepancy

### Phase 1 Behavior (`pd.to_datetime(series, errors="coerce")`)
* When pandas evaluated the series without specifying `format="mixed"`, it inspected the first row (`Row 0`: `'08-01-2008 00:00'`) and inferred a hyphenated datetime format template (`%m-%d-%Y %H:%M`).
* When pandas subsequently encountered the `6,638` slash-formatted rows containing `/` and 12-hour `AM/PM` tags, the strict single-format parser failed on all `6,638` slash-formatted rows and coerced them to `NaT`.
* Result: Only the `4,395` hyphen-formatted rows succeeded, creating the illusion that `6,638` records were unparseable or missing.

### Phase 2 Behavior (`pd.to_datetime(series, format="mixed", errors="coerce")`)
* By specifying `format="mixed"`, pandas evaluates each row against its respective format specification.
* Both Pattern A (`6,638` slash rows) and Pattern B (`4,395` hyphen rows) are parsed correctly into valid `datetime64[ns]` objects.
* Result: `6,638 + 4,395 = 11,033` / `11,033` (`100.0%` parsed).

---

## 4. Specific Verification Items Checklist

1. **Exact Raw `event_date` Null / Empty Count**:
   * Total Rows: `11,033`
   * Raw Null Count: `0`
   * Raw Empty Strings: `0`
   * Genuinely Present Raw Values: `11,033` (`100.0%`)

2. **Values Valid After Parsing**:
   * Valid Datetime Objects: `11,033` (`100.0%`)
   * Unparseable / Coerced `NaT` Values: `0` (`0.0%`)

3. **Check for Placeholder or Malformed Values**:
   * Keywords searched: `00/00`, `1900`, `9999`, `unknown`, `N/A`, `null`, `none`, `0000`.
   * Result: **0 suspicious placeholder values found.**

4. **Verification of Non-Fabrication**:
   * No missing dates were converted into valid dates (raw null count = 0).
   * No date values were fabricated, interpolated, or forward-filled.
   * All 11,033 parsed dates correspond 1-to-1 with genuine, empirical timestamps in the original raw NASA export file.

---

## 5. Representative Sample Comparisons

| Row Index | Event ID | Raw `event_date` String | Format Pattern | Phase 1 Default Parsed | Phase 2 `format="mixed"` Parsed | Integrity Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `684` | `'08-01-2008 00:00'` | Hyphen | `2008-08-01 00:00:00` | `2008-08-01 00:00:00` | **Genuine & Matching** |
| `1` | `956` | `'01-02-2009 02:00'` | Hyphen | `2009-01-02 02:00:00` | `2009-01-02 02:00:00` | **Genuine & Matching** |
| `2` | `973` | `'01/19/2007 12:00:00 AM'` | Slash | `NaT` *(parser failure)* | `2007-01-19 00:00:00` | **Genuine (Fixed in Phase 2)** |
| `3` | `1067` | `'07/31/2009 12:00:00 AM'` | Slash | `NaT` *(parser failure)* | `2009-07-31 00:00:00` | **Genuine (Fixed in Phase 2)** |
| `4` | `2603` | `'10/16/2010 12:00:00 PM'` | Slash | `NaT` *(parser failure)* | `2010-10-16 12:00:00` | **Genuine (Fixed in Phase 2)** |
| `5` | `4203` | `'02/16/2012 12:00:00 AM'` | Slash | `NaT` *(parser failure)* | `2012-02-16 00:00:00` | **Genuine (Fixed in Phase 2)** |
| `11` | `8253` | `'12/21/2014 08:10:00 AM'` | Slash | `NaT` *(parser failure)* | `2014-12-21 08:10:00` | **Genuine (Fixed in Phase 2)** |

---

## 6. Conclusion & Recommendation

The Phase 2 date parsing behavior using `format="mixed"` is **empirically correct and scientifically sound**. The Phase 1 count of 4,395 was an artifact of pandas default single-format inferencing failing on slash-formatted timestamps. No modification to the processing pipeline is required.
