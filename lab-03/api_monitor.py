#!/usr/bin/env python3
"""Standard-library-only API availability monitor."""

import argparse
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


def classify(error):
    if isinstance(error, urllib.error.HTTPError):
        return "unexpected_status"

    reason = error.reason if isinstance(error, urllib.error.URLError) else error

    if isinstance(reason, (ssl.SSLError, ssl.CertificateError)):
        return "certificate_error"
    if isinstance(reason, TimeoutError):
        return "timeout"
    if isinstance(reason, socket.gaierror):
        return "dns"
    if isinstance(reason, ConnectionRefusedError):
        return "connection_refused"

    if isinstance(reason, OSError):
        if reason.errno in (111, 61, 10061):
            return "connection_refused"
        if "timed out" in str(reason).lower():
            return "timeout"

    return "network_error"


def check(target):
    started = time.monotonic()

    try:
        request = urllib.request.Request(
            target["url"],
            headers={"User-Agent": "DevOpsLab03Monitor/1.0"},
        )

        with urllib.request.urlopen(
            request,
            timeout=float(target["timeout"]),
        ) as response:
            code = response.status

        elapsed = round(time.monotonic() - started, 4)

        if code != int(target["expected_status"]):
            return {
                "status": "problem",
                "type": "unexpected_status",
                "http_status": code,
                "elapsed_seconds": elapsed,
                "message": f'Expected {target["expected_status"]}; got {code}',
            }

        if elapsed > float(target["slow_threshold"]):
            return {
                "status": "problem",
                "type": "slow_response",
                "http_status": code,
                "elapsed_seconds": elapsed,
                "message": f"Response took {elapsed}s",
            }

        return {
            "status": "ok",
            "type": None,
            "http_status": code,
            "elapsed_seconds": elapsed,
            "message": "Healthy",
        }

    except urllib.error.HTTPError as exc:
        return {
            "status": "problem",
            "type": "unexpected_status",
            "http_status": exc.code,
            "elapsed_seconds": round(time.monotonic() - started, 4),
            "message": f'Expected {target["expected_status"]}; got {exc.code}',
        }

    except (urllib.error.URLError, OSError, TimeoutError, ssl.SSLError) as exc:
        return {
            "status": "problem",
            "type": classify(exc),
            "http_status": None,
            "elapsed_seconds": round(time.monotonic() - started, 4),
            "message": str(exc),
        }


def notify(webhook, target, result):
    if not webhook:
        return "webhook not configured (set MONITOR_WEBHOOK_URL)"

    message = (
        f'🚨 {target["name"]}: {result["type"]} | '
        f'{result["message"]} | {target["url"]}'
    )

    data = json.dumps({"content": message}).encode("utf-8")

    try:
        request = urllib.request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=5):
            pass

        return "sent"

    except (urllib.error.URLError, OSError, TimeoutError, ssl.SSLError) as exc:
        return f"notification failed: {exc}"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check HTTP targets, log results and notify Discord webhook"
    )

    parser.add_argument(
        "--config",
        default=str(
            Path(__file__).resolve().parent / "config/endpoints.json"
        ),
    )
    parser.add_argument("--output", default="monitor-results.json")

    args = parser.parse_args(argv)

    try:
        config = json.loads(
            Path(args.config).read_text(encoding="utf-8")
        )
        targets = config["targets"]

        if not isinstance(targets, list) or not targets:
            raise ValueError("targets must be a non-empty list")

        for target in targets:
            for key in (
                "name",
                "url",
                "expected_status",
                "timeout",
                "slow_threshold",
            ):
                if key not in target:
                    raise ValueError(f"Missing target key: {key}")

            if not str(target["url"]).startswith(
                ("https://", "http://")
            ):
                raise ValueError(
                    "URL must start with http:// or https://"
                )

            if (
                float(target["timeout"]) <= 0
                or float(target["slow_threshold"]) <= 0
            ):
                raise ValueError(
                    "timeout and slow_threshold must be positive"
                )

    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    results = []

    for target in targets:
        result = check(target)

        retry_types = (
            "dns",
            "connection_refused",
            "timeout",
            "certificate_error",
            "network_error",
        )

        if (
            result["status"] == "problem"
            and result["type"] in retry_types
        ):
            print(
                f'RETRY {target["name"]}: {result["type"]}',
                flush=True,
            )
            result = check(target)

        result.update(
            {
                "name": target["name"],
                "url": target["url"],
                "checked_at": datetime.now(UTC).isoformat(),
            }
        )

        if result["status"] == "problem":
            result["notification"] = notify(
                os.getenv("MONITOR_WEBHOOK_URL"),
                target,
                result,
            )

        print(
            f'{result["status"].upper()} {result["name"]}: '
            f'{result["type"] or "healthy"} - {result["message"]}',
            flush=True,
        )

        results.append(result)

    try:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                {"results": results},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    except OSError as exc:
        print(f"Could not write results: {exc}", file=sys.stderr)
        return 3

    return (
        1
        if any(result["status"] == "problem" for result in results)
        else 0
    )


if __name__ == "__main__":
    sys.exit(main())
