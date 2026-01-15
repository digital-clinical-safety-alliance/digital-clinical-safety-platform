
# Copilot Prompt (copy everything below)

You are analysing an existing repository called **Digital Clinical Safety Platform (DCSP)**.

The goal is to produce a new file called `spec.md` for a successor project named **Turva**.

Turva is a continuation and evolution of DCSP, not a rewrite from scratch. Your task is to extract, generalise, and formalise **everything conceptually useful** from the DCSP repository so it can be carried forward.

### Ground rules

- Do **not** describe frontend or backend technologies
- Do **not** mention Django, MkDocs, or any implementation framework
- Do **not** include UI component descriptions
- Do **not** assume any specific database or API design
- Focus on **domain concepts, workflows, artefacts, governance, and system behaviour**
- Write in **clear, plain British English**
- Avoid abbreviations where possible
- Prefer declarative statements over marketing language

---

### What to extract from the DCSP repository

You should inspect the repository structure, documentation, models, and content to identify and describe:

1. **System purpose and scope**
   - What problem DCSP exists to solve
   - What it explicitly does and does not attempt to do
   - Who it is for (roles, not job titles)

2. **Core domain concepts**
   Describe all meaningful concepts, for example:
   - Hazard
   - Risk
   - Mitigation
   - Safety case
   - Clinical system
   - Deployment or release
   - Organisation
   - User roles and responsibilities

   Each concept should include:
   - A short definition
   - Why it exists
   - How it relates to other concepts

3. **Clinical safety workflow**
   Describe the end-to-end lifecycle, including:
   - Hazard identification
   - Risk assessment
   - Mitigation design
   - Review and approval
   - Residual risk acceptance
   - Ongoing monitoring and review

   Emphasise that this is **continuous**, not a one-off process.

4. **Governance and accountability model**
   Extract how DCSP handles:
   - Clinical responsibility
   - Ownership of hazards and risks
   - Review and sign-off
   - Separation of clinical judgement from technical implementation

5. **Regulatory alignment**
   Describe how the system supports compliance with:
   - NHS England clinical safety standards (for example DCB0129 and DCB0160)
   - Without reproducing the standards verbatim
   - Focus on *evidence generation* rather than document production

6. **Evidence and auditability**
   Capture how DCSP treats:
   - Traceability
   - Change history
   - Decision provenance
   - Justification of risk decisions
   - Audit readiness

7. **Information architecture**
   Describe the types of artefacts the system manages, such as:
   - Hazard logs
   - Risk assessments
   - Safety justifications
   - Supporting evidence
   - Generated reports

   Focus on *what information exists*, not file formats.

8. **Reporting and outputs**
   Describe:
   - What reports or summaries the system can generate
   - Who they are intended for
   - When they are used (for example during assurance or incident review)

9. **Non-goals and constraints**
   Explicitly document what the system is not responsible for, such as:
   - Clinical decision making
   - Real-time patient care
   - Replacing professional judgement

10. **Design principles carried forward into Turva**
    Identify implicit principles in DCSP, for example:
    - Safety as a first-class concern
    - Structured over free-text where safety matters
    - Human readability
    - Auditability by default
    - Minimising administrative burden

---

### Output format

Produce a single Markdown file named `spec.md` with the following high-level structure:

- Introduction
- Purpose and scope
- Core concepts
- Clinical safety lifecycle
- Governance and accountability
- Regulatory alignment
- Evidence and audit model
- Information architecture
- Reporting and outputs
- Non-goals
- Design principles

The tone should be calm, precise, and professional. This document should be suitable for clinicians, engineers, safety officers, and regulators to read and agree upon.

Do not include speculative features. Only include what can be reasonably inferred from the existing DCSP repository.