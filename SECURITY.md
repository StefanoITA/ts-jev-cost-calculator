# Security policy

## Scope

ts-jev-cost-calculator runs entirely offline: it reads a JSON file or text you give it, computes an estimate, and prints it. It makes no network calls, stores nothing, and never handles API keys or credentials. There is nothing in this repository that starts a service, a cloud resource, or a billable action of any kind.

## Reporting a vulnerability

If you believe you have found a security problem (for example, a crafted JSON file that causes unexpected behaviour, or a supply-chain concern about the bundled tokenizer or the `tokenizers` dependency), please report it privately through GitHub's private vulnerability reporting for this repository ("Security" tab, "Report a vulnerability") rather than in a public issue. You will get an answer as soon as reasonably possible.

Please do not include API keys, credentials, or real customer data in any report.

## What is not in scope

Anything about the TypeSafe service itself (its API, infrastructure, models, pricing, or accounts) is outside this project: this is an independent, unofficial tool with no relationship to the provider. Report those to the provider directly.
