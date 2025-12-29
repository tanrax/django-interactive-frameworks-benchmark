# Django Interactive Frameworks Benchmark

Performance comparison of Django's main interactive frameworks. This project implements the same alert system using five different approaches: Django LiveView (WebSocket), traditional SSR, django-htmx (AJAX), Django Unicorn (reactive components), and Django Reactor (Phoenix LiveView style). The goal is to measure and compare their real-world performance, network overhead, and user experience characteristics.

## Technology Comparison

| Feature | LiveView (`/`) | SSR (`/ssr/`) | django-htmx (`/htmx/`) | Unicorn (`/unicorn/`) | Reactor (`/reactor/`) |
|---------|----------------|---------------|-----------------|----------------------|----------------------|
| **Transport** | WebSocket | HTTP | AJAX | AJAX | WebSocket |
| **Update Type** | Real-time | Full reload | Partial | Reactive | Real-time |
| **Multi-user** | ✅ Broadcast | ❌ | ❌ | ❌ | ✅ Broadcast |
| **Infrastructure** | Redis + Channels | Django only | Django only | Django only | Redis + Channels |

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

## Dependencies

- **[django-liveview](https://django-liveview.andros.dev/)** - WebSocket reactive framework
- **[django-htmx](https://django-htmx.readthedocs.io/)** `==1.22.0` - HTMX middleware for Django
- **[django-unicorn](https://www.django-unicorn.com/)** `==0.62.0` - Reactive components
- **[django-reactor](https://github.com/edelvalle/reactor)** `==5.3.0b0` - Phoenix LiveView for Django
- **[Django Channels](https://channels.readthedocs.io/)** + **[Redis](https://redis.io/)** - WebSocket infrastructure
- **[Daphne](https://github.com/django/daphne)** - ASGI server

## Technology Documentation

- **[Django LiveView](https://django-liveview.andros.dev/)** - Official Django LiveView documentation
- **[HTMX](https://htmx.org/)** - Official HTMX documentation and examples
- **[Django Unicorn](https://www.django-unicorn.com/docs/)** - Complete Unicorn documentation
- **[Django Reactor](https://github.com/edelvalle/reactor)** - Phoenix LiveView but for Django
- **[Django](https://docs.djangoproject.com/)** - Django official documentation (for SSR implementation)

## Performance Testing

Comprehensive performance tests were conducted across all implementations to measure response times for the "Create Alert" action. Tests were performed with 10 iterations per implementation using Chrome DevTools and the Performance API.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Templates not updating | `docker compose restart web` |
| django-htmx 403 CSRF | Check `hx-headers` in `<body>` tag |
| Dark tables | Add `data-theme="light"` to `<html>` |

## Features

| Feature | LiveView | SSR | django-htmx | Unicorn | Reactor |
|---------|:--------:|:---:|:----:|:-------:|:-------:|
| Create alerts | ✅ | ✅ | ✅ | ✅ | ✅ |
| View details | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete | ✅ | ✅ | ✅ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ✅ | ✅ |
| Modals | ✅ | ❌ | ✅ | ✅ | ✅ |
| Form validation | ✅ | ✅ | ✅ | ✅ | ✅ |
| No page reload | ✅ | ❌ | ✅ | ✅ | ✅ |

---

**MIT License** - Reference implementation for Django web technologies
