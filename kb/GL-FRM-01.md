---
source_id: "GL-FRM-01"
doc_type: "guideline"
title: "Kisan Samriddhi Yojana — Scheme Guideline"
language: "en"
authority_level: 1
scheme_id: "SCH-FRM-01"
last_updated: "2026-04-01"
effective_from: "2026-04-01"
valid_until: ""
supersedes: ""
---

# Kisan Samriddhi Yojana (SCH-FRM-01)

- **English:** Kisan Samriddhi Yojana
- **Hindi (Devanagari):** किसान समृद्धि योजना
- **Kannada:** ಕಿಸಾನ್ ಸಮೃದ್ಧಿ ಯೋಜನೆ
- **Tamil:** கிசான் சம்ரித்தி திட்டம்
- **Implementing Department:** Department of Agriculture & Rural Prosperity, Government of Mitrapur Pradesh

## 1 Purpose

The Kisan Samriddhi Yojana offers direct annual income supplementation to small and marginal rural cultivators in Mitrapur Pradesh. The assistance is designed to offset seasonal input costs—such as seeds, organic manures, and soil preparation—and reduce reliance on informal credit.

## 2 Benefit

- **Amount:** ₹6,000 per year.
- **Disbursement Schedule:** Released in two equal biannual instalments of ₹3,000 each (Kharif window in June and Rabi window in November) directly into the beneficiary's verified bank account via DBT.
- **Limit:** Restricted to one active benefit enrolment per eligible cultivating household per financial year.

## 3 Eligibility

An applicant must meet all of the following criteria:

- **Occupation:** `occupation = farmer` (actively engaged in crop cultivation on owned or recorded cultivable land in Mitrapur Pradesh).
- **Land Holding:** `land_holding_acres <= 5.0` (total cultivable agricultural land held by the applicant in Mitrapur Pradesh must not exceed 5.0 acres).
- **Residence Type:** `residence_type = rural` (applicant must reside in a notified Gram Panchayat area of Mitrapur Pradesh).

## 4 Required Documents

- **Mitrapur Resident Identity Card** — **Mandatory.** *Validity note:* Must be active and reflect a rural residential address within Mitrapur Pradesh.
- **Certified Land Holding Extract (Mitrapur Bhoomi Record)** — **Mandatory.** *Validity note:* Must be issued or digitally verified by the Village Revenue Office within the last 6 months and clearly state total acreage.
- **Rural Residence Certificate** (issued by the Gram Panchayat Secretary or Block Development Office) — **Mandatory.** *Validity note:* Valid for 12 months from the date of issue.
- **Bank Account Proof (Passbook / Cancelled Cheque)** — **Mandatory.** *Validity note:* Account must be active, DBT-enabled, and held in the applicant's name.
- **Farmer Registration Slip / Soil Health Card** — **Optional.** *Validity note:* Valid if issued within the past 24 months; expedites agricultural verification but is not mandatory for submission.

## 5 Application Process

1. Register and fill out the Kisan Samriddhi application form on the **MitraSeva Citizen Portal** or through the local **Gram Panchayat MitraKendra**.
2. Attach the certified land holding record and rural residency documents; obtain a unique **Application Reference Number (ARN)**.
3. The Village Agricultural Extension Officer cross-checks land acreage against the Mitrapur Bhoomi Registry and confirms active cultivation within 15 working days.
4. **Final Decision:** Automated portal eligibility calculators are informational only. The **Department of Agriculture & Rural Prosperity makes the final decision** on application approval, instalment release, or rejection.
5. Application submission and disbursement are completely free of charge (see `POL-FEE-01`).

## 6 Last Date and Validity

- **Status:** Open (continuous enrolment).
- **Effective From:** `2026-04-01`
- **Last Date to Apply:** None (rolling acceptance; applications approved after a seasonal cutoff are queued for the next biannual cycle).
- **Validity:** Valid continuously until modified or withdrawn by an official order of the Department of Agriculture & Rural Prosperity.
