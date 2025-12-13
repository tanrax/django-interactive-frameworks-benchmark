from django.core.management.base import BaseCommand

from alerts.models import Alert


class Command(BaseCommand):
	help = 'Clear all alerts from the database'

	def handle(self, *args, **options):
		count = Alert.objects.all().count()
		Alert.objects.all().delete()
		self.stdout.write(
			self.style.SUCCESS(f'Successfully deleted {count} alerts')
		)
