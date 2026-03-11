import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from authentication.models import Registration1,Profile_visitors,Express_interests

class Command(BaseCommand):
    help = 'Sends "Upgrade to Premium" emails to users based on behavioral triggers'

    def handle(self, *args, **options):
        today = timezone.now().date()
        three_days_ago = today - datetime.timedelta(days=3)

        self.stdout.write(f"--- Processing Premium Upgrade Triggers: ---")
        
        potential_users = Registration1.objects.filter(Status=1,Plan_id=7)
        
        sent_count = 0
        
        for user in potential_users:
            trigger_reason = None
            
                    # Count Express Interests where status = 1
            express_interest_count = Express_interests.objects.filter(
                profile_from=user.ProfileId,
                status=1
            ).count()
            # Count Profile Views
            profile_view_count = Profile_visitors.objects.filter(
                profile_id=user.ProfileId
            ).count()

            print("test1",profile_view_count)
            if express_interest_count > 3 and profile_view_count > 10 and  user.DateOfJoin and user.DateOfJoin.date() <= three_days_ago:
                print("testererer")
                trigger_reason = "Sent 3+ express interests"

       
        
            
                if trigger_reason:
                    if user.EmailId:
                        subject = 'Upgrade to Premium & Connect Faster 💍'
                        context = {
                            'ProfileName': user.Profile_name or user.ProfileId,
                            
                        }
                        
                        html_content = render_to_string('user_api/authentication/premium_upgrade.html', context)
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
                            
                            
                            sent_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'Sent Upgrade email to {user.EmailId} (Reason: {trigger_reason})'
                            ))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f'Failed to send to {user.EmailId}: {str(e)}'
                            ))
                    else:
                        self.stdout.write(self.style.WARNING(f'User {user.ProfileId} has no email address.'))

        self.stdout.write(self.style.SUCCESS(f"\nPremium upgrade triggers completed. Total sent: {sent_count}"))
