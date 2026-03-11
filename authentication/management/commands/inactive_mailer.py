from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from authentication.models import Registration1


class Command(BaseCommand):
    help = "Quarterly Marital Status Mailer"

    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        if today.day != 1 or today.month not in [2, 5, 8, 11]:
            self.stdout.write("Not scheduled quarter day.")
            return

        users = Registration1.objects.filter(
            Status=1
        ).exclude(
            EmailId__isnull=True
        ).exclude(
            EmailId=""
        )

        for user in users:
            try:
                html_content = render_to_string(
                    "user_api/authentication/inactive_mail.html",
                    {
                        "ProfileName": user.Profile_name or "Member",
                        "UnsubscribeLink": "https://vysyamala.com/unsubscribe"
                    }
                )

                msg = EmailMultiAlternatives(
                    subject="Vysyamala - Still looking for your soulmate?",
                    body="Marital Status Check",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.EmailId],
                )

                msg.attach_alternative(html_content, "text/html")
                msg.send()

                self.stdout.write(f"Sent: {user.ProfileId}")

            except Exception as e:
                self.stdout.write(f"Failed: {user.ProfileId} - {str(e)}")