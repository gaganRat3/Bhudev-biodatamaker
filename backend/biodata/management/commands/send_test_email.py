from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send a test email using configured EMAIL settings. Usage: manage.py send_test_email --to=you@example.com'

    def add_arguments(self, parser):
        parser.add_argument('--to', dest='to', help='Recipient email address', required=False)

    def handle(self, *args, **options):
        to = options.get('to') or getattr(settings, 'EMAIL_HOST_USER', None)
        if not to:
            self.stderr.write('No recipient specified and EMAIL_HOST_USER not configured.')
            return

        subject = 'Test email from biodata project'
        message = 'This is a test email sent from the biodata project to verify SMTP settings.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

        self.stdout.write(f"Sending test email to: {to} using backend {getattr(settings, 'EMAIL_BACKEND', 'unknown')}")

        try:
            send_mail(subject=subject, message=message, from_email=from_email, recipient_list=[to], fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f"Email successfully sent to {to}"))
            logger.info("Test email sent to %s", to)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to send email: {e!r}"))
            logger.exception("Failed to send test email")
