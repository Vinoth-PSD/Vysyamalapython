from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from matrimony import models, serializers
from matrimony.helpers import get_profile_details, Get_profile_image, get_default_or_blurred_image

def can_get_viewd_profile_count(profile_id,req_profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    

    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    # print('current_datetime',timezone.now())
    # print('current_date',current_date)

    # print(plan)
    
    check_aldready_visits = models.Profile_visitors.objects.filter(profile_id=profile_id,viewed_profile=req_profile_id).count()
    print('check_aldready_visits',check_aldready_visits)
    if int(check_aldready_visits) >= 1:
        return True
   
    # Check if the plan allows sending express interests
    if plan and plan.profile_permision_toview is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.profile_permision_toview == 0:
            return False  # Not allowed to send express interests
        elif plan.profile_permision_toview == 1:
            return True  # Unlimited express interests
        else:
                        # Check how many visitor counts does user have in their plan
            #print('894563')
                       
            if plan_id in [6, 7, 8, 9]:   #those plan count was not for per day those all for pverall plan count
                
                visit_int_count = models.Profile_visitors.objects.filter(
                        profile_id=profile_id
                    ).exclude(viewed_profile=req_profile_id).count()

                print('visit_int_count',visit_int_count)
                print('profile_permision_toview',plan.profile_permision_toview)

                if visit_int_count < plan.profile_permision_toview:
                        return True  # Within the express interest limit
                else:
                        return False  # Reached the limit

            else:
                
                start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)

                    # print('date',date.today())
                visit_int_count = models.Profile_visitors.objects.filter(
                        profile_id=profile_id,
                        datetime__gte=start_of_day, 
                        datetime__lt=end_of_day
                    ).exclude(viewed_profile=req_profile_id).count()
                print('visit_int_count',visit_int_count)
                print('profile_permision_toview',plan.profile_permision_toview)

                    # print('visit_int_count',visit_int_count)
                    # print('profile_permision_toview',plan.profile_permision_toview)

                if visit_int_count < plan.profile_permision_toview:
                        return True  # Within the express interest limit
                else:
                        return False  # Reached the limit

    return False  # If no plan or plan is restricted

def get_permission_limits(profile_id, column_name):
    get_limits = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,status=1).first()

    if get_limits and hasattr(get_limits, column_name):  
        return getattr(get_limits, column_name)  # Dynamically fetch the column value

    return None  # Return None if no record exists or column is invalid

    #return True


class ProfileDetailFetcher:
    def __init__(self, profile_id, user_profile_id):
        self.profile_id = profile_id
        self.user_profile_id = user_profile_id
        self.profile_details = get_profile_details([user_profile_id])[0]
        self.my_profile_details = get_profile_details([profile_id])[0]

    def fetch(self):
        profile = self.profile_details
        my_gender = self.my_profile_details['Gender']

        image_data = self._get_profile_images(profile, my_gender)
        extra_data = self._get_additional_details(profile)
        active_status = self._get_login_status(profile.get('Last_login_date'))

        response = {
            'profile_data': profile,
            'user_images': image_data,
            'extra': extra_data,
            'status': active_status,
        }

        vysy_data = self._get_vysy_assist_data()
        if vysy_data:
            response['vysy_assist'] = vysy_data

        return response

    def _get_profile_images(self, profile, gender):
        photo_viewing = get_permission_limits(self.profile_id, 'photo_viewing')
        if photo_viewing:
            return Get_profile_image(profile['ProfileId'], gender, 'all', profile['Photo_protection'])
        return get_default_or_blurred_image(profile['ProfileId'], gender)

    def _get_additional_details(self, profile):
        def get_obj(model, field, key='id'):
            try:
                return getattr(model.objects.get(**{key: profile[field]}), 'name', None)
            except model.DoesNotExist:
                return None

        return {
            'complexion': self._get_model_desc(models.Profilecomplexion, 'complexion_id', 'complexion_desc'),
            'highest_education': self._get_model_desc(models.Edupref, 'RowId', 'EducationLevel', 'highest_education'),
            'profession': self._get_model_desc(models.Profespref, 'RowId', 'profession', 'profession'),
            'profile_for': self._get_model_desc(models.Profileholder, 'Mode', 'ModeName', 'Profile_for'),
            'marital_status': self._get_model_desc(models.ProfileMaritalstatus, 'StatusId', 'MaritalStatus', 'Profile_marital_status'),
            'family_status': self._get_model_desc(models.Familystatus, 'id', 'status', 'family_status'),
            'birthstar': self._get_model_desc(models.Birthstar, 'id', 'star', 'birthstar_name'),
            'rasi': self._get_model_desc(models.Rasi, 'id', 'name', 'birth_rasi_name'),
            'horoscope': self._get_horoscope(profile)
        }

    def _get_model_desc(self, model, key_field, desc_field, profile_key=None):
        field = profile_key or key_field
        try:
            return getattr(model.objects.get(**{key_field: self.profile_details[field]}), desc_field)
        except model.DoesNotExist:
            return None

    def _get_horoscope(self, profile):
        permission = get_permission_limits(self.profile_id, 'eng_print')
        file = profile.get('horoscope_file')

        if not file or permission == 0:
            return {
                'available': 0,
                'text': 'Not available',
                'link': ''
            }

        return {
            'available': 1,
            'text': 'Horoscope Available',
            'link': settings.MEDIA_URL + file
        }

    def _get_login_status(self, last_login):
        if not isinstance(last_login, datetime):
            return {'status': 'Newly registered'}

        days_diff = (timezone.now().replace(tzinfo=None) - last_login).days
        status = "Active User" if days_diff <= 30 else "In Active User"
        return {'last_visit': last_login.strftime("(%B %d, %Y)"), 'status': status}

    def _get_vysy_assist_data(self):
        if not get_permission_limits(self.profile_id, 'vys_assist'):
            return None

        try:
            assist = models.Profile_vysassist.objects.get(profile_from=self.profile_id, profile_to=self.user_profile_id)
            followups = models.ProfileVysAssistFollowup.objects.filter(assist_id=assist.id).order_by('-update_at')

            if followups.exists():
                return serializers.ProfileVysAssistFollowupSerializer(followups, many=True).data
            return [{
                "comments": assist.to_message + ' (Request sent)',
                "update_at": assist.req_datetime
            }]
        except models.Profile_vysassist.DoesNotExist:
            return None
