---
source_id: "GL-HOU-01"
doc_type: "guideline"
title: "Gramin Awas Sahayata — Scheme Guideline"
language: "en"
authority_level: 1
scheme_id: "SCH-HOU-01"
last_updated: "2026-04-01"
effective_from: "2026-04-01"
valid_until: "2026-11-20"
supersedes: ""
---

# Gramin Awas Sahayata (SCH-HOU-01)

- **English:** Gramin Awas Sahayata
- **Hindi (Devanagari):** ग्रामीण आवास सहायता
- **Kannada:** ಗ್ರಾಮೀಣ ವಸತಿ ಸಹಾಯ
- **Tamil:** கிராமப்புற வீட்டுவசதி உதவி
- **Implementing Department:** Department of Rural Housing & Habitation, Government of Mitrapur Pradesh

## 1 Purpose

Gramin Awas Sahayata provides financial construction grants to low-income rural households in priority districts of Mitrapur Pradesh to build or upgrade weather-resilient permanent dwellings. Phase I specifically targets rural habitations in Nayagaon and Dakshinpur districts experiencing high housing deficits.

## 2 Benefit

- **Amount:** ₹1,20,000 total housing grant per eligible household.
- **Disbursement Mode:** Released via DBT in three construction-linked instalments following geo-tagged verification:
  1. **Tranche 1 (₹40,000):** Upon sanction and foundation/plinth layout verification.
  2. **Tranche 2 (₹40,000):** Upon completion of walls up to lintel level.
  3. **Tranche 3 (₹40,000):** Upon completion of roofing and basic sanitation fitting.

## 3 Eligibility

An applicant household must satisfy all of the following rules:

- **Residence Type:** `residence_type = rural` (must reside in a notified Gram Panchayat area).
- **Household Income:** `annual_household_income <= ₹1,80,000`.
- **Eligible Districts:** `district` must be **Nayagaon** OR **Dakshinpur** (`district in {Nayagaon, Dakshinpur}`). Applicants from all other districts of Mitrapur Pradesh are ineligible under this phase.
- **Housing Condition:** The household must not already own a permanent reinforced-concrete (pucca) house in Mitrapur Pradesh.

## 4 Required Documents

- **Mitrapur Resident Identity Card** — **Mandatory.** *Validity note:* Must be active and indicate residence in Nayagaon or Dakshinpur district.
- **Rural Residence & Gram Sabha Verification Certificate** — **Mandatory.** *Validity note:* Issued by the Gram Panchayat Secretary within the last 6 months confirming rural status in Nayagaon or Dakshinpur.
- **Annual Household Income Certificate** (issued by the Block Revenue Officer) — **Mandatory.** *Validity note:* Valid for 12 months from the date of issue.
- **Homestead Land Ownership / Patta Extract** — **Mandatory.** *Validity note:* Issued or certified within the last 12 months confirming lawful possession of the residential plot.
- **Bank Account Proof (Passbook / Cancelled Cheque)** — **Mandatory.** *Validity note:* Active DBT-enabled account held by the head of household (preferably the senior female member).
- **Photograph of Existing Dwelling / Proposed Site** — **Optional.** *Validity note:* Must be taken within 30 days of application if uploaded upfront; otherwise captured during official inspection.

## 5 Application Process

1. Submit the application online on the **MitraSeva Citizen Portal** or in person at the **Block Development Office (BDO)** or **Gram Panchayat MitraKendra** in Nayagaon or Dakshinpur.
2. Collect the **Application Reference Number (ARN)** upon submission.
3. The Block Housing Verification Team conducts a physical home-site inspection and verifies income and district residency within 25 working days.
4. **Final Decision:** Gram Sabha recommendations and site visits serve as verification inputs only. The **Department of Rural Housing & Habitation makes the final decision** on beneficiary selection, grant sanction, tranche release, or rejection.
5. No fee is payable at any stage of application, inspection, or tranche release (see `POL-FEE-01`).

## 6 Last Date and Validity

- **Status:** Open for Phase I (Nayagaon and Dakshinpur districts).
- **Effective From:** `2026-04-01`
- **Last Date to Apply (`apply_until`):** `2026-11-20` (all applications must be submitted on or before `2026-11-20`).
- **Validity:** Valid until `2026-11-20` for new applications; sanctioned beneficiaries retain entitlement to milestone tranches for up to 18 months from their individual sanction date.
