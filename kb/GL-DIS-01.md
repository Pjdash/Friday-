---
source_id: "GL-DIS-01"
doc_type: "guideline"
title: "Divyang Sahayata Pension — Scheme Guideline"
language: "en"
authority_level: 1
scheme_id: "SCH-DIS-01"
last_updated: "2026-04-01"
effective_from: "2026-04-01"
valid_until: ""
supersedes: ""
---

# Divyang Sahayata Pension (SCH-DIS-01)

- **English:** Divyang Sahayata Pension
- **Hindi (Devanagari):** दिव्यांग सहायता पेंशन
- **Kannada:** ದಿವ್ಯಾಂಗ ಸಹಾಯ ಪಿಂಚಣಿ
- **Tamil:** மாற்றுத்திறனாளி உதவி ஓய்வூதியம்
- **Implementing Department:** Commissionerate for Persons with Disabilities, Government of Mitrapur Pradesh

## 1 Purpose

The Divyang Sahayata Pension provides regular monthly financial assistance to persons with benchmark or severe disabilities residing in Mitrapur Pradesh. The pension supports daily living needs, assistive care, and economic independence, with an explicit income-ceiling exemption for individuals with severe disability of 80% or above.

## 2 Benefit

- **Amount:** ₹2,000 per month.
- **Disbursement Mode:** Transferred monthly via DBT to the beneficiary's verified bank account (or legal guardian's designated account where the beneficiary is a minor or requires legal guardianship) by the 7th working day of each month.

## 3 Eligibility

An applicant must reside in Mitrapur Pradesh and satisfy all required conditions below:

- **Disability Status (Required):** `is_disabled = Y` (certified person with disability).
- **Minimum Disability Threshold (Required):** `disability_percent >= 40` (assessed by a District Medical Board of Mitrapur Pradesh).
- **Income / Severe Disability Clause (At least ONE required):**
  - `annual_household_income <= ₹2,00,000`, **OR**
  - `disability_percent >= 80` (applicants certified with 80% or higher disability are exempt from the annual household income ceiling).
- **Logical Rule:** `is_disabled = Y AND disability_percent >= 40 AND (annual_household_income <= ₹2,00,000 OR disability_percent >= 80)`.

## 4 Required Documents

- **Mitrapur Resident Identity Card** — **Mandatory.** *Validity note:* Must be active and unrevoked.
- **District Medical Board Disability Certificate** — **Mandatory.** *Validity note:* Must explicitly state the assessed disability percentage (`>= 40%`). Permanent certificates remain valid indefinitely; temporary/reviewable certificates must not be expired on the date of application and must be renewed before expiry to continue pension payouts.
- **Annual Household Income Certificate** (issued by the Block Revenue Officer) — **Mandatory** if `disability_percent` is between `40` and `79`; **Optional** (not required) if `disability_percent >= 80`. *Validity note:* Valid for 12 months from the date of issue.
- **Bank Account Proof (Passbook / Cancelled Cheque)** — **Mandatory.** *Validity note:* Active DBT-enabled bank account in the beneficiary's name (or legally appointed guardian's name with guardianship order).
- **Recent Passport-Size Photograph** — **Mandatory.** *Validity note:* Taken within the last 6 months.
- **Legal Guardianship Certificate** — **Optional** (Mandatory only if applying through a legal guardian for a minor or person needing high support). *Validity note:* Must be currently valid and issued by the District Local Level Committee or competent court.

## 5 Application Process

1. Apply online via the **MitraSeva Citizen Portal** or at the nearest **MitraKendra Facilitation Centre** or **District Disability Welfare Office**. Home-assisted enrolment can be requested via the state toll-free helpline for applicants with mobility barriers.
2. Upload or submit the Disability Certificate and supporting records to generate an **Application Reference Number (ARN)**.
3. The District Disability Welfare Officer validates the Medical Board certificate number and, where applicable, income records within 15 working days.
4. **Final Decision:** Portal pre-screening and facilitation centre receipts do not constitute approval. The **Commissionerate for Persons with Disabilities makes the final decision** on eligibility, pension sanction, continuation, or rejection.
5. No fee is charged for application, medical verification linkage, or pension disbursement (see `POL-FEE-01`).

## 6 Last Date and Validity

- **Status:** Open (continuous enrolment throughout the year).
- **Effective From:** `2026-04-01`
- **Last Date to Apply:** None (no closing date).
- **Validity:** Remains in effect continuously unless revised or superseded by an official order of the Commissionerate for Persons with Disabilities.
