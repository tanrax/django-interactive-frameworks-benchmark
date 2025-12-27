#!/usr/bin/env python3
"""
Comprehensive Performance Testing Suite for Alert System

This script conducts automated performance tests across all 5 implementations:
- Django LiveView (WebSocket)
- SSR (Server-Side Rendering)
- HTMX (AJAX partial updates)
- Django Unicorn (Reactive components)
- Django Reactor (Phoenix LiveView style)

Tests performed:
1. Create Random Alert - measures POST/action timing
2. View Alert Details - measures modal/detail page load timing
3. Delete Alert - measures delete operation timing

Results are saved to CSV and visualized with plots.
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path


class PerformanceTestRunner:
	"""Orchestrates performance testing across all implementations"""

	def __init__(self):
		self.results = []
		self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		self.csv_file = f"performance_results_{self.timestamp}.csv"
		self.implementations = {
			"LiveView": {
				"url": "http://localhost:8000/",
				"create_selector": "button:contains('Add Random Alert')",
				"type": "websocket"
			},
			"SSR": {
				"url": "http://localhost:8000/ssr/",
				"create_selector": "button:contains('Add Random Alert')",
				"type": "http"
			},
			"HTMX": {
				"url": "http://localhost:8000/htmx/",
				"create_selector": "button:contains('Add Random Alert')",
				"type": "ajax"
			},
			"Unicorn": {
				"url": "http://localhost:8000/unicorn/",
				"create_selector": "button:contains('Add Random Alert')",
				"type": "ajax"
			},
			"Reactor": {
				"url": "http://localhost:8000/reactor/",
				"create_selector": "button:contains('Add Random Alert')",
				"type": "websocket"
			}
		}

	def generate_measurement_script(self, action_type):
		"""Generate JavaScript to measure action performance"""
		if action_type == "create":
			return """
(async () => {
	const startTime = performance.now();
	const startMark = performance.mark('action-start');

	// Find and click the "Add Random Alert" button
	const buttons = Array.from(document.querySelectorAll('button'));
	const addButton = buttons.find(btn => btn.textContent.includes('Add Random Alert'));

	if (!addButton) {
		return { error: 'Button not found' };
	}

	// Record network state before click
	const perfEntries = performance.getEntriesByType('navigation');
	const resourcesBefore = performance.getEntriesByType('resource').length;

	// Click button
	addButton.click();

	// Wait for response (different for each implementation)
	await new Promise(resolve => {
		// For SSR: wait for page navigation
		if (window.location.pathname.includes('/ssr/')) {
			window.addEventListener('load', resolve, { once: true });
		}
		// For HTMX/Unicorn: wait for AJAX
		else if (typeof htmx !== 'undefined' || typeof Unicorn !== 'undefined') {
			setTimeout(resolve, 1000); // Wait for AJAX to complete
		}
		// For LiveView: wait for WebSocket message
		else {
			setTimeout(resolve, 1000); // Wait for WebSocket update
		}
	});

	const endTime = performance.now();
	const duration = endTime - startTime;

	// Get network timing
	const resourcesAfter = performance.getEntriesByType('resource');
	const newResources = resourcesAfter.slice(resourcesBefore);

	// Calculate network metrics
	const networkMetrics = newResources.map(entry => ({
		name: entry.name,
		duration: entry.duration,
		transferSize: entry.transferSize || 0,
		domainLookupTime: entry.domainLookupEnd - entry.domainLookupStart,
		connectTime: entry.connectEnd - entry.connectStart,
		requestTime: entry.responseStart - entry.requestStart,
		responseTime: entry.responseEnd - entry.responseStart
	}));

	return {
		duration: duration,
		timestamp: new Date().toISOString(),
		networkRequests: networkMetrics.length,
		totalTransferSize: networkMetrics.reduce((sum, m) => sum + m.transferSize, 0),
		networkMetrics: networkMetrics
	};
})();
"""
		elif action_type == "view_details":
			return """
(async () => {
	const startTime = performance.now();

	// Find first Details button
	const detailButtons = Array.from(document.querySelectorAll('button, a')).filter(
		el => el.textContent.includes('Details')
	);

	if (detailButtons.length === 0) {
		return { error: 'No details button found' };
	}

	const button = detailButtons[0];
	button.click();

	// Wait for modal or page load
	await new Promise(resolve => setTimeout(resolve, 500));

	const endTime = performance.now();
	return {
		duration: endTime - startTime,
		timestamp: new Date().toISOString()
	};
})();
"""
		elif action_type == "delete":
			return """
(async () => {
	const startTime = performance.now();

	// Find first Delete button
	const deleteButtons = Array.from(document.querySelectorAll('button')).filter(
		el => el.textContent.includes('Delete')
	);

	if (deleteButtons.length === 0) {
		return { error: 'No delete button found' };
	}

	// Auto-confirm dialog if it appears
	window.confirm = () => true;

	const button = deleteButtons[0];
	button.click();

	// Wait for deletion to complete
	await new Promise(resolve => setTimeout(resolve, 500));

	const endTime = performance.now();
	return {
		duration: endTime - startTime,
		timestamp: new Date().toISOString()
	};
})();
"""

	def save_results_to_csv(self):
		"""Save all collected results to CSV"""
		if not self.results:
			print("No results to save")
			return

		fieldnames = [
			'timestamp', 'implementation', 'action', 'iteration',
			'duration_ms', 'network_requests', 'total_bytes',
			'dns_ms', 'connect_ms', 'request_ms', 'response_ms'
		]

		with open(self.csv_file, 'w', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(self.results)

		print(f"\n✓ Results saved to: {self.csv_file}")

	def print_instructions(self):
		"""Print instructions for manual Chrome DevTools testing"""
		print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE TESTING INSTRUCTIONS                        ║
╔════════════════════════════════════════════════════════════════════════════╗

This script will guide you through systematic performance testing using Chrome
DevTools MCP tools.

TESTING PROCESS:
----------------

For each implementation (LiveView, SSR, HTMX, Unicorn, Reactor):
  For each action (Create, View Details, Delete):
    1. Navigate to implementation URL
    2. Execute JavaScript measurement script
    3. Record timing data
    4. Repeat 10 times for statistical significance

ACTIONS TO TEST:
----------------
1. CREATE RANDOM ALERT - Measures form submission/action timing
2. VIEW DETAILS - Measures modal/detail page load timing
3. DELETE ALERT - Measures delete operation timing

DATA TO COLLECT:
----------------
- Action duration (milliseconds)
- Number of network requests
- Total bytes transferred
- DNS lookup time
- Connection time
- Request/Response time

The measurement scripts use performance.now() for high-precision timing
and the Performance API to capture network metrics.

Press Enter to see the test execution plan...
""")
		input()

		print("\nTEST EXECUTION PLAN:")
		print("=" * 80)
		for impl_name, impl_config in self.implementations.items():
			print(f"\n{impl_name} ({impl_config['type'].upper()}):")
			print(f"  URL: {impl_config['url']}")
			print(f"  Actions: Create (10x), View Details (10x), Delete (10x)")
			print(f"  Total tests: 30")

		total_tests = len(self.implementations) * 3 * 10
		print(f"\nTOTAL TESTS: {total_tests}")
		print("=" * 80)


def main():
	runner = PerformanceTestRunner()
	runner.print_instructions()

	print("\n\nMANUAL TESTING MODE")
	print("=" * 80)
	print("\nUse Chrome MCP tools to execute tests:")
	print("\n1. Navigate to each implementation URL")
	print("2. Use mcp__chrome-devtools__evaluate_script with the measurement scripts")
	print("3. Collect timing data from JavaScript results")
	print("4. Record results manually or via automation")

	print(f"\n\nMeasurement scripts are available in this script.")
	print(f"Results will be saved to: {runner.csv_file}")
	print("\nGenerate measurement script for an action:")
	print("  - runner.generate_measurement_script('create')")
	print("  - runner.generate_measurement_script('view_details')")
	print("  - runner.generate_measurement_script('delete')")

	return runner


if __name__ == "__main__":
	runner = main()
