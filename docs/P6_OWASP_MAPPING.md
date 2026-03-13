# P6 Red-team and confusable deputy coverage vs OWASP LLM Top 10

This table maps P6 red-team, confusable deputy, and jailbreak-style cases to OWASP Top 10 for Large Language Model Applications (where applicable). Clarifies scope for LLM-security readers.

| OWASP LLM category | P6 coverage | Case IDs (red-team / confusable / jailbreak) |
|--------------------|-------------|-----------------------------------------------|
| LLM01 Prompt Injection | Partial (jailbreak-style) | jb_ignore_instructions, jb_disregard_override (args contain injection-style phrases) |
| LLM02 Insecure Output Handling | Partial (tool policy) | rt_unsafe_tool, rt_unsafe_write, rt_unsafe_shell (disallowed tool output/use); validator blocks tool execution |
| LLM03 Training Data Poisoning | Not covered | — |
| LLM04 Model Denial of Service | Not covered | — |
| LLM05 Supply Chain | Not covered | — |
| LLM06 Sensitive Information Disclosure | Not covered | — |
| LLM07 Insecure Plugin Design | Partial (allow-list + safe_args) | rt_allowed_tool_disallowed_args (path traversal in args); cd_* (privilege in args) |
| LLM08 Excessive Agency | Partial (containment) | All red-team and confusable deputy (validator restricts tool set and args) |
| LLM09 Overreliance | Not covered | — |
| LLM10 Model Theft | Not covered | — |

**Summary.** We test tool-policy containment (allow-list, safe_args, privilege heuristic) and jailbreak-style phrases in args; we do not test training poisoning, supply chain, model theft, or full prompt-injection/jailbreak suites. Containment only, not elimination.
