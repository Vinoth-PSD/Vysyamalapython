from django.core.mail import send_mail  # To send the email
from django.template.loader import render_to_string  # To render HTML templates
from django.conf import settings  # To access the default email settings


def send_email_notification(from_profile_id,from_profile_name,to_name,to_email, message_title, to_message,notification_type):
        
        print('Express intrests from_profile_id',from_profile_id,notification_type)
        
        subject = message_title

        print('subject',subject)
        
        
        if (notification_type=='update_profile'):
        
            context = {
                'recipient_name': to_name,
                'profile_name': from_profile_name,
                'updated_details':to_message,
                'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id
            }

            html_content = render_to_string('user_api/authentication/profile_update_notification.html', context)
        
        elif(notification_type=='express_interests'):

            context = {
                'recipient_name': to_name,
                'profile_name': from_profile_name,
                'from_profile_id': from_profile_id,
                'updated_details':to_message,
                'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id
            }
            html_content = render_to_string('user_api/authentication/send_express_Interests.html', context)

        elif(notification_type=='express_interests_update'):

            context = {
                'recipient_name': to_name,
                'profile_name': from_profile_name,
                'from_profile_id': from_profile_id,
                'updated_details':to_message,
                'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id,
                'action':'accept'

            }

            html_content = render_to_string('user_api/authentication/accepting_express_Interests.html', context)

        recipient_list = [to_email]

        # send_mail(subject,settings.DEFAULT_FROM_EMAIL,recipient_list,fail_silently=False,html_message=html_content)
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
                subject,
                '',  # No plain text version
                from_email,
                recipient_list,  # Recipient list should be a list
                fail_silently=False,
                html_message=html_content
            )
        print('Email send sucessfully')
