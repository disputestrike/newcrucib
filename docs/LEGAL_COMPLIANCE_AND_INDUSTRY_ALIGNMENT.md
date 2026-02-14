# Legal Compliance & Industry Alignment

This document compares CrucibAI’s legal/AUP approach to **OpenAI**, **Anthropic**, **Vercel**, and **common law** so we stay competitive and within what’s allowed.

---

## How others handle it

### OpenAI (Usage Policies, Oct 2025)
- **Protect people:** Illicit activities, weapons, terrorism/violence, harassment, defamation, suicide/self-harm, sexual violence, non-consensual intimate content, malicious cyber activity, IP infringement, real-money gambling, unlicensed legal/medical advice, circumventing safeguards.
- **Respect privacy:** No facial recognition without consent, no real-time biometric ID in public, no use of likeness without consent, no social scoring/profiling, no criminal-offense prediction based on traits.
- **Minors:** No CSAM (including AI-generated), grooming, age-inappropriate content, promoting self-harm/unhealthy behavior to minors, underage roleplay.
- **Empower people:** No fraud/scams/spam/impersonation, no election interference, no automation of high-stakes decisions (legal, medical, financial, housing, employment, etc.) without human review.
- **Enforcement:** Moderation tools for developers, appeals process, can throttle/suspend/terminate.

### Anthropic (Usage Policy, Sep 2025)
- **Universal standards:** Illegal activity, critical infrastructure compromise, computer/network attacks, weapons design, violence/hate, privacy/identity violations, children’s safety (CSAM, grooming, sexualization of minors), psychologically harmful content, misinformation, undermining democratic processes, criminal justice/censorship/surveillance misuse, fraudulent/abusive practices, platform abuse, sexually explicit content.
- **High-risk use cases:** Legal, healthcare, insurance, finance, employment/housing, academic testing, media — require **human-in-the-loop** and **disclosure** that AI is involved.
- **Enforcement:** Safeguards team; may throttle, suspend, terminate, or block/modify outputs; report to authorities for CSAM/coercion of minors; appeals via usersafety@anthropic.com.

### Vercel (AUP + AI Policy)
- **AUP:** Unlawful activity, fraud, hate speech, harassment, child exploitation, terrorism promotion, IP infringement; violation = material breach, suspension/termination.
- **AI:** Responsible AI; no “high risk” AI in platform services as per EU AI Act where applicable; fraud prevention and abuse detection; no training on customer source code.

### Common legal baseline
- **US:** CFAA (computer fraud), COPPA (minors), state privacy laws, DMCA (copyright).
- **EU:** GDPR, EU AI Act (transparency, human oversight, prohibited practices for high-risk AI).
- **Widely shared norms:** Block illegal content, protect minors, prohibit CSAM (report where required), no unlicensed high-stakes advice, no election/deception at scale, appeals path.

---

## CrucibAI alignment

| Area | OpenAI / Anthropic / Vercel | CrucibAI (current) | Status |
|------|-----------------------------|---------------------|--------|
| Illegal (drugs, weapons, fraud, trafficking) | Yes | Keyword block (illegal category) | Aligned |
| Adult / sexually explicit | Yes | Keyword block (adult category) | Aligned |
| Gambling (unlicensed) | Yes | Keyword block (gambling category) | Aligned |
| Harassment (doxxing, revenge porn, stalking) | Yes | Keyword block (harassment category) | Aligned |
| Child safety (CSAM, grooming) | Yes + report to NCMEC etc. | Keywords (child abuse, csam) | Aligned; add grooming/minor sexualization; consider reporting |
| Self-harm / suicide facilitation | Yes | Not in keyword list | **Added** |
| Misinformation / election deception | Yes | Not in keyword list | **Added** |
| Weapons / explosives (CBRNE) | Yes | Partial (bomb, weapon sales) | **Expanded** |
| Critical infrastructure attack | Yes | Not in keyword list | **Added** |
| Unlicensed legal/medical/financial advice apps | Yes (no tailored advice without pro) | Not in keyword list | **Added** |
| Privacy / surveillance abuse | Yes | Partial (stalking) | **Expanded** |
| Hate / violence / terrorism | Yes | Partial | **Expanded** |
| Appeals process | Yes | Documented (appeals@crucibai.com) | Aligned |
| Logging blocked requests | Yes (enforcement + review) | db.blocked_requests + admin review | Aligned |

---

## Implementation

- **`backend/agents/legal_compliance.py`** is expanded with the categories and keywords above so we:
  - Block the same **types** of requests as OpenAI, Anthropic, and Vercel.
  - Stay within what’s **allowed by law** (no illegal content, protect minors, no unlicensed high-stakes advice, etc.).
- **Policy pages** (Terms, AUP, Privacy, DMCA) already state prohibited uses and enforcement; they are consistent with this alignment.
- **Admin Legal** (blocked requests, review, escalate) matches industry practice of monitoring and acting on violations.

This keeps CrucibAI’s legal approach at the **same standard** as other AI products and within what’s **allowed within law**, without building anything specific to a single vertical (e.g. property management); the same rules apply to any kind of app (basketball, solar, property, etc.).
