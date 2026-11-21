---
source_id: "GL-FRM-02"
doc_type: "guideline"
title: "Krishi Sinchai Sahayata — Scheme Guideline"
language: "en"
authority_level: 1
scheme_id: "SCH-FRM-02"
last_updated: "2026-04-01"
effective_from: "2026-04-01"
valid_until: ""
supersedes: ""
---

# Krishi Sinchai Sahayata (SCH-FRM-02)

- **English:** Krishi Sinchai Sahayata
- **Hindi (Devanagari):** कृषि सिंचाई सहायता
- **Kannada:** ಕೃಷಿ ನೀರಾವರಿ ಸಹಾಯ
- **Tamil:** வேளாண் பாசன உதவித் திட்டம்
- **Implementing Department:** Department of Irrigation & Farm Infrastructure, Government of Mitrapur Pradesh

## 1 Purpose

Krishi Sinchai Sahayata promotes water-efficient micro-irrigation across Mitrapur Pradesh by subsidising drip-irrigation equipment for marginal farmers and Scheduled Caste (SC) / Scheduled Tribe (ST) cultivators. The scheme lowers groundwater extraction while improving crop yield resilience.

## 2 Benefit

- **Amount:** ₹12,000 drip-irrigation subsidy (one-time capital grant per eligible farm holding).
- **Disbursement Mode:** Credited directly to the beneficiary's bank account via DBT following verified installation and field inspection of drip-irrigation laterals, emitters, and filtration units purchased from an empanelled or GST-registered vendor.

## 3 Eligibility

An applicant must satisfy the primary occupation rule **AND** at least one of the two qualifying criteria below:

- **Primary Condition (Required):** `occupation = farmer` (active cultivator with recorded agricultural land in Mitrapur Pradesh).
- **Qualifying Condition (At least ONE required):**
  - `land_holding_acres <= 2.5` (marginal landholding of 2.5 acres or less), **OR**
  - `category` is `SC` or `ST` (Scheduled Caste or Scheduled Tribe farmer, irrespective of landholding size).
- **Logical Rule:** `occupation = farmer AND (land_holding_acres <= 2.5 OR category in {SC, ST})`.

## 4 Required Documents

- **Mitrapur Resident Identity Card** — **Mandatory.** *Validity note:* Must be active and unrevoked.
- **Certified Land Holding Extract (Mitrapur Bhoomi Record)** — **Mandatory.** *Validity note:* Issued within the last 6 months showing total holding in acres and plot survey number.
- **Caste / Community Certificate (SC or ST)** — **Mandatory** if claiming eligibility under the SC/ST clause with `land_holding_acres > 2.5`; **Optional** if qualifying solely via `land_holding_acres <= 2.5`. *Validity note:* Permanent validity when issued by a Sub-Divisional Magistrate or competent Revenue Authority of Mitrapur Pradesh.
- **Drip-Irrigation Quotation / Tax Invoice** — **Mandatory** (quotation at application; final invoice prior to disbursement). *Validity note:* Quotation must be dated within 60 days of application; invoice must be dated after preliminary technical clearance.
- **Bank Account Proof (Passbook / Cancelled Cheque)** — **Mandatory.** *Validity note:* Active DBT-enabled account in the applicant's name.
- **Water Source Verification Note** (borewell, open well, or canal access confirmation) — **Optional.** *Validity note:* Valid for 12 months; accelerates site inspection if attached upfront.

## 5 Application Process

1. Apply online via the **MitraSeva Citizen Portal** or at the **District Irrigation Facilitation Desk** with land records, category certificate (where applicable), and equipment quotation.
2. Receive an **Application Reference Number (ARN)** and a provisional technical feasibility inspection date.
3. A Junior Irrigation Engineer inspects the plot post-installation and uploads geo-tagged verification photos within 20 working days.
4. **Final Decision:** Technical inspections and vendor quotations do not automatically guarantee grant release. The **Department of Irrigation & Farm Infrastructure makes the final decision** on sanction, subsidy quantum, and disbursement.
5. Zero application or inspection fees apply under this scheme (see `POL-FEE-01`).

## 6 Last Date and Validity

- **Status:** Open (rolling acceptance throughout the financial year).
- **Effective From:** `2026-04-01`
- **Last Date to Apply:** None (no closing date; subject to annual budgetary allocation).
- **Validity:** Remains effective until amended or superseded by an official notification from the Department of Irrigation & Farm Infrastructure.
