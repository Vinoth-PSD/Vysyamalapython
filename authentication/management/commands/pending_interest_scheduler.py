from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from authentication import models


class Command(BaseCommand):
    help = "Send monthly reminder for pending interests older than 7 days, but only one mail per user"

    def handle(self, *args, **kwargs):
        one_week_ago = timezone.now() - timedelta(days=7)

        interests = models.Express_interests.objects.filter(
            status="1",
            req_datetime__lte=one_week_ago
        )

        profile_ids = interests.values_list("profile_to", flat=True).distinct()

        for profile_id in profile_ids:
            try:
                profile = models.Registration1.objects.get(ProfileId=profile_id)
            except models.Registration1.DoesNotExist:
                continue

            pending_count = interests.filter(profile_to=profile_id).count()

            context = {
                "ProfileName": profile.ProfileId,
                "PendingCount": pending_count
            }

            html_content = render_to_string(
                "user_api/authentication/Pending_Interests.html",
                context
            )

            send_mail(
                subject="You have pending interests waiting!",
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.EmailId],
                html_message=html_content,
                fail_silently=False,
            )

            self.stdout.write(f"Mail sent to {profile.EmailId} with {pending_count} pending interests")

        self.stdout.write("Monthly scheduler completed")