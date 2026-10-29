# Security and privacy

This public demo has no provider credentials, backend, network integration, or real
account state. Do not use GitHub issues to transmit sensitive material.

## If something sensitive is exposed

Stop publication and further copying. Notify the verified owner through an already
trusted private channel; do not post the value or a private log in a public report.
The owner should handle revocation/rotation, exposure review, and repository cleanup
under explicit authorization. Deleting a file or comment does not remove every copy.
Never test a suspected credential or attempt to log in with it.

For a vulnerability in the demo, share a minimal synthetic reproduction. For a
sensitive report, use a verified private maintainer channel or GitHub private
vulnerability reporting **if available**; this starter does not enable that setting.

## Guardrails and limits

`scripts/validate.py` fails on unknown JSON fields, unsupported schema keywords,
duplicate JSON keys, non-allowlisted values, inconsistent mock lifecycle states,
and selected credential-shaped patterns. Diagnostics identify locations, not values.
The public demo schema deliberately accepts only a narrow set of synthetic strings.

The scanner is a **pattern scanner, not a guarantee**. It is not a complete secret,
personal-data, or entropy detector. It cannot inspect GitHub issues, external links,
remote history, screenshots, encrypted data, or uncommitted files outside its input.
CI validates the example dataset and tests; it is not a repository-wide DLP service.
Manual review of every public change is required. Do not broaden the schema as a
shortcut for publishing real data. Use a separate approved private system instead.

Issue forms guide people but cannot enforce authorization, identity, or confidentiality.
No workflow consumes issues/comments, and no user-provided text is executed.
