# Django Interactive Frameworks Benchmark

Performance comparison of Django's main interactive frameworks. This project implements the same alert system using six different approaches: Django LiveView (WebSocket), traditional SSR, django-htmx (AJAX), Django Unicorn (reactive components), Django Reactor (Phoenix LiveView style), and djust (Rust-powered Phoenix LiveView style). The goal is to measure and compare their real-world performance, network overhead, and user experience characteristics.

## Technology Comparison

| Feature | Django LiveView (`/`) | SSR (`/ssr/`) | django-htmx (`/htmx/`) | Unicorn (`/unicorn/`) | Reactor (`/reactor/`) | djust (`/djust/`) |
|---------|----------------|---------------|-----------------|----------------------|----------------------|-------------------|
| **Transport** | WebSocket | HTTP | AJAX | AJAX | WebSocket | WebSocket |
| **Update Type** | Real-time | Full reload | Partial | Reactive | Real-time | Real-time (VDOM patches) |
| **Multi-user** | ✅ Broadcast | ❌ | ❌ | ❌ | ✅ Broadcast | ✅ Broadcast |
| **Infrastructure** | Redis + Channels | Django only | Django only | Django only | Redis + Channels | Redis + Channels + Rust |

## Results Summary and Performance Conclusions

[You can see the results on my blog](https://en.andros.dev/blog/06892b5b/performance-comparison-of-djangos-main-interactive-frameworks/)

## Run your own tests: Quick Start

```bash
docker compose up --build
```

Access at `http://localhost:8000/` - Navigation bar switches between implementations.

## Implementation Details

| Aspect | Implementation |
|--------|---------------|
| **django-htmx CSRF** | `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>` |
| **Theme** | `<html data-theme="light">` (Bulma CSS) |
| **Templates** | `templates/alerts/{ssr,htmx,unicorn}/` |
| **Components** | `alerts/components/alert_list.py` (Unicorn) |
| **Views** | All in `alerts/views.py` |
| **Reactor** | `alerts/reactor_components/live.py` |
| **djust** | `alerts/djust_components/live.py` |

## Dependencies

- **[django-liveview](https://django-liveview.andros.dev/)** - WebSocket reactive framework
- **[django-htmx](https://django-htmx.readthedocs.io/)** `==1.22.0` - HTMX middleware for Django
- **[django-unicorn](https://www.django-unicorn.com/)** `==0.62.0` - Reactive components
- **[django-reactor](https://github.com/edelvalle/reactor)** `==5.3.0b0` - Phoenix LiveView for Django
- **[djust](https://djust.org/)** `==0.4.2` - Rust-powered Phoenix LiveView-style framework for Django
- **[Django Channels](https://channels.readthedocs.io/)** + **[Redis](https://redis.io/)** - WebSocket infrastructure
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

## Technology Documentation

- **[Django LiveView](https://django-liveview.andros.dev/)** - Official Django LiveView documentation
- **[HTMX](https://htmx.org/)** - Official HTMX documentation and examples
- **[Django Unicorn](https://www.django-unicorn.com/docs/)** - Complete Unicorn documentation
- **[Django Reactor](https://github.com/edelvalle/reactor)** - Phoenix LiveView but for Django
- **[djust](https://djust.org/)** - Rust-powered reactive server-side rendering for Django
- **[Django](https://docs.djangoproject.com/)** - Django official documentation (for SSR implementation)

## Performance Testing

A fully automated benchmark drives each implementation through a headless Chromium (Playwright) and records the "Add Random Alert" round-trip. Everything runs in Docker, so results are reproducible on any machine.

### How it works

- The `bench` service (see `compose.yaml` + `Dockerfile.bench`) runs Playwright against the `web` container over Docker's internal network.
- For every implementation: the DB is wiped via `/_bench/clear/`, the page is loaded fresh, and two warmup iterations are discarded before measuring 10 real iterations.
- Each iteration clicks the real "Add Random Alert" button and stops the clock when a new row actually appears in the DOM (or, for SSR, when navigation completes).
- HTTP response bodies are captured via Playwright's `response.body()`; WebSocket frames are captured via `page.on("websocket")`.
- Results are written to a timestamped CSV. The plot script renders four comparison charts with Plotly.

### Reproducing the benchmark

Start the stack and run the bench service on demand:

```bash
# 1. Bring up the app
docker compose up -d --build

# 2. Run the benchmark (uses the "bench" profile so it stays out of the default up)
docker compose --profile bench run --rm bench

# 3. Regenerate the four PNG charts from the latest CSV
docker compose --profile bench run --rm bench python generate_plotly_plots.py
```

The CSV lands in the project root as `performance_results_YYYYMMDD_HHMMSS.csv` (git-ignored). You can also filter which implementations to measure:

```bash
docker compose --profile bench run --rm bench python run_performance_tests.py --only djust "Django LiveView" --iterations 20
```

### Scripts

| File | Purpose |
|---|---|
| `run_performance_tests.py` | Playwright-driven benchmark runner (entrypoint of the `bench` service) |
| `generate_plotly_plots.py` | Renders the four comparison PNGs from the most recent CSV |
| `Dockerfile.bench` | Playwright Python image with Plotly and Kaleido |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Templates not updating | `docker compose restart web` |
| django-htmx 403 CSRF | Check `hx-headers` in `<body>` tag |
| Dark tables | Add `data-theme="light"` to `<html>` |
| Bench can't reach web | Both services must be on the same compose network; the runner uses `BENCH_BASE_URL=http://web:8000` by default |

## Features

| Feature | Django LiveView | SSR | django-htmx | Unicorn | Reactor | djust |
|---------|:---------------:|:---:|:----:|:-------:|:-------:|:-----:|
| Create alerts | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View details | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Modals | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Form validation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| No page reload | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |

---

**MIT License** - Reference implementation for Django web technologies
