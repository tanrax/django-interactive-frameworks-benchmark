#!/usr/bin/env python3
"""
Generate Plotly PNG charts from the most recent performance_results_*.csv.

Produces four charts that mirror the originals shipped with the article:
  - plot_response_time.png
  - plot_network_requests.png
  - plot_data_transfer.png
  - plot_stability.png

Usage (inside bench container):
  python generate_plotly_plots.py
Outputs land in /bench (mounted to the project root).
"""

import csv
import glob
from collections import defaultdict
from pathlib import Path
from statistics import mean

import plotly.graph_objects as go


PALETTE = ['#3273dc', '#48c774', '#ffdd57', '#f14668', '#9b59b6', '#00d1b2']
LOWER_IS_BETTER = dict(
	x=0.98, y=0.98, xref='paper', yref='paper',
	text='\u2b07 Lower is Better',
	showarrow=False,
	bgcolor='wheat', opacity=0.75,
	font=dict(size=12),
	bordercolor='black', borderwidth=1, borderpad=6,
	xanchor='right', yanchor='top',
)
LAYOUT_COMMON = dict(
	plot_bgcolor='white',
	paper_bgcolor='white',
	font=dict(family='Inter, system-ui, sans-serif', size=14),
	margin=dict(l=60, r=30, t=70, b=60),
	yaxis=dict(gridcolor='#e5e5e5', zerolinecolor='#d0d0d0'),
	xaxis=dict(gridcolor='#e5e5e5'),
)


def load_latest_csv() -> tuple[dict, str]:
	files = glob.glob('performance_results_*.csv')
	if not files:
		raise SystemExit('No performance_results_*.csv found. Run the benchmark first.')
	latest = max(files, key=lambda x: Path(x).stat().st_mtime)
	print(f'Loading {latest}')
	data = defaultdict(list)
	with open(latest) as f:
		for row in csv.DictReader(f):
			if row.get('error') or int(row['iteration']) < 0:
				continue
			data[row['implementation']].append({
				'iteration': int(row['iteration']),
				'duration_ms': float(row['duration_ms']),
				'http_requests': int(row.get('http_requests') or 0),
				'response_bytes': int(row.get('response_bytes') or 0),
			})
	return dict(data), latest


def sort_by_speed(data: dict) -> dict:
	return dict(sorted(data.items(), key=lambda kv: mean([m['duration_ms'] for m in kv[1]])))


def bar_chart(data, title, value_fn, label_fn, yaxis_title, output):
	impls = list(data.keys())
	values = [value_fn(data[i]) for i in impls]
	labels = [label_fn(v) for v in values]
	colors = [PALETTE[i % len(PALETTE)] for i in range(len(impls))]

	fig = go.Figure(go.Bar(
		x=impls, y=values,
		text=labels, textposition='outside',
		marker=dict(color=colors, line=dict(color='#222', width=1)),
	))
	fig.update_layout(
		title=dict(text=title, font=dict(size=18, color='#222'), x=0.5, xanchor='center'),
		yaxis_title=yaxis_title,
		annotations=[LOWER_IS_BETTER],
		**LAYOUT_COMMON,
	)
	# Headroom so the outside labels don't clip the title/annotation.
	ymax = max(values) if values else 0
	fig.update_yaxes(range=[0, ymax * 1.22 if ymax > 0 else 1])
	fig.write_image(output, width=1000, height=600, scale=2)
	print(f'\u2713 {output}')


def response_time_chart(data):
	bar_chart(
		data,
		title='Create Alert - Average Response Time',
		value_fn=lambda rows: mean(r['duration_ms'] for r in rows),
		label_fn=lambda v: f'{v:.2f} ms',
		yaxis_title='Duration (ms)',
		output='plot_response_time.png',
	)


def network_requests_chart(data):
	bar_chart(
		data,
		title='HTTP Requests per Action',
		value_fn=lambda rows: mean(r['http_requests'] for r in rows),
		label_fn=lambda v: f'{v:.1f}',
		yaxis_title='HTTP requests per action',
		output='plot_network_requests.png',
	)


def data_transfer_chart(data):
	bar_chart(
		data,
		title='Data Transfer per Action',
		value_fn=lambda rows: mean(r['response_bytes'] for r in rows) / 1024,
		label_fn=lambda v: f'{v:.2f} KB',
		yaxis_title='Data transfer (KB)',
		output='plot_data_transfer.png',
	)


def stability_chart(data):
	fig = go.Figure()
	for idx, (impl, rows) in enumerate(data.items()):
		rows_sorted = sorted(rows, key=lambda r: r['iteration'])
		fig.add_trace(go.Scatter(
			x=[r['iteration'] + 1 for r in rows_sorted],
			y=[r['duration_ms'] for r in rows_sorted],
			mode='lines+markers',
			name=impl,
			line=dict(color=PALETTE[idx % len(PALETTE)], width=2),
			marker=dict(size=8),
		))
	fig.update_layout(
		title=dict(text='Performance Stability Across Iterations', font=dict(size=18, color='#222'), x=0.5, xanchor='center'),
		xaxis_title='Iteration',
		yaxis_title='Duration (ms)',
		legend=dict(bgcolor='rgba(255,255,255,0.85)', bordercolor='#999', borderwidth=1),
		annotations=[{**LOWER_IS_BETTER, 'text': '\u2b07 Lower & Flatter is Better'}],
		**LAYOUT_COMMON,
	)
	fig.write_image('plot_stability.png', width=1100, height=600, scale=2)
	print('\u2713 plot_stability.png')


def main() -> int:
	data, _ = load_latest_csv()
	if not data:
		print('No measurements.')
		return 1
	data = sort_by_speed(data)
	print('Order fastest→slowest:', ', '.join(data.keys()))
	response_time_chart(data)
	network_requests_chart(data)
	data_transfer_chart(data)
	stability_chart(data)
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
