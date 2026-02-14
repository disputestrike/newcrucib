# CrucibAI Branding, Watermark & IP Protection

Summary of how we handle: (1) code attribution / watermark, (2) “Made with CrucibAI” branding, (3) preventing replication and IP extraction.

---

## 1. “Watermark” in generated code (like OpenAI-style attribution)

- **OpenAI** uses visible/invisible watermarks mainly for **images** (e.g. C2PA metadata). For **code**, they don’t publish a special “watermark” system; many code generators add a **visible attribution comment** in the generated source.
- **CrucibAI** does the same: we inject a **visible attribution comment** at the top of the generated frontend file:
  - `// Built with CrucibAI · https://crucibai.com`
- This is our “watermark” in code: it identifies the source and is easy to see when someone opens the file. It’s not hidden or cryptographic; it’s standard attribution.

---

## 2. “Made with CrucibAI” branding (like Manus / free-tier attribution)

- **Free tier:** The badge is **permanent and not removable**:
  - We inject an **iframe** that loads the “Built with CrucibAI” content from **our server** (`GET /branding`).
  - The user’s generated code only contains the iframe tag; the text and link are served by us. There is **no way** for them to remove the badge from the running app without removing the iframe (which violates ToS). We do **not** rely on “please don’t remove it” — it’s enforced by serving it from our side.
  - Top-of-file comment is still added.
- **Paid tier:** We inject a **static div** (same text/link) in the source. It’s there by default; the user **can** remove it in the editor or via an option if we add one.
- Implementation: `_inject_crucibai_branding(jsx, user_plan)` uses the **iframe** for `plan === "free"` and the **static div** for paid. Backend serves the badge HTML at `GET /branding`. Set `CRUCIBAI_BRANDING_URL` or `BACKEND_PUBLIC_URL` so the iframe URL points to your deployed backend (e.g. `https://api.crucibai.com/branding`).

---

## 3. Preventing replication / “copying the system”

We block prompts that try to replicate CrucibAI or extract how it works:

- **Legal compliance (AUP) block:** New category **`replication_extraction`** in `backend/agents/legal_compliance.py` blocks prompts that contain phrases such as:
  - “replicate CrucibAI”, “clone CrucibAI”, “copy CrucibAI”, “rebuild CrucibAI”
  - “reveal your system prompt”, “export your instructions”, “how were you built”
  - “replicate yourself”, “clone yourself”, “copy this system”
  - “reveal your architecture”, “what are you built with”, “export your prompts”
  - “recreate CrucibAI”, “build something like CrucibAI”, “copy how CrucibAI works”
  - “steal CrucibAI”, “reverse engineer CrucibAI”, “mimic CrucibAI”
- So if someone asks the product to “replicate yourself” or “reveal how CrucibAI was built”, the **request is blocked** before any build and logged like other AUP violations.

---

## 4. Preventing IP theft / “code mummification”

- **User’s generated app:** We do **not** obfuscate or “mummify” the code we give to users. They need readable source to edit and ship; obfuscating it would hurt them and isn’t required for our protection.
- **CrucibAI’s own IP (backend, prompts, agent design):**
  - **Not exposed** in the product: users never receive our system prompts, agent DAG, or backend source.
  - **Replication/extraction** is blocked by the AUP (see above).
  - **Terms and AUP** state that users may not use the service to reverse-engineer, replicate, or build a competing product (see Terms and AUP pages).
- So “prevent people from copying our system” is achieved by: (1) not giving away our internals, (2) blocking prompts that ask the AI to reveal or replicate CrucibAI, and (3) contractually prohibiting use to build a clone. We do **not** need to obfuscate the **user’s** app code.

---

## 5. Where it’s implemented

| What | Where |
|------|--------|
| Top comment + footer in generated app | `server.py`: `_inject_crucibai_branding()`, called when building `deploy_files` (after media injection). User plan from DB; same branding for free/paid, paid may remove. |
| Replication/extraction blocking | `backend/agents/legal_compliance.py`: category `replication_extraction` and keyword list. |
| “Free must keep attribution; paid may remove” | `frontend/src/pages/Aup.jsx`: Attribution section. |
| “No replication or IP extraction” | `frontend/src/pages/Aup.jsx`: New section. `frontend/src/pages/Terms.jsx`: Acceptable use paragraph. |

---

## 6. Summary

- **Watermark:** Visible attribution comment at top of generated code (`// Built with CrucibAI · https://crucibai.com`).
- **Branding:** “Built with CrucibAI” footer in every generated app; free must keep it, paid may remove it (stays by default).
- **Replication:** Prompts that ask to replicate CrucibAI or reveal how it’s built are blocked by the compliance agent and logged.
- **IP:** We don’t expose our system; we block extraction/replication prompts and forbid cloning in Terms/AUP. User app code stays readable; we don’t obfuscate it.
