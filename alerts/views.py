from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Alert
from .forms import AlertForm
import random


def index(request):
	alerts = Alert.objects.all()
	return render(request, 'alerts/index.html', {'alerts': alerts})


# SSR Views (Standard Django with full page reloads)
def ssr_index(request):
	alerts = Alert.objects.all()
	return render(request, 'alerts/ssr/index.html', {'alerts': alerts})


def ssr_create_alert(request):
	if request.method == 'POST':
		form = AlertForm(request.POST)
		if form.is_valid():
			alert = form.save()
			messages.success(request, f'New {alert.type} alert created!')
			return redirect('alerts:ssr_index')
	else:
		form = AlertForm()
	return render(request, 'alerts/ssr/create.html', {'form': form})


def ssr_create_random_alert(request):
	if request.method == 'POST':
		alert_types = ['INFO', 'WARNING', 'CRITICAL']
		random_type = random.choice(alert_types)
		Alert.objects.create(type=random_type, description='Random alert')
		messages.success(request, f'Random {random_type} alert created!')
	return redirect('alerts:ssr_index')


def ssr_delete_alert(request, alert_id):
	if request.method == 'POST':
		alert = get_object_or_404(Alert, id=alert_id)
		alert.delete()
		messages.success(request, 'Alert deleted successfully!')
	return redirect('alerts:ssr_index')


def ssr_alert_detail(request, alert_id):
	alert = get_object_or_404(Alert, id=alert_id)
	return render(request, 'alerts/ssr/detail.html', {'alert': alert})


# HTMX Views (Partial HTML updates)
def htmx_index(request):
	alerts = Alert.objects.all()
	return render(request, 'alerts/htmx/index.html', {'alerts': alerts})


def htmx_alerts_table(request):
	alerts = Alert.objects.all()
	return render(request, 'alerts/htmx/partials/alerts_table.html', {'alerts': alerts})


def htmx_create_alert(request):
	if request.method == 'POST':
		form = AlertForm(request.POST)
		if form.is_valid():
			alert = form.save()
			if request.htmx:
				alerts = Alert.objects.all()
				response = render(request, 'alerts/htmx/partials/alerts_table.html', {'alerts': alerts})
				response['HX-Trigger'] = f'{{"showNotification": {{"message": "New {alert.type} alert created!", "type": "success"}}}}'
				return response
			messages.success(request, f'New {alert.type} alert created!')
			return redirect('alerts:htmx_index')
		else:
			if request.htmx:
				return render(request, 'alerts/htmx/partials/create_form.html', {'form': form}, status=422)
	else:
		form = AlertForm()

	if request.htmx:
		return render(request, 'alerts/htmx/partials/create_form.html', {'form': form})
	return render(request, 'alerts/htmx/create.html', {'form': form})


def htmx_create_random_alert(request):
	if request.method == 'POST':
		alert_types = ['INFO', 'WARNING', 'CRITICAL']
		random_type = random.choice(alert_types)
		alert = Alert.objects.create(type=random_type, description='Random alert')

		if request.htmx:
			alerts = Alert.objects.all()
			response = render(request, 'alerts/htmx/partials/alerts_table.html', {'alerts': alerts})
			response['HX-Trigger'] = f'{{"showNotification": {{"message": "Random {random_type} alert created!", "type": "success"}}}}'
			return response

		messages.success(request, f'Random {random_type} alert created!')
	return redirect('alerts:htmx_index')


def htmx_delete_alert(request, alert_id):
	if request.method == 'POST' or request.method == 'DELETE':
		alert = get_object_or_404(Alert, id=alert_id)
		alert.delete()

		if request.htmx:
			alerts = Alert.objects.all()
			response = render(request, 'alerts/htmx/partials/alerts_table.html', {'alerts': alerts})
			response['HX-Trigger'] = '{"showNotification": {"message": "Alert deleted successfully!", "type": "success"}}'
			return response

		messages.success(request, 'Alert deleted successfully!')
	return redirect('alerts:htmx_index')


def htmx_alert_detail(request, alert_id):
	alert = get_object_or_404(Alert, id=alert_id)
	if request.htmx:
		return render(request, 'alerts/htmx/partials/alert_modal.html', {'alert': alert})
	return render(request, 'alerts/htmx/detail.html', {'alert': alert})


# Django Unicorn Views
def unicorn_index(request):
	return render(request, 'alerts/unicorn/index.html')


# Django Reactor Views
def reactor_index(request):
	return render(request, 'alerts/reactor/index.html')
