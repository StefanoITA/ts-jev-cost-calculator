# Disclaimer

## No affiliation

ts-jev-cost-calculator is an independent, community-made, open-source project. It is not affiliated with, endorsed by, sponsored by, licensed by, or in any way officially connected to TypeSafe, the TypeSafe AI service, the Jev family of models, "System One", or any of their owners, operators, subsidiaries or affiliates. The author has no commercial or contractual relationship with them.

## Trademarks

"TypeSafe", "TypeSafe AI", "Jev", "System One" and any related product names, logos, domain names and marks are trademarks or registered trademarks of their respective owners. They appear in this project only to identify the third-party service the tool is designed to work with (nominative fair use). No trademark rights are claimed, and the use of these names does not imply any endorsement, approval or association. The name "ts-jev-cost-calculator" is purely descriptive. If a trademark owner believes a use in this repository is inappropriate, please open an issue and it will be addressed promptly.

## Not official information

Every number produced by this tool is an estimate. Token counts and costs are derived from the author's own statistical model of the `usage` counts returned by the API; the price and the limits are taken from the provider's public documentation at the time of writing. Nothing here comes from any agreement, specification or non-public information, and nothing here is a benchmark or a statement about the performance, quality or speed of the service. They are not pricing, billing, quota or contractual information of any kind. The only authoritative sources for what you are charged are your provider's official price list, your invoices, and the `usage` field returned in your own API responses. Prices, limits, model versions and tokenization can change at any time without notice; the author has no control over them and no obligation to update this project.

## No proprietary material

This project contains no code, model weights, tokenizer files or data belonging to TypeSafe. The bundled proxy tokenizer is an unrelated, publicly available open-source component (Qwen/Qwen2.5-7B tokenizer, Apache License 2.0, see NOTICE). The estimator is a statistical model: its coefficients were obtained by fitting a linear model on the token counts that the API itself reports in the `usage` field during the author's ordinary use of the API, in accordance with its public documentation. The author makes no statement about any contractual relationship with the service provider. No attempt was made to access, extract or analyse any internal component of the service. The tool never contacts the API and never sends data anywhere.

## Your own terms of service

Using this tool does not change, replace or interpret the terms you have accepted with your service provider. Every user remains solely responsible for their own compliance with those terms and with applicable law. The tool provides no access to any service, contains no credentials, does not act as a standalone or intermediary service, and does not call any API.

## Examples

The example request in `examples/` is a fictional customer message written for illustration; any resemblance to real persons, orders or companies is coincidental. The example response is the answer the API returned for that fictional input and is included only to demonstrate the `usage` command.

## Takedown

If a rights holder considers any part of this repository inappropriate, please open an issue or contact the author: the project will be renamed, or the content removed, promptly and without dispute.

## No warranty, no liability

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY CLAIM, DAMAGES, COSTS, LOSSES OR OTHER LIABILITY (INCLUDING, WITHOUT LIMITATION, UNEXPECTED API CHARGES, REJECTED REQUESTS OR BUSINESS DECISIONS BASED ON AN ESTIMATE), WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR ITS USE. Use it at your own risk and always verify important figures against real responses.

## License

The project is released under the MIT License (see LICENSE). Third-party components keep their own licenses (see NOTICE).
