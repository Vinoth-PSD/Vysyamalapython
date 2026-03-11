from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from authentication import models
from authentication.views import calculate_points_and_get_empty_fields  # adjust path if needed


class Command(BaseCommand):
    help = "Send monthly email to users whose profile completion is below 80%"

    def handle(self, *args, **kwargs):

        registrations = models.Registration1.objects.filter(Status=1)

        total_sent = 0

        for user in registrations:

            profile_id = user.ProfileId
            result = calculate_points_and_get_empty_fields(profile_id)

            completion_percentage = int(result['completion_percentage'])

            if completion_percentage < 80:

                try:
                    email = user.EmailId
                    name = user.Profile_name

                    context = {
                            "Profile_Name": name,
                            "CompletionPercentage": completion_percentage,
                    }

                    subject = "Complete Your Profile – Increase Your Match Chances!"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email = [email]

                    html_content = render_to_string(
                        "user_api/authentication/Completion_Percentage.html",
                        context
                    )

                    msg = EmailMultiAlternatives(subject, "", from_email, to_email)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    self.stdout.write(self.style.SUCCESS(
                        f"Mail sent to {email} | Completion: {completion_percentage}%"
                    ))

                    total_sent += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error sending to {email} - {str(e)}"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"Monthly completion scheduler completed. Total mails sent: {total_sent}"
        ))