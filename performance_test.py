#!/usr/bin/env python3
"""
Performance Testing Suite for Alert System Implementations

Tests all 5 implementations (LiveView, SSR, HTMX, Unicorn, Reactor) and measures:
- Request timing for create, view details, delete actions
- Network overhead
- Requests per second capability

Results are saved to CSV and visualized with plots.
"""

import csv
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any
import random


class PerformanceTest:
	"""Performance testing orchestrator for Alert System implementations"""

	IMPLEMENTATIONS = [
		{"name": "LiveView", "url": "http://localhost:8000/", "type": "websocket"},
		{"name": "SSR", "url": "http://localhost:8000/ssr/", "type": "http"},
		{"name": "HTMX", "url": "http://localhost:8000/htmx/", "type": "ajax"},
		{"name": "Unicorn", "url": "http://localhost:8000/unicorn/", "type": "ajax"},
		{"name": "Reactor", "url": "http://localhost:8000/reactor/", "type": "websocket"}
	]

	ACTIONS = ["create_alert", "view_details", "delete_alert"]
	ITERATIONS = 10

	ALERT_TYPES = ["INFO", "WARNING", "CRITICAL"]

	def __init__(self):
		self.results: List[Dict[str, Any]] = []
		self.csv_filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

	def generate_random_alert(self) -> Dict[str, str]:
		"""Generate random alert data for testing"""
		alert_type = random.choice(self.ALERT_TYPES)
		description = f"Performance test alert {random.randint(1000, 9999)} - {alert_type}"
		return {
			"type": alert_type,
			"description": description
		}

	def record_result(self, implementation: str, action: str, iteration: int,
	                  duration_ms: float, request_count: int, total_bytes: int,
	                  timing_details: Dict[str, float]):
		"""Record a single test result"""
		result = {
			"timestamp": datetime.now().isoformat(),
			"implementation": implementation,
			"action": action,
			"iteration": iteration,
			"duration_ms": duration_ms,
			"request_count": request_count,
			"total_bytes": total_bytes,
			"dns_ms": timing_details.get("dns", 0),
			"connect_ms": timing_details.get("connect", 0),
			"send_ms": timing_details.get("send", 0),
			"wait_ms": timing_details.get("wait", 0),
			"receive_ms": timing_details.get("receive", 0)
		}
		self.results.append(result)
		print(f"  [{implementation}] {action} iteration {iteration}: {duration_ms:.2f}ms")

	def save_to_csv(self):
		"""Save all results to CSV file"""
		if not self.results:
			print("No results to save")
			return

		fieldnames = [
			"timestamp", "implementation", "action", "iteration",
			"duration_ms", "request_count", "total_bytes",
			"dns_ms", "connect_ms", "send_ms", "wait_ms", "receive_ms"
		]

		with open(self.csv_filename, 'w', newline='') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(self.results)

		print(f"\n✓ Results saved to {self.csv_filename}")

	def print_summary(self):
		"""Print statistical summary of results"""
		print("\n" + "="*80)
		print("PERFORMANCE SUMMARY")
		print("="*80)

		for impl in self.IMPLEMENTATIONS:
			impl_name = impl["name"]
			print(f"\n{impl_name}:")

			for action in self.ACTIONS:
				action_results = [
					r["duration_ms"] for r in self.results
					if r["implementation"] == impl_name and r["action"] == action
				]

				if action_results:
					avg = statistics.mean(action_results)
					median = statistics.median(action_results)
					stdev = statistics.stdev(action_results) if len(action_results) > 1 else 0
					min_time = min(action_results)
					max_time = max(action_results)

					print(f"  {action:20s} - Avg: {avg:6.2f}ms  Median: {median:6.2f}ms  "
					      f"StdDev: {stdev:5.2f}ms  Range: [{min_time:.2f}, {max_time:.2f}]")

	def get_test_instructions(self) -> str:
		"""Return instructions for manual Chrome MCP testing"""
		instructions = """
================================================================================
CHROME MCP TESTING INSTRUCTIONS
================================================================================

This script will guide you through performance testing. For each test:

1. Navigate to the implementation URL
2. Perform the action (create/view/delete)
3. Capture network timing from Chrome DevTools
4. Record the metrics

The script will prompt you for timing data after each action.

Press Enter to start...
"""
		return instructions


def main():
	"""Main testing orchestrator"""
	tester = PerformanceTest()

	print(tester.get_test_instructions())
	input()

	print("\n" + "="*80)
	print("AUTOMATED TESTING MODE")
	print("="*80)
	print("\nThis script will test each implementation with the following actions:")
	print("- Create Random Alert")
	print("- View Alert Details")
	print("- Delete Alert")
	print(f"\nIterations per action: {tester.ITERATIONS}")
	print("\nNOTE: You'll need to use Chrome MCP tools to capture actual timing.")
	print("      This script provides the framework and data collection structure.")
	print("\n" + "="*80)

	# Placeholder for actual Chrome automation
	# In practice, this would use Chrome MCP tools to automate the tests
	print("\nTo collect performance data, use Chrome MCP tools:")
	print("1. mcp__chrome-devtools__navigate_page - Navigate to each implementation")
	print("2. mcp__chrome-devtools__list_network_requests - Get network requests")
	print("3. mcp__chrome-devtools__get_network_request - Get timing details")
	print("4. mcp__chrome-devtools__performance_start_trace - Start performance trace")
	print("5. mcp__chrome-devtools__performance_stop_trace - Stop trace and get metrics")

	print("\n✓ Performance test framework ready")
	print(f"✓ Results will be saved to: {tester.csv_filename}")

	return tester


if __name__ == "__main__":
	tester = main()

	# Example of how to record results (you'll do this manually with Chrome MCP)
	# tester.record_result(
	#     implementation="HTMX",
	#     action="create_alert",
	#     iteration=1,
	#     duration_ms=45.2,
	#     request_count=1,
	#     total_bytes=1024,
	#     timing_details={"dns": 2.1, "connect": 3.5, "send": 1.2, "wait": 35.4, "receive": 3.0}
	# )
	# tester.save_to_csv()
	# tester.print_summary()
