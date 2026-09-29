"""
CareerLens AI - Requirement Matcher & Hard Gates Evaluator
Evaluates atomic requirements against candidate evidence using Noul and Score primitives.
"""

from __future__ import annotations

from typing import List, Tuple
from app.models.domain.job import JobProfile
from app.models.domain.candidate import CandidateProfile
from app.models.domain.evidence import Evidence, EvidenceAssessment
from app.models.domain.decision import HardRequirementGate
from app.engines.extraction.evidence_builder import find_evidence_for_requirement
from app.engines.jev.client import jev_client
from app.engines.laya.client import laya_client
from app.engines.jev.questions import build_requirement_questions, clean_question_id
from app.core.logger import get_logger

logger = get_logger(__name__)


def evaluate_candidate_requirements(
    job_profile: JobProfile,
    candidate_profile: CandidateProfile,
    evidences: List[Evidence],
    pipeline_mode: str = "typesafe",
) -> Tuple[List[EvidenceAssessment], List[HardRequirementGate], bool]:
    """
    Evaluates candidate evidence against target job requirements:
    1. Collects requirements to test (hard gates + top required skills).
    2. Builds parallel Noul and Score questions.
    3. Executes 1 batch Jev call.
    4. Evaluates hard gates and returns (assessments, gates, all_passed).
    """
    req_names = [r.name for r in job_profile.hard_requirements]
    for s in job_profile.required_skills:
        if s not in req_names and len(req_names) < 8:
            req_names.append(s)

    if not req_names:
        return [], [], True

    # Assemble contextual state for Jev: relevant candidate snippets + profile summary
    evidence_lines: List[str] = []
    for req in req_names:
        matched_ev = find_evidence_for_requirement(req, evidences)
        if matched_ev:
            for ev in matched_ev[:2]:
                evidence_lines.append(f"[{req} evidence ({ev.section})]: {ev.text}")
        else:
            evidence_lines.append(
                f"[{req}]: No specific evidence bullet found in resume."
            )

    state_text = (
        f"Candidate Summary & Experience Overview:\n{candidate_profile.summary_text}\n\n"
        f"{candidate_profile.experience_text[:1200]}\n\n"
        f"Candidate Verified Evidence Snippets:\n" + "\n".join(evidence_lines)
    )

    questions = build_requirement_questions(req_names)
    client = laya_client if pipeline_mode == "laya_local" else jev_client
    answers = client.predict(state={"text": state_text}, questions=questions)

    assessments: List[EvidenceAssessment] = []
    hard_gates: List[HardRequirementGate] = []
    all_gates_passed = True
    hard_req_names = {r.name.lower() for r in job_profile.hard_requirements}

    for req in req_names:
        safe_id = clean_question_id(req)
        gate_ans = answers.get(f"gate_{safe_id}", {})
        direct_ans = answers.get(f"direct_{safe_id}", {})
        str_ans = answers.get(f"strength_{safe_id}", {})

        sat_prob = float(gate_ans.get("noul", 0.50))
        direct_prob = float(direct_ans.get("noul", 0.50))
        strength_score = float(str_ans.get("score", 2.0))
        conf = float(gate_ans.get("confidence", 0.70))

        # Check matched snippet texts
        matched_ev = find_evidence_for_requirement(req, evidences)
        snippets = [ev.text for ev in matched_ev[:3]]

        # Determine verdict
        if sat_prob >= 0.70:
            verdict = "satisfied"
        elif sat_prob >= 0.40:
            verdict = "partially_satisfied"
        else:
            verdict = "missing"

        is_hard = req.lower() in hard_req_names
        assessments.append(
            EvidenceAssessment(
                requirement_name=req,
                is_hard_requirement=is_hard,
                satisfied_probability=sat_prob,
                direct_evidence_probability=direct_prob,
                evidence_strength=strength_score,
                relevance_score=strength_score,
                confidence=conf,
                verdict=verdict,
                evidence_snippets=snippets,
            )
        )

        # Hard Gate Verification
        if is_hard:
            passed = sat_prob >= 0.40
            if not passed:
                all_gates_passed = False

            hard_gates.append(
                HardRequirementGate(
                    requirement_name=req,
                    passed=passed,
                    probability=sat_prob,
                    confidence=conf,
                    reason=(
                        f"Requirement satisfied (P={sat_prob:.2f})"
                        if passed
                        else f"Critical hard requirement '{req}' unmet (P={sat_prob:.2f} < 0.40)."
                    ),
                )
            )

    logger.info(
        f"Requirement Evaluation complete: requirements={len(assessments)}, "
        f"hard_gates={len(hard_gates)}, all_hard_gates_passed={all_gates_passed}"
    )

    return assessments, hard_gates, all_gates_passed
