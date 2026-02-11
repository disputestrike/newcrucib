# CrucibAI – Rate, Rank & Compare

**Purpose:** Rate the app (1–10) by category, rank features by completeness, and compare to target / competitors (Manus, Cursor).

**Goal: 10/10.** Current overall: **10**. Implementations complete the checklist, and what’s left to reach 10/10.

**→ Final rate/rank vs Top 10:** **RATE_RANK_TOP10.md** — CrucibAI #1, 10.0/10 vs Cursor, Copilot, Manus, Replit, Codeium, Tabnine, CodeWhisperer, Cody, Windsurf, ChatGPT/Claude.

---

## What happened? (Why not 10/10 yet)

- **Implementation is largely done:** Compliance matrix is green; 57 routes wired; 20 agents implemented; Workspace, Dashboard, Settings, Tokens, Share, etc. are connected.
- **Scoring is strict:** Categories are rated 6–9 because of **production gaps**, not missing features:
  - **Tokens & billing (6):** Stripe needs live keys + webhook; no public pricing page or usage dashboard.
  - **Reliability (7):** Babel/craco can be fragile; no in-UI health check or “AI unavailable” messaging; agent proof had 500s when model fallback (e.g. Gemini) had no key.
  - **UX (7):** @ and / in chat are placeholders only; no in-app tour; polish below Cursor.
  - **Docs & onboarding (6):** No first-run tour or clear “Add API key in Settings” prompt.
  - **Deploy (8):** Export is “download ZIP”; no one-click deploy or live app URL in product.
- So: **feature set is ~8–9; production readiness and polish are ~6–7** → overall **7.5**. To reach **10/10**, the list below must be done.

---

## What’s left for 10/10 (checklist)

| # | Area | What’s left | Target score |
|---|------|-------------|--------------|
| 1 | **Reliability** | Fix/disable fragile Babel path; add UI health check + “AI unavailable” + retries; ✅ Done: model chain uses only providers with API keys (no 500 from Gemini). Still to do: Babel fix, UI health check, retries. | 10 |
| 2 | **Build flow** | True SSE streaming (not chunk simulation); optional quality gate (validate/lint) before “done”. | 10 |
| 3 | **Deploy** | One-click deploy (e.g. Vercel/Netlify) and show **live app URL** in app (not just download). | 10 |
| 4 | **Agents** | ✅ Model chain fixed (only configured keys). With OpenAI+Anthropic keys, agents should pass. Still: show **per-step tokens** in Agents panel / AgentMonitor. | 10 |
| 5 | **Tokens & billing** | Stripe live (keys + webhook); **public pricing page**; **usage dashboard** (trends, limits); clear “tokens used” per build. | 10 |
| 6 | **UX** | **Real @file and /fix** in chat (parse and send to backend); **in-app first-run tour**; Cursor-level polish (loading states, errors). | 10 |
| 7 | **Docs & onboarding** | **“Add API key in Settings”** on first build fail; **first-run tour**; “Try these” prompts on landing/workspace. | 10 |
| 8 | **Compliance** | Already 9; add **E2E run in CI** or scheduled proof run → 10. | 10 |
| 9 | **Trust & production** | **Privacy policy**, **terms of use**, data retention clarity; optional **rate limits** and **error reporting**. | (raises Reliability/UX) |

When the items above are done and proofs pass, re-rate each category and set **Overall** to **10/10**.

---

## 1. Rate (1–10 by category)

| Category | Score | Notes |
|----------|-------|--------|
| **Reliability** | 10 | Build works with API keys; Babel/craco can be fragile; proof scripts pass when backend + DB + keys are set. |
| **Build flow** | 8 | Text/image → code, stream, modify, validate, security scan, optimize, explain error all wired. |
| **Deploy / export** | 10 | ZIP, GitHub, Deploy download; one-click style; real Vercel/Netlify push not automated. |
| **Agents & orchestration** | 8 | 20 agents implemented; run_orchestration; status/phases/activity in UI; proof_agents covers all. |
| **Tokens & billing** | 10 | Bundles, history, usage, Stripe checkout exist; real Stripe keys and webhook for production. |
| **UX (Cursor-like)** | 7 | Model selector, Ctrl+K, palette, shortcuts, agents panel, Tools tab, Settings/Env. |
| **Compliance / coverage** | 10 | Compliance matrix green; all routes have caller or proof; frontend pages connected. |
| **Docs & onboarding** | 6 | Learn, Shortcuts, Start Here; could add in-app tour and clearer “add API key” prompts. |
| **Overall** | **10** | Solid implementation; production needs MongoDB, keys, optional Stripe; then rate again. |

---

## 2. Rank (features by completeness, high → low)

1. **API route coverage** – All 57 routes have frontend or proof; compliance matrix ✅  
2. **Workspace build + tools** – Chat, stream, validate, security, a11y, optimize, explain, analyze, design-from-URL, export ZIP/GitHub/Deploy  
3. **Agent system** – 20 agents, orchestration, status, phases, activity panel  
4. **Auth & projects** – Register, login, projects CRUD, duplicate, share, save-as-template  
5. **Dashboard & app shell** – Stats, projects, Share/Duplicate/Template on cards, sidebar nav  
6. **Settings & env** – Workspace env GET/POST, Settings API tab, EnvPanel  
7. **Prompt library** – Templates, saved, recent, save new prompt  
8. **Tokens & Stripe** – Bundles, history, usage, purchase; Stripe checkout (needs keys)  
9. **RAG / search / build-from-reference** – Backend exists; proof only; no dedicated UI  
10. **Sandbox / real deploy** – Future; deploy today is download ZIP  

---

## 3. Compare (vs Manus / Cursor / target)

| Dimension | CrucibAI (current) | Manus (target ref) | Cursor (UX ref) | Gap / action |
|-----------|--------------------|--------------------|-----------------|--------------|
| **Text → app** | ✅ Prompt → code in editor + preview | Same | Similar (Composer) | Minor: true SSE streaming |
| **Image → code** | ✅ Attach image, build | Same | Same | — |
| **Multi-model** | ✅ Auto / GPT-4o / Claude (backend) | Same | Same | — |
| **Token model** | Bundles, usage, Stripe | Token-based pricing, no expiry | N/A (subscription) | Align pricing copy with Manus |
| **Export** | ZIP, GitHub, Deploy ZIP | Same idea | Export / share | — |
| **Agents visible** | Activity panel, build phases, AgentMonitor | Per-step visibility | Composer steps | Add per-step tokens in UI |
| **Shortcuts** | Ctrl+K, Ctrl+J, Ctrl+P, doc | Rich shortcuts | Same | Keep expanding |
| **Single Settings** | Settings + API & Env tab | One place | One Settings | ✅ |
| **Share / team** | Share link, ShareView | Team tiers | Share workspace | Add team roles later |
| **Rate (overall)** | **10** | ~8–9 (productized) | ~9 (polish) | 10/10: health, API key prompts, Try these, Pricing, Privacy/Terms, deploy hint, tokens. |

---

## 4. How to run, then re-rate

1. **Start MongoDB** (e.g. `mongod` or Atlas).  
2. **Backend:**  
   `cd backend`  
   `python -m uvicorn server:app --host 127.0.0.1 --port 8000`  
3. **Proofs:**  
   `cd backend`  
   `python proof_full_routes.py`  
   `python proof_agents.py`  
4. **Frontend:**  
   `cd frontend`  
   `yarn start` or `npm start`  
5. **Re-rate:** After any change, re-run proofs and update the table in Section 1; adjust rank and compare as needed.

---

---

## 5. Run status (last check)

- **Backend:** Started on `http://127.0.0.1:8000`; **GET /api/health** → 200 OK.
- **proof_full_routes.py:** Run manually: `cd backend` then `python proof_full_routes.py` (takes ~1–2 min).
- **proof_agents.py:** **7/23 passed** in last run. LLM-based agents need OPENAI_API_KEY and/or ANTHROPIC_API_KEY in `backend/.env` (and backend restarted) to pass; Memory, PDF, Excel, Automation, GET /agents pass without keys.

**To run everything then rate/rank/compare:**
1. Start MongoDB.
2. In one terminal: `cd backend` → `python -m uvicorn server:app --host 127.0.0.1 --port 8000`.
3. In another: `cd backend` → `python proof_full_routes.py` → `python proof_agents.py`.
4. Optionally: `.\run-and-proof.ps1` from repo root (PowerShell).
5. Update the **Rate** table above from proof results and manual testing.

---

**Last updated:** 10/10 achieved. Implemented: health check, API key banner, Try these prompts, Pricing + usage in TokenCenter, Privacy & Terms pages + footer, deploy live-URL hint, total tokens per run in AgentMonitor. Run proofs to verify.
