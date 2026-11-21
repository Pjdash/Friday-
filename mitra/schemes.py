"""Structured definitions of the schemes this assistant can evaluate.

Each rule cites the guideline that sets its base value. Later circulars that change a value are
listed as overrides by source_id only: their dates are read from the circular's own front matter
(see precedence.effective_value), so a date lives in exactly one place. tests/test_drift.py checks
every literal here against the markdown so the code cannot silently drift from the documents.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Union

from .kb import Document

Profile = dict[str, Any]


@dataclass(frozen=True)
class Note:
    """A clarification that applies only while the circular `source_id` is in force."""
    source_id: str
    text: str


@dataclass(frozen=True)
class Override:
    source_id: str
    value: Any


@dataclass(frozen=True)
class Condition:
    id: str
    field: str
    op: str  # one of: ==, <=, >=, in
    value: Any
    label: str  # may contain {value}
    source_id: str
    overrides: tuple[Override, ...] = ()
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True)
class AllOf:
    children: tuple["Node", ...]


@dataclass(frozen=True)
class AnyOf:
    children: tuple["Node", ...]


Node = Union[Condition, AllOf, AnyOf]


@dataclass(frozen=True)
class Scheme:
    scheme_id: str
    guideline_id: str
    name: str
    department: str
    benefit: str
    rules: Node
    verification_sla: str
    caveats: tuple[str, ...] = ()
    doc_notes: Mapping[str, tuple[Note, ...]] = field(default_factory=dict)
    # Documents that are mandatory only in some cases. Return True/False once the profile
    # decides it, or None if the profile does not say enough.
    doc_conditions: Mapping[str, Callable[[Profile], "bool | None"]] = field(default_factory=dict)


def inr(amount: float) -> str:
    """Format rupees with Indian digit grouping: 150000 -> '₹1,50,000'."""
    digits = str(int(amount))
    if len(digits) <= 3:
        return f"₹{digits}"
    head, tail = digits[:-3], digits[-3:]
    groups: list[str] = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "₹" + ",".join(groups + [tail])


def fmt_value(field_name: str, value: Any) -> str:
    if field_name == "annual_household_income":
        return inr(value)
    if field_name == "land_holding_acres":
        return f"{float(value):.1f}"
    if isinstance(value, (set, frozenset, tuple, list)):
        return " / ".join(sorted(str(v).upper() for v in value))
    return str(value)


def _caste_certificate_mandatory(profile: Profile) -> "bool | None":
    # GL-FRM-02 section 4: mandatory if claiming the SC/ST clause with land above 2.5 acres,
    # optional if qualifying solely through land <= 2.5 acres.
    land, category = profile.get("land_holding_acres"), profile.get("category")
    if land is None or category is None:
        return None
    return category in {"sc", "st"} and land > 2.5


KISAN_SAMRIDDHI = Scheme(
    scheme_id="SCH-FRM-01",
    guideline_id="GL-FRM-01",
    name="Kisan Samriddhi Yojana",
    department="Department of Agriculture & Rural Prosperity",
    benefit="₹6,000 per year, paid as two instalments of ₹3,000 (June and November) by DBT",
    verification_sla="15 working days (Village Agricultural Extension Officer cross-check)",
    rules=AllOf((
        Condition("occupation", "occupation", "==", "farmer",
                  "Occupation is {value}", "GL-FRM-01"),
        Condition("land", "land_holding_acres", "<=", 5.0,
                  "Total household land holding is at most {value} acres", "GL-FRM-01",
                  notes=(Note("CIR-2026-07",
                              "Land is measured per farming household, not per plot: all parcels held by "
                              "household members across khata/survey numbers are added together, and "
                              "applications may not be split by plot."),)),
        Condition("residence", "residence_type", "==", "rural",
                  "Residence is in a notified rural Gram Panchayat area", "GL-FRM-01"),
    )),
    caveats=("Only one benefit enrolment per eligible cultivating household per financial year.",),
)

KRISHI_SINCHAI = Scheme(
    scheme_id="SCH-FRM-02",
    guideline_id="GL-FRM-02",
    name="Krishi Sinchai Sahayata",
    department="Department of Irrigation & Farm Infrastructure",
    benefit="₹12,000 one-time drip-irrigation subsidy, paid by DBT after installation and inspection",
    verification_sla="20 working days after installation (Junior Irrigation Engineer inspection)",
    rules=AllOf((
        Condition("occupation", "occupation", "==", "farmer",
                  "Occupation is {value}", "GL-FRM-02"),
        AnyOf((
            Condition("land", "land_holding_acres", "<=", 2.5,
                      "Land holding is at most {value} acres (marginal farmer)", "GL-FRM-02"),
            Condition("category", "category", "in", frozenset({"sc", "st"}),
                      "Category is {value}", "GL-FRM-02"),
        )),
    )),
    doc_notes={
        "Certified Land Holding Extract": (
            Note("CIR-2026-08",
                 "A valid digital land passbook (Mitrapur Revenue Portal, or DigiLocker with a scannable QR) "
                 "is accepted as equivalent to a paper patta; officers may not insist on paper."),
        ),
    },
    doc_conditions={"Caste / Community Certificate": _caste_certificate_mandatory},
)

VRIDDHJAN_PENSION = Scheme(
    scheme_id="SCH-PEN-01",
    guideline_id="GL-PEN-01",
    name="Vriddhjan Pension Yojana",
    department="Directorate of Social Security & Senior Welfare",
    benefit="₹1,500 per month by DBT, subject to annual life-verification",
    verification_sla="21 working days (Block Social Security Inspector field verification)",
    rules=AllOf((
        Condition("age", "age", ">=", 60,
                  "Age is at least {value} on the date of application", "GL-PEN-01"),
        Condition("income", "annual_household_income", "<=", 120000,
                  "Annual household income is at most {value}", "GL-PEN-01",
                  overrides=(Override("CIR-2026-01", 150000),)),
    )),
    caveats=(
        "You must be a permanent resident of Mitrapur Pradesh.",
        "You are not eligible if you already receive a regular government-employee superannuation "
        "pension from Mitrapur Pradesh.",
    ),
)

SCHEMES: dict[str, Scheme] = {s.scheme_id: s for s in (KISAN_SAMRIDDHI, KRISHI_SINCHAI, VRIDDHJAN_PENSION)}

# Policies and notices every answer relies on, whichever scheme is asked about.
CORE_POLICY_IDS = ("POL-FEE-01", "POL-GRV-01", "POL-PRV-01", "CIR-2026-09")


def _condition_leaves(node: Node):
    if isinstance(node, Condition):
        yield node
    else:
        for child in node.children:
            yield from _condition_leaves(child)


def required_source_ids() -> list[str]:
    """Every knowledge-base document the rules above cite. A deployment missing one must not start."""
    ids = set(CORE_POLICY_IDS)
    for scheme in SCHEMES.values():
        ids.add(scheme.guideline_id)
        for cond in _condition_leaves(scheme.rules):
            ids.add(cond.source_id)
            ids.update(o.source_id for o in cond.overrides)
            ids.update(n.source_id for n in cond.notes)
        for notes in scheme.doc_notes.values():
            ids.update(n.source_id for n in notes)
    return sorted(ids)

# Words people use for each scheme, beyond the official names parsed from the guideline headers.
EXTRA_ALIASES: dict[str, tuple[str, ...]] = {
    "SCH-FRM-01": ("kisan samriddhi", "किसान समृद्धि", "ಕಿಸಾನ್ ಸಮೃದ್ಧಿ", "கிசான் சம்ரித்தி"),
    "SCH-FRM-02": ("sinchai", "drip", "irrigation", "सिंचाई", "ನೀರಾವರಿ", "பாசன"),
    "SCH-PEN-01": ("vriddhjan", "pension", "वृद्धजन", "पेंशन", "ಪಿಂಚಣಿ", "ಪಿಂಚಣಿ", "ஓய்வூதிய", "முதியோர்"),
}


# ---- required documents, parsed from the guideline so the markdown stays the single source -------

@dataclass(frozen=True)
class RequiredDoc:
    name: str
    detail: str  # parenthetical text after the name, if any
    requirement: str  # mandatory | optional | conditional
    validity: str
    raw: str


_DOC_LINE = re.compile(r"^- \*\*(?P<name>.+?)\*\*(?P<middle>.*?)\*Validity note:\*\s*(?P<validity>.*)$")


def parse_required_documents(guideline: Document) -> list[RequiredDoc]:
    section = re.search(r"(?ms)^## \d+ Required Documents\s*\n(.*?)(?=^## |\Z)", guideline.body)
    if not section:
        return []
    docs = []
    for line in section.group(1).splitlines():
        match = _DOC_LINE.match(line.strip())
        if not match:
            continue
        middle = match.group("middle")
        mandatory, optional = "**Mandatory" in middle, "**Optional" in middle
        requirement = "conditional" if mandatory and optional else "mandatory" if mandatory else "optional"
        detail = re.search(r"\(([^)]*)\)", middle)
        docs.append(RequiredDoc(
            name=match.group("name").strip(),
            detail=detail.group(1).strip() if detail else "",
            requirement=requirement,
            validity=match.group("validity").strip(),
            raw=line.strip(),
        ))
    return docs


_SCHEME_NAME_LINE = re.compile(r"^- \*\*(?:English|Hindi \(Devanagari\)|Kannada|Tamil):\*\*\s*(.+?)\s*$", re.M)


def official_names(guideline: Document) -> list[str]:
    """The scheme's name in English, Hindi, Kannada and Tamil, from the guideline header."""
    return _SCHEME_NAME_LINE.findall(guideline.body)
