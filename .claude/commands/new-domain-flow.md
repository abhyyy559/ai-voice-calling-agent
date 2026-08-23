Use the conversation-ai-agent to create a new call domain config.

Ask me (if not already given in this conversation) for: the domain name, the goal of the call, the ordered list of questions/topics to cover, the structured fields to extract (name, type, required/optional), and any escalation triggers specific to this domain.

Then produce a new file under /domain-configs following the existing format (see /domain-configs/absent-student.json as the reference example), plus 2-3 example conversation snippets with their expected extracted output, so qa-eval-agent can turn them into regression tests.

Confirm at the end: this should have required zero changes to /backend or /voice-agent code — if it did, flag that as a violation of the domain-independence requirement in PRD.md §4.3 and explain what forced the code change.
