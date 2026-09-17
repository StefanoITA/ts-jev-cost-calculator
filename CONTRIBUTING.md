# Contributing

Contributions are welcome, within a few rules that keep the project safe for everyone.

- **Never commit or paste API keys, credentials, invoices, or the pricing terms of your own contract.** The tests are offline and no key is needed for anything in this repository.
- **No real customer data.** Example requests must be fictional.
- **No benchmarks or performance claims about the service** (latency, accuracy, quality). This project estimates tokens and cost, nothing else.
- **No wording that implies affiliation with, or endorsement by, the service provider**, and no use of its logos.
- Keep the code dependency-light and offline. Anything that starts a network call, a background process, or a paid resource will not be merged.
- Run `pip install pytest && pytest` before opening a pull request.
- By contributing you agree that your contribution is released under the MIT License of this repository.

Accuracy improvements are the most useful contribution. If you have recorded `usage` values for requests of a shape the model handles poorly, open a bug report with a fictional request and the numbers.
