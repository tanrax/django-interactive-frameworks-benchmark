from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
	path('', views.index, name='index'),

	# SSR (Standard Django) routes
	path('ssr/', views.ssr_index, name='ssr_index'),
	path('ssr/create/', views.ssr_create_alert, name='ssr_create_alert'),
	path('ssr/create-random/', views.ssr_create_random_alert, name='ssr_create_random_alert'),
	path('ssr/delete/<int:alert_id>/', views.ssr_delete_alert, name='ssr_delete_alert'),
	path('ssr/detail/<int:alert_id>/', views.ssr_alert_detail, name='ssr_alert_detail'),

	# HTMX routes
	path('htmx/', views.htmx_index, name='htmx_index'),
	path('htmx/alerts-table/', views.htmx_alerts_table, name='htmx_alerts_table'),
	path('htmx/create/', views.htmx_create_alert, name='htmx_create_alert'),
	path('htmx/create-random/', views.htmx_create_random_alert, name='htmx_create_random_alert'),
	path('htmx/delete/<int:alert_id>/', views.htmx_delete_alert, name='htmx_delete_alert'),
	path('htmx/detail/<int:alert_id>/', views.htmx_alert_detail, name='htmx_alert_detail'),

	# Django Unicorn routes
	path('unicorn/', views.unicorn_index, name='unicorn_index'),

	# Django Reactor routes
	path('reactor/', views.reactor_index, name='reactor_index'),
]
