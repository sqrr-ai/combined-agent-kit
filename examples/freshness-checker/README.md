# Source freshness checker example

Published September 15, 2026 by Combined.
Interactive guide: https://www.trycombined.com/resources/data-freshness-for-ai-agents#freshness-checker

Use the free browser checker to compare source or dataset commit timestamps with a policy chosen for your decision. No account is required. Inputs are held in page memory, and the checker makes no network calls, saves no inputs and includes no input values in a share URL. Downloads intentionally contain the metadata and policy you entered.

## Synthetic example

- `example-input.json` follows the maintained Combined get_freshness structured payload: `{ "data": [ ...sources ] }`. Every identity and value is fictional.
- `example-policy.json` selects three required datasets and a fixed decision time, September 15, 2026 at 12:00 UTC. It is a teaching policy, not a service guarantee or automatically enforced configuration.
- `expected-results.json` records the expected result specified before the checker: one required timestamp within policy, one stale, and one unknown.

HubSpot's synthetic source last committed two hours before the decision, but its selected company dataset is 30 hours old, exceeding the 24-hour dataset policy. Stripe invoices are one hour old within a four-hour limit. Intercom's selected dataset has no successful commit timestamp, even though the source has a timestamp and a syncing state. Source state does not override dataset age.

## Check your own timestamps

Start a new check and add source/dataset timestamps manually, or paste the structured JSON from Combined's get_freshness tool. Do not paste credentials or business records. Keep an explicit UTC or offset suffix and seconds in timestamps, such as `2026-09-15T12:00:00Z` or `2026-09-15T15:00:00+03:00`. Fractional seconds up to microseconds are accepted.

Review which items are required and set the age limit for each. Imports use dataset timestamps when datasets are listed, otherwise the source timestamp. A source-only check does not establish that required datasets exist. An empty data array is not a passing check.

When updating metadata for an existing check, matching identities retain their thresholds and required flags. Missing identities stay visible as unknown; new identities start optional. Manual requirements without an ID cannot be matched to imported IDs and remain missing. Start a new check to replace the intended scope.

Input is bounded to 131,072 characters, eight sources and 64 displayed checks. The checker does not execute imported text or follow URLs. Use smaller source/dataset selections for larger responses.

At the exact age limit, the timestamp meets the policy. A missing or invalid commit, a commit after the decision time, or absent metadata stays unknown. Invalid decision times, invalid required age limits and a policy with no required items disable downloads until corrected. Optional stale/unknown items, including invalid optional thresholds, remain visible without blocking required timestamps. Apply or discard pending JSON edits before downloading.

## What the report establishes

The JSON download includes schemaVersion, decision time, selected behavior, requirements, supplied metadata, per-item reason codes and a summary. Markdown includes the same policy/evidence and a reusable agent instruction. Obtain current metadata and use a new decision time for the next answer.

This is a calculation over supplied commit timestamps. It does not authenticate an account or prove permissions, query success, source-change-to-agent propagation delay, complete upstream records/fields/history, or a correct business answer. No fresh timestamp can turn missing data into zero activity. The policy does not enforce a production agent or trigger a sync.

References:
- https://www.trycombined.com/docs/integrations/mcp
- https://www.trycombined.com/docs/concepts/sources-and-freshness
- https://www.trycombined.com/resources/verify-ai-agent-business-data-answers
