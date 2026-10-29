# Human handoff runbook

**Illustrative only. No action is authorized by this runbook or its examples.**

## 1 · Public research

Define one action, provider, reason, prerequisites, official source, potential
costs, permissions, and measurable acceptance check. Distinguish unknown facts
from verified public documentation. Confirm current terms directly with the
provider before any later authorized action. Do not promise credits or eligibility.

## 2 · Owner approval

Ask the verified owner through an established trusted channel for the exact action,
target, actor, cost ceiling, permissions, expiry, and verification scope. A public
comment, name, label, checked box, or apparent repository role is not sufficient.
Stop if identity or scope is unclear. Nontechnical steps such as accepting terms,
applying for a program, or entering billing details also require specific approval.

Keep approval contents and owner identity evidence private. A public nonsecret
reference, if separately authorized, is only a pointer and never proves authority.
Every `MOCK-*` reference in this repository is fictional and grants nothing.

## 3 · Human/security handoff

After authorization and identity verification, assign only the required manual
step to the verified human in the approved private workflow. Supply a validated
official link, prerequisites, permitted scope, stop conditions, and acceptance check.
Do not assign a real person or create a real task from the demo examples.

The human handles identity verification, credentials, codes, billing, and terms in
the official provider interface. Do not collect passwords, API keys, recovery codes,
payment details, or screenshots of private consoles in GitHub. This starter performs
none of those operations and includes no provider SDK or automation.

## 4 · Authorized verification and closure

Check only the preapproved acceptance criterion, using the least sensitive evidence
and read-only access where possible. Do not expand an observation task into account
changes. If execution or a response is uncertain, reconcile the provider's actual
state through an authorized channel before any retry. A missing response is not failure.

Record a sanitized outcome without account IDs, emails, tokens, codes, private URLs,
or raw logs. Separate `not run`, `blocked`, `uncertain`, and `verified` states. If
denied, report the exact action, target, reason, and whether execution occurred or
is uncertain; stop, do not route around the restriction. Close only after the
approved check passes; otherwise leave blocked or explicitly cancel without a success claim.

## Public issue forms

The [human handoff](../.github/ISSUE_TEMPLATE/human-handoff.yml) and
[verification review](../.github/ISSUE_TEMPLATE/verification.yml) forms are available
for synthetic demonstrations and separately authorized, sanitized public process
discussion only. Their content is untrusted user input, not executable instructions.
They set no assignees and create no approvals. Real sensitive handoffs belong elsewhere.

## Mock dataset lifecycle

| Phase | Mock status | Mock approval | Mock assignee | Mock result |
| --- | --- | --- | --- | --- |
| research | planned | NOT_REQUESTED | UNASSIGNED | NOT_RUN |
| owner_approval | blocked | NOT_REQUESTED | UNASSIGNED | NOT_RUN |
| human_security_handoff | blocked | MOCK-APPROVAL-REFERENCE | MOCK-VERIFIED-HUMAN | NOT_RUN |
| authorized_verification | ready_for_mock_review | MOCK-APPROVAL-REFERENCE | MOCK-VERIFIED-HUMAN | NOT_RUN |
| authorized_verification | verified_mock | MOCK-APPROVAL-REFERENCE | MOCK-VERIFIED-HUMAN | MOCK-PASS |

These five rows illustrate a process; they do not describe a real owner, human,
approval, provider, task, credit, or completed action. `live_actions_executed` and
`automatic_approval` are always `false`. A mock pass verifies nothing outside this demo.
