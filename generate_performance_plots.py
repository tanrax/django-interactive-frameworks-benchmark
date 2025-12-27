#!/usr/bin/env python3
"""
Generate Performance Comparison Plots

Creates comparative visualizations of performance test results across
all 5 implementations: LiveView, Reactor, SSR, HTMX, and Unicorn.

Generates:
1. Average duration comparison (bar chart)
2. Duration distribution (box plot)
3. Request time breakdown (stacked bar chart)
4. Network overhead comparison (bytes transferred)
5. Iteration performance trends (line chart)
"""

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from pathlib import Path
import glob

def load_latest_csv():
	"""Load the most recent performance results CSV"""
	csv_files = glob.glob("performance_results_*.csv")
	if not csv_files:
		raise FileNotFoundError("No performance results CSV found. Run compile_performance_data.py first.")

	latest_csv = max(csv_files, key=lambda x: Path(x).stat().st_mtime)
	print(f"Loading data from: {latest_csv}")

	data = {'LiveView': [], 'Reactor': [], 'SSR': [], 'django-htmx': [], 'Unicorn': []}

	with open(latest_csv, 'r') as f:
		reader = csv.DictReader(f)
		for row in reader:
			impl = row['implementation']
			data[impl].append({
				'iteration': int(row['iteration']),
				'duration_ms': float(row['duration_ms']),
				'network_requests': int(row['network_requests']),
				'total_bytes': int(row['total_bytes']),
				'dns_ms': float(row['dns_ms']),
				'connect_ms': float(row['connect_ms']),
				'request_ms': float(row['request_ms']),
				'response_ms': float(row['response_ms'])
			})

	return data, latest_csv

def plot_average_duration(data, output_file='plot_avg_duration.png'):
	"""Bar chart comparing average duration across implementations"""
	implementations = list(data.keys())
	averages = [np.mean([m['duration_ms'] for m in data[impl]]) for impl in implementations]

	# Color scheme (5 implementations)
	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(implementations, averages, color=colors, alpha=0.8, edgecolor='black')

	# Add value labels on bars
	for bar, avg in zip(bars, averages):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height,
		        f'{avg:.2f}ms',
		        ha='center', va='bottom', fontweight='bold', fontsize=11)

	ax.set_ylabel('Average Duration (ms)', fontsize=12, fontweight='bold')
	ax.set_title('Create Alert Action - Average Response Time', fontsize=14, fontweight='bold')
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_duration_distribution(data, output_file='plot_duration_distribution.png'):
	"""Box plot showing duration distribution"""
	implementations = list(data.keys())
	durations = [[m['duration_ms'] for m in data[impl]] for impl in implementations]

	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bp = ax.boxplot(durations, labels=implementations, patch_artist=True,
	                showmeans=True, meanline=True)

	# Color the boxes
	for patch, color in zip(bp['boxes'], colors):
		patch.set_facecolor(color)
		patch.set_alpha(0.6)

	ax.set_ylabel('Duration (ms)', fontsize=12, fontweight='bold')
	ax.set_title('Response Time Distribution (10 iterations)', fontsize=14, fontweight='bold')
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_timing_breakdown(data, output_file='plot_timing_breakdown.png'):
	"""Stacked bar chart showing request timing breakdown"""
	implementations = list(data.keys())

	# Calculate averages for each timing component
	dns_avgs = [np.mean([m['dns_ms'] for m in data[impl]]) for impl in implementations]
	connect_avgs = [np.mean([m['connect_ms'] for m in data[impl]]) for impl in implementations]
	request_avgs = [np.mean([m['request_ms'] for m in data[impl]]) for impl in implementations]
	response_avgs = [np.mean([m['response_ms'] for m in data[impl]]) for impl in implementations]

	x = np.arange(len(implementations))
	width = 0.6

	fig, ax = plt.subplots(figsize=(10, 6))

	# Stacked bars
	p1 = ax.bar(x, dns_avgs, width, label='DNS Lookup', color='#ff6b6b')
	p2 = ax.bar(x, connect_avgs, width, bottom=dns_avgs, label='Connection', color='#4ecdc4')
	p3 = ax.bar(x, request_avgs, width,
	            bottom=np.array(dns_avgs) + np.array(connect_avgs),
	            label='Request/Wait', color='#45b7d1')
	p4 = ax.bar(x, response_avgs, width,
	            bottom=np.array(dns_avgs) + np.array(connect_avgs) + np.array(request_avgs),
	            label='Response', color='#96ceb4')

	ax.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
	ax.set_title('Network Timing Breakdown', fontsize=14, fontweight='bold')
	ax.set_xticks(x)
	ax.set_xticklabels(implementations)
	ax.legend(loc='upper left')
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_network_overhead(data, output_file='plot_network_overhead.png'):
	"""Bar chart comparing network overhead (bytes transferred)"""
	implementations = list(data.keys())
	avg_bytes = [np.mean([m['total_bytes'] for m in data[impl]]) for impl in implementations]

	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(implementations, avg_bytes, color=colors, alpha=0.8, edgecolor='black')

	# Add value labels
	for bar, bytes_val in zip(bars, avg_bytes):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height,
		        f'{bytes_val/1024:.1f} KB',
		        ha='center', va='bottom', fontweight='bold', fontsize=11)

	ax.set_ylabel('Bytes Transferred', fontsize=12, fontweight='bold')
	ax.set_title('Network Overhead - Data Transfer per Action', fontsize=14, fontweight='bold')
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_iteration_trends(data, output_file='plot_iteration_trends.png'):
	"""Line chart showing performance trends across iterations"""
	fig, ax = plt.subplots(figsize=(12, 6))

	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']
	markers = ['o', 'D', 's', '^', 'd']

	for (impl, color, marker) in zip(data.keys(), colors, markers):
		iterations = [m['iteration'] for m in data[impl]]
		durations = [m['duration_ms'] for m in data[impl]]
		ax.plot(iterations, durations, marker=marker, color=color, linewidth=2,
		        markersize=8, label=impl, alpha=0.8)

	ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
	ax.set_ylabel('Duration (ms)', fontsize=12, fontweight='bold')
	ax.set_title('Performance Trends Across Iterations', fontsize=14, fontweight='bold')
	ax.legend(loc='best', fontsize=11)
	ax.grid(True, alpha=0.3, linestyle='--')

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_response_time_comparison(data, output_file='plot_response_time.png'):
	"""Bar chart: Average Response Time - Lower is Better"""
	implementations = list(data.keys())
	averages = [np.mean([m['duration_ms'] for m in data[impl]]) for impl in implementations]
	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(implementations, averages, color=colors, alpha=0.8, edgecolor='black')

	for bar, avg in zip(bars, averages):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height, f'{avg:.2f}ms',
		        ha='center', va='bottom', fontweight='bold', fontsize=11)

	ax.set_ylabel('Duration (ms)', fontweight='bold', fontsize=12)
	ax.set_title('Average Response Time', fontweight='bold', fontsize=14)
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	# Add "Lower is Better" annotation
	ax.text(0.98, 0.98, '⬇ Lower is Better', transform=ax.transAxes,
	        fontsize=11, fontweight='bold', va='top', ha='right',
	        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_network_requests_comparison(data, output_file='plot_network_requests.png'):
	"""Bar chart: HTTP Requests - Lower is Better"""
	implementations = list(data.keys())
	avg_requests = [np.mean([m['network_requests'] for m in data[impl]]) for impl in implementations]
	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(implementations, avg_requests, color=colors, alpha=0.8, edgecolor='black')

	for bar, req in zip(bars, avg_requests):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height, f'{req:.1f}',
		        ha='center', va='bottom', fontweight='bold', fontsize=11)

	ax.set_ylabel('HTTP Requests per Action', fontweight='bold', fontsize=12)
	ax.set_title('HTTP Requests per Action', fontweight='bold', fontsize=14)
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	# Add "Lower is Better" annotation
	ax.text(0.98, 0.98, '⬇ Lower is Better', transform=ax.transAxes,
	        fontsize=11, fontweight='bold', va='top', ha='right',
	        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_data_transfer_comparison(data, output_file='plot_data_transfer.png'):
	"""Bar chart: Data Transfer - Lower is Better"""
	implementations = list(data.keys())
	avg_bytes = [np.mean([m['total_bytes'] for m in data[impl]]) / 1024 for impl in implementations]
	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']

	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(implementations, avg_bytes, color=colors, alpha=0.8, edgecolor='black')

	for bar, kb in zip(bars, avg_bytes):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height, f'{kb:.1f} KB',
		        ha='center', va='bottom', fontweight='bold', fontsize=11)

	ax.set_ylabel('Data Transfer (KB)', fontweight='bold', fontsize=12)
	ax.set_title('Network Overhead - Data Transfer per Action', fontweight='bold', fontsize=14)
	ax.grid(axis='y', alpha=0.3, linestyle='--')

	# Add "Lower is Better" annotation
	ax.text(0.98, 0.98, '⬇ Lower is Better', transform=ax.transAxes,
	        fontsize=11, fontweight='bold', va='top', ha='right',
	        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def plot_stability_comparison(data, output_file='plot_stability.png'):
	"""Line chart: Performance Stability - Lower and Flatter is Better"""
	implementations = list(data.keys())
	colors = ['#3273dc', '#9b59b6', '#48c774', '#ffdd57', '#f14668']
	markers = ['o', 'D', 's', '^', 'd']

	fig, ax = plt.subplots(figsize=(12, 6))

	for (impl, color, marker) in zip(implementations, colors, markers):
		iterations = [m['iteration'] for m in data[impl]]
		durations = [m['duration_ms'] for m in data[impl]]
		ax.plot(iterations, durations, marker=marker, color=color, linewidth=2,
		        markersize=8, label=impl, alpha=0.8)

	ax.set_xlabel('Iteration', fontweight='bold', fontsize=12)
	ax.set_ylabel('Duration (ms)', fontweight='bold', fontsize=12)
	ax.set_title('Performance Stability Across Iterations', fontweight='bold', fontsize=14)
	ax.legend(loc='best', fontsize=11)
	ax.grid(True, alpha=0.3, linestyle='--')

	# Add "Lower is Better" annotation
	ax.text(0.98, 0.98, '⬇ Lower & Flatter is Better', transform=ax.transAxes,
	        fontsize=11, fontweight='bold', va='top', ha='right',
	        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

	plt.tight_layout()
	plt.savefig(output_file, dpi=300, bbox_inches='tight')
	print(f"✓ Saved: {output_file}")
	plt.close()

def main():
	print("="*80)
	print("PERFORMANCE VISUALIZATION GENERATOR")
	print("="*80)

	try:
		data, csv_file = load_latest_csv()
		print(f"\nData loaded: {sum(len(v) for v in data.values())} measurements")

		print("\nGenerating plots...")
		plot_average_duration(data)
		plot_duration_distribution(data)
		plot_timing_breakdown(data)
		plot_network_overhead(data)
		plot_iteration_trends(data)

		# Generate 4 separate comparison plots
		plot_response_time_comparison(data)
		plot_network_requests_comparison(data)
		plot_data_transfer_comparison(data)
		plot_stability_comparison(data)

		print("\n" + "="*80)
		print("✓ All plots generated successfully!")
		print("="*80)
		print("\nPlot files:")
		print("  - plot_avg_duration.png          (Average response times)")
		print("  - plot_duration_distribution.png (Statistical distribution)")
		print("  - plot_timing_breakdown.png      (Network timing breakdown)")
		print("  - plot_network_overhead.png      (Data transfer comparison)")
		print("  - plot_iteration_trends.png      (Performance stability)")
		print("\n  Individual comparison plots (with 'Lower is Better' indicators):")
		print("  - plot_response_time.png         (Response time comparison)")
		print("  - plot_network_requests.png      (HTTP requests comparison)")
		print("  - plot_data_transfer.png         (Data transfer comparison)")
		print("  - plot_stability.png             (Performance stability)")

	except Exception as e:
		print(f"\n✗ Error: {e}")
		return 1

	return 0

if __name__ == "__main__":
	exit(main())
