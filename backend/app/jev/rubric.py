"""
CareerLens AI - TypeSafe Jev Resume Evaluation Rubric (Version 1.0)
Standardized, versioned definitions for System One primitives (Choice, Score, Noul).
"""

from __future__ import annotations

from typing import Dict, List , Any


RESUME_RUBRIC_V1: Dict[str, Any] = {
    "version": "1.0",
    
    # 7-level ordered scale for Score questions (0.0 to 6.0)
    "seniority_levels": [
        "Intern: Learning, assisting, student, academic projects, or coursework only (0 years).",
        "Junior: Early career professional (0-2 years) with limited ownership under direct supervision.",
        "Mid: Independent practical contributor (2-5 years) delivering standard features and technical work.",
        "Senior: Seasoned engineer (5+ years) owning architecture, mentorship, cross-team impact, and autonomy.",
        "Lead: Technical team lead guiding project execution, team standards, and technical direction.",
        "Staff: Broad organizational impact, cross-service architecture, and senior technical leadership.",
        "Principal: Company-wide engineering strategy, high-level technical direction, and principal ownership."
    ],

    # Choice criteria for candidate resume section classification
    "section_labels": {
        "experience": "Work history, employment, job positions, professional roles, and practical engagements.",
        "technical": "Technical proficiencies, programming languages, databases, tools, and technical stacks.",
        "education": "University degrees, academic background, college credentials, and graduation details.",
        "projects": "Personal software projects, academic coursework projects, and open-source contributions.",
        "certifications": "Official certifications, vendor credentials (AWS, GCP, etc.), and professional licenses.",
        "summary": "Professional summary, biography, career objective, or executive profile statement.",
        "other": "Contact details, personal hobbies, references, or unrecognized header items."
    },

    # Choice criteria for engineering role taxonomy
    "role_families": {
        "backend": "Backend engineering, API design, web servers, databases, microservices, and server-side logic.",
        "frontend": "Frontend web development, React, Next.js, UI/UX implementation, and client state management.",
        "full_stack": "Full stack engineering spanning both browser frontend and backend server components.",
        "ai_ml": "Machine learning, deep learning, PyTorch, computer vision, NLP, and model training/serving.",
        "data_engineering": "Data pipelines, ETL, Apache Spark, Kafka, distributed processing, and data warehouses.",
        "devops_cloud": "DevOps, Kubernetes, Docker, CI/CD pipelines, AWS/GCP cloud infrastructure, and SRE.",
        "mobile": "Native or cross-platform mobile apps (Android, iOS, Flutter, React Native).",
        "qa_testing": "Software testing, automated E2E suites, QA verification, and test framework engineering.",
        "security": "Application security, network defense, penetration testing, and compliance."
    },

    # Choice criteria for industry/technical domains
    "domain_taxonomy": {
        "web_cloud": "Cloud-native web applications, SaaS platforms, and distributed microservices.",
        "artificial_intelligence": "Machine learning, neural networks, predictive models, GenAI, and AI inference.",
        "data_analytics": "Big data infrastructure, streaming analytics, business intelligence, and warehousing.",
        "fintech": "Financial transactions, trading systems, payment processing, and banking technology.",
        "healthtech": "Healthcare systems, clinical data, EHR/EMR, and medical imaging applications.",
        "ecommerce": "Online retail, consumer marketplaces, inventory systems, and commerce platforms.",
        "general_software": "General software engineering, utilities, operating systems, and developer tooling."
    },

    # 6-level ordered scale for competency & skill strength (0.0 to 5.0)
    "skill_strength_levels": [
        "Level 0: No direct evidence or mentions found in resume.",
        "Level 1: Minimal exposure or conceptual mention only (e.g. listed in a keyword cloud).",
        "Level 2: Occasional use in academic coursework, tutorials, or minor non-production tasks.",
        "Level 3: Regular practical application in completed projects or professional work.",
        "Level 4: Strong professional production experience with substantial depth and ownership.",
        "Level 5: Deep architectural expertise, performance optimization, or core engineering mastery."
    ],

    # 6-level ordered scale for evidence quality (0.0 to 5.0)
    "evidence_strength_levels": [
        "Level 0: Zero verifiable evidence provided.",
        "Level 1: Vague keyword claim with no context, metrics, or description.",
        "Level 2: Basic descriptive mention in an academic or hobby project.",
        "Level 3: Specific project evidence detailing technology usage and deliverable outcomes.",
        "Level 4: Production work evidence with clear responsibilities, scale, and business impact.",
        "Level 5: Exceptional verifiable evidence showing leadership, architectural design, or quantifiable impact."
    ]
}


def seniority_score_to_label(score: float) -> str:
    """Maps continuous 0.0 to 6.0 seniority score into standard enterprise label."""
    if score < 0.8:
        return "Intern / Student"
    elif score < 1.8:
        return "Junior / Entry-Level"
    elif score < 2.8:
        return "Mid-Level"
    elif score < 3.8:
        return "Senior / Lead"
    elif score < 4.8:
        return "Lead / Staff"
    elif score < 5.6:
        return "Staff Engineer"
    return "Principal / Executive"
