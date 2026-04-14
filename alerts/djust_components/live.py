import random

from djust import LiveView
from djust.decorators import event_handler

from alerts.forms import AlertForm
from alerts.models import Alert


class AlertLiveView(LiveView):
	template_name = 'alerts/djust/index.html'
	login_required = False

	def mount(self, request, **kwargs):
		self.show_modal = False
		self.show_create_modal = False
		self.selected_alert_id = 0
		self.form_type = ''
		self.form_description = ''
		self.form_errors = {}
		self._load_alerts()

	def _load_alerts(self):
		self.alerts = list(
			Alert.objects.all().values('id', 'type', 'description', 'created_at')
		)

	def _selected_alert(self):
		if not self.selected_alert_id:
			return None
		alert = Alert.objects.filter(id=self.selected_alert_id).first()
		if not alert:
			return None
		return {
			'id': alert.id,
			'type': alert.type,
			'description': alert.description or 'No description provided',
			'created_at': alert.created_at,
		}

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
		context.update({
			'alerts': self.alerts,
			'show_modal': self.show_modal,
			'show_create_modal': self.show_create_modal,
			'selected_alert': self._selected_alert(),
			'form_type': self.form_type,
			'form_description': self.form_description,
			'form_errors': self.form_errors,
		})
		return context

	@event_handler
	def create_random_alert(self, **kwargs):
		random_type = random.choice(['INFO', 'WARNING', 'CRITICAL'])
		Alert.objects.create(type=random_type, description='Random alert')
		self._load_alerts()

	@event_handler
	def show_create_form(self, **kwargs):
		self.show_create_modal = True
		self.form_type = ''
		self.form_description = ''
		self.form_errors = {}

	@event_handler
	def close_create_modal(self, **kwargs):
		self.show_create_modal = False
		self.form_type = ''
		self.form_description = ''
		self.form_errors = {}

	@event_handler
	def update_type(self, value='', **kwargs):
		self.form_type = value

	@event_handler
	def update_description(self, value='', **kwargs):
		self.form_description = value

	@event_handler
	def create_alert(self, **kwargs):
		form = AlertForm(data={'type': self.form_type, 'description': self.form_description})
		if form.is_valid():
			form.save()
			self._load_alerts()
			self.show_create_modal = False
			self.form_type = ''
			self.form_description = ''
			self.form_errors = {}
		else:
			self.form_errors = {k: list(v) for k, v in form.errors.items()}

	@event_handler
	def show_detail(self, alert_id=None, **kwargs):
		self.selected_alert_id = int(alert_id) if alert_id else 0
		self.show_modal = True

	@event_handler
	def close_modal(self, **kwargs):
		self.show_modal = False
		self.selected_alert_id = 0

	@event_handler
	def delete_alert(self, alert_id=None, **kwargs):
		if alert_id:
			Alert.objects.filter(id=int(alert_id)).delete()
			self._load_alerts()
		self.show_modal = False
