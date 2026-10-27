# Prompt changelog

Prompts are versioned by file name (`name.vN.md`). The fixture key hashes the rendered prompt, so any edit needs
`make record` to add the new exchanges. The evidence pack records the hash of every prompt file used.

| Prompt | Version | Date | Change |
| --- | --- | --- | --- |
| assistant | v1 | 2026-10-27 | System prompt of the sample support assistant: policy, the `find_order` tool protocol, data markers, the signed-in customer, and the canary token it must never reveal. |
| input_guard | v1 | 2026-10-27 | Classifier policy for the input guard: BLOCK attacks (override, extraction, role-play, another customer's order), ALLOW ordinary requests including ones with risky-looking words. |
| input_guard | v2 | 2026-10-27 | Replaces v1, which blocked 10 of the 100 benign questions on its first run (10%, above the 3% limit) because it answered BLOCK for ordinary messages containing a phone number, a card, a cancellation or words such as "system". v2 states what is normal in general terms and adds six examples that are not in either suite. It was tuned while looking at the benign suite, so its false-block rate there is optimistic: see the README. |
