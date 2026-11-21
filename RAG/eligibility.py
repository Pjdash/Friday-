"""Deterministic eligibility check against the rules in force on a given date.

The result is a *preliminary* screening. The implementing department makes the final decision
(every guideline, section 5; POL-GRV-01 section 2), and the result always says so.
"""
from __future__ import annotations

import operator
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping

from . import precedence
from .kb import KnowledgeBase
from .precedence import Status
from .schemes import (
    SCHEMES, AllOf, AnyOf, Condition, Node, Note, Profile, Scheme,
    fmt_value, parse_required_documents,
)

DISCLAIMER = (
    "This is a preliminary check, not a decision. The {department} makes the final decision after "
    "verification. Applying is free of charge: never pay anyone or share an OTP."
)

_OPS = {
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "in": lambda actual, allowed: actual in allowed,
}
_OP_TEXT = {"==": "must be", "<=": "at most", ">=": "at least", "in": "one of"}


@dataclass
class ConditionResult:
    id: str
    label: str
    passed: bool | None  # None = the profile did not say
    detail: str
    sources: list[str]
    notes: list[str] = field(default_factory=list)


@dataclass
class DocumentItem:
    name: str
    requirement: str  # mandatory | optional | conditional
    validity: str
    notes: list[str] = field(default_factory=list)


@dataclass
class Verdict:
    scheme_id: str
    scheme_name: str
    as_of: str
    outcome: str  # meets_criteria | does_not_meet | needs_info | not_open
    summary: str
    conditions: list[ConditionResult]
    blockers: list[str]
    missing_fields: list[str]
    documents: list[DocumentItem]
    caveats: list[str]
    benefit: str
    department: str
    sources: list[str]
    disclaimer: str


# ---- profile handling ---------------------------------------------------------------------------

def age_on(dob: date, as_of: date) -> int:
    return as_of.year - dob.year - ((as_of.month, as_of.day) < (dob.month, dob.day))


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def normalize_profile(raw: Mapping[str, Any], as_of: date) -> Profile:
    """Clean a raw record (CSV strings, JSON, or text extraction) into typed, lower-cased fields."""
    profile: Profile = {}
    for key in ("occupation", "category", "residence_type", "district", "gender"):
        if not _blank(raw.get(key)):
            profile[key] = str(raw[key]).strip().lower()
    if not _blank(raw.get("annual_household_income")):
        profile["annual_household_income"] = int(float(str(raw["annual_household_income"]).replace(",", "")))
    if not _blank(raw.get("land_holding_acres")):
        profile["land_holding_acres"] = float(raw["land_holding_acres"])
    if not _blank(raw.get("age")):
        profile["age"] = int(raw["age"])
    elif not _blank(raw.get("date_of_birth")):
        dob = raw["date_of_birth"]
        profile["age"] = age_on(dob if isinstance(dob, date) else date.fromisoformat(str(dob)), as_of)
    return profile


# ---- rule evaluation ----------------------------------------------------------------------------

def _describe(node: Node) -> str:
    if isinstance(node, Condition):
        return node.id
    joiner = " AND " if isinstance(node, AllOf) else " OR "
    return "(" + joiner.join(_describe(child) for child in node.children) + ")"


def _active_notes(notes: tuple[Note, ...], kb: KnowledgeBase, as_of: date) -> list[str]:
    result = []
    for note in notes:
        doc = kb.get(note.source_id)
        if doc is not None and precedence.in_force(doc, as_of, kb):
            result.append(f"{note.text} ({note.source_id})")
    return result


def _evaluate_leaf(cond: Condition, profile: Profile, kb: KnowledgeBase, as_of: date) -> ConditionResult:
    value, source = precedence.effective_value(
        cond.value, cond.source_id, [(o.source_id, o.value) for o in cond.overrides], kb, as_of)
    shown = fmt_value(cond.field, value)
    label = cond.label.format(value=shown)
    sources = [source]
    notes = _active_notes(cond.notes, kb, as_of)
    actual = profile.get(cond.field)
    if actual is None:
        return ConditionResult(cond.id, label, None, f"{cond.field} was not provided", sources, notes)
    passed = bool(_OPS[cond.op](actual, value))
    detail = f"you: {fmt_value(cond.field, actual)}; {_OP_TEXT[cond.op]} {shown}"
    if source != cond.source_id:
        detail += f" (limit set by {source}; {cond.source_id} originally said {fmt_value(cond.field, cond.value)})"
    return ConditionResult(cond.id, label, passed, detail, sources, notes)


def _evaluate(node: Node, profile: Profile, kb: KnowledgeBase, as_of: date,
              results: list[ConditionResult]) -> tuple[bool | None, list[str]]:
    """Three-valued logic: (True | False | None for unknown, blockers).

    Appends every leaf result to `results`. `blockers` are the labels that actually make the node
    False: for an OR that is every branch, for an AND only the failing branches. A failing leaf
    inside an OR that another branch already satisfied is therefore never reported as a blocker.
    """
    if isinstance(node, Condition):
        leaf = _evaluate_leaf(node, profile, kb, as_of)
        results.append(leaf)
        return leaf.passed, ([leaf.label] if leaf.passed is False else [])
    outcomes = [_evaluate(child, profile, kb, as_of, results) for child in node.children]
    truths = [truth for truth, _ in outcomes]
    if isinstance(node, AllOf):
        if any(t is False for t in truths):
            return False, [b for t, blockers in outcomes if t is False for b in blockers]
        return (None if any(t is None for t in truths) else True), []
    if any(t is True for t in truths):
        return True, []
    if any(t is None for t in truths):
        return None, []
    return False, [b for _, blockers in outcomes for b in blockers]


def _leaf_fields(node: Node) -> list[str]:
    if isinstance(node, Condition):
        return [node.field]
    return [f for child in node.children for f in _leaf_fields(child)]


# ---- documents ----------------------------------------------------------------------------------

def _documents(scheme: Scheme, profile: Profile, kb: KnowledgeBase, as_of: date) -> list[DocumentItem]:
    guideline = kb.get(scheme.guideline_id)
    if guideline is None:
        return []
    items = []
    for doc in parse_required_documents(guideline):
        requirement = doc.requirement
        if requirement == "conditional":
            for prefix, rule in scheme.doc_conditions.items():
                if doc.name.startswith(prefix):
                    decided = rule(profile)
                    if decided is not None:
                        requirement = "mandatory" if decided else "optional"
        notes = []
        for prefix, doc_notes in scheme.doc_notes.items():
            if doc.name.startswith(prefix):
                notes += _active_notes(doc_notes, kb, as_of)
        items.append(DocumentItem(doc.name, requirement, doc.validity, notes))
    return items


# ---- public entry point -------------------------------------------------------------------------

def evaluate(scheme_id: str, raw_profile: Mapping[str, Any], kb: KnowledgeBase,
             as_of: date) -> Verdict:
    scheme = SCHEMES[scheme_id]
    profile = normalize_profile(raw_profile, as_of)
    guideline = kb.get(scheme.guideline_id)
    disclaimer = DISCLAIMER.format(department=scheme.department)

    def verdict(outcome: str, summary: str, conditions=(), missing=(), sources=(), blockers=()) -> Verdict:
        return Verdict(
            scheme_id=scheme.scheme_id, scheme_name=scheme.name, as_of=as_of.isoformat(),
            outcome=outcome, summary=summary, conditions=list(conditions), blockers=list(blockers),
            missing_fields=list(missing),
            documents=_documents(scheme, profile, kb, as_of), caveats=list(scheme.caveats),
            benefit=scheme.benefit, department=scheme.department,
            sources=sorted({scheme.guideline_id, *sources}), disclaimer=disclaimer,
        )

    if guideline is None:
        return verdict("not_open", f"{scheme.name}: the guideline is not in the knowledge base.")
    state = precedence.status_on(guideline, as_of, kb)
    if state is not Status.IN_FORCE:
        return verdict("not_open", f"{scheme.name} is not open for applications on {as_of} ({state.value}).")

    results: list[ConditionResult] = []
    outcome, blockers = _evaluate(scheme.rules, profile, kb, as_of, results)
    sources = {s for r in results for s in r.sources}
    fields = list(dict.fromkeys(_leaf_fields(scheme.rules)))
    missing = [f for f in fields if f not in profile]

    if outcome is True:
        return verdict("meets_criteria",
                       f"On the details given, you appear to meet the criteria for {scheme.name}.",
                       results, sources=sources)
    if outcome is False:
        return verdict("does_not_meet",
                       f"On the details given, you do not currently meet the criteria for {scheme.name}. "
                       "Not met: " + "; ".join(blockers) + ".",
                       results, sources=sources, blockers=blockers)
    return verdict("needs_info",
                   f"I need a few more details to check {scheme.name}: " + ", ".join(missing) + ".",
                   results, missing=missing, sources=sources)


def evaluate_all(raw_profile: Mapping[str, Any], kb: KnowledgeBase, as_of: date) -> list[Verdict]:
    return [evaluate(scheme_id, raw_profile, kb, as_of) for scheme_id in SCHEMES]
