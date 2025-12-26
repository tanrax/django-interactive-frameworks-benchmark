import random
from django_unicorn.components import UnicornView
from alerts.models import Alert
from alerts.forms import AlertForm


class AlertListView(UnicornView):
	alerts: list = []
	show_modal = False
	show_create_modal = False
	selected_alert = None
	form_class = AlertForm

	# Form fields
	type = ""
	description = ""

	def mount(self):
		self.load_alerts()

	def load_alerts(self):
		self.alerts = list(Alert.objects.all().values('id', 'type', 'description', 'created_at'))

	def create_random_alert(self):
		alert_types = ['INFO', 'WARNING', 'CRITICAL']
		random_type = random.choice(alert_types)
		Alert.objects.create(type=random_type, description='Random alert')
		self.load_alerts()
		self.call('showNotification', f'Random {random_type} alert created!', 'success')

	def show_create_form(self):
		self.show_create_modal = True
		self.type = ""
		self.description = ""

	def create_alert(self):
		if self.is_valid():
			alert = Alert.objects.create(type=self.type, description=self.description)
			self.load_alerts()
			self.show_create_modal = False
			self.type = ""
			self.description = ""
			self.call('showNotification', f'New {alert.type} alert created!', 'success')

	def delete_alert(self, alert_id: int):
		Alert.objects.filter(id=alert_id).delete()
		self.load_alerts()
		self.show_modal = False
		self.call('showNotification', 'Alert deleted successfully!', 'success')

	def show_detail(self, alert_id: int):
		alert = Alert.objects.filter(id=alert_id).first()
		if alert:
			self.selected_alert = {
				'id': alert.id,
				'type': alert.type,
				'description': alert.description or 'No description provided',
				'created_at': alert.created_at
			}
			self.show_modal = True

	def close_modal(self):
		self.show_modal = False
		self.selected_alert = None

	def close_create_modal(self):
		self.show_create_modal = False
		self.type = ""
		self.description = ""
