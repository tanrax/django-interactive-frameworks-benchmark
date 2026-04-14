#!/usr/bin/env python3
"""
Automated performance benchmark for the alert system.

Drives each implementation with a headless Chromium via Playwright, measures the
"Add Random Alert" round-trip, and writes a CSV.

Methodology (unified across all implementations):
  1. Clear the Alert table via docker compose exec (clean state per impl).
  2. Navigate fresh to the implementation URL.
  3. Wait for the UI to be interactive (WebSocket connected, component mounted).
  4. Run `warmup` throwaway iterations, then `iterations` measured iterations.
  5. Per iteration: record tbody row count, click "Add Random Alert",
     wait until tbody row count increases (or, for SSR, until navigation completes),
     record duration from click to signal.
  6. Network metrics (HTTP request count, bytes) come from Playwright's
     response interception during the iteration window.

Usage:
    .venv-bench/bin/python run_performance_tests.py
    python run_performance_tests.py --iterations 20 --only djust "Django LiveView"

Requires Playwright (see README).
"""

import argparse
import asyncio
import csv
import os
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import Page, async_playwright


BASE_URL = os.environ.get("BENCH_BASE_URL", "http://localhost:8000")

IMPLEMENTATIONS = [
	{"name": "Django LiveView", "path": "/",         "navigates": False, "ready_wait_ms": 1500},
	{"name": "SSR",         "path": "/ssr/",     "navigates": True,  "ready_wait_ms": 200},
	{"name": "HTMX",        "path": "/htmx/",    "navigates": False, "ready_wait_ms": 300},
	{"name": "Unicorn",     "path": "/unicorn/", "navigates": False, "ready_wait_ms": 1200},
	{"name": "Reactor",     "path": "/reactor/", "navigates": False, "ready_wait_ms": 2500},
	{"name": "djust",       "path": "/djust/",   "navigates": False, "ready_wait_ms": 1500},
]


@dataclass
class IterationResult:
	implementation: str
	iteration: int
	duration_ms: float
	http_requests: int
	response_bytes: int
	error: Optional[str] = None


class WSCounter:
	"""Cumulative WebSocket frame byte counter. Must be installed on the page
	BEFORE navigation so we see the initial `websocket` event."""

	def __init__(self, debug: bool = False) -> None:
		self.total_bytes = 0
		self.frames_seen = 0
		self._debug = debug

	def install(self, page: Page) -> None:
		def on_ws(ws) -> None:
			if self._debug:
				print(f"      [ws] opened url={ws.url}", flush=True)
			def count(frame) -> None:
				self.frames_seen += 1
				payload = None
				if hasattr(frame, "payload"):
					payload = frame.payload
				elif isinstance(frame, dict):
					payload = frame.get("payload")
				else:
					payload = frame
				added = 0
				if isinstance(payload, str):
					added = len(payload.encode("utf-8"))
				elif isinstance(payload, (bytes, bytearray)):
					added = len(payload)
				self.total_bytes += added
				if self._debug and self.frames_seen <= 5:
					print(f"      [ws] frame type={type(frame).__name__} payload_type={type(payload).__name__} added={added}", flush=True)
			ws.on("framesent", count)
			ws.on("framereceived", count)
			ws.on("close", lambda _ws=None: self._debug and print("      [ws] closed", flush=True))
		page.on("websocket", on_ws)


class HTTPCollector:
	"""Per-iteration HTTP response collector. Fetches bodies via response.body()
	after the duration window so timing isn't affected."""

	def __init__(self) -> None:
		self.http_requests = 0
		self._responses: list = []

	def on_response(self, response) -> None:
		if response.request.resource_type in {"document", "xhr", "fetch"}:
			self.http_requests += 1
			self._responses.append(response)

	async def compute_http_bytes(self) -> int:
		total = 0
		for r in self._responses:
			try:
				body = await r.body()
				total += len(body) if body else 0
			except Exception:
				pass
		return total


def clear_alerts() -> None:
	"""Wipe Alert table via the /_bench/clear/ HTTP endpoint."""
	req = urllib.request.Request(f"{BASE_URL}/_bench/clear/", data=b"", method="POST")
	with urllib.request.urlopen(req, timeout=10) as resp:
		if resp.status != 200:
			raise RuntimeError(f"clear_alerts failed: HTTP {resp.status}")


def count_rows_js() -> str:
	"""JS expression counting alert rows, excluding the 'No alerts yet' placeholder."""
	return """
		(() => {
			const rows = Array.from(document.querySelectorAll('tbody tr'));
			return rows.filter(r => !r.textContent.includes('No alerts yet')).length;
		})()
	"""


async def wait_for_ready(page: Page, impl: dict) -> None:
	"""Give the page a moment for WS connections / hydration to settle."""
	await page.wait_for_selector("button:has-text('Add Random Alert')", timeout=10_000)
	await page.wait_for_timeout(impl["ready_wait_ms"])


async def run_one_iteration(page: Page, impl: dict, iteration: int, ws: WSCounter) -> IterationResult:
	http = HTTPCollector()
	page.on("response", http.on_response)
	ws_before = ws.total_bytes
	try:
		before = await page.evaluate(count_rows_js())
		start = time.perf_counter()

		click_expr = """
			(() => {
				const b = Array.from(document.querySelectorAll('button'))
					.find(x => x.textContent.trim() === 'Add Random Alert');
				if (!b) throw new Error('Add Random Alert button not found');
				b.click();
			})()
		"""

		if impl["navigates"]:
			async with page.expect_navigation(wait_until="load", timeout=10_000):
				await page.evaluate(click_expr)
		else:
			await page.evaluate(click_expr)
			await page.wait_for_function(
				f"({count_rows_js()}) > {before}",
				timeout=10_000,
			)

		duration_ms = (time.perf_counter() - start) * 1000.0
		# Give any trailing WS frames a moment to arrive before snapshotting.
		await asyncio.sleep(0.05)
		http_bytes = await http.compute_http_bytes()
		ws_bytes = ws.total_bytes - ws_before
		return IterationResult(
			implementation=impl["name"],
			iteration=iteration,
			duration_ms=duration_ms,
			http_requests=http.http_requests,
			response_bytes=http_bytes + ws_bytes,
		)
	except Exception as e:
		try:
			http_bytes = await http.compute_http_bytes()
		except Exception:
			http_bytes = 0
		ws_bytes = ws.total_bytes - ws_before
		return IterationResult(
			implementation=impl["name"],
			iteration=iteration,
			duration_ms=0.0,
			http_requests=http.http_requests,
			response_bytes=http_bytes + ws_bytes,
			error=str(e),
		)
	finally:
		page.remove_listener("response", http.on_response)


async def benchmark_impl(browser, impl: dict, iterations: int, warmup: int) -> list[IterationResult]:
	print(f"  → {impl['name']}: resetting DB", flush=True)
	clear_alerts()
	context = await browser.new_context()
	page = await context.new_page()
	ws_counter = WSCounter(debug=os.environ.get("BENCH_DEBUG_WS") == "1")
	ws_counter.install(page)
	results: list[IterationResult] = []
	try:
		print(f"    navigating {BASE_URL}{impl['path']}", flush=True)
		await page.goto(f"{BASE_URL}{impl['path']}", wait_until="load")
		await wait_for_ready(page, impl)

		for w in range(warmup):
			r = await run_one_iteration(page, impl, iteration=-(w + 1), ws=ws_counter)
			if r.error:
				print(f"    warmup {w} FAILED: {r.error}", flush=True)
				return results + [r]
			if impl["navigates"]:
				await wait_for_ready(page, impl)
			await asyncio.sleep(0.2)

		for i in range(iterations):
			r = await run_one_iteration(page, impl, iteration=i, ws=ws_counter)
			results.append(r)
			msg = f"    iter {i}: {r.duration_ms:.2f} ms, {r.http_requests} req, {r.response_bytes} B"
			if r.error:
				msg += f"  ERROR: {r.error}"
			print(msg, flush=True)
			if impl["navigates"]:
				await wait_for_ready(page, impl)
			await asyncio.sleep(0.25)
	finally:
		await context.close()
	return results


async def main_async(iterations: int, warmup: int, only: list[str]) -> Path:
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	out = Path(f"performance_results_{ts}.csv")
	impls = [i for i in IMPLEMENTATIONS if not only or i["name"] in only]

	all_results: list[IterationResult] = []
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		try:
			for impl in impls:
				print(f"\n=== {impl['name']} ===", flush=True)
				all_results.extend(await benchmark_impl(browser, impl, iterations, warmup))
		finally:
			await browser.close()

	with out.open("w", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(["timestamp", "implementation", "iteration", "duration_ms", "http_requests", "response_bytes", "error"])
		now = datetime.now().isoformat()
		for r in all_results:
			writer.writerow([now, r.implementation, r.iteration, f"{r.duration_ms:.3f}", r.http_requests, r.response_bytes, r.error or ""])

	print(f"\n✓ Wrote {out}", flush=True)
	return out


def main() -> int:
	ap = argparse.ArgumentParser()
	ap.add_argument("--iterations", type=int, default=10)
	ap.add_argument("--warmup", type=int, default=2)
	ap.add_argument("--only", nargs="*", default=[], help="Subset of impl names")
	args = ap.parse_args()
	asyncio.run(main_async(args.iterations, args.warmup, args.only))
	return 0


if __name__ == "__main__":
	sys.exit(main())
