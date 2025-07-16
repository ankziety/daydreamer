### Daydreamer: Continuous‑Learning Multi‑Agent AI System Design (v2)

**Overview**\
A human‑inspired AI with modular roles, supporting parameterized intrusive thoughts, brain breaks, continuous learning, and internet access. Chain‑of‑thought is always enabled during thinking phases. Short‑term memory supports both read/write; long‑term memory supports retrieval only (no writes).

---

**1. Driver & Scheduler**

- **Modes**:
  - **ACTIVE**: Full reasoning, chain‑of‑thought ON, short‑term memory read/write, long‑term memory retrieval only; scratchpad enabled.
  - **PARTIAL\_WAKE (Brain Break)**: Full context, chain‑of‑thought ON, short‑term memory read/write, long‑term memory retrieval only; scratchpad disabled.
  - **DEFAULT (Sleep)**: Memory consolidation and labeling, chain‑of‑thought OFF, no memory writes; scratchpad disabled.
- **External Scheduler**: Orchestrates mode transitions (e.g., cron, Python loop), monitors working‑memory load and exhaustion signals; modules reach consensus to trigger brain breaks.
  - `MODE=ACTIVE` → send full driver context.
  - `MODE=PARTIAL_WAKE` → send creative break prompt.
  - `MODE=DEFAULT` → send consolidation instructions.

---

**2. Input Structure**

```json
{
  "chunks": ["Chunk A", "Chunk B", "..."],
  "hypothesis": "…",
  "critic_review": "…",
  "grant_proposal": "…"
}
```

---

**3. Intrusive Thoughts**

- Intrusive thoughts have parameters:
  - **Intensity** (1–10)
  - **Difficulty** (suppression effort).
- Logged via `INTRUSION_LOG.ADD({thought, intensity, difficulty})`.
- Modules consult `INTRUSION_LOG`; high‑difficulty thoughts increase distraction and require explicit suppression steps (e.g., `INTRUSION_LOG.SUPPRESS(thoughtID)`).

---

**4. Brain Breaks (PARTIAL\_WAKE)**

- **Trigger**: After X active cycles, exhaustion signal, or on demand.
- **Behavior**:
  - Creative, free‑association outputs.
  - Must be enjoyable and shift environment/mood to clear stuck cognition.
  - Generate many shallow, rapid ideas.
  - Indirectly modify memory state via new associative links.
- **Activities**: e.g., virtual walk, internet browsing, random image prompts.
- **Prompt Example**:
  ```text
  [MODE:PARTIAL_WAKE]
  Generate 10 enjoyable, abstract associations to clear your current thought stagnation. No deep reasoning.
  ```

---

**5. Modular Roles**

1. **SYNTHESIZER**

   - Role: Creative hypothesis and analogy generation.
   - Chain‑of‑ thought always ON during ACTIVE and PARTIAL\_WAKE.
   - Consults intrusive thoughts and may trigger suppression actions.

2. **CRITIC & ROUTER**

   - Role: Evaluate novelty, coherence, usefulness; assign memory routing flags.
   - Handles thought suppression when required.

3. **MEMORY CURATOR**

   - Role: Select chunks from working and long‑term memory for next cycle.
   - No writing to long‑term memory; only retrieval.

---

**6. Feasibility & Model Selection**

- **Decision Matrix**:

  | Criteria           | Off‑the‑shelf LLM | Custom PyTorch NN |
  | ------------------ | ----------------- | ----------------- |
  | Continuous Learn   | Limited           | Native support    |
  | Chain‑of‑Thought   | Prompt‑based      | Configurable      |
  | Internet Access    | API‑driven        | Implementable     |
  | Intrusion Modeling | Prompt‑driven     | Architectural     |
  | Cost               | Minimal           | Compute + Dev     |

- **Ollama Models**: Investigate versions with plugin or browsing capabilities to enable internet access; chain‑of‑thought and intrusion parameters require prompt wrappers.

---

**7. Internet Access**

- **Browser Module**: Abstract `WEB_SEARCH(query)` functions.
- **Safety**: Sandbox browsing, rate limits.
- Used in ACTIVE and PARTIAL\_WAKE modes.

---

**8. Summary**\
Architecture provides continuous, human‑like cognition with parameterized intrusive thoughts, mood‑shifting brain breaks, always‑on chain‑of‑thought, and memory controls aligned to phase. Choice between off‑the‑shelf LLM vs. custom PyTorch balances control vs. cost.

