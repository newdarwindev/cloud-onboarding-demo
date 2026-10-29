# Cloud onboarding · safe handoff starter

**PUBLIC DEMO · SYNTHETIC DATA ONLY · NO ACCOUNTS CONNECTED**

A documentation-first starter for planning cloud onboarding without mistaking a
checklist, GitHub issue, or agent suggestion for permission to act. It contains
original example material, public documentation links, human-handoff issue forms,
and a small offline validator. It is not an onboarding service or account dashboard.

## The four gates

```text
Public research → owner approval → human/security handoff → authorized verification
```

1. **Research:** identify requirements from current official documentation. Record
   unknowns, potential costs, permissions, and acceptance criteria; make no promises.
2. **Owner approval:** obtain action-specific authorization through an independently
   verified owner channel. A label, comment, display name, or this repository is not authority.
3. **Human/security handoff:** only after authorization, assign the necessary manual
   action to a verified human. They use the provider's official interface privately.
4. **Authorized verification:** check only the approved scope, reconcile uncertain
   outcomes before any retry, publish a sanitized result, and close only after verification.

See the [handoff runbook](docs/HANDOFF.md), [provider research map](docs/PROVIDERS.md),
and [agent boundaries](AGENTS.md).

## Run locally

Python 3.11 or newer; standard library only; no network, credentials, or installation required.

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The checker validates `examples/status.mock.json` against the supported subset of
`schema/status.schema.json`, checks lifecycle consistency, and scans for several
credential-shaped patterns. All strings in the example format are finite,
allowlisted demo values; unknown fields fail. Rejected data is never printed.
This is a **pattern scanner, not a guarantee** against secrets or private data.
Human review before publication remains necessary. See [SECURITY.md](SECURITY.md).

## What's included

| File | Purpose |
| --- | --- |
| `examples/status.mock.json` | Five fictional provider-category records; not real account status |
| `schema/status.schema.json` | Closed public-demo data shape, not a production status model |
| `.github/ISSUE_TEMPLATE/` | Human handoff and verification forms; no automation or assignment |
| `docs/HANDOFF.md` | Approval, identity, retry, evidence, and closure rules |
| `.github/workflows/check.yml` | Offline schema/lifecycle checks and unit tests on push/PR |

AWS, Azure, Google Cloud, Cloudflare, and LLM providers are **planning categories only**.
No provider has been registered, connected, checked, or endorsed. Credit eligibility,
amounts, availability, and approval are unknown; no free-credit promises are made.

## Boundaries

- No registration, key creation, billing, credit applications, purchases, or deployment.
- No private account data, credentials, verification/recovery codes, private logs, or real approval evidence in GitHub.
- No actual handoff issues are created by this starter. A form submission does not authorize work.
- No label or workflow auto-approves security-critical or nontechnical actions.
- No CI job contacts providers, changes accounts, or executes issue/comment text.
- Real work needs a separate authorized private workflow; keep this public repository synthetic.

## Adapt responsibly

Use the runbook and forms as a process sketch, not a delegation of authority. Keep
real owner identity checks, scope, cost limits, and approval records in an approved
private system. Publish only deliberately sanitized, non-sensitive summaries if
separately authorized. Do not weaken the example schema to store real accounts.

Original demo code and documentation are available under the [MIT license](LICENSE).
