#!/usr/bin/env python3
"""
Generate Performance Comparison Plots

Creates comparative visualizations of performance test results across
all 4 implementations: LiveView, SSR, HTMX, and Unicorn.

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

	data = {'LiveView': [], 'SSR': [], 'HTMX': [], 'Unicorn': []}

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

	# Color scheme
	colors = ['#3273dc', '#48c774', '#ffdd57', '#f14668']

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

	colors = ['#3273dc', '#48c774', '#ffdd57', '#f14668']

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

	colors = ['#3273dc', '#48c774', '#ffdd57', '#f14668']

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

	colors = ['#3273dc', '#48c774', '#ffdd57', '#f14668']
	markers = ['o', 's', '^', 'd']

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

def plot_comprehensive_comparison(data, output_file='plot_comprehensive.png'):
	"""Create a comprehensive 2x2 subplot comparison"""
	fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

	implementations = list(data.keys())
	colors = ['#3273dc', '#48c774', '#ffdd57', '#f14668']

	# 1. Average Duration (top-left)
	averages = [np.mean([m['duration_ms'] for m in data[impl]]) for impl in implementations]
	bars1 = ax1.bar(implementations, averages, color=colors, alpha=0.8, edgecolor='black')
	for bar, avg in zip(bars1, averages):
		height = bar.get_height()
		ax1.text(bar.get_x() + bar.get_width()/2., height, f'{avg:.2f}ms',
		         ha='center', va='bottom', fontweight='bold')
	ax1.set_ylabel('Duration (ms)', fontweight='bold')
	ax1.set_title('Average Response Time', fontweight='bold', fontsize=13)
	ax1.grid(axis='y', alpha=0.3)

	# 2. Network Requests (top-right)
	avg_requests = [np.mean([m['network_requests'] for m in data[impl]]) for impl in implementations]
	bars2 = ax2.bar(implementations, avg_requests, color=colors, alpha=0.8, edgecolor='black')
	for bar, req in zip(bars2, avg_requests):
		height = bar.get_height()
		ax2.text(bar.get_x() + bar.get_width()/2., height, f'{req:.1f}',
		         ha='center', va='bottom', fontweight='bold')
	ax2.set_ylabel('HTTP Requests', fontweight='bold')
	ax2.set_title('Network Requests per Action', fontweight='bold', fontsize=13)
	ax2.grid(axis='y', alpha=0.3)

	# 3. Bytes Transferred (bottom-left)
	avg_bytes = [np.mean([m['total_bytes'] for m in data[impl]]) / 1024 for impl in implementations]
	bars3 = ax3.bar(implementations, avg_bytes, color=colors, alpha=0.8, edgecolor='black')
	for bar, kb in zip(bars3, avg_bytes):
		height = bar.get_height()
		ax3.text(bar.get_x() + bar.get_width()/2., height, f'{kb:.1f} KB',
		         ha='center', va='bottom', fontweight='bold')
	ax3.set_ylabel('Data Transfer (KB)', fontweight='bold')
	ax3.set_title('Network Overhead', fontweight='bold', fontsize=13)
	ax3.grid(axis='y', alpha=0.3)

	# 4. Iteration Trends (bottom-right)
	markers = ['o', 's', '^', 'd']
	for (impl, color, marker) in zip(implementations, colors, markers):
		iterations = [m['iteration'] for m in data[impl]]
		durations = [m['duration_ms'] for m in data[impl]]
		ax4.plot(iterations, durations, marker=marker, color=color, linewidth=2,
		         markersize=6, label=impl, alpha=0.8)
	ax4.set_xlabel('Iteration', fontweight='bold')
	ax4.set_ylabel('Duration (ms)', fontweight='bold')
	ax4.set_title('Performance Stability', fontweight='bold', fontsize=13)
	ax4.legend(loc='best')
	ax4.grid(True, alpha=0.3)

	fig.suptitle('Alert System Performance Comparison', fontsize=16, fontweight='bold', y=0.995)
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
		plot_comprehensive_comparison(data)

		print("\n" + "="*80)
		print("✓ All plots generated successfully!")
		print("="*80)
		print("\nPlot files:")
		print("  - plot_avg_duration.png          (Average response times)")
		print("  - plot_duration_distribution.png (Statistical distribution)")
		print("  - plot_timing_breakdown.png      (Network timing breakdown)")
		print("  - plot_network_overhead.png      (Data transfer comparison)")
		print("  - plot_iteration_trends.png      (Performance stability)")
		print("  - plot_comprehensive.png         (All-in-one comparison)")

	except Exception as e:
		print(f"\n✗ Error: {e}")
		return 1

	return 0

if __name__ == "__main__":
	exit(main())
