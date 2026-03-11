from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import Registration1


class Command(BaseCommand):
    help = "Check membership expiry and send emails"

    def handle(self, *args, **kwargs):

        now = timezone.now()

        users = Registration1.objects.filter(
            membership_enddate__isnull=False,
            membership_enddate__lt=now,
            EmailId__isnull=False
        )

        for user in users:

            if user.plan_status == 1:
                self.send_mail(user)

                user.plan_status = 0
                user.expired_mail_last_sent = now
                user.save(update_fields=["plan_status", "expired_mail_last_sent"])

                self.stdout.write(f"Immediate expired mail sent: {user.ProfileId}")
            elif user.plan_status == 0 and user.expired_mail_last_sent:

                days_passed = (now - user.expired_mail_last_sent).days

                if days_passed >= 45:
                    self.send_mail(user)

                    user.expired_mail_last_sent = now
                    user.save(update_fields=["expired_mail_last_sent"])

                    self.stdout.write(f"45-day follow-up sent: {user.ProfileId}")


    def send_mail(self, user):
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings

    
        html_content = render_to_string(
            "user_api/authentication/membership_expired.html",
            {
                "ProfileName": user.Profile_name,
                "PlanName": user.Plan_id,
              
            }
        )

        msg = EmailMultiAlternatives(
            subject=f"Your {user.Plan_id} Membership Has Expired",
            body="Your membership has expired.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.EmailId],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()