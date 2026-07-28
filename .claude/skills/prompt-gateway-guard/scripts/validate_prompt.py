#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Call PromptGateway's POST /api/v1/validate endpoint and print its decision.

Sends the given prompt text to a running PromptGateway instance for policy
screening (PII, secrets, prompt-injection, toxicity, token-limit checks) and
prints the response JSON verbatim to stdout. Uses only the standard library
(urllib) so no extra dependency install is needed.

Prints one JSON object to stdout on success, matching PromptGateway's
PromptValidateResponse shape:
  {"request_id": "...", "decision": "ALLOW"|"FLAG"|"BLOCK", "risk_score": 0-100,
   "token_count": int, "sanitized_prompt": "...", "categories_triggered": [...],
   "timestamp": "...", "reason": "...", "validator_results": [...]}

On failure to reach the service, prints:
  {"result": "unreachable", "base_url": "...", "error": "..."}
On an HTTP error response (4xx/5xx), prints:
  {"result": "http_error", "status": <code>, "body": "..."}
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, help="Prompt text to validate (1-50000 chars)")
    parser.add_argument("--base-url", required=True, help="PromptGateway base URL, e.g. http://localhost:8000")
    parser.add_argument("--api-key", default="", help="Value for the X-API-Key header (omit if not required)")
    parser.add_argument("--user-id", default="", help="Optional user_id to attach to the request")
    parser.add_argument("--model", default="", help="Optional downstream model name (must be in PromptGateway's allowed_models policy list)")
    parser.add_argument("--timeout", type=float, default=15.0, help="Request timeout in seconds (default: %(default)s)")
    parser.add_argument("-o", "--output", help="Write result JSON here instead of stdout")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    body = {"prompt": args.prompt}
    if args.user_id:
        body["user_id"] = args.user_id
    if args.model:
        body["model"] = args.model

    url = args.base_url.rstrip("/") + "/api/v1/validate"
    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    if args.verbose:
        print(f"POST {url}", file=sys.stderr)

    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        result = {"result": "http_error", "status": exc.code, "body": exc.read().decode("utf-8", errors="replace")}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        result = {"result": "unreachable", "base_url": args.base_url, "error": str(exc)}

    output_text = json.dumps(result)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
