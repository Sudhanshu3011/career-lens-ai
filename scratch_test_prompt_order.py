import os
import sys

sys.path.insert(0, "backend")

from app.infrastructure.ml.laya_client import laya_client

agent_inst = laya_client.router.load("default")

# Prompt A: Current layout (JD first, Candidate last)
prompt_a = """Target Position: Senior Full Stack ML Engineer

Job Description:
Senior Full Stack ML Engineer with 5+ years experience in Python, PyTorch, React, Node.js, Docker, Kubernetes, and AWS.

Objective Skill Verification:
- Technical Skill Overlap: 0.0%
- Verified Matched Skills: NONE
- Critical Missing Requirements: Python, PyTorch, React, Node.js, Docker, Kubernetes, AWS

Candidate Profile:
Candidate Technical Skills: HTML5, SEO, Technical Writing, WordPress
Experience: Content Writer at MindInventory writing blogs, marketing copies, PR, and social media posts.
"""

# Prompt B: Inverted layout (Candidate first, Target Requisition second)
prompt_b = """Candidate Profile Under Review:
Current Title: Sr. Technical Content Writer
Candidate Technical Skills: HTML5, SEO, Technical Writing, WordPress
Candidate Experience: 5 years as Content Writer writing blogs, web copies, PR, whitepapers, and digital marketing materials.

Target Job Requirements:
Position: Senior Full Stack ML Engineer
Required Core Skills: Python, PyTorch, React, Node.js, Docker, Kubernetes, AWS.
Objective Match Result: 0% match. Candidate lacks all required programming and ML engineering skills.
"""

# Test 1: Criteria with specific skills in each option
q_specific = {
    "type": "choice",
    "instructions": "Evaluate whether the candidate's skills satisfy the technical requirements for Senior Full Stack ML Engineer.",
    "criteria": {
        "high": "Candidate has strong hands-on expertise in Python, PyTorch, React, and ML engineering.",
        "mid": "Candidate has partial software development skills but lacks deep ML experience.",
        "low": "Candidate has no software engineering or ML skills; background is in writing, marketing, or non-engineering.",
    },
}

# Test 2: Standard generic criteria
q_generic = {
    "type": "choice",
    "instructions": "Evaluate how thoroughly the candidate's technical skills satisfy the core requirements for Senior Full Stack ML Engineer.",
    "criteria": {
        "high": "Matches nearly all or all essential technical skills and frameworks required.",
        "mid": "Matches a substantial portion of skills but misses some key technologies.",
        "low": "Matches few or none of the required technical skills; entirely different discipline.",
    },
}

res_a1 = agent_inst.system_one(prompt_a, {"q": q_specific})
res_b1 = agent_inst.system_one(prompt_b, {"q": q_specific})
res_a2 = agent_inst.system_one(prompt_a, {"q": q_generic})
res_b2 = agent_inst.system_one(prompt_b, {"q": q_generic})

print("Prompt A (JD first) + Specific criteria:", res_a1["answers"]["q"]["probabilities"])
print("Prompt B (Candidate first) + Specific criteria:", res_b1["answers"]["q"]["probabilities"])
print("Prompt A (JD first) + Generic criteria:", res_a2["answers"]["q"]["probabilities"])
print("Prompt B (Candidate first) + Generic criteria:", res_b2["answers"]["q"]["probabilities"])
