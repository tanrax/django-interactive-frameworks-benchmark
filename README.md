# Django Interactive Frameworks Benchmark

Performance comparison of Django's main interactive frameworks. This project implements the same alert system using four different approaches: Django LiveView (WebSocket), traditional SSR, HTMX (AJAX), and Django Unicorn (reactive components). The goal is to measure and compare their real-world performance, network overhead, and user experience characteristics.

## Technology Comparison

| Feature | LiveView (`/`) | SSR (`/ssr/`) | HTMX (`/htmx/`) | Unicorn (`/unicorn/`) |
|---------|----------------|---------------|-----------------|----------------------|
| **Transport** | WebSocket | HTTP | AJAX | AJAX |
| **Update Type** | Real-time | Full reload | Partial | Reactive |
| **Multi-user** | ✅ Broadcast | ❌ | ❌ | ❌ |
| **Infrastructure** | Redis + Channels | Django only | Django only | Django only |

## Quick Start

```bash
docker compose up --build
```

Access at `http://localhost:8000/` - Navigation bar switches between implementations.

## Implementation Details

| Aspect | Implementation |
|--------|---------------|
| **HTMX CSRF** | `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>` |
| **Theme** | `<html data-theme="light">` (Bulma CSS) |
| **Templates** | `templates/alerts/{ssr,htmx,unicorn}/` |
| **Components** | `alerts/components/alert_list.py` (Unicorn) |
| **Views** | All in `alerts/views.py` |

## Dependencies

- **[django-liveview](https://django-liveview.andros.dev/)** - WebSocket reactive framework
- **[django-htmx](https://django-htmx.readthedocs.io/)** `==1.22.0` - HTMX middleware for Django
- **[django-unicorn](https://www.django-unicorn.com/)** `==0.62.0` - Reactive components
- **[Django Channels](https://channels.readthedocs.io/)** + **[Redis](https://redis.io/)** - WebSocket infrastructure
- **[Daphne](https://github.com/django/daphne)** - ASGI server

## Technology Documentation

- **[Django LiveView](https://django-liveview.andros.dev/)** - Official Django LiveView documentation
- **[HTMX](https://htmx.org/)** - Official HTMX documentation and examples
- **[Django Unicorn](https://www.django-unicorn.com/docs/)** - Complete Unicorn documentation
- **[Django](https://docs.djangoproject.com/)** - Django official documentation (for SSR implementation)

## Performance Testing

Comprehensive performance tests were conducted across all implementations to measure response times for the "Create Alert" action. Tests were performed with 10 iterations per implementation using Chrome DevTools and the Performance API.

### Results Summary

| Implementation | Avg Response Time | Network Requests | Data Transfer | Technology |
|---------------|------------------|------------------|---------------|-----------|
| **LiveView** | **9.35ms** | 0 (WebSocket) | 450 bytes | WebSocket messages |
| **HTMX** | **16.48ms** | 1 HTTP request | ~37 KB | AJAX partial HTML |
| **Unicorn** | **26.76ms** | 1 HTTP request | ~71 KB | AJAX component sync |
| **SSR** | **47.25ms** | 2 HTTP requests | ~8.5 KB | POST + redirect GET |

### Performance Visualizations

All charts indicate that **lower values are better** for optimal performance.

#### Response Time Comparison
![Response Time Comparison](plot_response_time.png)

*Average response times across implementations. LiveView (9.35ms) is fastest, followed by HTMX (16.48ms), Unicorn (26.76ms), and SSR (47.25ms).*

#### HTTP Requests per Action
![HTTP Requests Comparison](plot_network_requests.png)

*Number of HTTP requests required per action. LiveView uses 0 HTTP requests (WebSocket), while SSR requires 2 (POST + redirect).*

#### Data Transfer Overhead
![Data Transfer Comparison](plot_data_transfer.png)

*Amount of data transferred per action. LiveView transfers minimal data (0.4 KB), while Unicorn transfers the most (71 KB).*

#### Performance Stability
![Performance Stability](plot_stability.png)

*Response time consistency across 10 iterations. Lower and flatter lines indicate better, more stable performance.*

### Key Findings

**🏆 Speed Winner: LiveView (9.35ms)**
- WebSocket communication eliminates HTTP overhead
- Real-time bidirectional connection already established
- No HTML parsing/rendering on each action
- Best for: Real-time dashboards, collaborative apps, live updates

**🥈 Runner-up: HTMX (16.48ms)**
- Efficient AJAX partial updates minimize data transfer
- Only updates affected DOM sections
- Low payload size, fast server response
- Best for: Modern UX with minimal JavaScript

**🥉 Third Place: Unicorn (26.76ms)**
- Component-based approach adds overhead
- Full component state synchronization
- Larger payloads due to component data
- Best for: Interactive forms with complex state

**4️⃣ Traditional: SSR (47.25ms)**
- Full page reload requires complete render cycle
- Two HTTP requests (POST + redirect GET)
- Browser must parse and render entire page
- Best for: SEO-critical pages, simple CRUD apps

### Performance Conclusions

1. **WebSocket vs HTTP**: LiveView's persistent WebSocket connection provides ~43% faster responses than HTMX and ~80% faster than SSR.

2. **Partial Updates Win**: HTMX's partial HTML updates are ~65% faster than SSR's full page reloads, demonstrating the efficiency of targeted DOM updates.

3. **Component Overhead**: Unicorn's component synchronization adds ~62% overhead compared to HTMX's simpler approach, trading speed for richer state management.

4. **Network Efficiency**: LiveView transfers the least data (450 bytes) while Unicorn transfers the most (71 KB), showing that component-based approaches have higher bandwidth costs.

5. **Stability**: All implementations show consistent performance across iterations, with minimal variance in response times.

### When to Choose Each Technology

- **Choose LiveView** when you need real-time collaboration, live dashboards, or the absolute fastest user interactions
- **Choose HTMX** for modern, responsive UIs without JavaScript frameworks, excellent balance of speed and simplicity
- **Choose Unicorn** for complex forms with rich interactivity and two-way data binding
- **Choose SSR** for traditional applications where SEO and simplicity are priorities over speed

### Reproducing Performance Tests

To reproduce the performance tests and generate your own plots:

1. **Ensure the application is running:**
   ```bash
   docker compose up --build
   ```

2. **Run automated tests (HTMX and Unicorn):**
   - Open Chrome and navigate to `http://localhost:8000/htmx/`
   - Use Chrome DevTools to execute the JavaScript performance tests
   - The test scripts are available in `run_performance_tests.py`

3. **Compile performance data:**
   ```bash
   python3 compile_performance_data.py
   ```
   This generates a CSV file with all test results.

4. **Generate visualization plots:**
   ```bash
   python3 generate_performance_plots.py
   ```
   This creates 6 PNG files with comparative visualizations.

**Performance Test Scripts:**
- `performance_test.py` - Framework and data structure definitions
- `run_performance_tests.py` - JavaScript measurement scripts for browser testing
- `compile_performance_data.py` - Compiles results from all implementations into CSV
- `generate_performance_plots.py` - Creates comparative plots using matplotlib

**Requirements for testing:**
- Python 3.x
- matplotlib (`pip install matplotlib`)
- Chrome browser with DevTools
- Running Docker containers

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Templates not updating | `docker compose restart web` |
| HTMX 403 CSRF | Check `hx-headers` in `<body>` tag |
| Dark tables | Add `data-theme="light"` to `<html>` |

## Features

| Feature | LiveView | SSR | HTMX | Unicorn |
|---------|:--------:|:---:|:----:|:-------:|
| Create alerts | ✅ | ✅ | ✅ | ✅ |
| View details | ✅ | ✅ | ✅ | ✅ |
| Delete | ✅ | ✅ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ✅ |
| Modals | ✅ | ❌ | ✅ | ✅ |
| Form validation | ✅ | ✅ | ✅ | ✅ |
| No page reload | ✅ | ❌ | ✅ | ✅ |

---

**MIT License** - Reference implementation for Django web technologies
