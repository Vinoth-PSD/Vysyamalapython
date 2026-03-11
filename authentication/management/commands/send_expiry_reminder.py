import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from authentication.models import Registration1,PlanDetails



class Command(BaseCommand):
    help = 'Sends automated reminders for membership expiry (3 days before)'

    def handle(self, *args, **options):

        today = timezone.now().date()
        target_date = today + datetime.timedelta(days=3)

        self.stdout.write(f"--- Processing Membership Expiry Reminders for {target_date} ---")

        start_datetime = timezone.make_aware(
        datetime.datetime.combine(target_date, datetime.time.min)
        )

        end_datetime = timezone.make_aware(
        datetime.datetime.combine(target_date, datetime.time.max)
        )

        expiring_users = Registration1.objects.filter(
        membership_enddate__range=(start_datetime, end_datetime)
        )
        self.stdout.write(f"Found {expiring_users.count()} users with membership expiring on {target_date}.")

        for user in expiring_users:

            if user.EmailId:

                # ✅ Dynamic Days Left
                days_left = (user.membership_enddate.date() - today).days

                # ✅ Fetch Plan Name from plan_master
                plan_name = "Membership Plan"
                if user.Plan_id:
                    try:
                        plan = PlanDetails.objects.get(id=user.Plan_id)
                        plan_name = plan.plan_name
                    except PlanDetails.DoesNotExist:
                        plan_name = "Membership Plan"

                subject = 'Your Membership Expires Soon - Action Required'

                context = {
                    'ProfileName': user.Profile_name or user.ProfileId,
                    'PlanName': plan_name,
                    'DaysLeft': days_left,
                }

                html_content = render_to_string('user_api/authentication/expiry_notification.html', context)
                text_content = strip_tags(html_content)
                

                text_content = strip_tags(html_content)

                try:
                    msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.EmailId]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)

                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully sent expiry email to {user.EmailId}')
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send expiry email to {user.EmailId}: {str(e)}')
                    )

        self.stdout.write(self.style.SUCCESS("\nMembership expiry triggers completed successfully."))
