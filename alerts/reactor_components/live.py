import random
from reactor.component import Component
from alerts.models import Alert
from alerts.forms import AlertForm


class XAlertList(Component):
	_template_name = 'reactor/x-alert-list.html'

	show_modal: bool = False
	show_create_modal: bool = False
	selected_alert_id: int = 0
	alerts = []

	# Form fields
	type: str = ""
	description: str = ""
	form_errors = {}

	async def mount(self):
		await self.load_alerts()

	async def load_alerts(self):
		self.alerts = list(
			Alert.objects.all().values('id', 'type', 'description', 'created_at')
		)

	async def create_random_alert(self):
		alert_types = ['INFO', 'WARNING', 'CRITICAL']
		random_type = random.choice(alert_types)
		Alert.objects.create(type=random_type, description='Random alert')
		await self.load_alerts()

	async def show_create_form(self):
		self.show_create_modal = True
		self.type = ""
		self.description = ""
		self.form_errors = {}

	async def create_alert(self):
		form = AlertForm(data={'type': self.type, 'description': self.description})
		if form.is_valid():
			alert = form.save()
			await self.load_alerts()
			self.show_create_modal = False
			self.type = ""
			self.description = ""
			self.form_errors = {}
		else:
			self.form_errors = dict(form.errors)

	async def delete_alert(self, alert_id: int):
		Alert.objects.filter(id=alert_id).delete()
		await self.load_alerts()
		self.show_modal = False

	async def show_detail(self, alert_id: int):
		self.selected_alert_id = alert_id
		self.show_modal = True

	async def close_modal(self):
		self.show_modal = False
		self.selected_alert_id = 0

	async def close_create_modal(self):
		self.show_create_modal = False
		self.type = ""
		self.description = ""
		self.form_errors = {}

	def get_selected_alert(self):
		if self.selected_alert_id:
			alert = Alert.objects.filter(id=self.selected_alert_id).first()
			if alert:
				return {
					'id': alert.id,
					'type': alert.type,
					'description': alert.description or 'No description provided',
					'created_at': alert.created_at
				}
		return None
