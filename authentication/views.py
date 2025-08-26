from django.contrib.auth.models import User  # Import the User model
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView,status
#from .models import AuthUser,Profileholder,Profileheights  # Assuming AuthUser is your user model
from . import models
from rest_framework import status
from . import serializers
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from PIL import Image
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
import io
import os
from django.core.files.base import ContentFile
from django.db.models import Q ,Case, When, Value, IntegerField
import requests
from collections import defaultdict
from datetime import datetime , date
from django.utils.timezone import localtime,now
from django.utils import timezone
from .models import SentWithoutAddressEmailLog
from .models import SentWithoutAddressPrintPDFLog

from io import BytesIO
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser, FormParser
import zipfile
from datetime import datetime, timedelta
import base64
import re

from django.template.loader import render_to_string

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
# from xhtml2pdf import pisa
from django.db import connection
# from django.core.mail import send_mail

from django.core.mail import send_mail, EmailMultiAlternatives
import secrets
from .encryption_utils import encrypt_password, decrypt_password
from django.contrib.auth.hashers import make_password, check_password
from .utils import send_email_notification
import razorpay

import logging
logger = logging.getLogger(__name__)

import hmac
import hashlib
import base64

from django.http import HttpRequest, Http404


from xhtml2pdf import pisa
from django.db import connection
from django.core.mail import send_mail
# from deep_translator import GoogleTranslator
from django.core.mail import EmailMessage
from PyPDF2 import PdfMerger
from accounts.models import LoginDetails
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import SentWithoutAddressPrintwpPDFLog

# from rest_framework.permissions import IsAuthenticated
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication
# import imgkit
from django.core.files.base import ContentFile
import base64
import tempfile
from django.http import HttpResponse
#config = imgkit.config(wkhtmltoimage="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe")
import uuid
from azure.storage.blob import BlobServiceClient
from urllib.parse import urlparse
from azure.storage.blob import ContentSettings  # Add this import
# from authentication.helpers.matching import get_matching_score_util
from authentication.helpers.matching import preload_matching_scores , get_matching_score_util
from django.core.cache import cache

from django.core.cache import caches
import hashlib
from pathlib import Path
from django.forms.models import model_to_dict
import time  # For performance measurement
import logging
from functools import lru_cache
from django.db.models import Prefetch




class LoginView(APIView):
    # authentication_classes = []
    # permission_classes = []


    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = JsonResponse({'detail': 'OK'})
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  # Include other headers as needed
        return JsonResponse(response)



    

    def post(self, request, *args, **kwargs):
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        fcm_token = data.get('fcm_token')
        # print('Username, password',username,password)
        

        
        try:
            # auth_user = models.Registration1.objects.get(ProfileId=username,Password=password)
            #auth_user = models.Registration1.objects.get(ProfileId=username, Password__iexact=password)
            #ency_password=encrypt_password(password)
            # print('ency_password', ency_password)
            auth_user = models.Registration1.objects.get(ProfileId=username, Status__in=[0,1,2,3])
                      
            # if check_password(password,auth_user.Password):
            if password == auth_user.Password:
                user, created = User.objects.get_or_create(username=auth_user.ProfileId)
                if created:
                    # Handle user creation logic if needed
                    pass
                    
                # Authentication successful, create token
                token, created = Token.objects.get_or_create(user=user)

                notify_count=models.Profile_notification.objects.filter(profile_id=username, is_read=0).count()

                logindetails=models.Registration1.objects.filter(ProfileId=username).first()

                profile_for=logindetails.Profile_for
                try:
                        Profile_owner = models.Profileholder.objects.get(Mode=profile_for).ModeName
                except models.Profileholder.DoesNotExist:
                        Profile_owner = None
                
                logindetails.Last_login_date=timezone.now()
                

                if(fcm_token):

                    logindetails.fcm_token=fcm_token

                logindetails.save()

                

                login_log = models.profile_loginLogs(
                        profile_id=username,
                        user_token=token.key,
                        login_datetime=datetime.now(),  # Use the current datetime or specify a custom datetime
                        logout_datetime=None  # Set to None initially; update when the user logs out
                    )
                
                login_log.save()



                horodetails=models.Horoscope.objects.filter(profile_id=username).first()
                
                #get first image for the profile icon
                profile_images=models.Image_Upload.objects.filter(profile_id=username).first()  

                plan_id = logindetails.Plan_id
                plan_limits_json=''
                if plan_id:
                    plan_limits=models.PlanFeatureLimit.objects.filter(plan_id=plan_id)
                
                    serializer = serializers.PlanFeatureLimitSerializer(plan_limits, many=True)
                    plan_limits_json = serializer.data


                gender = logindetails.Gender
                height = logindetails.Profile_height
                marital_status=logindetails.Profile_marital_status
                quick_reg=logindetails.quick_registration
                if not quick_reg:
                    quick_reg=0

                profile_icon=''
                profile_completion=0
                birth_star_id=''
                birth_rasi_id=''
                profile_image=''
                if horodetails:
                    birth_star_id=horodetails.birthstar_name
                    birth_rasi_id=horodetails.birth_rasi_name

                if profile_images:
                    profile_icon=profile_images.image.url
                    profile_image = profile_icon
                #default image icon
                else:

                    profile_icon = 'men.jpg' if gender == 'male' else 'women.jpg'
                    profile_image = settings.MEDIA_URL+profile_icon
                    
                    
                # profile_image = settings.MEDIA_URL+profile_icon


                #logindetails_exists = models.Registration1.objects.filter(ProfileId=username).filter(Profile_address__isnull=False).exclude(Profile_address__exact='').first()
                logindetails_exists = models.Registration1.objects.filter(ProfileId=username).first()
                family_details_exists=models.Familydetails.objects.filter(profile_id=username).first()
                horo_details_exists=models.Horoscope.objects.filter(profile_id=username).first()
                education_details_exists=models.Edudetails.objects.filter(profile_id=username).first()
                partner_details_exists=models.Partnerpref.objects.filter(profile_id=username).first()

                profile_planfeature = models.Profile_PlanFeatureLimit.objects.filter(profile_id=username, status=1).first()
                valid_till = profile_planfeature.membership_todate if profile_planfeature else None

                #check the address is exists for the contact s page contact us details stored in the logindetails page only
                if not logindetails_exists:
                    
                    profile_completion=1     #contact details not exists   

                elif not family_details_exists:
                    
                    profile_completion=2    #Family details not exists   

                elif not horo_details_exists:
                    profile_completion=3    #Horo details not exists   

                elif not education_details_exists:
                    profile_completion=4        #Edu details not exists   

                elif not partner_details_exists:
                    profile_completion=5            #Partner details not exists   

                return JsonResponse({'status': 1,'token':token.key ,'profile_id':username ,'message': 'Login Successful',"notification_count":notify_count,"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,"gender":gender,"height":height,"marital_status":marital_status,"custom_message":1,"birth_star_id":birth_star_id,"birth_rasi_id":birth_rasi_id,"profile_owner":Profile_owner,"quick_reg":quick_reg,"plan_limits":plan_limits_json,"valid_till":valid_till}, status=200)

            else:
            # Password is incorrect
             return JsonResponse({'status': 0, 'message': 'Invalid credentials'})
        except models.Registration1.DoesNotExist:
            return JsonResponse({'status': 0, 'message': 'Invalid credentials'})
        

class LogoutView(APIView):
    def post(self, request):
        # Get the token key from the request header or data
        token_key = request.POST.get('token_key', None)

        if token_key:
            # Retrieve the token object based on the token key
            try:
                token = Token.objects.get(key=token_key)
            except Token.DoesNotExist:
                return JsonResponse({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete the token from the database
            token.delete()
            return JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Token key not provided'}, status=status.HTTP_400_BAD_REQUEST)





class Otp_verify(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)  # Debugging: print incoming data
        
        serializer = serializers.OtpSerializers(data=request.data)
        if serializer.is_valid():
            
          return JsonResponse({"message": "OTP verified successfully."}, status=status.HTTP_201_CREATED)
            
        else:
            #return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({"Status":0,"message": "Enter a valid Otp"}, status=status.HTTP_201_CREATED)


class Get_resend_otp(APIView):

     def post(self, request, *args, **kwargs):
       
        serializer = serializers.ResendOtpSerializers(data=request.data)

        

        if serializer.is_valid():
            # print('data123456')
            
            ProfileId= serializer.validated_data.get('ProfileId')

            # print('data123456',ProfileId)
            
            Otp=serializer.validated_data.get('Otp')
            numbers=serializer.validated_data.get('mobile_no')
            # print('Otp',Otp)
            # print('numbers',numbers)
            #serializer.update()
            
            sms_sender = SendSMS()
            message_id = sms_sender.send_sms(Otp, numbers)
            dlr_status = sms_sender.check_dlr(message_id)
            available_credit = sms_sender.available_credit()

            response_data = {
                    "message": "OTP resent successfully.",
                    "Send Message Response": message_id,
                    "Delivery Report Status": dlr_status,
                    "Available Credit": available_credit
                }
            
            models.Basic_Registration.objects.filter(ProfileId=ProfileId).update(Otp=Otp)
            return JsonResponse({"Status":1,"response_data":response_data,"profile_id":ProfileId,"message": "Otp resent sucessfully"}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # else:
        #     #return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #     return JsonResponse({"Status":0,"message": "Enter a valid Otp"}, status=status.HTTP_201_CREATED)





class Registrationstep1(APIView):

    def post(self, request, *args, **kwargs):
       
        serializer = serializers.Registration1Serializer(data=request.data)

        # data1 = json.loads(request.body)
        # mobile_no = data1.get('mobile_no')

        #print('Serializer ',serializer)
        mobile_country =request.data.get('mobile_country')
        if serializer.is_valid():
            serializer.save()
            mobile_no = serializer.validated_data.get('Mobile_no')
            Profile_for = serializer.validated_data.get('Profile_for')
            ProfileId= serializer.validated_data.get('ProfileId')
            Gender= serializer.validated_data.get('Gender')
            EmailId= serializer.validated_data.get('EmailId')
            #mobile_country=serializer.validated_data.get('mobile_country')
            
            Profile_Owner = models.Profileholder.objects.get(Mode=Profile_for)

            otp = serializer.validated_data.get('Otp')
            #otp =123456
            numbers = serializer.validated_data.get('Mobile_no')

                # Create an instance of SendSMS and send OTP

            #comented on 30th jully to hardcode value to set

            print('mobile_country',mobile_country)

            if((mobile_country=='91')):

                sms_sender = SendSMS()
                message_id = sms_sender.send_sms(otp, numbers)
                dlr_status = sms_sender.check_dlr(message_id)
                available_credit = sms_sender.available_credit()

                response_data = {
                        "message": "OTP sent successfully.",
                        "Send Message Response": message_id,
                        "Delivery Report Status": dlr_status,
                        "Available Credit": available_credit
                    }
                verify_type='Mobile Otp'
            else:
                
                context={
                        "otp":otp
                    }
                html_content = render_to_string('user_api/authentication/registration_otp.html', context)               
                recipient_list = [EmailId]

                # send_mail(subject,settings.DEFAULT_FROM_EMAIL,recipient_list,fail_silently=False,html_message=html_content)
                from_email = settings.DEFAULT_FROM_EMAIL
                
                subject='Vysyamala Mobile otp verification'

                response_data={ 
                    "message": "OTP sent successfully."
                    }
                send_mail(
                        subject,
                        '',  # No plain text version
                        from_email,
                        recipient_list,  # Recipient list should be a list
                        fail_silently=False,
                        html_message=html_content
                    )
                verify_type='Email Otp'




            return JsonResponse({"Status":1,"profile_owner":Profile_Owner.ModeName,"response_data":response_data,'Gender':Gender,"Mobile_no":mobile_no,"profile_id":ProfileId,"message": "Registration successful","verify_type":verify_type}, status=status.HTTP_201_CREATED)
        
        else:
            # return JsonResponse(serializer.errors, status=status.HTTP_200_OK)
            return JsonResponse({
                "Status": 0,  # Adding status here to indicate failure
                "errors": serializer.errors
            }, status=status.HTTP_200_OK)


# class Registrationstep2(APIView):

#     def post(self, request, *args, **kwargs):
#         serializer = serializers.Registration2Serializer(data=request.data)
        
#         if serializer.is_valid():
#             profile_id = serializer.validated_data.get('ProfileId')
#             try:
#                 registration = models.Registration1.objects.get(ProfileId=profile_id)
#                 serializer.update(registration, serializer.validated_data)
#                 return JsonResponse({"Status": 1, "message": "Registration step 2 successful"}, status=status.HTTP_200_OK)
#             except  models.Registration1.DoesNotExist:
#                 return JsonResponse({"Status": 0, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Registrationstep2(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.Registration2Serializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('ProfileId')  
            # print('profile_id',profile_id)     
            
            try:
                #print('profil id',profile_id)
                # Check if the profile exists in Registration1 table
                
                registration = models.Basic_Registration.objects.get(ProfileId=profile_id,Status=0)
                
                try:
                    last_record = models.Registration1.objects.latest('ContentId')
                    last_record_id = last_record.ContentId
                except models.Registration1.DoesNotExist:
                     last_record_id = 0 
                
                numeric_part = str(last_record_id + 1).zfill(3) 

                # if last_record.Gender.lower()=='male':
                if registration.Gender.strip().lower() == 'male':
                
                    new_profile_id = f"VM{numeric_part}" 
                else :
                    new_profile_id = f"VF{numeric_part}"
                
                # Update or create in Registration2 table
                registration_data = {
                    'ProfileId': new_profile_id,
                    'Profile_for': registration.Profile_for,
                    'Gender': registration.Gender,
                    'Mobile_no': registration.Mobile_no,
                    'EmailId': registration.EmailId,
                    'Password': registration.Password,
                    'Profile_name': serializer.validated_data.get('Profile_name'),
                    'Profile_marital_status': serializer.validated_data.get('Profile_marital_status'),
                    'Profile_dob': serializer.validated_data.get('Profile_dob'),
                    'Profile_height': serializer.validated_data.get('Profile_height'),
                    'Profile_complexion': serializer.validated_data.get('Profile_complexion'), 
                    'DateOfJoin': timezone.now(), 
                    'Otp': 0,
                    'Status': 0,
                    'temp_profileid':profile_id,
                    'Reset_OTP_Time':None,
                    'Plan_id':7, #by default free plan
                    'primary_status':0,
                    'secondary_status':26,  #free and the newly registered
                    'plan_status':7

                    
                    # Add other fields as needed
                }

                #print('registration_data',registration_data)
                
                # Use Registration2 model serializer to create or update
                # registration2_serializer = serializers.Registration2Serializer(data=registration_data)
                # if registration2_serializer.is_valid():
                #     # registration2_instance, created = models.Registration1.objects.create(
                #     #     temp_profileid=profile_id,
                #     #     defaults=registration_data
                #     # )
                #     registration2_instance = registration2_serializer.save()
                insert_rowintables={
                    'profile_id': new_profile_id
                }

                # insert_planrowintables={
                #     'profile_id': new_profile_id,
                #     'plan_id':7
                # }
                registration2_instance = models.Registration1.objects.create(**registration_data)

                horosocope_instance = models.Horoscope.objects.create(**insert_rowintables)
                family_instance = models.Familydetails.objects.create(**insert_rowintables)
                education_instance = models.Edudetails.objects.create(**insert_rowintables)
                Partner_instance = models.Partnerpref.objects.create(**insert_rowintables)
                # profile_planinstance=models.Profile_PlanFeatureLimit.objects.create(**insert_planrowintables)
                profile_suggestedinstance=models.ProfileSuggestedPref.objects.create(**insert_rowintables)
                profile_profilevisibility=models.ProfileVisibility.objects.create(**insert_rowintables)

                membership_fromdate = date.today()
                membership_todate = membership_fromdate + timedelta(days=365)
                
                plan_features = models.PlanFeatureLimit.objects.filter(plan_id=7)

                # profile_feature_objects = [
                #     models.Profile_PlanFeatureLimit(**{**model_to_dict(feature), 
                #                                        'profile_id': new_profile_id,'plan_id':7,'membership_fromdate':membership_fromdate,'membership_todate':membership_todate})
                #     for feature in plan_features
                # ] #by default basic plan

                # profile_feature_objects = [
                #     models.PlanFeatureLimit(
                #         **{k: v for k, v in model_to_dict(feature).items() if k != 'id'},  # Exclude 'id'
                #         profile_id=new_profile_id,
                #         plan_id=7,
                #         membership_fromdate=membership_fromdate,
                #         membership_todate=membership_todate
                #     )
                #     for feature in plan_features
                # ]
                
                # models.Profile_PlanFeatureLimit.objects.bulk_create(profile_feature_objects)

                # basic_reg = models.Basic_Registration.objects.get(ProfileId=profile_id)
                # basic_reg.status = 1  # Update status field as needed
                # basic_reg.save()

                plan_features = models.PlanFeatureLimit.objects.filter(plan_id=7)

                # print(plan_features)
                # print('exit1234')

                profile_feature_objects = [
                    models.Profile_PlanFeatureLimit(
                        **{k: v for k, v in model_to_dict(feature).items() if k != 'id'},  # Exclude 'id'
                        profile_id=new_profile_id,
                        # plan_id=7,
                        membership_fromdate=membership_fromdate,
                        membership_todate=membership_todate,
                        status=1
                    )
                    for feature in plan_features
                ]

                models.Profile_PlanFeatureLimit.objects.bulk_create(profile_feature_objects)

                basic_reg = models.Basic_Registration.objects.get(ProfileId=profile_id)
                basic_reg.status = 1  # Update status field as needed
                basic_reg.save()
            
                subject = "Welcome to Vysyamala!"
                context = {
                    'Profile_name': registration_data['Profile_name'],
                    'new_profile_id': new_profile_id,
                }

                html_content = render_to_string('user_api/authentication/welcome_email_template.html', context)



                
                recipient_list = [registration_data['EmailId']]

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

                    
                    
                    #if created:
                return JsonResponse({"Status": 1, "message": "Registration step 2 successful","profile_id":new_profile_id}, status=status.HTTP_201_CREATED)
                    # else:
                    #     return JsonResponse({"Status": 1, "message": "Registration step 2 updated successfully"}, status=status.HTTP_200_OK)
                
                # else:
                #     return JsonResponse(registration2_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            except models.Basic_Registration.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class Contact_registration(APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.ContactSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('ProfileId')
            try:
                registration = models.Registration1.objects.get(ProfileId=profile_id)
                serializer.update(registration, serializer.validated_data)
                return JsonResponse({"Status": 1, "message": "Contact details saved successful"}, status=status.HTTP_200_OK)
            except  models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_Profileholder(APIView):
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            profileholders = models.Profileholder.objects.filter(is_deleted=0)
            serializer =serializers.CustomProfileholderSerializer(profileholders, many=True)
            
            data_dict = {item['owner_id']: item for item in serializer.data}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profileholder.DoesNotExist:
            return JsonResponse({'error': 'Profileholder not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Marital_Status(APIView):

    def post(self, request, *args, **kwargs):
        try:

            # state = models.Profilestate.objects.get(id=state_id)

            MaritalStatus =  models.ProfileMaritalstatus.objects.filter(is_deleted=0).order_by('-MaritalStatus')
            serializer =serializers.CustomMaritalSerializer(MaritalStatus, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.ProfileMaritalstatus.DoesNotExist:
            return JsonResponse({'error': 'Marital status not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_Height(APIView):

    def post(self, request, *args, **kwargs):
        try:
            heights =  models.Profileheights.objects.filter(is_deleted=0)
            serializer =serializers.CustomHeightSerializer(heights, many=True)
            
            data_dict = {item['height_id']: item for item in serializer.data}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profileheights.DoesNotExist:
            return JsonResponse({'error': 'Profileheights not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Complexion(APIView):

    def post(self, request, *args, **kwargs):
        try:
            complexions =  models.Profilecomplexion.objects.filter(is_deleted=0)
            serializer =serializers.CustomComplexionSerializer(complexions, many=True)
            
            data_dict = {item['complexion_id']: item for item in serializer.data}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profilecomplexion.DoesNotExist:
            return JsonResponse({'error': 'ProfileComplexion not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_Country(APIView):

    def post(self, request, *args, **kwargs):
        try:
            countrries =  models.Profilecountry.objects.filter(is_active=1,is_deleted=0)
            serializer =serializers.CustomCountrySerializer(countrries, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            #print(data_dict)
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profilecountry.DoesNotExist:
            return JsonResponse({'error': 'Country lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Get_State(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        country_id = data.get('country_id')
        try:
            if not country_id:
                #raise serializers.ValidationError("State ID is required")
                return JsonResponse({'error': 'Country id is reuired'}, status=status.HTTP_404_NOT_FOUND)

            states =  models.Profilestate.objects.filter(is_active=1,country_id=country_id,is_deleted=0)
            serializer =serializers.CustomStateSerializer(states, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.Profilestate.DoesNotExist:
            return JsonResponse({'error': 'State lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_City(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        district_id = data.get('district_id')
        try:

            if not district_id:
                #raise serializers.ValidationError("State ID is required")
                return JsonResponse({'error': 'district_id is reuired'}, status=status.HTTP_404_NOT_FOUND)
            # state = models.Profilestate.objects.get(id=state_id)

            cities =  models.Profilecity.objects.filter(is_deleted=0,district_id=district_id)
            serializer =serializers.CustomCitySerializer(cities, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.Profilecity.DoesNotExist:
            return JsonResponse({'error': 'city lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_District(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        state_id = data.get('state_id')
        try:

            if not state_id:
                #raise serializers.ValidationError("State ID is required")
                return JsonResponse({'error': 'state_id is reuired'}, status=status.HTTP_404_NOT_FOUND)
            # state = models.Profilestate.objects.get(id=state_id)

            district =  models.Profiledistrict.objects.filter(is_deleted=0,state_id=state_id).order_by('name')
            serializer =serializers.CustomDistictSerializer(district, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.Profiledistrict.DoesNotExist:
            return JsonResponse({'error': 'District lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_DistrictPref(APIView):

    def post(self, request):
        try:
            # Fetch Districtpref records where is_deleted=0
            districts = models.Districtpref.objects.filter(is_deleted=0)
            # Serialize the results
            serializer = serializers.DistrictprefSerializer(districts, many=True)

            # Structure the response data with status and message
            response_data = {
                "status": "success",
                "message": "Masterdistrictpref fetched successfully",
                "data": serializer.data  # Use the serializer data directly
            }

            # Return custom response format
            return JsonResponse(response_data, status=status.HTTP_200_OK)
        except models.Districtpref.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "District preferences not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validate_required_fields(data, required_fields):
    """
    Validate that the required fields are present and not empty in the provided data.
    
    Args:
    data (dict): The dictionary to validate.
    required_fields (list): A list of required field names as strings.
    
    Returns:
    tuple: (is_valid, missing_fields)
        is_valid (bool): Whether all required fields are present and non-empty.
        missing_fields (list): A list of missing or empty fields.
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields

    #print('Username, password',username,password)




class Get_Parent_Occupation(APIView):

    def post(self, request, *args, **kwargs):
        try:
            parent_occupation =  models.Parentoccupation.objects.filter(is_deleted=0)
            serializer =serializers.CustomParentOccupSerializer(parent_occupation, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Parentoccupation.DoesNotExist:
            return JsonResponse({'error': 'Parent Occupation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# class ImageSetUpload(APIView):
#     def post(self, request, *args, **kwargs):
#         files = request.FILES.getlist('image_files')
#         profile_id = request.data.get('profile_id')
#         photo_protection = request.data.get('photo_protection')
#         quick_reg = request.data.get('quick_reg')
#         image_objects = []

#         if not profile_id:
#             return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if not files:
#             return JsonResponse({"error": "image_files is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if not photo_protection:
#             return JsonResponse({"error": "photo_protection is required"}, status=status.HTTP_400_BAD_REQUEST)

        
#         if not quick_reg:
#             quick_reg=0
        
        
#         for file in files:
#             # Open the image
#             img = PILImage.open(file)

#             # Resize the image
#             img = img.resize((201, 200))  # Example size, adjust as needed

#             # Add watermark
#             watermark_text = "Vysyamala app"
#             watermark_img = PILImage.new('RGBA', img.size, (255, 255, 255, 0))

#             draw = ImageDraw.Draw(watermark_img)

#             # font_path = "user_api/assets/PlaywriteAUVIC-VariableFont_wght.ttf"  # Update with your font path
#             font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'PlaywriteAUVIC-VariableFont_wght.ttf')

#             # print('font_path',font_path)

#             font_size = 36  # Adjust as needed

#             try:
#                 font = ImageFont.truetype(font_path, font_size)
#             except IOError:
#                 font = ImageFont.load_default()
            
#             textwidth, textheight = draw.textsize(watermark_text, font)

#             # Position the text at the bottom right
#             # x = img.width - textwidth - 10
#             # y = img.height - textheight - 10
#             # Calculate the position for the watermark to be centered
#             x = (img.width - textwidth) / 2
#             y = (img.height - textheight) / 2

#             draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
            
#             img = img.convert('RGBA')

#             # Combine original image with watermark
#             watermarked = PILImage.alpha_composite(img, watermark_img)

#             # Save to a BytesIO object
#             output = io.BytesIO()
#             watermarked = watermarked.convert("RGB")
#             watermarked.save(output, format='JPEG')
#             output.seek(0)

#             # Create a new Image instance and save
#             image_instance = models.Image_Upload(profile_id=profile_id)
#             image_instance.image.save(file.name,ContentFile(output.read()), save=True)
#             image_objects.append(image_instance)

#         serializer = serializers.ImageSerializer(image_objects, many=True)
        
#         photo_password = request.data.get('photo_password')
#         video_url = request.data.get('video_url')
#         photo_protection = int(request.data.get('photo_protection'))

#         models.Registration1.objects.filter(ProfileId=profile_id).update(Photo_password=photo_password,Video_url=video_url,Photo_protection=photo_protection,quick_registration=quick_reg)
#         #return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
#         return JsonResponse(serializer.data, safe=False)
    


# class ImageSetUpload(APIView):
#     def post(self, request, *args, **kwargs):
#         files = request.FILES.getlist('image_files')
#         profile_id = request.data.get('profile_id')
#         photo_protection = request.data.get('photo_protection')
#         quick_reg = request.data.get('quick_reg')
#         image_objects = []

#         if not profile_id:
#             return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if not files:
#             return JsonResponse({"error": "image_files is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if not photo_protection:
#             return JsonResponse({"error": "photo_protection is required"}, status=status.HTTP_400_BAD_REQUEST)

#         if not quick_reg:
#             quick_reg = 0
        
#         # Path to the watermark logo
#         logo_path = os.path.join('vysya_color_logo.png')

#         print('logo_path',logo_path)

#         for file in files:
#             # Open the image
#             img = PILImage.open(file)

#             # Resize the image
#             img = img.resize((201, 200))  # Example size, adjust as needed

#             # Add the logo watermark
#             try:
#                 with PILImage.open(logo_path) as logo:
#                     # Resize the logo
#                     logo_width, logo_height = 50, 50  # Adjust size as needed
#                     # Use ANTIALIAS instead of Resampling for older Pillow versions
#                     logo.thumbnail((logo_width, logo_height), PILImage.LANCZOS)

#                     # Ensure the logo has transparency
#                     logo = logo.convert("RGBA")

#                     # Position the logo at bottom-right corner
#                     img_width, img_height = img.size
#                     # position = (img_width - logo_width - 10, img_height - logo_height - 10)  # Offset 10px from edges
#                     position = (img_width - logo_width - 10, 10)  # Offset 10px from the top-right corner



#                     # Paste the logo onto the image
#                     img.paste(logo, position, logo)
#             except Exception as e:
#                 print(f"Error adding logo watermark: {e}")


#             # Save to a BytesIO object
#             output = io.BytesIO()
#             img = img.convert("RGB")
#             img.save(output, format='JPEG')
#             output.seek(0)

#             # Create a new Image instance and save
#             image_instance = models.Image_Upload(profile_id=profile_id)
#             image_instance.image.save(file.name, ContentFile(output.read()), save=True)
#             image_objects.append(image_instance)

#         serializer = serializers.ImageSerializer(image_objects, many=True)
        
#         # Update additional fields in Registration1 table
#         photo_password = request.data.get('photo_password')
#         video_url = request.data.get('video_url')
#         photo_protection = int(request.data.get('photo_protection'))

#         models.Registration1.objects.filter(ProfileId=profile_id).update(
#             Photo_password=photo_password,
#             Video_url=video_url,
#             Photo_protection=photo_protection,
#             quick_registration=quick_reg
#         )

#         return JsonResponse(serializer.data, safe=False)


class ImageSetUpload(APIView):
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('image_files')
        profile_id = request.data.get('profile_id')
        photo_protection = request.data.get('photo_protection')
        quick_reg = request.data.get('quick_reg')
        image_objects = []

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not files:
            return JsonResponse({"error": "image_files is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not photo_protection:
            return JsonResponse({"error": "photo_protection is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not quick_reg:
            quick_reg = 0
        
        # Path to the watermark logo
        logo_path = os.path.join('vysya_color_logo.png')

        #print('logo_path', logo_path)

        for file in files:
            # Open the image
            img = PILImage.open(file)

            # Define the target dimensions (desired size)
            target_width = 201
            target_height = 200

            # Check if resizing is necessary (only if the image is larger than target size)
            img_width, img_height = img.size
            if img_width > target_width or img_height > target_height:
                # Resize the image to fit within the target size, maintaining aspect ratio
                img.thumbnail((target_width, target_height), PILImage.LANCZOS)

            # Add the logo watermark
            try:
                with PILImage.open(logo_path) as logo:
                    # Resize the logo
                    logo_width, logo_height = 68, 18  # Adjust size as needed
                    logo.thumbnail((logo_width, logo_height), PILImage.LANCZOS)

                    # Ensure the logo has transparency
                    logo = logo.convert("RGBA")

                    img_width, img_height = img.size 
                    # Position the logo at the top-left corner
                    #position = (10, 10)  # Offset 10px from the top-left corner
                    position = (img_width - logo_width - 10, 10)
                    # Paste the logo onto the image
                    img.paste(logo, position, logo)
            except Exception as e:
                print(f"Error adding logo watermark: {e}")

            # Save to a BytesIO object
            output = io.BytesIO()
            img = img.convert("RGB")  # Ensure it's saved as RGB if it's RGBA
            img.save(output, format='JPEG', quality=90)  # Medium quality to reduce size
            output.seek(0)

            # Create a new Image instance and save
            image_instance = models.Image_Upload(profile_id=profile_id)
            image_instance.image.save(file.name, ContentFile(output.read()), save=True)
            image_objects.append(image_instance)

        serializer = serializers.ImageSerializer(image_objects, many=True)
        
        # Update additional fields in Registration1 table
        photo_password = request.data.get('photo_password')
        video_url = request.data.get('video_url')
        photo_protection = int(request.data.get('photo_protection'))

        models.Registration1.objects.filter(ProfileId=profile_id).update(
            Photo_password=photo_password,
            Video_url=video_url,
            Photo_protection=photo_protection,
            quick_registration=quick_reg
        )

        return JsonResponse(serializer.data, safe=False)






class Horoscope_upload(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('horoscope_file')
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file:
            return JsonResponse({"error": "horoscope_file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (e.g., less than 10MB)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({"error": "File size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        valid_extensions = ['doc','docx','pdf', 'png', 'jpeg', 'jpg']
        file_extension = os.path.splitext(file.name)[1][1:].lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"error": "Invalid file type. Accepted formats are: doc, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Horoscope instance and save the file
        try:

            # horoscope_instance = models.Horoscope(profile_id=profile_id)
            horoscope_instance,created = models.Horoscope.objects.get_or_create(profile_id=profile_id)
            horoscope_instance.horoscope_file.save(file.name, ContentFile(file.read()), save=True)
            horoscope_instance.horo_file_updated = timezone.now()
            horoscope_instance.save()

            serializer = serializers.HorosuploadSerializer(horoscope_instance)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
        
        except models.Horoscope.DoesNotExist:
            return JsonResponse({"error": "Profile with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
    

class Idproof_upload(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('idproof_file')
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file:
            return JsonResponse({"error": "idproof_file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (e.g., less than 10MB)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({"error": "File size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        valid_extensions = ['doc','docx', 'pdf', 'png', 'jpeg', 'jpg']
        file_extension = os.path.splitext(file.name)[1][1:].lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"error": "Invalid file type. Accepted formats are: doc, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Horoscope instance and save the file
        # idproof_instance = models.Registration1(ProfileId=profile_id)
        # idproof_instance.Profile_idproof.save(file.name, ContentFile(file.read()), save=True)
        # #horoscope_instance.horo_file_updated = timezone.now()
        # idproof_instance.save()

        # serializer = serializers.IdproofuploadSerializer(idproof_instance)
        # return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
        try:
            # Fetch the existing record for the given profile_id
            idproof_instance = models.Registration1.objects.get(ProfileId=profile_id)

            # Update the file for the existing record
            idproof_instance.Profile_idproof.save(file.name, ContentFile(file.read()), save=True)
            idproof_instance.save()

            serializer = serializers.IdproofuploadSerializer(idproof_instance)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"error": "Profile with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
    

class Divorceproof_upload(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('divorcepf_file')
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file:
            return JsonResponse({"error": "divorcepf_file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (e.g., less than 10MB)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({"error": "File size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        valid_extensions = ['doc','docx', 'pdf', 'png', 'jpeg', 'jpg']
        file_extension = os.path.splitext(file.name)[1][1:].lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"error": "Invalid file type. Accepted formats are: doc, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:        
            # Create a new Horoscope instance and save the file
            idproof_instance = models.Registration1.objects.get(ProfileId=profile_id)
            idproof_instance.Profile_divorceproof.save(file.name, ContentFile(file.read()), save=True)
            #horoscope_instance.horo_file_updated = timezone.now()
            idproof_instance.save()

            serializer = serializers.divorcecertiuploadSerializer(idproof_instance)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except models.Registration1.DoesNotExist:
            return JsonResponse({"error": "Profile with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

       
class Get_Property_Worth(APIView):

    def post(self, request, *args, **kwargs):
        try:
            property_worth =  models.Propertyworth.objects.all()
            serializer =serializers.CustomPropertyWorthSerializer(property_worth, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  

            return JsonResponse(data_dict, safe=False)
        except  models.Propertyworth.DoesNotExist:
            return JsonResponse({'error': 'Property Worth not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Due to not clarity i comented the previouse highest code and passed the education details in table data to the highest master that is used for the partner preferenses

class Get_Highest_Education(APIView):

    def post(self, request, *args, **kwargs):
        try:
            edupref =  models.Edupref.objects.filter(is_deleted=0)
            serializer =serializers.CustomHighestEduSerializer(edupref, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Edupref.DoesNotExist:
            return JsonResponse({'error': 'Highest Education not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_Degree_list(APIView):

    def post(self, request, *args, **kwargs):
        try:
            
            edu_level = request.data.get('edu_level')
            field_of_study = request.data.get('field_of_study')

            if not edu_level:
                return JsonResponse({'error': "'edu_level' is a required field."}, status=status.HTTP_400_BAD_REQUEST)
            if not field_of_study:
                return JsonResponse({'error': "'field_of_study' is a required field."}, status=status.HTTP_400_BAD_REQUEST)
                        
            #print('outside',field_of_study)
            #if edu_level == '2' or edu_level == '3':
            if edu_level == '1' or edu_level == '2':
                field_ofstudy = models.Profileedu_degree.objects.filter(
                    Q(is_deleted=0, fieldof_study=field_of_study) |
                    Q(is_deleted=0, id="86")  # Include "Others" option
                )
            else:
                field_ofstudy = models.Profileedu_degree.objects.filter(
                    Q(is_deleted=0, edu_level=edu_level, fieldof_study=field_of_study) |
                    Q(is_deleted=0, id="86")  # Include "Others" option
                )


            serializer =serializers.CustomField_degree(field_ofstudy, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profileedu_degree.DoesNotExist:
            return JsonResponse({'error': 'Field of study not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_Field_ofstudy(APIView):

    def post(self, request, *args, **kwargs):
        try:
            field_ofstudy =  models.Profilefieldstudy.objects.filter(is_deleted=0)
            serializer =serializers.CustomField_study(field_ofstudy, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profilefieldstudy.DoesNotExist:
            return JsonResponse({'error': 'Field of study not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


   
class Get_Ug_Degree(APIView):

    def post(self, request, *args, **kwargs):
        try:
            ug_degree =  models.Ugdegree.objects.filter(is_deleted=0)
            serializer =serializers.CustomUgDegreeSerializer(ug_degree, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
            return JsonResponse(data_dict, safe=False)
        except  models.Ugdegree.DoesNotExist:
            return JsonResponse({'error': 'UgDegree not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Get_Ug_Degree(APIView):

    def post(self, request, *args, **kwargs):
        try:
            ug_degree =  models.Ugdegree.objects.filter(is_deleted=0)
            serializer =serializers.CustomUgDegreeSerializer(ug_degree, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
            return JsonResponse(data_dict, safe=False)
        except  models.Ugdegree.DoesNotExist:
            return JsonResponse({'error': 'UgDegree not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class Get_Annual_Income(APIView):

    def post(self, request, *args, **kwargs):
        try:
            annual_income =  models.Annualincome.objects.filter(is_deleted=0)
            serializer =serializers.CustomAnnualIncSerializer(annual_income, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
            return JsonResponse(data_dict, safe=False)
        except  models.Annualincome.DoesNotExist:
            return JsonResponse({'error': 'AnnualIncome not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Place_Of_Birth(APIView):

    def post(self, request, *args, **kwargs):
        try:
            place_of_birth =  models.Placeofbirth.objects.filter(is_deleted=0)
            serializer =serializers.CustomPlaceOfBirSerializer(place_of_birth, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)} 

            return JsonResponse(data_dict, safe=False)
        except  models.Placeofbirth.DoesNotExist:
            return JsonResponse({'error': 'PlaceOfBirth not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Lagnam_Didi(APIView):

    def post(self, request, *args, **kwargs):
        try:
            lagnam_didi =  models.Lagnamdidi.objects.filter(is_deleted=0)
            serializer =serializers.CustomLagnamDidiSerializer(lagnam_didi, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)} 

            return JsonResponse(data_dict, safe=False)
        except  models.Lagnamdidi.DoesNotExist:
            return JsonResponse({'error': 'LagnamDidi not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Dasa_Name(APIView):

    def post(self, request, *args, **kwargs):
        try:
            dasa_name =  models.Dasaname.objects.filter(is_deleted=0)
            serializer =serializers.CustomDasaNameSerializer(dasa_name, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)} 

            return JsonResponse(data_dict, safe=False)
        except  models.Dasaname.DoesNotExist:
            return JsonResponse({'error': 'DasaName not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Get_Birth_Star(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        state_id = data.get('state_id')
        try:
            # birth_star =  models.Birthstar.objects.order_by('star')
            birth_star = models.Birthstar.objects.filter(is_deleted=0).order_by('star')
            serializer =serializers.CustomBirthStarSerializer(birth_star, many=True,  context={'state_id': state_id})
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            #print(data_dict)
            
            return JsonResponse(data_dict, safe=False)
        except  models.Birthstar.DoesNotExist:
            return JsonResponse({'error': 'BirthStar lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Rasi(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        birth_id = data.get('birth_id')
        state_id = data.get('state_id')
        try:
            if not birth_id:
                #raise serializers.ValidationError("State ID is required")
                return JsonResponse({'error': 'birth id is reuired'}, status=status.HTTP_404_NOT_FOUND)

            
            #rasi = models.Rasi.objects.filter(Q(star_id__contains=birth_id) | Q(star_id__contains=birth_id)).order_by('name')
            # rasi =  models.Rasi.objects.filter(star_id__contains=birth_id).order_by('name')
            #rasi = models.Rasi.objects.filter(star_id__contains=f',{birth_id},').order_by('name')
            rasi = models.Rasi.objects.filter(
            Q(star_id=birth_id) |              # Exact match '1'
            Q(star_id__startswith=birth_id+',') | # Starts with '1,'
            Q(star_id__endswith=','+birth_id) |   # Ends with ',1'
            Q(star_id__contains=','+birth_id+',')    # Contains ',1,'
         ).order_by('name')

            serializer =serializers.CustomRasiSerializer(rasi, many=True,  context={'state_id': state_id})
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.Rasi.DoesNotExist:
            return JsonResponse({'error': 'Rasi lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SendSMS:
    def __init__(self):
        self.url = 'http://pay4sms.in'
        self.token = '76111ad0d3c72d750e36ec22c6e5105d'
        self.credit = '2'
        self.sender = 'VYSYLA'
        # self.message_template = 'Dear Customer, {} is the OTP for Edit profile. Please enter it in the space provided in the Website. Thank you for using Vysyamala.com'
        self.message_template = 'Dear Customer,{} is the OTP for mobile verification. Please enter it in the space provided in the Website. Thank you for using Vysyamala.com'

    def send_sms(self, otp, numbers):
        message = self.message_template.format(otp)
        message = requests.utils.quote(message)
        sms_url = f"{self.url}/sendsms/?token={self.token}&credit={self.credit}&sender={self.sender}&number={numbers}&message={message}"
        response = requests.get(sms_url)
        return response.text

    def check_dlr(self, message_id):
        dlr_url = f"{self.url}/Dlrcheck/?token={self.token}&msgid={message_id}"
        response = requests.get(dlr_url)
        return response.text

    def available_credit(self):
        credit_url = f"{self.url}/Credit-Balance/?token={self.token}"
        response = requests.get(credit_url)
        return response.text
    
class Get_FamilyType(APIView):

    def post(self, request, *args, **kwargs):
        try:
            familytype =  models.Familytype.objects.filter(is_deleted=0)
            serializer =serializers.CustomFamilyTypeSerializer(familytype, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Familytype.DoesNotExist:
            return JsonResponse({'error': 'Familytype not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Get_FamilyStatus(APIView):

    def post(self, request, *args, **kwargs):
        try:
            familystat =  models.Familystatus.objects.filter(is_deleted=0)
            serializer =serializers.CustomFamilyStatSerializer(familystat, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Familystatus.DoesNotExist:
            return JsonResponse({'error': 'Familystatus not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Get_FamilyValue(APIView):

    def post(self, request, *args, **kwargs):
        try:
            familyvalue =  models.Familyvalue.objects.filter(is_deleted=0)
            serializer =serializers.CustomFamilyValSerializer(familyvalue, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Familyvalue.DoesNotExist:
            return JsonResponse({'error': 'Familystatus not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Get_Matchstr_Pref(APIView):

    def post(self, request):
        input_serializer = serializers.MatchingStarInputSerializer(data=request.data)
        if input_serializer.is_valid():
            birth_star_id = input_serializer.validated_data['birth_star_id']
            gender = input_serializer.validated_data['gender']
            birth_rasi_id = input_serializer.validated_data['birth_rasi_id']
            data = models.MatchingStarPartner.get_matching_stars(birth_rasi_id,birth_star_id,gender)
            output_serializer = serializers.MatchingStarSerializer(data, many=True)

            grouped_data = defaultdict(list)

            # for item in data:
            #     match_count = item['match_count']
            #     grouped_data[match_count].append(item)

            # # Construct the response structure with specific conditions for 15 and 0 counts
            # response = {}
            
            # for count, items in grouped_data.items():
            #     if count == 15:
            #         response["Yega poruthams"] = items
            #     elif count == 0:
            #         response["No poruthas"] = items
            #     else:
            #         response[f"{count} Poruthas"] = items

            for item in data:
                match_count = item['match_count']
                grouped_data[match_count].append(item)

            # Construct the response structure with specific conditions for 15 and 0 counts
            response = {}

            for count, items in grouped_data.items():
                if count == 15:
                    response["Yega poruthams"] = items
                elif count == 0:
                    response["No poruthas"] = items
                else:
                    response[f"{count} Poruthas"] = items

            return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


            # return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
        return JsonResponse(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        #     return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        
        # return JsonResponse(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_State_Pref(APIView):

    def post(self, request, *args, **kwargs):
        try:
            statepref =  models.Statepref.objects.filter(is_deleted=0)
            serializer =serializers.CustomStatePrefSerializer(statepref, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Statepref.DoesNotExist:
            return JsonResponse({'error': 'StatePref not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Get_Edu_Pref(APIView):

    def post(self, request, *args, **kwargs):
        try:
            edupref =  models.Edupref.objects.filter(is_deleted=0)
            serializer =serializers.CustomEduPrefSerializer(edupref, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Edupref.DoesNotExist:
            return JsonResponse({'error': 'EduPref not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Get_Profes_Pref(APIView):

    def post(self, request, *args, **kwargs):
        try:
            profespref =  models.Profespref.objects.filter(is_deleted=0)
            serializer =serializers.CustomProfesPrefSerializer(profespref, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Profespref.DoesNotExist:
            return JsonResponse({'error': 'ProfesPref not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Horoscope_registration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.HoroscopeSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            rasi_kattam = serializer.validated_data.get('rasi_kattam')
            mars_dosham=''
            rahu_kethu_dosham=''

            try:
                # Check if the profile_id exists in Registration1 table
                models.Registration1.objects.get(ProfileId=profile_id)

                # rasi_kattam = serializer.validated_data.get('rasi_kattam')


                if(rasi_kattam):
                    mars_dosham, rahu_kethu_dosham=GetMarsRahuKethuDoshamDetails(rasi_kattam)
                    


                # Check if horoscope details already exist for the profile_id
                try:
                    horoscope = models.Horoscope.objects.get(profile_id=profile_id)
                    # Update existing horoscope details
                    for key, value in serializer.validated_data.items():
                        setattr(horoscope, key, value)

                    horoscope.calc_chevvai_dhosham = mars_dosham
                    horoscope.calc_raguketu_dhosham = rahu_kethu_dosham

                    horoscope.save()
                    return JsonResponse({"Status": 1, "message": "Horoscope details updated successfully"}, status=status.HTTP_200_OK)
                
                except models.Horoscope.DoesNotExist:
                    # Create new horoscope details
                    serializer.save()
                    return JsonResponse({"Status": 1, "message": "Horoscope details saved successfully"}, status=status.HTTP_201_CREATED)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Invalid Profile_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse(serializer.errors, status=status.HTTP_200_OK)

class Family_registration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.FamilydetaiSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')

            try:
                # Check if the profile_id exists in Registration1 table
                models.Registration1.objects.get(ProfileId=profile_id)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Invalid Profile_id"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Update existing record if profile_id exists
                family_details = models.Familydetails.objects.get(profile_id=profile_id)
                for key, value in serializer.validated_data.items():
                    setattr(family_details, key, value)
                family_details.save()
                return JsonResponse({"Status": 1, "message": "Family details updated successfully"}, status=status.HTTP_200_OK)

            except models.Familydetails.DoesNotExist:
                # Create new record if profile_id does not exist
                serializer.save()
                return JsonResponse({"Status": 1, "message": "Family details saved successfully"}, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Education_registration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.EdudetailSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')

            try:
                # Check if the profile_id exists in Registration1 table
                check_data = models.Registration1.objects.get(ProfileId=profile_id)

                # Check if education details already exist for the profile_id
                try:
                    education_details = models.Edudetails.objects.get(profile_id=profile_id)
                    # Update existing education details
                    for key, value in serializer.validated_data.items():
                        setattr(education_details, key, value)
                    education_details.save()
                    return JsonResponse({"Status": 1, "message": "Education details updated successfully"}, status=status.HTTP_200_OK)
                
                except models.Edudetails.DoesNotExist:
                    # Create new education details
                    serializer.save()
                    return JsonResponse({"Status": 1, "message": "Education details saved successfully"}, status=status.HTTP_201_CREATED)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Invalid Profile_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Partner_pref_registration(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Make a mutable copy of the data
 
        # ===== Handle pref_porutham_star and generate pref_porutham_star_rasi =====
        pref_star_ids = data.get('pref_porutham_star')
        if pref_star_ids:
            try:
                id_list = [int(i.strip()) for i in pref_star_ids.split(',') if i.strip().isdigit()]
 
                matches = models.MatchingStarPartner.objects.filter(id__in=id_list)
 
                star_rasi_pairs = [
                    f"{m.dest_star_id}-{m.dest_rasi_id}" for m in matches
                ]
 
                data['pref_porutham_star_rasi'] = ",".join(star_rasi_pairs)
 
            except Exception as e:
                return JsonResponse({
                    "Status": 0,
                    "message": f"Invalid pref_porutham_star input. Error: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = serializers.PartnerprefSerializer(data=data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')

            try:
                # Check if the profile_id exists in Registration1 table
                models.Registration1.objects.get(ProfileId=profile_id)

                # Check if partner preferences already exist for the profile_id
                try:
                    partner_pref = models.Partnerpref.objects.get(profile_id=profile_id)
                    # Update existing partner preferences
                    for key, value in serializer.validated_data.items():
                        setattr(partner_pref, key, value)
                    partner_pref.save()
                    return JsonResponse({"Status": 1, "message": "Partner details updated successfully"}, status=status.HTTP_200_OK)
                
                except models.Partnerpref.DoesNotExist:
                    # Create new partner preferences
                    serializer.save()
                    return JsonResponse({"Status": 1, "message": "Partner details saved successfully"}, status=status.HTTP_201_CREATED)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Invalid Profile_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class Get_palns(APIView):
    def post(self, request, *args, **kwargs):
       profile_id = request.data.get('profile_id')

 
       if not profile_id:
            try:
                    data = models.PlanDetails.get_plan_details()
                    output_serializer = serializers.PlanSerializer(data, many=True)

                    grouped_data = defaultdict(list)
                    for item in data:
                            match_count = item['plan_name']
                            grouped_data[match_count].append(item)

                        # Construct the response structure
                    response = {f"{count}": items for count, items in grouped_data.items()}             
                        
                    return JsonResponse({"Status": 1, "message": "fetched data successfully","data":response},status=status.HTTP_201_CREATED)
                
            except Exception as e:

                return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
       else:
        # 📝 Your "else part" logic here
                # print('85412')
                registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
                plan_id = registration.Plan_id    
                
                # plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id).first()

                plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id__in=[1, 2, 3,14,15,17]).first()
                # print("plan",plan)
                # print("plan_id",plan_id)
                # current_date = now().date()
                current_time = timezone.now()
                current_date = current_time.date()

                # print(plan.membership_todate,'todate')
                # print(current_date,'current_date')
               
                if plan:
                    # print('123456789')
                    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date: #If plan is expired
                        # print('123456789')
                        try:
                                data = models.PlanDetails.get_plan_details_renewal()
                                output_serializer = serializers.PlanSerializer(data, many=True)

                                grouped_data = defaultdict(list)
                                for item in data:
                                        match_count = item['plan_name']
                                        grouped_data[match_count].append(item)

                                    # Construct the response structure
                                response = {f"{count}": items for count, items in grouped_data.items()}             
                                    
                                return JsonResponse({"Status": 1, "message": "fetched data successfully","data":response},status=status.HTTP_201_CREATED)
                            
                        except Exception as e:

                            return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
                        
                    else :  #if the plan still not expired
                            try:
                                data = models.PlanDetails.get_plan_details()
                                output_serializer = serializers.PlanSerializer(data, many=True)

                                grouped_data = defaultdict(list)
                                for item in data:
                                        match_count = item['plan_name']
                                        grouped_data[match_count].append(item)

                                    # Construct the response structure
                                response = {f"{count}": items for count, items in grouped_data.items()}             
                                    
                                return JsonResponse({"Status": 1, "message": "fetched data successfully","data":response},status=status.HTTP_201_CREATED)
                            
                            except Exception as e:

                                return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

                else :  #IF Plan Not exits in the table
                    
                    

                    try:
                        data = models.PlanDetails.get_plan_details()
                        output_serializer = serializers.PlanSerializer(data, many=True)

                        grouped_data = defaultdict(list)
                        for item in data:
                                match_count = item['plan_name']
                                grouped_data[match_count].append(item)

                            # Construct the response structure
                        response = {f"{count}": items for count, items in grouped_data.items()}             
                            
                        return JsonResponse({"Status": 1, "message": "fetched data successfully","data":response},status=status.HTTP_201_CREATED)
                    
                    except Exception as e:

                        return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        
class Get_save_details(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.SavedetailsSerializer(data=request.data)
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page_id = serializer.validated_data.get('page_id')

            fetch_data = None 
            serialized_data=None
            
            try:
                    if(page_id=='1'):
                    
                        fetch_data = models.Registration1.objects.get(ProfileId=profile_id)
                        serializer_class = serializers.ContactSerializer
                    
                    if(page_id=='2'):
                    
                        fetch_data = models.Registration1.objects.get(ProfileId=profile_id)
                        serializer_class = serializers.ProfileImagesSerializer

                    if(page_id=='3'):
                    
                    #  print('inside the cond')
                    
                        fetch_data = models.Familydetails.objects.get(profile_id=profile_id)
                        serializer_class = serializers.FamilydetaiSerializer
                    
                    if(page_id=='4'):
                    
                    #print('inside the cond')
                    
                        fetch_data = models.Edudetails.objects.get(profile_id=profile_id)
                        serializer_class = serializers.EdudetailSerializer

                    if(page_id=='5'):
                    
                    #print('inside the cond')
                    
                        fetch_data = models.Horoscope.objects.get(profile_id=profile_id)
                        serializer_class = serializers.HoroscopeSerializer
                    
                    if(page_id=='6'):
                    
                    #print('inside the cond')
                    
                        fetch_data = models.Partnerpref.objects.get(profile_id=profile_id)
                        serializer_class = serializers.PartnerprefSerializer

                    if fetch_data and serializer_class:
                        serialized_data = serializer_class(fetch_data).data
                    #print('inside the cond')
                    #fetched_serializers=serializers.FamilydetaiSerializer(fetch_data)

                    #print(serialized_data)     

                    # serializer.save()
                    if(serialized_data):
                        return JsonResponse({"Status": 1, "message": "fetched data successfully","data": serialized_data}, status=status.HTTP_201_CREATED)
                    else:
                        return JsonResponse({"Status": 0, "message": "No data"}, status=status.HTTP_201_CREATED)


            except models.Registration1.DoesNotExist:
                return JsonResponse(
                    {"error": "Profile not found in Registration1"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except models.Familydetails.DoesNotExist:
                return JsonResponse(
                    {"error": "Profile not found in Familydetails"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except models.Edudetails.DoesNotExist:
                return JsonResponse(
                    {"error": "Profile not found in Edudetails"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except models.Horoscope.DoesNotExist:
                return JsonResponse(
                    {"error": "Profile not found in Horoscope"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except models.Partnerpref.DoesNotExist:
                return JsonResponse(
                    {"error": "Profile not found in Partnerpref"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 



class Login_with_mobileno(APIView):
    def generate_otp(self):
        # Implement your OTP generation logic here
        import random
        return str(random.randint(100000, 999999))

    def post(self, request, *args, **kwargs):
        # print(request.data)  # Debugging statement to print incoming data
        serializer = serializers.LoginWithMobileSerializer(data=request.data)

        if serializer.is_valid():
            mobile_number = serializer.validated_data.get('Mobile_no')
            # print("Validated mobile number:", mobile_number)  # Debugging statement
            
            

            print('mobile_number',mobile_number)
            # Check if the mobile number exists in Registration table
            normalized_input = mobile_number.strip()
            if len(normalized_input) == 10:
                normalized_input_with_prefix = '91' + normalized_input
            elif len(normalized_input) == 12 and normalized_input.startswith('91'):
                normalized_input_with_prefix = normalized_input
                normalized_input = normalized_input[2:]  # Strip '91' for 10-digit version
            else:
                return JsonResponse({"status": 0, "message": "Invalid mobile number format."}, status=status.HTTP_200_OK)

            # Try matching either format
            try:
                profile = (
                    models.Registration1.objects
                    .filter(
                        Q(Mobile_no=normalized_input) | Q(Mobile_no=normalized_input_with_prefix),
                        Status__in=[0, 1, 2, 3],
                    )
                    .order_by('DateOfJoin')  # or 'created_at' if you have it
                    .first()
                )

            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": 0, "message": "Invalid Number"}, status=status.HTTP_200_OK)
            # Generate OTP
            otp = self.generate_otp()

            # Send OTP via SMS (implement SendSMS() appropriately)
            
            #Below code commented on 30th jully 2024 harcode value set as 1234

            sms_sender = SendSMS()  # Ensure SendSMS class is implemented and imported correctly
            message_id = sms_sender.send_sms(otp, mobile_number)
            dlr_status = sms_sender.check_dlr(message_id)
            available_credit = sms_sender.available_credit()

            # Save OTP to UserProfile
            profile.Otp = otp
            #profile.Otp = 123456 #otp
            profile.save()

            # Prepare response data
            response_data = {
                "message": "OTP sent successfully.",
                "Send Message Response": message_id,
                "Delivery Report Status": dlr_status,
                "Available Credit": available_credit
            }

            return JsonResponse({"status": 1, "response_data": response_data, "message": "OTP sent successfully."}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_200_OK)
        
class Login_verifyotp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.VerifyOtpSerializer(data=request.data)
        
        if serializer.is_valid():
            mobile_number = serializer.validated_data.get('Mobile_no')
            otp = serializer.validated_data.get('Otp')
            normalized_input = mobile_number.strip()
            if len(normalized_input) == 10:
                normalized_input_with_prefix = '91' + normalized_input
            elif len(normalized_input) == 12 and normalized_input.startswith('91'):
                normalized_input_with_prefix = normalized_input
                normalized_input = normalized_input[2:]  # Strip '91' for 10-digit version
            else:
                return JsonResponse({"status": 0, "message": "Invalid mobile number format."}, status=status.HTTP_200_OK)

            # Try matching either format
            try:
                profile = (
                    models.Registration1.objects
                    .filter(
                        Q(Mobile_no=normalized_input) | Q(Mobile_no=normalized_input_with_prefix),Otp=otp,
                        Status__in=[0, 1, 2, 3],
                    )
                    .order_by('DateOfJoin')  # or 'created_at' if you have it
                    .first()
                )
                print('profile',profile.ProfileId)

                # Get or create user safely without unpacking error
                try:
                    user, created = User.objects.get_or_create(username=profile.ProfileId)
                except User.MultipleObjectsReturned:
                    # Filter and get a consistent user if duplicates exist
                    user = User.objects.filter(username=profile.ProfileId).order_by('id').first()
                    created = False

                # Print if needed
                print("User:", user, "Created:", created)

                # Get or create auth token, same pattern
                try:
                    token, _ = Token.objects.get_or_create(user=user)
                except Token.MultipleObjectsReturned:
                    token = Token.objects.filter(user=user).order_by('created').first()
                
                profile_id=profile.ProfileId



                notify_count=models.Profile_notification.objects.filter(profile_id=profile_id, is_read=0).count()

                logindetails=models.Registration1.objects.filter(ProfileId=profile_id).first()
                profile_for = logindetails.Profile_for
                try:
                        Profile_owner = models.Profileholder.objects.get(Mode=profile_for).ModeName
                except models.Profileholder.DoesNotExist:
                        Profile_owner = None

                quick_reg=logindetails.quick_registration
                
                if not quick_reg:
                    quick_reg=0

                logindetails.Last_login_date=timezone.now()
                logindetails.save()



                horodetails=models.Horoscope.objects.filter(profile_id=profile_id).first()
                
                #get first image for the profile icon
                profile_images=models.Image_Upload.objects.filter(profile_id=profile_id).first()          
                plan_id = logindetails.Plan_id
                plan_limits_json=''
                if plan_id:
                    plan_limits=models.PlanFeatureLimit.objects.filter(plan_id=plan_id)
                
                    serializer = serializers.PlanFeatureLimitSerializer(plan_limits, many=True)
                    plan_limits_json = serializer.data


                gender = logindetails.Gender
                height = logindetails.Profile_height
                marital_status=logindetails.Profile_marital_status


                profile_planfeature = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id, status=1).first()
                valid_till = profile_planfeature.membership_todate if profile_planfeature else None

                profile_icon=''
                profile_completion=0
                birth_star_id=''
                birth_rasi_id=''
                if horodetails:
                    birth_star_id=horodetails.birthstar_name
                    birth_rasi_id=horodetails.birth_rasi_name
                
                profile_image=''

                if profile_images:
                    profile_icon=profile_images.image.url
                    profile_image =profile_icon
                #default image icon
                else:
                    
                    profile_icon = 'men.jpg' if gender == 'male' else 'women.jpg'
                    profile_image = settings.MEDIA_URL+profile_icon
                    


                logindetails_exists = models.Registration1.objects.filter(ProfileId=profile_id).filter(Profile_address__isnull=False).exclude(Profile_address__exact='').first()

                family_details_exists=models.Familydetails.objects.filter(profile_id=profile_id).first()
                horo_details_exists=models.Horoscope.objects.filter(profile_id=profile_id).first()
                education_details_exists=models.Edudetails.objects.filter(profile_id=profile_id).first()
                partner_details_exists=models.Partnerpref.objects.filter(profile_id=profile_id).first()

                #check the address is exists for the contact s page contact us details stored in the logindetails page only
                if not logindetails_exists:
                    
                    profile_completion=1     #contact details not exists   

                elif not family_details_exists:
                    
                    profile_completion=2    #Family details not exists   

                elif not horo_details_exists:
                    profile_completion=3    #Horo details not exists   

                elif not education_details_exists:
                    profile_completion=4        #Edu details not exists   

                elif not partner_details_exists:
                    profile_completion=5       
                
                
                
                # return JsonResponse({'status': 1, 'token': token.key, 'message': 'Login Successful'}, status=status.HTTP_200_OK)
                return JsonResponse({'status': 1,'token':token.key ,'profile_id':profile_id ,'message': 'Login Successful',"notification_count":notify_count,"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,"gender":gender,"height":height,"marital_status":marital_status,"custom_message":1,"birth_star_id":birth_star_id,"birth_rasi_id":birth_rasi_id,"profile_owner":Profile_owner,"quick_reg":quick_reg,"plan_limits":plan_limits_json,"valid_till":valid_till}, status=200)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": 0, "message": "Invalid OTP or mobile number."}, status=status.HTTP_200_OK)
        
        return JsonResponse({'status': 0, 'message': 'Invalid credentials'}, status=status.HTTP_200_OK)


class Send_profile_intrests(APIView):
    def post(self, request):
        serializer = serializers.ExpressintrSerializer(data=request.data)

        # print('serializer',serializer)

        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')
            to_express_message = serializer.validated_data.get('to_express_message')

                # print('profile_from',profile_from)
                # print('profile_to',profile_to)
            
            # print('int_status',int_status)

            get_limits=can_send_express_interest(profile_from)
            # print(get_limits)

            if get_limits is True or int(int_status) == 0:  #status 0 is revoke the sending express interests so it doesn't express have to check condition with the limits
                # print('get_limits',get_limits)

                # print('statussuccess')

                # Check if an entry with the same profile_from and profile_to already exists
                existing_entry = models.Express_interests.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
                
                if existing_entry:
                    # Update the status to 0 if the entry already exists
                    #existing_entry.status = 0
                    existing_entry.status = int_status
                    existing_entry.express_message = to_express_message
                    existing_entry.req_datetime = timezone.now()
                    existing_entry.save()

                    # models.Profile_notification.objects.create(
                    #     profile_id=profile_to,
                    #     from_profile_id=profile_from,
                    #     notification_type='express_interests',
                    #     message='You received a express interests update from profile ID '+profile_from,
                    #     is_read=0,
                    #     created_at=timezone.now()
                    # )



                    return JsonResponse({"Status": 0, "message": "Express interests updated"}, status=status.HTTP_200_OK)
                else:
                    # Create a new entry with status 1
                    serializer.save(status=1)
                    to_message = to_express_message or f'You received an interest from profile ID {profile_from}'

                    message_title="Received Interests from the profile "+profile_from

                    models.Profile_notification.objects.create(
                        profile_id=profile_to,
                        from_profile_id=profile_from,
                        notification_type='express_interests',
                        message_titile=message_title,
                        #to_message='You received a express interests from profile ID '+profile_from,
                        to_message = to_message,
                        is_read=0,
                        created_at=timezone.now()
                    )

                    from_profile=models.Registration1.objects.get(ProfileId=profile_from)
                    from_profile_name=from_profile.Profile_name
                    
                    to_profile=models.Registration1.objects.get(ProfileId=profile_to)
                    to_profile_name=to_profile.Profile_name
                    
                    choosen_medium=to_profile.Notifcation_enabled
                                
                                
                    if(choosen_medium):
                                                            
                        chosen_alert_types = [int(alert_type) for alert_type in choosen_medium.split(',')]
                                        
                        # Fetch alert settings based on chosen_alert_types
                        alert_settings = models.ProfileAlertSettings.objects.filter(id__in=chosen_alert_types,notification_type='express_interests' , status=1)
                        
                        # print(alert_settings)
                        
                        send_email = False
                        send_sms = False
                        notification_type='express_interests'

                        for alert_setting in alert_settings:
                            if alert_setting.alert_type == 1:  # Assuming '1' is for email
                                send_email = True
                            # elif alert_setting.alert_type == 2:  # Assuming '2' is for SMS
                            #     send_sms = True

                        # print('send_email',send_email)
                        # print('send_sms',send_sms)

                        if send_email:
                            send_email_notification(profile_from,from_profile_name,to_profile_name,to_profile.EmailId, message_title, to_message,notification_type)

                return JsonResponse({"Status": 1, "message": "Express interests sent successfully"}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"Status":0, "message": "Today Limit Reached , Get full access - upgrade your package today!"}, status=status.HTTP_200_OK)
            
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_expresint_status(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        
        
        profile_id = request.data.get('profile_id')
        profile_to = request.data.get('profile_to')

        if not profile_id:
            return JsonResponse({"Status": 0, "message": "profile_id is required"}, status=status.HTTP_200_OK)
        
        if not profile_to:
            return JsonResponse({"Status": 0, "message": "profile_to is required"}, status=status.HTTP_200_OK)
        
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            profile_to = request.data.get('profile_to')
        try:
            # Check if your profile sent the interest

            print('profile_id',profile_id)
            print('profile_to',profile_to)
            my_interests = models.Express_interests.objects.filter(profile_from=profile_id, profile_to=profile_to).first()
            
            if my_interests:
                # If your profile sent the interest, get the status
                print('12345')
                interest_status = my_interests.status
                sent_by_me = True
            else:
                # If no interest was found from your profile, check if they sent the interest
                their_interests = models.Express_interests.objects.filter(profile_from=profile_to, profile_to=profile_id).first()
                print('123456789')
                if their_interests:
                    # If they sent the interest, get the status
                    interest_status = their_interests.status
                    sent_by_me = False
                else:
                    print('123489')
                    # If no interests were found at all
                    interest_status = None
                    sent_by_me = None

            combined_data = {
                        "status":1,
                        "interest_status":interest_status,
                        "sent_by_me":sent_by_me
                    }

            return JsonResponse({"Status": 1, "message": "Fetched express sucessfully", "data": combined_data }, status=status.HTTP_200_OK)
        except models.Express_interests.DoesNotExist:
                # Handle any other potential exceptions
                interest_status = None
                sent_by_me = None
                return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)

# Use interest_status and sent_by_me as needed



def get_profile_details(profile_ids):
    #profiles = models.Get_profiledata.get_profile_details.objects.filter(ProfileId__in=profile_ids)
    profiles = models.Get_profiledata.get_profile_details(profile_ids)
    
    
    
    return profiles


class Get_profile_intrests_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            try:
                fetch_data = models.Express_interests.objects.filter(profile_to=profile_id,status=1)
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_from', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    myprofile_det=models.Registration1.objects.filter(ProfileId=profile_id).first()
                    my_gender=myprofile_det.Gender

                    received_intrests_count = {'status': 1,'profile_to':profile_id}
                    received_int_count = count_records(models.Express_interests, received_intrests_count)
                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    restricted_profile_details = [
                        {
                            "int_profileid": detail.get("ProfileId"),
                            "int_profile_name": detail.get("Profile_name"),
                            #"int_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            # "int_Profile_img":Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "int_Profile_img": image_function(detail),
                            "int_profile_age": calculate_age(detail.get("Profile_dob")),
                            "int_profile_notes": 'Iam intrested in your profile if you are intrested in my profile , please contact me',
                            "int_status":1,
                            "int_verified":detail.get('Profile_verified'),
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched interests and profile details successfully", "data": combined_data,"int_count":received_int_count}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class Get_dashboard_details(APIView):
    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')

            gender = serializer.validated_data.get('gender')

            user = models.Registration1.objects.get(ProfileId=profile_id)
            gender= user.Gender.lower()

            #mutual_condition = {'status': 2,'profile_from':profile_id,'profile_to':profile_id}
            # matching_profile_counts = Q(status=2) & (Q(profile_from=profile_id) | Q(profile_to=profile_id))

            profile_details = models.Get_profiledata.get_profile_match_count(profile_id)
            
            default_img=''


            my_oposit_gender=''
            if gender.lower()=='male':
                
                default_img='default_bride.png'
                my_oposit_gender='female'


            if gender.lower()=='female':
                
                default_img='default_groom.png'
                my_oposit_gender='male'
                                


            #print('profile_details',profile_details)

            #if profile_details.status_code != 200 or profile_details is None:
            #if getattr(profile_details, 'status_code', None) != 200 or profile_details is None:
            # if profile_details is None:
            #     matching_profile_count = 0
            #     profile_ids=[]
            # else:
            #     matching_profile_count = len(profile_details)
            #     profile_ids = [profile['ProfileId'] for profile in profile_details]

            if profile_details and isinstance(profile_details, list):
                matching_profile_count = len(profile_details)
                try:
                    profile_ids = [profile['ProfileId'] for profile in profile_details]
                except (TypeError, KeyError):
                    profile_ids = []
            else:
                matching_profile_count = 0
                profile_ids = []

               
                #print('profile_ids',profile_ids)


            def get_filtered_images(profile_ids):
               # base_url = "http://103.214.132.20:8000/media/"
                base_url =settings.MEDIA_URL
                # Return empty list if no profile_ids provided
                if not profile_ids:
                     return [
                        {"1": f"{base_url}{default_img}"},
                        {"2": f"{base_url}{default_img}"},
                        {"3": f"{base_url}{default_img}"},
                        {"4": f"{base_url}{default_img}"},
                        {"5": f"{base_url}{default_img}"}
                    ]

                # Create placeholders for each profile_id
                placeholders = ', '.join(['%s'] * len(profile_ids))

                # Define the SQL query to fetch images
                sql_query = f"""
                SELECT id, profile_id, image
                FROM profile_images
                WHERE profile_id IN (
                    SELECT ProfileId
                    FROM logindetails
                    WHERE Photo_protection != 1
                    AND ProfileId IN ({placeholders})
                )
                ORDER BY RAND()
                LIMIT 5;
                """

                # Execute the query
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, profile_ids)
                    images = cursor.fetchall()


                if not images:
                    default_images = [
                        {"1": f"{base_url}{default_img}"},
                        {"2": f"{base_url}{default_img}"},
                        {"3": f"{base_url}{default_img}"},
                        {"4": f"{base_url}{default_img}"},
                        {"5": f"{base_url}{default_img}"}
                    ]
                    image_data = [
                        {
                            str(index + 1): url
                        }
                        for index, url in enumerate(default_images)
                    ]




                # # Convert the fetched data to a list of lists
                # image_data = [
                #     [f"{base_url}{image[2]}"]  # Only three columns are selected: id, profile_id, image
                #     for image in images
                # ]

                # return image_data
            
                else:

                        image_data = [
                            {
                                str(index + 1): f"{base_url}{image[2]}"  # Append base URL to image path
                            }
                            for index, image in enumerate(images)
                        ]
                        
                        return image_data
            

            filtered_image_paths = get_filtered_images(profile_ids)

            # Usage
            # profile_ids = ['VY240001', 'VY240002', 'VY240003', 'VY240004', 'VY240005', 'VY240006', 'VY240007', 'VY240008', 'VY240009']
            
            #mutual_condition = {'status': 2,'profile_from':profile_id,'profile_to':profile_id}
            mutual_condition = Q(status=2) & (Q(profile_from=profile_id) | Q(profile_to=profile_id))
            personal_notes_condition={'status': 1,'profile_id':profile_id}
            wishlist_condition = {'status': 1,'profile_from':profile_id}
            received_intrests_count = {'status': 1,'profile_to':profile_id}
            sent_intrest_count = {'status': 1,'profile_from':profile_id}
            viewed_profile_count = {'status': 1,'profile_id':profile_id}
            my_vistor_count = {'status': 1,'viewed_profile':profile_id}
            photo_int_count = {'status': 1,'profile_to':profile_id}
            gallery_count = matching_gallery(profile_id)

            # print('gallery_count',gallery_count)

            # gallery_count = {'status': 1}
            # gallery_count = {'status': 1}
            
            
            # Call the dashbiard counts through one function
            mutual_int_count = count_records_forQ(models.Express_interests, mutual_condition)
            personal_notes_count = count_records(models.Profile_personal_notes, personal_notes_condition)
            wishlist_count = count_records(models.Profile_wishlists, wishlist_condition)
            received_int_count = count_records(models.Express_interests, received_intrests_count)
            sent_int_count = count_records(models.Express_interests, sent_intrest_count)
            myvisitor_count = count_records(models.Profile_visitors, my_vistor_count)
            viewed_profile_count = count_records(models.Profile_visitors, viewed_profile_count)

            photo_int_count = count_records(models.Photo_request, photo_int_count)
            #gallery_count = count_records(models.Express_interests, filter_condition)
            
            profile_ids = [profile_id]
            profile_details = get_profile_details(profile_ids)

            #print('Profile_id',profile_details[0]['ProfileId'])
            plan_id = profile_details[0].get('plan_id', None)  # Safely get plan_id

            if plan_id in (6, 7, 8, 9):
                plan_name='Free'
            
            elif plan_id:
                try:
                    plan_name = models.PlanDetails.objects.get(id=plan_id).plan_name
                except models.PlanDetails.DoesNotExist:
                    plan_name = ''  # Return empty value if plan not found
            else:
                plan_name = ''  # Return empty value if plan_id is empty

            
            result_percen=calculate_points_and_get_empty_fields(profile_id)

            # print("Total Points:", result_percen['total_points'])
            # print("Completed Points:", result_percen['completed_points'])
            # print("Completion Percentage:", result_percen['completion_percentage'])
            # print("Empty Fields:", result_percen['empty_fields'])

            profile_planfeature = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,status=1).first()

            prof_details= {
                            "profile_id": profile_details[0]['ProfileId'],
                            "profile_name": profile_details[0]['Profile_name'],
                            # "package_name": profile_details[0]['Package_name'] if profile_details[0]['Package_name'] else "No package",
                            "package_name":plan_name,
                            # "package_validity":profile_details[0]['PaymentExpire'] if profile_details[0]['PaymentExpire'] else " ",
                            "package_validity":profile_planfeature.membership_todate.date() if profile_planfeature.membership_todate else " ",
                            #"completion_per":result_percen['completion_percentage'],
                            "completion_per":int(result_percen['completion_percentage']),
                            "empty_fields":result_percen['empty_fields'],
                            #"profile_image":"http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png"
                            "profile_image": Get_profile_image(profile_details[0]['ProfileId'],my_oposit_gender,1,0)
                           
                        }

            combined_data={
                    "matching_profile_count":matching_profile_count,
                    "mutual_int_count":mutual_int_count,
                    "wishlist_count":wishlist_count,
                    "personal_notes_count":personal_notes_count,
                    "received_int_count":received_int_count,
                    "sent_int_count":sent_int_count,
                    "myvisitor_count":myvisitor_count,
                    "viewed_profile_count":viewed_profile_count,
                    "profile_details":prof_details,
                    "profile_verified":profile_details[0]['Profile_verified'],
                    "gallery_count":gallery_count,
                    "photo_int_count":photo_int_count,
                    "image_data":filtered_image_paths
            }


            return JsonResponse({"Status": 1, "message": "Fetched Dashboard details successfully", "data": combined_data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def matching_gallery(profile_id):
    try:
        user = models.Registration1.objects.get(ProfileId=profile_id)
        gender = user.Gender.lower()

        profile_details = models.Get_profiledata.get_profile_match_count(profile_id)

        # Check that profile_details is a non-empty list
        if isinstance(profile_details, list) and profile_details:
            profile_ids = [profile['ProfileId'] for profile in profile_details]
            placeholders = ', '.join(['%s'] * len(profile_ids))

            base_url = settings.MEDIA_URL  # not used here, just retained from your code

            # SQL query to count distinct profile IDs from images
            sql_query_count = f"""
                SELECT COUNT(DISTINCT pi.profile_id)
                FROM profile_images pi
                JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                WHERE ld.Photo_protection != 1
                AND ld.ProfileId IN ({placeholders})
            """

            with connection.cursor() as cursor:
                cursor.execute(sql_query_count, profile_ids)
                total_records = cursor.fetchone()[0]  # Get total count

            return total_records
        else:
            return 0

    except models.Registration1.DoesNotExist:
        return 0

    except Exception as e:
        print(f"Error in matching_gallery: {e}")
        return 0





#commented by vinoth for getting matching galler error for no record on 05-0625

# def matching_gallery(profile_id):
    

#         user = models.Registration1.objects.get(ProfileId=profile_id)
#         gender = user.Gender.lower()

#         profile_details = models.Get_profiledata.get_profile_match_count(profile_id)
            
#         if profile_details is not None and getattr(profile_details, 'status_code', None) != 400:
#         #if profile_details is not None and profile_details.status_code != 400 :
#         #  if profile_details.status_code != 200 or profile_details is None:
#                 profile_ids = [profile['ProfileId'] for profile in profile_details]
#                 placeholders = ', '.join(['%s'] * len(profile_ids))

#                 # base_url = 'http://103.214.132.20:8000/'
#                 base_url = settings.MEDIA_URL

#                                 # Define the SQL query to fetch total images count
#                 sql_query_count = f"""SELECT COUNT(DISTINCT pi.profile_id)
#                                 FROM profile_images pi
#                                 JOIN logindetails ld ON pi.profile_id = ld.ProfileId
#                                 WHERE ld.Photo_protection != 1
#                                 AND ld.ProfileId IN ({placeholders})"""
                
#                 with connection.cursor() as cursor:
#                             cursor.execute(sql_query_count, profile_ids)
#                             total_records = cursor.fetchone()[0]  # Get total count

#                             # print('total_records',total_records)

#                 return total_records
#         else :
#                 return 0



# class Get_Gallery_lists(APIView):    
#     def post(self, request):

#         profile_id = request.data.get('profile_id')

#         # print(settings.IMAGE_BASEURL) 

#         if not profile_id:
#             return JsonResponse({"Status": 0, "message": "Profile_id is required"}, status=status.HTTP_200_OK)
                
#         serializer = serializers.Profile_idValidationSerializer(data=request.data)

#         if serializer.is_valid():
#             profile_id = serializer.validated_data.get('profile_id')

#             page = int(request.data.get('page_number', 1))
#             per_page = int(request.data.get('per_page', 10))  

#             user = models.Registration1.objects.get(ProfileId=profile_id)
#             gender = user.Gender

#             profile_details = models.Get_profiledata.get_profile_match_count(profile_id)

#             if profile_details is None:
#                 return JsonResponse({"Status": 0, "message": "No matching Records for the profiles"}, status=status.HTTP_200_OK)
#             else:
#                 profile_ids = [profile['ProfileId'] for profile in profile_details]
#                 placeholders = ', '.join(['%s'] * len(profile_ids))

#                 # base_url = 'http://103.214.132.20:8000/media/'
#                 base_url = settings.MEDIA_URL

#                 # Define the SQL query to fetch total images count
#                 sql_query_count = f"""
#                 SELECT COUNT(DISTINCT pi.profile_id)
#                 FROM profile_images pi
#                 JOIN logindetails ld ON pi.profile_id = ld.ProfileId
#                 WHERE ld.Photo_protection != 1
#                 AND ld.ProfileId IN ({placeholders})
#                 """

#                 # Execute the count query
#                 with connection.cursor() as cursor:
#                     cursor.execute(sql_query_count, profile_ids)
#                     total_records = cursor.fetchone()[0]  # Get total count

#                 # Now define the SQL query to fetch paginated images
#                 sql_query_paginated = f"""
#                 SELECT pi.id, pi.profile_id, pi.image
#                 FROM profile_images pi
#                 JOIN logindetails ld ON pi.profile_id = ld.ProfileId
#                 WHERE ld.Photo_protection != 1
#                 AND ld.ProfileId IN ({placeholders})
#                 GROUP BY pi.profile_id
#                 LIMIT {per_page} OFFSET {(page - 1) * per_page};
#                 """

#                 # Execute the paginated query
#                 with connection.cursor() as cursor:
#                     cursor.execute(sql_query_paginated, profile_ids)
#                     paginated_images = cursor.fetchall()

#                 if not paginated_images:
#                     return JsonResponse({"Status": 0, "message": "No matching image Fetched"}, status=status.HTTP_200_OK)
#                 else:
#                     image_data = [
#                         {
#                             "profile_id": image[1],  # Assuming image[1] contains the profile ID
#                             "img_url": f"{base_url}{image[2]}"  # Append base URL to image path
#                         }
#                         for image in paginated_images
#                     ]

#                     # Create dictionary for all profile IDs
#                     all_profile_ids = {str(index + 1): image[1] for index, image in enumerate(paginated_images)}

#                     combined_data = {
#                         "image_data": image_data,
#                         "page": page,
#                         "per_page": per_page,
#                         "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
#                         "total_records": total_records,
#                         "all_profile_ids": all_profile_ids
#                     }

#                     return JsonResponse({"Status": 1, "message": "Image Fetched successfully", "data": combined_data}, status=status.HTTP_200_OK)

class Get_Gallery_lists(APIView):    
    def post(self, request):
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"Status": 0, "message": "Profile_id is required"}, status=status.HTTP_200_OK)

        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  

            # Get gender
            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)
                gender = user.Gender
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Profile not found"}, status=status.HTTP_200_OK)

            # Get matching profile details
            profile_details = models.Get_profiledata.get_profile_match_count(profile_id)
            if not profile_details:
                return JsonResponse({"Status": 0, "message": "No matching records for the profiles"}, status=status.HTTP_200_OK)

            profile_ids = [profile['ProfileId'] for profile in profile_details]
            if not profile_ids:
                return JsonResponse({"Status": 0, "message": "No profiles found"}, status=status.HTTP_200_OK)

            placeholders = ', '.join(['%s'] * len(profile_ids))
            base_url = settings.MEDIA_URL

            # Optimized Query to Get Total Records & Paginated Images
            sql_query = f"""
            WITH RankedImages AS (
                SELECT pi.id, pi.profile_id, pi.image,
                       ROW_NUMBER() OVER (PARTITION BY pi.profile_id ORDER BY pi.id ASC) AS rn
                FROM profile_images pi
                JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                WHERE ld.Photo_protection != 1
                AND ld.ProfileId IN ({placeholders})
                ORDER BY ld.DateOfJoin DESC
            )
            SELECT id, profile_id, image
            FROM RankedImages
            WHERE rn = 1
            LIMIT {per_page} OFFSET {(page - 1) * per_page};
            """

            total_records_query = f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT pi.profile_id
                FROM profile_images pi
                JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                WHERE ld.Photo_protection != 1
                AND ld.ProfileId IN ({placeholders})
            ) AS subquery;
            """

            with connection.cursor() as cursor:
                # Fetch total count
                cursor.execute(total_records_query, profile_ids)
                total_records = cursor.fetchone()[0]

                # Fetch paginated images
                cursor.execute(sql_query, profile_ids)
                paginated_images = cursor.fetchall()

            if not paginated_images:
                return JsonResponse({"Status": 0, "message": "No matching image fetched"}, status=status.HTTP_200_OK)

            photo_viewing=get_permission_limits(profile_id,'photo_viewing')
            if(photo_viewing==1):
                image_data = [
                    {
                        "profile_id": image[1],
                        "img_url": f"{base_url}{image[2]}"
                    }
                    for image in paginated_images
                ]
            else:
                image_data = [
                    {
                        "profile_id": image[1],
                        "img_url": f"{base_url}{image[2].replace('profile_images/', 'blurred_images/')}"
                    }
                    for image in paginated_images
                ]

            all_profile_ids = {str(index + 1): image[1] for index, image in enumerate(paginated_images)}

            combined_data = {
                "image_data": image_data,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_records + per_page - 1) // per_page,
                "total_records": total_records,
                "all_profile_ids": all_profile_ids
            }

            return JsonResponse({"Status": 1, "message": "Image fetched successfully", "data": combined_data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"Status": 0, "message": "Invalid input data"}, status=status.HTTP_200_OK)

    #return 

#get dashboard records counts records
def count_records(model_n, filter_condition):
    """
    Counts records based on the given filter condition.
    
    :param model: The Django model to query.
    :param filter_condition: A dictionary of conditions to filter the records.
    :return: The count of records that match the filter condition.
    """
    # Filter the records based on the condition
    # queryset = model_n.objects.filter(**filter_condition)
    queryset = model_n.objects.filter(**filter_condition)
    # Get the count of the filtered records
    count = queryset.count()
    
    return count

def count_records_forQ(model_n, filter_condition):
    """
    Counts records based on the given filter condition.
    
    :param model: The Django model to query.
    :param filter_condition: A dictionary of conditions to filter the records.
    :return: The count of records that match the filter condition.
    """
    # Filter the records based on the condition
    # queryset = model_n.objects.filter(**filter_condition)
    queryset = model_n.objects.filter(filter_condition)
    # Get the count of the filtered records
    count = queryset.count()
    
    return count

class My_intrests_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:
                                
                all_profiles = models.Express_interests.objects.filter(profile_from=profile_id, status=1)

                # Now, create the dictionary of all profile IDs.
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_to', flat=True))}

                # Get the total number of records.
                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page
                
                
                fetch_data = models.Express_interests.objects.filter(profile_from=profile_id,status=1)[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_to', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status

                    # sent_intrest_count = {'status': 1,'profile_from':profile_id}
                    # sent_int_count = count_records(models.Express_interests, sent_intrest_count)
                    
                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status != 0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    restricted_profile_details = [
                        {
                            "myint_profileid": detail.get("ProfileId"),
                            "myint_profile_name": detail.get("Profile_name"),
                            # "myint_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "myint_Profile_img": image_function(detail),    
                            "myint_profile_age": calculate_age(detail.get("Profile_dob")),
                            "myint_verified":detail.get("Profile_verified"),
                            "myint_height":detail.get("Profile_height"),
                            "myint_star":detail.get("star_name"),
                            "myint_profession":getprofession(detail.get("profession")),
                            "myint_city":detail.get("Profile_city"),
                            "myint_degree":get_degree(detail.get("ug_degeree")),
                            "myint_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "myint_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "myint_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "myint_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "myint_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "myint_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                            
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched interests and profile details successfully", "data": combined_data , "myint_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_mutual_intrests(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            
            try:
                all_profiles = models.Express_interests.objects.filter(
                    (Q(profile_from=profile_id) | Q(profile_to=profile_id)) & Q(status=2)
                )

                # Get both profile_from and profile_to IDs, and exclude the current profile_id
                profile_to_ids = all_profiles.values_list('profile_to', flat=True)
                profile_from_ids = all_profiles.values_list('profile_from', flat=True)

                # Combine and exclude the current profile_id
                all_profile_ids = set(profile_to_ids) | set(profile_from_ids)
                # all_profile_ids_1 = {str(index + 1): pid for index, pid in enumerate(all_profile_ids) if pid != profile_id}
                # all_profile_ids_1 = {str(i + 1): pid for i=0, pid in enumerate(all_profile_ids) if pid != profile_id}
                #all_profile_ids_1 = {str(i + 1): pid for i, pid in enumerate(all_profile_ids) if pid != profile_id}
                # all_profile_ids_1 = {str(i + 1): pid for i, pid in enumerate(all_profile_ids) if pid != profile_id}
                all_profile_ids_1 = {str(index + 1): pid for index, pid in enumerate([pid for pid in all_profile_ids if pid != profile_id])}



                total_records=len(all_profile_ids_1)
                start = (page - 1) * per_page
                end = start + per_page

                #fetch_data = models.Express_interests.objects.filter(profile_from=profile_id , profile_to=profile_id)
                fetch_data = models.Express_interests.objects.filter(
                    (Q(profile_from=profile_id) | Q(profile_to=profile_id)) &  Q(status=2))[start:end]

                if fetch_data.exists():
                    #profile_ids = fetch_data.values_list('profile_to', flat=True)
                    
                                                            
                    # Get profile_to IDs
                    profile_to_ids = fetch_data.values_list('profile_to', flat=True)

                    # Get profile_from IDs
                    profile_from_ids = fetch_data.values_list('profile_from', flat=True)

                    # Combine both sets of IDs
                    all_profile_ids = set(profile_to_ids) | set(profile_from_ids)

                    # Exclude the current profile_id
                    profile_ids = [pid for pid in all_profile_ids if pid != profile_id]
                                        
                    
                    
                    profile_details = get_profile_details(profile_ids)


                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender

                    my_status=profile_data.Status

                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status != 0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    # mutual_condition = Q(status=2) & (Q(profile_from=profile_id) | Q(profile_to=profile_id))
                    # mutual_int_count = count_records_forQ(models.Express_interests, mutual_condition)
                    
                    restricted_profile_details = [
                        {
                            "mutint_profileid": detail.get("ProfileId"),
                            "mutint_profile_name": detail.get("Profile_name"),
                            # "mutint_Profile_img":  Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),                           
                            "mutint_Profile_img": image_function(detail),
                            "mutint_profile_age": calculate_age(detail.get("Profile_dob")),
                            "mutint_verified":detail.get("Profile_verified"),
                            "mutint_height":detail.get("Profile_height"),
                            "mutint_star":detail.get("star_name"),
                            "mutint_profession":getprofession(detail.get("profession")),
                            "mutint_city":detail.get("Profile_city"),
                            "mutint_degree":get_degree(detail.get("ug_degeree")),
                            "mutint_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "mutint_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "mutint_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "mutint_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "mutint_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "mutint_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids_1,
                        "page_id":4
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched interests and profile details successfully", "data": combined_data,"mut_int_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No interests found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class Update_profile_intrests(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')

        # Initialize serializer with the incoming data
        serializer = serializers.Update_ExpressintrSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_from')
            profile_to = serializer.validated_data.get('profile_id')
            #status = serializer.validated_data.get('status')
            try:
                    # Get the instance to be updated
                    instance = models.Express_interests.objects.get(profile_from=profile_from, profile_to=profile_to)

                
            except models.Express_interests.DoesNotExist:
                    return JsonResponse({"Status": 0, "message": "Express interests entry not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Update the instance using the serializer's update method
            serializer.update(instance, serializer.validated_data)

            return JsonResponse({"Status": 1, "message": "Express interests updated successfully"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class Mark_profile_wishlist(APIView):
    def post(self, request):
        serializer = serializers.ProfileWishlistSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')

            get_limits=can_save_bookmark(profile_from)

            if get_limits is True: 
          
                # Check if an entry with the same profile_from and profile_to already exists
                existing_entry = models.Profile_wishlists.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
                
                if existing_entry:
                    # Update the status to 0 if the entry already exists
                    #existing_entry.status = 0
                    existing_entry.status = int_status
                    existing_entry.save()
                    return JsonResponse({"Status": 1, "message": "Wishlists updated"}, status=status.HTTP_200_OK)
                else:
                    # Create a new entry with status 1
                    serializer.save(status=1)
                    return JsonResponse({"Status": 1, "message": "Wishlists marked sucessfully"}, status=status.HTTP_200_OK)
        
            else:
                return JsonResponse({"Status": 0, "message": "No access to bookmark the profile"}, status=status.HTTP_200_OK)

        
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Get_profile_wishlist(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')  
            
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  

           

            try:
                # total_records = models.Profile_wishlists.objects.filter(profile_from=profile_id, status=1).count()

                all_profiles = models.Profile_wishlists.objects.filter(profile_from=profile_id, status=1)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_to', flat=True))}
                    
                    # Get the total number of records
                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page

                fetch_data = models.Profile_wishlists.objects.filter(profile_from=profile_id,status=1)[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_to', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status
                    # wishlist_condition = {'status': 1,'profile_from':profile_id}
                    
                    # wishlist_count = count_records(models.Profile_wishlists, wishlist_condition)

                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')


               
                    if photo_viewing == 1 and my_status!=0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    restricted_profile_details = [
                        {
                            "wishlist_profileid": detail.get("ProfileId"),
                            "wishlist_profile_name": detail.get("Profile_name"),
                            # "wishlist_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            # "wishlist_Profile_img":  Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),                                                        
                            "wishlist_Profile_img": image_function(detail),
                            "wishlist_profile_age": calculate_age(detail.get("Profile_dob")),
                            "wishlist_verified":detail.get("Profile_verified"),
                            "wishlist_height":detail.get("Profile_height"),
                            "wishlist_star":detail.get("star_name"),
                            "wishlist_profession":getprofession(detail.get("profession")),
                            "wishlist_degree":get_degree(detail.get("ug_degeree")),
                            "wishlist_city":get_city_name(detail.get("Profile_city")),
                            "wishlist_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "wishlist_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "wishlist_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "wishlist_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "wishlist_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "wishlist_profile":Get_wishlist(profile_id,detail.get("ProfileId")),

                            # "wishlist_profile_notes": 'Iam intrested in your profile if you are intrested in my profile , please contact me',
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched wishlists and profile details successfully", "data": combined_data ,"wishlist_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No wishlists found for the given profile ID"}, status=status.HTTP_404_NOT_FOUND)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No wishlists found for the given profile ID"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Create_profile_visit(APIView):
    def post(self, request):
        serializer = serializers.CreatevistsSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            viewed_profile = serializer.validated_data.get('viewed_profile')
            #int_status = serializer.validated_data.get('status')
            datetime_value =  serializer.validated_data.get('datetime', timezone.now())
            
            # print('datetime_value',datetime_value)
            
            # Check if an entry with the same profile_id and viewed_profile already exists
            existing_entry, created = models.Profile_visitors.objects.update_or_create(
                profile_id=profile_id, viewed_profile=viewed_profile, 
                defaults={'status': 1,'datetime': datetime_value})
            
            if created:
                message = "Profile view inserted"
                status_code = status.HTTP_201_CREATED
            else:
                message = "Profile view updated"
                status_code = status.HTTP_200_OK
            
            return JsonResponse({"Status": 1, "message": message}, status=status_code)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class My_profile_visit(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:
                
                all_profiles = models.Profile_visitors.objects.filter(viewed_profile=profile_id)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_id', flat=True))}

                total_records = all_profiles.count()
                start = (page - 1) * per_page
                end = start + per_page

                
                fetch_data = models.Profile_visitors.objects.filter(viewed_profile=profile_id)[start:end]
                if fetch_data.exists():
                    
                    profile_ids = fetch_data.values_list('profile_id', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status
                    # my_vistor_count = {'status': 1,'viewed_profile':profile_id}

                    # myvisitor_count = count_records(models.Profile_visitors, my_vistor_count)
                    # total_records=myvisitor_count
                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status!=0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    restricted_profile_details = [
                        {
                            "viwed_profileid": detail.get("ProfileId"),
                            "viwed_profile_name": detail.get("Profile_name"),
                            # "viwed_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "viwed_Profile_img": image_function(detail),
                            "viwed_profile_age": calculate_age(detail.get("Profile_dob")),
                            "viwed_verified":detail.get("Profile_verified"),
                            "viwed_height":detail.get("Profile_height"),
                            "viwed_star":detail.get("star_name"),
                            "viwed_profession":getprofession(detail.get("profession")),
                            "viwed_city":detail.get("Profile_city"),
                            "viwed_degree":get_degree(detail.get("ug_degeree")),
                            "viwed_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "viwed_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "viwed_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "viwed_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "viwed_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "viwed_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                             
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched viewed profile  lists successfully", "data": combined_data,"viewd_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No viewed profiles found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No viewed profiles found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class My_viewed_profiles(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10)) 
            try:
                
                all_profiles = models.Profile_visitors.objects.filter(profile_id=profile_id)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('viewed_profile', flat=True))}

                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page
                
                
                fetch_data = models.Profile_visitors.objects.filter(profile_id=profile_id)[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('viewed_profile', flat=True)
                    profile_details = get_profile_details(profile_ids)
                    
                    # viewed_profile_count_cont = {'status': 1,'profile_id':profile_id}
                    # viewed_profile_count = count_records(models.Profile_visitors, viewed_profile_count_cont)
                    
                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)
                    
                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status

                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status!= 0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)

                    restricted_profile_details = [
                        {
                            "visited_profileid": detail.get("ProfileId"),
                            "visited_profile_name": detail.get("Profile_name"),
                            # "visited_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            # "visited_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "visited_Profile_img": image_function(detail),
                            "visited_profile_age": calculate_age(detail.get("Profile_dob")),
                            "visited_verified":detail.get("Profile_verified"),
                            "visited_height":detail.get("Profile_height"),
                            "visited_star":detail.get("star_name"),
                            "visited_profession":getprofession(detail.get("profession")),
                            "visited_city":detail.get("Profile_city"),
                            "visited_degree":get_degree(detail.get("ug_degeree")),
                            "visited_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "visited_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "visited_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "visited_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "visited_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "visited_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                            
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched viewed profile  lists successfully", "data": combined_data,"viewed_profile_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No viewed profiles found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No viewed profiles found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class Save_personal_notes(APIView):
    def post(self, request):
        serializer = serializers.CreatepnotesSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            notes = serializer.validated_data.get('notes')
            #int_status = serializer.validated_data.get('status')
            datetime_value =  serializer.validated_data.get('datetime', timezone.now())
            
            

            get_limits=can_save_personal_notes(profile_id)
            # print(get_limits)

            if get_limits is True:
                
                # Check if an entry with the same profile_id and viewed_profile already exists
                existing_entry, created = models.Profile_personal_notes.objects.update_or_create(
                    profile_id=profile_id, profile_to=profile_to,
                    defaults={'status': 1,'datetime': datetime_value,'notes':notes})
                
                if created:
                    message = "Profile notes inserted"
                    status_code = status.HTTP_201_CREATED
                else:
                    message = "Profile notes updated"
                    status_code = status.HTTP_200_OK
                
                return JsonResponse({"Status": 1, "message": message}, status=status_code)
            else:
                return JsonResponse({"Status":0, "message": "Get full access - upgrade your package today!"}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Get_personal_notes(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:
                
                all_profiles = models.Profile_personal_notes.objects.filter(profile_id=profile_id)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_id', flat=True))}

                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page
                
                
                fetch_data = models.Profile_personal_notes.objects.filter(profile_id=profile_id)[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_to', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status
                    



                    # personal_notes = fetch_data.values_list('profile_id','notes','datetime')

                    personal_notes = fetch_data.values_list('profile_to','notes','datetime')



                    notes_mapping = {profile_to: (notes, datetime) for profile_to, notes, datetime in personal_notes}

                   

                    # personal_notes_condition={'status': 1,'profile_id':profile_id}

                    # personal_notes_count = count_records(models.Profile_personal_notes, personal_notes_condition)
                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status != 0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                                      
                    restricted_profile_details = [
                        {
                            "notes_profileid": detail.get("ProfileId"),
                            "notes_profile_name": detail.get("Profile_name"),
                            # "notes_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            # "notes_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "notes_Profile_img": image_function(detail),
                            "notes_profile_age": calculate_age(detail.get("Profile_dob")),
                            "notes_details": notes_mapping.get(detail.get("ProfileId"), ('notes', ''))[0],  # Get notes from the mapping
                            "notes_datetime": notes_mapping.get(detail.get("ProfileId"), ('datetime', ''))[1],
                            "notes_verified":detail.get("Profile_verified"),  # Get datetime from the mapping
                            "notes_height":detail.get("Profile_height"),
                            "notes_star":detail.get("star_name"),
                            "notes_profession":getprofession(detail.get("profession")),
                            "notes_city":detail.get("Profile_city"),
                            "notes_degree":get_degree(detail.get("ug_degeree")),
                            "notes_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "notes_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "notes_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "notes_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "notes_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "notes_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched Notes  lists successfully", "data": combined_data,"personal_note_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No Noteslists found for the given profile ID"}, status=status.HTTP_404_NOT_FOUND)
            except models.Profile_personal_notes.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No Noteslists found for the given profile ID"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def calculate_age(dob):
    """
    Calculate age based on date of birth.
    
    Args:
    dob (datetime.date): The date of birth.
    
    Returns:
    int or None: The calculated age or None if dob is not provided.
    """
    if dob:
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    return None



def Get_wishlist(profile_id,user_profile_id):
   
    if profile_id and user_profile_id:
        
        
         existing_entry=models.Profile_wishlists.objects.filter(profile_from=profile_id,profile_to=user_profile_id,status=1)

         if existing_entry:

            return 1
                  
         else:
              return 0
    return None


def preload_wishlist(profile_id, profile_ids_to_check):
    """
    Optimized wishlist checker to preload all wished profiles in one query.
    Returns a set of profile_to IDs that are in the wishlist.
    """
    if not profile_ids_to_check:
        return set()

    wishes = models.Profile_wishlists.objects.filter(
        profile_from=profile_id,
        profile_to__in=profile_ids_to_check,
        status=1
    ).values_list('profile_to', flat=True)

    return set(wishes)






def Get_expressstatus(profile_id, user_profile_id):
    if profile_id and user_profile_id:
        print(f'profile_id: {profile_id}, user_profile_id: {user_profile_id}')

        # Get the first matching entry
        existing_entry = models.Express_interests.objects.filter(profile_from=profile_id, profile_to=user_profile_id).first()

        #print('existing_entry:', existing_entry)

        if existing_entry:
            # Serialize the single instance
            serializer = serializers.ExpressInterestsSerializer(existing_entry)
            # Return only the status
            return serializer.data['status']
        else:
            
            return 0

    return 0  # Return 0 if no entry exists or profile_id/user_profile_id are not provided



def Get_personalnotes_value(profile_id, user_profile_id):
    if profile_id and user_profile_id:
        #print(f'profile_id: {profile_id}, user_profile_id: {user_profile_id}')

        # Get the first matching entry
        existing_entry = models.Profile_personal_notes.objects.filter(profile_id=profile_id, profile_to=user_profile_id).first()

        #print('existing_entry:', existing_entry)

        if existing_entry:
            # Serialize the single instance
            serializer = serializers.PersonalnotesSerializer(existing_entry)
            # Return only the status
            return serializer.data['notes']
        else:
            
            return ''

    return ''  # Return 0 if no entry exists or profile_id/user_profile_id are not provided



def get_degree(degeree):

    # print('degeree',degeree)
    if isinstance(degeree, str):
        return degeree
    
    try:
        
        Profile_ug_degree = models.Ugdegree.objects.get(id=degeree).degree
    
    except models.Ugdegree.DoesNotExist:
        Profile_ug_degree = None 
    
    return Profile_ug_degree


# def getprofession(profession):

#     # print('degeree',degeree)

#     try:
        
#         Profile_profession = models.Profespref.objects.get(RowId=profession).profession
    
#     except models.Profespref.DoesNotExist:
#                 Profile_profession = None 
    
#     return Profile_profession

def getprofession(profession):
    try:
        if not profession:  # handles None, '', 0
            return None

        # Fetch profession description
        profile_profession = models.Profespref.objects.get(RowId=profession).profession

    except (models.Profespref.DoesNotExist, ValueError, TypeError):
        # Return None if not found or invalid ID
        profile_profession = None

    return profile_profession






def Get_matching_score(source_star_id, source_rasi_id,dest_star_id,dest_rasi_id,gender):
    
    # print('source_star_id : ',source_star_id,'source_rasi_id: ',source_rasi_id,'dest_star_id: ', dest_star_id , 'dest_rasi_id: ',dest_rasi_id,'gender',gender)

    # print('outside if cond')
    if source_star_id and source_rasi_id and dest_star_id and dest_rasi_id:
        # print('inside if cond')
       

        # Get the first matching entry
        existing_entry = models.MatchingStarPartner.objects.filter(source_star_id=source_star_id, source_rasi_id=source_rasi_id, dest_star_id=dest_star_id,dest_rasi_id=dest_rasi_id,gender=gender)

        # print('existing_entry',existing_entry)
        if existing_entry:

            # print('inside existing entry')
            # Serialize the single instance
            serializer = serializers.MatchingscoreSerializer(existing_entry,many=True)

            match_count = serializer.data[0].get('match_count', 0)
            # Return only the status
            if(match_count==15):
                matching_score=100
            else:
                matching_score=match_count*10            

            # print('matching_score',matching_score)
            return matching_score
        else:
            # print('query not executed')
            return 0

    # print('if Not executed cond')
    return 0  # Return 0 if no entry exists or profile_id/user_profile_id are not provided



def get_permission_limits(profile_id, column_name):
    
    if column_name == 'photo_viewing':
    
        get_limits = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,status=1).first()

        if get_limits and hasattr(get_limits, column_name):  
            return getattr(get_limits, column_name)  # Dynamically fetch the column value
    else:
        limits  = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,status=1).first()

        if not limits :
            return None  # No active record found

        print('expired date',limits.membership_todate)
        print('Current date',date.today())

        if getattr(limits, 'membership_todate', None) and limits.membership_todate.date() < date.today():
            return 0  # Membership expired
        
        return getattr(limits, column_name, None)

        # if get_limits and hasattr(get_limits, column_name):  
        #     return getattr(get_limits, column_name)  # Dynamically fetch the column value
    
    return None  # Return None if no record exists or column is invalid

    #return True


# Initialize Azure Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)

def get_profile_image_azure_optimized(user_profile_id, gender, no_of_image, photo_protection):
    """
    Optimized image retrieval with:
    - Dual caching (Redis + local fallback)
    - Pre-generated blurred images
    - Efficient database queries
    - Comprehensive error handling
    """
    # Configuration
    DEFAULT_IMAGES = {
        'male': f"{settings.MEDIA_URL}default_bride.png",
        'female': f"{settings.MEDIA_URL}default_groom.png",
        'default': f"{settings.MEDIA_URL}default_img.png",
        'locked': f"{settings.MEDIA_URL}default_photo_protect.png"
    }

    # Cache keys
    cache_key = f"img:{user_profile_id}:{no_of_image}"
    blurred_cache_key = f"img_blurred:{user_profile_id}:{no_of_image}"
    
    try:
        redis_cache = caches['images']
        
        # ===== 1. PHOTO PROTECTION HANDLING =====
        if photo_protection == 1:
            blurred_cache_key = f"img_blurred:{user_profile_id}:{no_of_image}"
            
            # Try cache first
            if cached := redis_cache.get(blurred_cache_key):
                return cached

            # Get original images from DB
            images = models.Image_Upload.objects.filter(
                profile_id=user_profile_id,
                image_approved=1,
                is_deleted=0
            ).order_by('id').values_list('image', flat=True)[:10]  # Limit to 10

            if not images:
                return DEFAULT_IMAGES['locked'] if no_of_image == 1 else \
                    {str(i): DEFAULT_IMAGES['locked'] for i in range(1, no_of_image+1)}

            # Prepare URLs for blur check
            original_urls = [f"{settings.MEDIA_URL}{img}" for img in (
                [images[0]] if no_of_image == 1 else images[:10]
            )]

            # Get blurred images in batch
            blurred_results = get_blurred_images_updated(original_urls, return_multiple=(no_of_image != 1))

            # Process results
            if no_of_image == 1:
                result = blurred_results if isinstance(blurred_results, str) else \
                    blurred_results.get(original_urls[0], DEFAULT_IMAGES['locked'])
            else:
                result = {
                    str(i+1): blurred_results.get(url, DEFAULT_IMAGES['locked'])
                    for i, url in enumerate(original_urls)
                }

            # Cache results
            if result and result != DEFAULT_IMAGES['locked']:
                redis_cache.set(blurred_cache_key, result, timeout=3600)
            return result

        # ===== 2. REGULAR IMAGE FLOW =====
        # Check cache first
        if cached := redis_cache.get(cache_key):
            return cached
            
        # Database lookup
        if user_profile_id:
            query = models.Image_Upload.objects.filter(
                profile_id=user_profile_id,
                image_approved=1,
                is_deleted=0
            ).order_by('id')
            
            if no_of_image == 1:
                image_name = query.values_list('image', flat=True).first()
                if image_name:
                    image_url = f"{settings.MEDIA_URL}{image_name}"
                    redis_cache.set(cache_key, image_url, timeout=86400)  # 24h cache
                    return image_url
            else:
                images = list(query.values_list('image', flat=True)[:10])
                if images:
                    result = {str(i+1): f"{settings.MEDIA_URL}{img}" 
                            for i, img in enumerate(images)}
                    redis_cache.set(cache_key, result, timeout=86400)
                    return result

        # ===== 3. FALLBACK =====
        gender_key = str(gender).lower() if gender else 'default'
        gender_key = gender_key if gender_key in ('male', 'female') else 'default'
        return DEFAULT_IMAGES[gender_key]
        
    except Exception as e:
        logger.error(f"Image loading failed: {str(e)}", exc_info=True)
        # Fallback to local cache
        local_cache = caches['default']
        if photo_protection == 1:
            if cached := local_cache.get(blurred_cache_key):
                return cached
        else:
            if cached := local_cache.get(cache_key):
                return cached
                
        return DEFAULT_IMAGES['default']





# image_cache = caches['images']
# BASE_DIR = Path(__file__).resolve().parent.parent
# def Get_profile_image_optimized(user_profile_id, gender, no_of_image, photo_protection):
#     """
#     Ultra-optimized image retrieval with:
#     - Multi-level caching
#     - Async-ready structure
#     - Zero unnecessary queries
#     - Pre-computed defaults
#     """
#     # Static configuration - loaded once at startup
#     DEFAULT_IMAGES = {
#         'male': f"{settings.MEDIA_URL}default_bride.png",
#         'female': f"{settings.MEDIA_URL}default_groom.png",
#         'default': f"{settings.MEDIA_URL}default_img.png",
#         'locked': f"{settings.MEDIA_URL}default_photo_protect.png"
#     }
    
#     # Fast path for photo protection
#     if photo_protection == 1:
#         return DEFAULT_IMAGES['locked']
    
#     gender_str = str(gender).lower() if gender is not None else 'default'

#     cache_key = f"img_{user_profile_id}_{no_of_image}"

#     # 1. First try: Memory cache
#     if cached := image_cache.get(cache_key):
#         return cached

#     # 2. Second try: Filesystem cache
#     # Get the proper cache path using your project's BASE_DIR
#     fs_cache_dir = BASE_DIR / 'cache' / 'images'
#     fs_cache_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

#     # Create hashed filename
#     hashed_filename = f"{hashlib.md5(cache_key.encode()).hexdigest()}.cache"
#     fs_cache_path = fs_cache_dir / hashed_filename
#     if os.path.exists(fs_cache_path):
#         with open(fs_cache_path, 'r') as f:
#             cached_data = f.read()
#         image_cache.set(cache_key, cached_data, timeout=3600)
#         return cached_data
    
#     # 3. Database lookup (optimized)
#     if user_profile_id:
#         # Using values_list() avoids model instantiation
#         images = models.Image_Upload.objects.filter(
#             Q(profile_id=user_profile_id) &
#             Q(image_approved=1) &
#             Q(is_deleted=0)
#         ).order_by('id').values_list('image', flat=True)[:10]
        
#         if images:
#             # Direct URL construction avoids serialization
#             media_url = settings.MEDIA_URL
#             if no_of_image == 1:
#                 result = f"{media_url}{images[0]}"
#             else:
#                 result = {str(i+1): f"{media_url}{img}" for i, img in enumerate(images)}
            
#             # Cache the result
#             image_cache.set(cache_key, result, timeout=3600)
#             with open(fs_cache_path, 'w') as f:
#                 f.write(str(result))
#             return result
    
#     # Fallback to default image
#     default_key = gender_str if gender_str in ('male', 'female') else 'default'
#     result = DEFAULT_IMAGES[default_key]
#     image_cache.set(cache_key, result, timeout=3600)
#     return result



def Get_profile_image_New(user_profile_id, gender, no_of_image, photo_protection):
    # Configuration from settings
    base_url = settings.MEDIA_URL
    default_images = {
        'male': base_url + 'default_bride.png',
        'female': base_url + 'default_groom.png',
        'default': base_url + 'default_img.png',
        'locked': base_url + 'default_photo_protect.png'
    }
    
    # Handle photo protection case
    if photo_protection == 1:
        return default_images['locked']
    
    # Get approved images for the profile
    images = models.Image_Upload.objects.filter(
        profile_id=user_profile_id,
        image_approved=1,
        is_deleted=0
    ).order_by('id')[:10] if user_profile_id else None
    
    # Handle single image request
    if no_of_image == 1:
        if images and images.exists():
            image_url = serializers.ImageGetSerializer(images[0]).data['image']
            if validate_image_url(image_url):
                return image_url
        return default_images.get(gender.lower(), default_images['default'])
    
    # Handle multiple images request
    else:
        if images and images.exists():
            serializer = serializers.ImageGetSerializer(images, many=True)
            return {
                str(i+1): entry['image'] 
                for i, entry in enumerate(serializer.data)
            }
        default_img = default_images.get(gender.lower(), default_images['default'])
        return {"1": default_img, "2": default_img}

def validate_image_url(url):
    """Helper function to validate image URL"""
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False




def Get_profile_image(user_profile_id,gender,no_of_image,photo_protection):

    # print("Execution time before return image ",datetime.now())
    

    #base_url='http://103.214.132.20:8000'
    base_url=settings.MEDIA_URL
    #base_url='http://127.0.0.1:8000/'
    
    #default_img_grrom='media/default_groom.png'
    default_img_bride='default_bride.png'
    default_img_groom='default_groom.png'
    default_lock='default_photo_protect.png'
    default_img='default_img.png'
    
    #return  base_url + default_img

    if photo_protection !=1:        

        if user_profile_id:
        
            if(no_of_image==1):

                # print('no_of_image','1')

                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()           
            
                if get_entry:
                        # Serialize the single instance
                        serializer = serializers.ImageGetSerializer(get_entry)
                        # Return only the status
                        # return serializer.data['image']
                        image_url = serializer.data['image']

                        # print('image_url',image_url)
                        try:
                            response = requests.head(image_url, timeout=5)
                            if response.status_code == 200:
                                return image_url
                        except requests.RequestException:
                            pass  # Fall back to default if request fails
                        
                        # Return default image if no image found or image does not exist
                        # print("Execution time before return one image ",datetime.now())
                        return  base_url + default_img

                else:
                        
                        
                        #return 0
                        if(gender.lower()=='male'):
                           
                            return base_url+default_img_bride
                        
                        if(gender.lower()=='female'):
                            return base_url+default_img_groom
                        
                    
            else:
                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0)[:10]
                if get_entry.exists():
                    # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry,many=True)
                    # Return only the status
                    images_dict = {
                        str(index + 1): entry['image']
                        for index, entry in enumerate(serializer.data)
                    }
                    #print(images_dict)
                    # print("Execution time before return all image ",datetime.now())
                    return images_dict
                    
                else:                
                    default_img = default_img_bride if gender == 'male' else default_img_groom
                    # print("Execution time before return default image ",datetime.now())
                    return {"1":  base_url + default_img,"2":  base_url + default_img}
                
    else:

        # print('photo protection is true')

        if(no_of_image==1):
            get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()   

                #print('get_entry',get_entry)        
                    
            if get_entry:
                        # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry)
                                # Return only the status
                    img_base64=get_blurred_image(serializer.data['image'])
                    
                    
                    # print("Execution time when blur image return ",datetime.now())
                    return img_base64,
            else :
                
                if(gender=='male'):
                        # print("Execution time when blur image failed ",datetime.now())
                        
                        return base_url+default_img_bride
                                
                if(gender=='female'):
                        # print("Execution time when blur image failed ",datetime.now())
                                    
                        return base_url+default_img_groom

        else:

                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()   
     
                    
                if get_entry:
                        # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry)
                                # Return only the status
                    img_base64=get_blurred_image(serializer.data['image'])

                    # print("Execution time when return blur image failed ",datetime.now())
                    
                    return {"1": img_base64}
                        
                    # else:
                    #     raise Exception(f"Failed to download image. Status code: {response.status_code}")
             
                else:
                    if(gender=='male'):

                        # print("Execution time when return blur image failed ",datetime.now())
                        
                        return {"1": base_url+default_img_bride }
                                
                    if(gender=='female'):

                        # print("Execution time when return blur image failed ",datetime.now())
                                    
                        return {"1": base_url+default_img_groom }


def get_default_or_blurred_image(user_profile_id,gender):

            # print("Execution time on blurred image start ",datetime.now())
            
            base_url=settings.MEDIA_URL
            #base_url='http://127.0.0.1:8000/'
            
            #default_img_grrom='media/default_groom.png'
            default_img_bride='default_bride.png'
            default_img_groom='default_groom.png'
            default_lock='default_photo_protect.png'

            get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()   

                #print('get_entry',get_entry)        
                    
            if get_entry:
                        # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry)
                                # Return only the status
                    img_base64=get_blurred_image(serializer.data['image'])
                    
                    
                    
                    return img_base64,
            else :
                
                if(gender=='male'):
                        
                        return base_url+default_img_bride
                                
                if(gender=='female'):
                                    
                        return base_url+default_img_groom



def Get_image_profile(user_profile_id):
    base_url = settings.MEDIA_URL
    default_img_bride = 'default_bride.png'
    default_img_groom = 'default_groom.png'
    user_profile = models.Registration1.objects.get(ProfileId=user_profile_id)
    
    gender = user_profile.Gender
    photo_protection = user_profile.Photo_protection

    # Default to the appropriate image based on gender
    if not photo_protection:
        get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()
        if get_entry:
            serializer = serializers.ImageGetSerializer(get_entry)
            return serializer.data['image']
        
        return base_url + (default_img_groom if gender.lower() == 'male' else default_img_bride)
    
    get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id,image_approved=1,is_deleted=0).first()
    if get_entry:
        serializer = serializers.ImageGetSerializer(get_entry)
        img_base64 = get_blurred_image(serializer.data['image'])
        return img_base64  # Ensure this returns a string
    
    # Fallback to a default blurred image in case of no entry found
    return settings.MEDIA_URL + 'default_img.png'



class Get_prof_list_match(APIView):

    def post(self, request):
        # print("Execution time when starts ",datetime.now())
        serializer = serializers.GetproflistSerializer(data=request.data)

        if serializer.is_valid():            
            
            profile_id = serializer.validated_data['profile_id']
            profile_data =  models.Registration1.objects.get(ProfileId=profile_id) 
            
            search_profile_id = request.data.get('search_profile_id')

            search_profession= request.data.get('search_profession')
            search_age= request.data.get('search_age')
            search_location= request.data.get('search_location')


            order_by = request.data.get('order_by')
            
            gender=profile_data.Gender


            #psgination code

            received_per_page = request.data.get('per_page')
            received_page_number = request.data.get('page_number')

                # Set default values if not provided
            if received_per_page is None:
                    per_page = 10
            else:
                    try:
                        per_page = int(received_per_page)
                    except (ValueError, TypeError):
                        per_page = 10  # Fall back to default if conversion fails

            if received_page_number is None:
                    page_number = 1
            else:
                    try:
                        page_number = int(received_page_number)
                    except (ValueError, TypeError):
                        page_number = 1  # Fall back to default if conversion fails

                # Ensure valid values for pagination
            per_page = max(1, per_page)
            page_number = max(1, page_number)

                # Calculate the starting record for the SQL LIMIT clause
            start = (page_number - 1) * per_page
            # print("Execution time before matching list fetch ",datetime.now())
            profile_details , total_count ,profile_with_indices = models.Get_profiledata.get_profile_list(gender,profile_id,start,per_page,search_profile_id,order_by,search_profession,search_age,search_location)
            # print("Execution time after matching list fetch ",datetime.now())
            my_profile_id = [profile_id]   

            # print('my_profile_id',my_profile_id) 

            # print('profile_details',profile_details)        

            # print("Execution time before matching list details get ",datetime.now())
            my_profile_details = get_profile_details(my_profile_id)
            # print("Execution time after matching list details get ",datetime.now())
            # print('my_profile_details',my_profile_details)
            my_pstatus=my_profile_details[0]['pstatus']
            my_gender=my_profile_details[0]['Gender']
            my_star_id=my_profile_details[0]['birthstar_name']
            my_rasi_id=my_profile_details[0]['birth_rasi_name']

            photo_viewing=get_permission_limits(profile_id,'photo_viewing')

            if photo_viewing == 1 and my_pstatus !=0:
                # print("Execution time before image starts ",datetime.now())
                image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
            else:
                # sprint("Execution time before blur image starts ",datetime.now())
                image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)


            
            # print('Testing','8752145')

            #print('matching profile limit 1',profile_details[0])

            #return JsonResponse(response_data, status=status.HTTP_200_OK)

            
            # timming = datetime.now()

            print("Execution time before loop ",datetime.now())

            if profile_details:                
                # Preload matching scores into a dictionary

                preload_matching_scores()
                score_map = cache.get("matching_score_map", {})

                # Standardize your inputs
                my_star_id_str = str(my_star_id)
                my_rasi_id_str = str(my_rasi_id)
                my_gender_lower = my_gender.lower()

                # Generate the full list efficiently
                
                profile_to_ids = [detail.get("ProfileId") for detail in profile_details]
                wishlisted_ids = preload_wishlist(profile_id, profile_to_ids)
                restricted_profile_details = []
                
                
                for detail in profile_details:
                    dest_star = str(detail.get("birthstar_name"))
                    dest_rasi = str(detail.get("birth_rasi_name"))
                    profile_to = detail.get("ProfileId")

                    key = (my_star_id_str, my_rasi_id_str, dest_star, dest_rasi, my_gender_lower)
                    match_count = score_map.get(key, 0)
                    matching_score = 100 if match_count == 15 else match_count * 10



                    # photo_protection = detail.get("Photo_protection", 0)

                    # profile_img = get_profile_image_azure_optimized(
                    #     user_profile_id=profile_to,
                    #     gender=detail.get("Gender"),
                    #     no_of_image=1,
                    #     photo_protection=1
                    # )

                    restricted_profile_details.append({
                        "profile_id": detail.get("ProfileId"),
                        "profile_name": detail.get("Profile_name"),
                        "profile_img": image_function(detail),
                        #"profile_img": profile_img,
                        "profile_age": calculate_age(detail.get("Profile_dob")),
                        "profile_gender": detail.get("Gender"),
                        "height": detail.get("Profile_height"),
                        "weight": detail.get("weight"),
                        "degree": get_degree(detail.get("ug_degeree")),
                        "star": detail.get("star"),
                        "profession": getprofession(detail.get("profession")),
                        "location": detail.get("Profile_city"),
                        "photo_protection": detail.get("Photo_protection"),
                        "matching_score": matching_score,
                        # "wish_list":Get_wishlist(profile_id,detail.get("ProfileId")),
                        "wish_list": 1 if profile_to in wishlisted_ids else 0,
                        "verified":detail.get('Profile_verified'),
                    })
                
                print("Execution time after loop ",datetime.now())
            
                combined_data = {
                            #"interests": serialized_fetch_data,
                            "profiles": restricted_profile_details
                        }
                
                return JsonResponse({"Status": 1, "message": "Matching records fetched successfully","profiles": restricted_profile_details,"total_count":total_count,
                            'received_per_page': received_per_page,
                            'received_page_number': received_page_number,
                            'calculated_per_page': per_page,
                            'calculated_page_number': page_number,
                            'all_profile_ids':profile_with_indices,
                            'search_result':"1"

                            }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"Status": 0, "message": "No matching records ","search_result": "1" }, status=status.HTTP_200_OK)
        

        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_profile_det_match_old(APIView):

 def post(self, request):
        #profile_id = 'VY240013'
      profile_id = request.data.get('profile_id')
      user_profile_id = request.data.get('user_profile_id')
      page_id = request.data.get('page_id')
    
    #   print('match_profile_id',user_profile_id)
    
      serializer = serializers.GetproflistSerializer_details(data=request.data)
      if serializer.is_valid():   

       getviewlimits=can_get_viewd_profile_count(profile_id,user_profile_id) #Check Limits for the profile id based on their plan
    #    print('getviewlimits',getviewlimits)
    #    if getviewlimits is True or int(page_id)!=1 :   #if page id is not 1 than it is not a new profile details view 

       if getviewlimits is True or (page_id is not None and int(page_id) != 1):

                #profile_ids = profile_id
                #   print('match_profile_id',user_profile_id)

                profile_ids = [user_profile_id]
                profile_details = get_profile_details(profile_ids)
                my_profile_id =[profile_id]

                my_profile_details = get_profile_details(my_profile_id)

                my_gender=my_profile_details[0]['Gender']
                my_star_id=my_profile_details[0]['birthstar_name']
                my_rasi_id=my_profile_details[0]['birth_rasi_name']
                
                plan_id=my_profile_details[0]['Plan_id']

                
                if plan_id!='':

                    try:
                            Plan_sbnscrption = models.PlanDetails.objects.get(id=plan_id)
                            Plan_subscribed=1
                            
                    except models.PlanDetails.DoesNotExist:
                            Plan_subscribed=0
                else:
                        Plan_subscribed=0



                photo_viewing=get_permission_limits(profile_id,'photo_viewing')
                
                #commented by vinoth 16-05-25

                # print("Execution time before image ",datetime.now())

                if photo_viewing == 1:
                    #  print("Execution time before image ",datetime.now())
                     user_images =  lambda detail: get_profile_image_azure_optimized(profile_details[0]['ProfileId'], my_gender, 'all', profile_details[0]['Photo_protection'])
                    #  print("Execution time after image  ",datetime.now())
                else:
                    # print("Execution time before image ",datetime.now())
                    user_images = lambda detail: get_profile_image_azure_optimized(profile_details[0]['ProfileId'], my_gender,'all',1)
                    # print("Execution time after image  ",datetime.now())
               
                try:
                    complexion_id = profile_details[0].get('Profile_complexion')
                    if complexion_id and str(complexion_id).isdigit():
                        Profile_complexion = models.Profilecomplexion.objects.get(complexion_id=complexion_id).complexion_desc
                    else:
                        Profile_complexion = None
                except models.Profilecomplexion.DoesNotExist:
                    Profile_complexion = None

                # Handle highest_education safely
                try:
                    highest_edu_id = profile_details[0].get('highest_education')
                    if highest_edu_id and str(highest_edu_id).isdigit():
                        Profile_high_edu = models.Edupref.objects.get(RowId=highest_edu_id).EducationLevel
                    else:
                        Profile_high_edu = ''
                except models.Edupref.DoesNotExist:
                    Profile_high_edu = ''

                try:
                    field_of_study_id = profile_details[0].get('field_ofstudy')
                    if field_of_study_id:
                        Profile_field_study = models.Profilefieldstudy.objects.get(id=field_of_study_id).field_of_study
                    else:
                        Profile_field_study = ''
                except models.Profilefieldstudy.DoesNotExist:
                    Profile_field_study = ''

                try:
                    profession_id = profile_details[0].get('profession')
                    if profession_id and str(profession_id).isdigit():
                        Profile_profession = models.Profespref.objects.get(RowId=profession_id).profession
                    else:
                        Profile_profession = None
                except models.Profespref.DoesNotExist:
                    Profile_profession = None

                try:
                        Profile_owner = models.Profileholder.objects.get(Mode=profile_details[0]['Profile_for']).ModeName
                except models.Profileholder.DoesNotExist:
                        Profile_owner = None

                try:
                        Profile_marital_status = models.ProfileMaritalstatus.objects.get(StatusId=profile_details[0]['Profile_marital_status']).MaritalStatus
                except models.ProfileMaritalstatus.DoesNotExist:
                        Profile_marital_status = None
                
                try:
                    family_status_id = profile_details[0].get('family_status')
                    if family_status_id and str(family_status_id).isdigit():
                        Profile_family_status = models.Familystatus.objects.get(id=family_status_id).status
                    else:
                        Profile_family_status = None
                except models.Familystatus.DoesNotExist:
                    Profile_family_status = None

                now = timezone.now()

                    # Convert now to a naive datetime
                now_naive = now.replace(tzinfo=None)
                one_month_ago = now_naive - timedelta(days=30)
                Profile_status_active = ''
                last_login_date=profile_details[0]['Last_login_date']
                last_visit=''
            
                if last_login_date:
                # Check if the date is the default invalid value
                    if last_login_date == '0000-00-00 00:00:00':
                        last_login_date = None
                        Profile_status_active = "Newly registered"
                        # print(last_login_date,'last_login_date0000')
                    else:

                            try:

                                    last_visit =profile_details[0]['Last_login_date'].strftime("(%B %d, %Y)") 
                                        
                            except ValueError:
                                last_login_date = None
                            last_login_date = None

                        # Compare the last_login_date with one_month_ago
                            if last_login_date and last_login_date < one_month_ago:
                                    Profile_status_active = "In Active User"  # Mark as inactive if last login is older than zone month
                            else:
                                    Profile_status_active = "Active User"
                else:
                        Profile_status_active = "Newly registered"  # Handle case where Last_login_date is None or empty
                    
                try:
                        profile_star_name = models.Birthstar.objects.get(id=profile_details[0]['birthstar_name']).star
                except models.Birthstar.DoesNotExist:
                        profile_star_name = None

                try:
                        profile_rasi_name = models.Rasi.objects.get(id=profile_details[0]['birth_rasi_name']).name
                except models.Rasi.DoesNotExist:
                        profile_rasi_name = None

                Profile_horoscope=0
                Profile_horoscope_txt='Not available'
                Profile_horoscope_file = profile_details[0]['horoscope_file_admin']
                Profile_horoscope_file_link=''
                if(Profile_horoscope_file):
                                    
                        Profile_horoscope=1
                        Profile_horoscope_txt="Horoscope Available"
                        
                        Profile_horoscope_file_link=settings.MEDIA_URL+Profile_horoscope_file 

                
                vysy_assist_enable=get_permission_limits(profile_id,'vys_assist')
                try:
                    vys_assits=True
                    vys_status_list = models.Profile_vysassist.objects.get(profile_from=profile_id, profile_to=user_profile_id)
                    followups =  models.ProfileVysAssistFollowup.objects.filter(assist_id=vys_status_list.id).order_by('-update_at')
                    # vysystatus_serializer = serializer.ProfileVysAssistFollowupSerializer(followups, many=True)
                    if followups.exists():
                        vysystatus_serializer = serializers.ProfileVysAssistFollowupSerializer(followups, many=True).data
                    else:
                        vysystatus_serializer = [{
                            "comments": vys_status_list.to_message+' (Request sent)',
                            "update_at": vys_status_list.req_datetime
                        }]

                except models.Profile_vysassist.DoesNotExist:
                   vys_assits=False
                   vysystatus_serializer=None
                   
                permission_contact_details=get_permission_limits(profile_id, 'contact_details')
                permission_horosocpegrid_details=get_permission_limits(profile_id, 'horoscope_grid_details')

                # print('permission_contact_details',permission_contact_details)
                # print('permission_horosocpegrid_details',permission_horosocpegrid_details)

                
                eng_print=get_permission_limits(profile_id,'eng_print')  #user uploaded horoscope grid download permision
                
                if eng_print == 0:

                    Profile_horoscope=0
                    Profile_horoscope_txt='Not available'
                    Profile_horoscope_file_link=''

                
                photo_request=0

                if profile_details[0]['Photo_protection']==1:
                    photo_request=1 

                current_image_count = models.Image_Upload.objects.filter(profile_id=profile_details[0]['ProfileId']).count()              
                if current_image_count==0:
                     photo_request=1 
            
                try:
                    lagnam_didi_id = profile_details[0]['lagnam_didi']
                    if lagnam_didi_id:
                        lagnam_didi = models.Lagnamdidi.objects.get(id=lagnam_didi_id)
                        lagnam_didi_name = lagnam_didi.name
                    else:
                        lagnam_didi_name = None  # Default value if null or empty
                except models.Lagnamdidi.DoesNotExist:
                    lagnam_didi_name = None  # Handle case where object doesn't exist


                
                annual_income_id = profile_details[0]['anual_income']
                annual_income_name=''
                try:
                    if annual_income_id:
                        annual_income = models.Annualincome.objects.get(id=annual_income_id)
                        annual_income_name = annual_income.income
                    else:
                        annual_income=None
                        annual_income_name=''
                except models.Annualincome.DoesNotExist:
                    annual_income_name = None


                def dosham_value_formatter(value):
                    if isinstance(value, str):
                        return {"0": "Unknown", "1": "Yes", "2": "No"}.get(value, value)
                    elif isinstance(value, int):
                        return {0: "Unknown", 1: "Yes", 2: "No"}.get(value, value)
                    return value

                try:
                    lagnam_didi_id = profile_details[0]['lagnam_didi']
                    if lagnam_didi_id:
                        lagnam_didi = models.Lagnamdidi.objects.get(id=lagnam_didi_id)
                        lagnam_didi_name = lagnam_didi.name
                    else:
                        lagnam_didi_name = None  # Default value if null or empty
                except models.Lagnamdidi.DoesNotExist:
                    lagnam_didi_name = None  # Handle case where object doesn't exist


                profile_data={
                        "basic_details": {
                            "profile_id": profile_details[0]['ProfileId'],
                            "profile_name": profile_details[0]['Profile_name'],
                            "age": calculate_age(profile_details[0]['Profile_dob']),
                            "weight": profile_details[0]['weight'],
                            "height": profile_details[0]['Profile_height'],
                            "star":  profile_details[0]['star_name'],
                            "profession": Profile_profession,
                            "education": Profile_high_edu +' '+Profile_field_study,
                            "about": profile_details[0]['about_self'],
                            "gothram": profile_details[0]['suya_gothram'],
                            "horoscope_available": Profile_horoscope,
                            "horoscope_available_text": Profile_horoscope_txt,
                            "horoscope_link":Profile_horoscope_file_link,
                            "user_status": Profile_status_active,
                            "verified":profile_details[0]['Profile_verified'],
                            "last_visit":last_visit,
                            "user_profile_views": count_records(models.Profile_visitors, {'status': 1,'viewed_profile':user_profile_id}),
                            "wish_list": Get_wishlist(profile_id,user_profile_id),
                            "express_int": Get_expressstatus(profile_id,user_profile_id),
                            "personal_notes": Get_personalnotes_value(profile_id,user_profile_id),

                            # "wish_list": 1,
                            # "express_int": 1,
                            # "personal_notes": "dfG",
                            # "matching_score": "75%",

                            #"matching_score":Get_matching_score(my_star_id,my_rasi_id,profile_details[0]['birthstar_name'],profile_details[0]['birth_rasi_name'],my_gender),
                            "matching_score":get_matching_score_util(source_star_id=my_star_id,source_rasi_id=my_rasi_id,dest_star_id=profile_details[0]['birthstar_name'],dest_rasi_id=profile_details[0]['birth_rasi_name'],gender=my_gender),
                            "plan_subscribed":Plan_subscribed,
                            "vysy_assist_enable":vysy_assist_enable,
                            "vys_assits":vys_assits,
                            "vys_list":vysystatus_serializer
                        },
                        "photo_protection":profile_details[0]['Photo_protection'],
                        "photo_request":photo_request,
                        # "user_images":user_images,
                        "user_images":user_images(profile_details[0]),
                        # "user_images": {
                        #         "1": "https://vysyamat.blob.core.windows.net/vysyamala/default_groom.png"
                        #     },
                        "personal_details": {
                            "profile_name": profile_details[0]['Profile_name'],
                            "gender": profile_details[0]['Gender'],
                            "age": calculate_age(profile_details[0]['Profile_dob']),
                            "dob": format_date_of_birth(profile_details[0]['Profile_dob']),
                            "place_of_birth": profile_details[0]['place_of_birth'],
                            "time_of_birth": format_time_am_pm(profile_details[0]['time_of_birth']),                   
                            "height": profile_details[0]['Profile_height'],
                            "marital_status": Profile_marital_status,
                            "blood_group": profile_details[0]['blood_group'],
                            "about_self": profile_details[0]['about_self'],
                            "complexion": Profile_complexion,
                            "hobbies": profile_details[0]['hobbies'],
                            "physical_status": "No" if profile_details[0]['Pysically_changed'] == 0 else "1" if profile_details[0]['Pysically_changed'] == 1 else profile_details[0]['Pysically_changed'] ,
                            "eye_wear": profile_details[0]['eye_wear'] ,
                            "weight": profile_details[0]['weight'] ,
                            "body_type": profile_details[0]['body_type'] ,
                            "profile_created_by": Profile_owner,
                        },
                        "education_details": {
                            "education_level": Profile_high_edu+' '+Profile_field_study,
                            "education_detail": " ",
                            "ug_degeree": get_degree(profile_details[0]['ug_degeree']),
                            "about_education": profile_details[0]['about_edu'],
                            "profession": Profile_profession,
                            "designation": profile_details[0]['designation'],
                            "company_name": profile_details[0]['company_name'],
                            "business_name": profile_details[0]['business_name'],
                            "business_address": profile_details[0]['business_address'],
                            "annual_income": annual_income_name,
                            "gross_annual_income": profile_details[0]['actual_income'],
                            # "place_of_stay": profile_details[0]['Profile_city'],
                            "place_of_stay":get_place_of_work(profile_details),
                        },
                        "family_details": {
                            "about_family": profile_details[0]['about_family'],
                            "father_name": profile_details[0]['father_name'],                            
                            "father_occupation": profile_details[0]['father_occupation'],
                            "mother_name": profile_details[0]['mother_name'],
                            "mother_occupation": profile_details[0]['mother_occupation'],
                            "family_status": Profile_family_status,
                            "no_of_sisters": profile_details[0]['no_of_sister'],
                            "no_of_brothers": profile_details[0]['no_of_brother'],
                            "no_of_sis_married": profile_details[0]['no_of_sis_married'],
                            "no_of_bro_married": profile_details[0]['no_of_bro_married'],
                            "property_details": profile_details[0]['property_details'],
                            "father_alive": profile_details[0]['father_alive'],
                            "mother_alive": profile_details[0]['mother_alive'],
                        },
                        "horoscope_details": {
                            "rasi": profile_rasi_name,
                            "star_name": profile_star_name,
                            "lagnam": lagnam_didi_name,
                            "nallikai": profile_details[0]['nalikai'],
                            "didi": profile_details[0]['didi'],
                            "surya_gothram": profile_details[0]['suya_gothram'],
                            "dasa_name": get_dasa_name(profile_details[0]['dasa_name']),
                            "dasa_balance": dasa_format_date(profile_details[0]['dasa_balance']),
                            "chevvai_dosham": dosham_value_formatter(profile_details[0]['chevvai_dosaham']),
                            "sarpadosham":  dosham_value_formatter(profile_details[0]['ragu_dosham']),
                            "madulamn": profile_details[0]['madulamn'],                           
                            # "rasi_kattam":profile_details[0]['rasi_kattam'],
                            # "amsa_kattam":profile_details[0]['amsa_kattam'],
                        }
                        # "contact_details": {
                        #     "address": profile_details[0]['Profile_address'],
                        #     "city": get_city_name(profile_details[0]['Profile_city']),
                        #     "district": get_district_name(profile_details[0]['Profile_district']),
                        #     "state": get_state_name(profile_details[0]['Profile_state']),
                        #     "country": get_country_name(profile_details[0]['Profile_country']),                           
                        #     "phone": profile_details[0]['Mobile_no'],
                        #     "mobile": profile_details[0]['Mobile_no'],
                        #     "whatsapp": profile_details[0]['Profile_whatsapp'],
                        #     "email": profile_details[0]['EmailId'],
                        # }
                    }
                
                     # Conditionally add horoscope_details if allowed
                if permission_horosocpegrid_details != 0:  # Replace with your actual condition
                        profile_data["horoscope_details"].update({
                            "rasi_kattam": profile_details[0]['rasi_kattam'],
                            "amsa_kattam": profile_details[0]['amsa_kattam'],
                        })

                    # Conditionally add contact_details if allowed
                if permission_contact_details != 0:  # Replace with your actual condition
                        profile_data["contact_details"] = {
                            "address": profile_details[0]['Profile_address'],
                            "city": get_city_name(profile_details[0]['Profile_city']),
                            "district": get_district_name(profile_details[0]['Profile_district']),
                            "state": get_state_name(profile_details[0]['Profile_state']),
                            "country": get_country_name(profile_details[0]['Profile_country']),                           
                            "phone": profile_details[0]['Profile_alternate_mobile'],
                            "mobile": profile_details[0]['Mobile_no'],
                            "whatsapp": profile_details[0]['Profile_whatsapp'],
                            "email": profile_details[0]['EmailId'],
                        }

                profile_details_response = profile_data

            
                return JsonResponse(profile_details_response, safe=False, status=status.HTTP_200_OK)

       else:
            return JsonResponse({'status': 'failure', 'message': 'Limit Reached to view the profile'}, status=status.HTTP_201_CREATED)
    
      return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class Get_profile_det_match(APIView):
    # Cache settings (seconds)
    PROFILE_CACHE_TTL = 60
    PERMISSION_CACHE_TTL = 300
    
    @lru_cache(maxsize=128)
    def _get_cached_permission(self, profile_id, permission_type):
        """Cached permission check with fallback to DB"""
        cache_key = f"perm_{profile_id}_{permission_type}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        result = get_permission_limits(profile_id, permission_type)
        cache.set(cache_key, result, self.PERMISSION_CACHE_TTL)
        return result

    def _get_cached_profile(self, profile_id):
        """Fetch profile with optimized queries and caching"""
        cache_key = f"profile_full_{profile_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        # Optimized query with prefetching
        profile = get_profile_details([profile_id])
        if not profile:
            return None
            
        cache.set(cache_key, profile[0], self.PROFILE_CACHE_TTL)
        return profile[0]

    def post(self, request):
        
        from_profile = get_object_or_404(models.Registration1, ProfileId=request.data['profile_id'])
        to_profile = get_object_or_404(models.Registration1, ProfileId=request.data['user_profile_id'])
 
        if from_profile.Gender == to_profile.Gender:
            return JsonResponse(
            {'status': 'failure', 'message': 'Cant view the same Gender Profile'},
            status=status.HTTP_201_CREATED
        )


        if from_profile.Status==0:
            return JsonResponse(
            {'status': 'failure', 'message': 'Your Profile is not activated Yet'},
            status=status.HTTP_201_CREATED
        )
 
 
        start_time = time.time()
        
        # 1. Initial Validation
        serializer = serializers.GetproflistSerializer_details(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile_id = request.data['profile_id']
        user_profile_id = request.data['user_profile_id']
        page_id = request.data.get('page_id', '1')

        # 2. Check View Limits
        if not (can_get_viewd_profile_count(profile_id, user_profile_id) or 
            (page_id and int(page_id) != 1)):
            return JsonResponse(
                {'status': 'failure', 'message': 'Limit Reached to view the profile'}, 
                status=status.HTTP_201_CREATED
            )

        # 3. Get Profiles with Caching
        my_profile = self._get_cached_profile(profile_id)
        user_profile = self._get_cached_profile(user_profile_id)
        
        if user_profile['pstatus']==4:
            # print('profile Deleted')
            return JsonResponse(
                {'status': 'failure', 'message': 'The Profile is Deleted'},
                status=status.HTTP_200_OK
            )
        
        if not my_profile or not user_profile:
            return JsonResponse(
                {'status': 'failure', 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        

        # 4. Get Permissions
        permissions = {
            'photo_viewing': self._get_cached_permission(profile_id, 'photo_viewing'),
            'vys_assist': self._get_cached_permission(profile_id, 'vys_assist'),
            'contact_details': self._get_cached_permission(profile_id, 'contact_details'),
            'horoscope_grid': self._get_cached_permission(profile_id, 'horoscope_grid_details'),
            'eng_print': self._get_cached_permission(profile_id, 'eng_print')
        }

        # 5. Prepare Response Data (Maintaining Original Structure)
        response_data = {
            "basic_details": self._prepare_basic_details_full(my_profile, user_profile, permissions),
            "photo_protection": user_profile['Photo_protection'],
            "photo_request": self._get_photo_request_status(user_profile),
            "user_images": self._get_profile_images(
                user_profile['ProfileId'],
                my_profile['Gender'],
                permissions['photo_viewing'],
                user_profile['Photo_protection']
            ) if permissions['photo_viewing'] else {},
            "personal_details": self._prepare_personal_details_full(user_profile),
            "education_details": self._prepare_education_details_full(user_profile),
            "family_details": self._prepare_family_details_full(user_profile),
            "horoscope_details": self._prepare_horoscope_details_full(user_profile, permissions['horoscope_grid'])
        }

        # 6. Add Contact Details if Permitted
        if permissions['contact_details']:
            response_data["contact_details"] = self._prepare_contact_details_full(user_profile)

        logger.info(f"Profile API executed in {time.time() - start_time:.2f}s")
        return JsonResponse(response_data, status=status.HTTP_200_OK)

    # Full Detail Preparation Helpers (Maintaining Original Structure)
    def _prepare_basic_details_full(self, my_profile, user_profile, permissions):
        """Maintains all original basic_details fields"""
        return {
            "profile_id": user_profile['ProfileId'],
            "profile_name": user_profile['Profile_name'],
            "age": calculate_age(user_profile['Profile_dob']),
            "weight": user_profile.get('weight', '0'),
            "height": user_profile['Profile_height'],
            "star": user_profile['star_name'],
            "profession": self._get_profession_name(user_profile.get('profession')),
            "education": f"{self._get_education_level(user_profile.get('highest_education'))} {self._get_field_of_study(user_profile.get('field_ofstudy'))}".strip(),
            "degeree":self._get_degree_name(user_profile.get('degree'),user_profile.get('other_degree')),
            "about": user_profile.get('about_self', ''),
            "gothram": user_profile.get('suya_gothram', ''),
            "horoscope_available": 1 if user_profile.get('horoscope_file_admin') and permissions['eng_print'] else 0,
            "horoscope_available_text": "Horoscope Available" if user_profile.get('horoscope_file_admin') and permissions['eng_print'] else "Not available",
            "horoscope_link": f"{settings.MEDIA_URL}{user_profile['horoscope_file_admin']}" if user_profile.get('horoscope_file_admin') and permissions['eng_print'] else '',
            "user_status": self._get_user_status(user_profile['Last_login_date']),
            "verified": user_profile['Profile_verified'],
            "last_visit": self._format_last_visit(user_profile['Last_login_date']),
            "user_profile_views": count_records(models.Profile_visitors, {'status': 1, 'viewed_profile': user_profile['ProfileId']}),
            "wish_list": Get_wishlist(my_profile['ProfileId'], user_profile['ProfileId']),
            "express_int": Get_expressstatus(my_profile['ProfileId'], user_profile['ProfileId']),
            "personal_notes": Get_personalnotes_value(my_profile['ProfileId'], user_profile['ProfileId']),
            "matching_score": get_matching_score_util(
                my_profile['birthstar_name'],
                my_profile['birth_rasi_name'],
                user_profile['birthstar_name'],
                user_profile['birth_rasi_name'],
                my_profile['Gender']
            ),
            "plan_subscribed": 1 if my_profile['Plan_id'] and models.PlanDetails.objects.filter(id=my_profile['Plan_id']).exists() else 0,
            "vysy_assist_enable": permissions['vys_assist'],
            "vys_assits": self._has_vysya_assist(my_profile['ProfileId'], user_profile['ProfileId']),
            "vys_list": self._get_vysya_assist_data(my_profile['ProfileId'], user_profile['ProfileId'])
        }

    def _prepare_personal_details_full(self, profile_data):
        """Maintains all original personal_details fields"""
        return {
            "profile_name": profile_data['Profile_name'],
            "gender": profile_data['Gender'],
            "age": calculate_age(profile_data['Profile_dob']),
            "dob": format_date_of_birth(profile_data['Profile_dob']),
            "place_of_birth": profile_data.get('place_of_birth', ''),
            "time_of_birth": format_time_am_pm(profile_data.get('time_of_birth', '')),
            "height": profile_data['Profile_height'],
            "marital_status": self._get_marital_status(profile_data.get('Profile_marital_status')),
            "blood_group": profile_data.get('blood_group', ''),
            "about_self": profile_data.get('about_self', ''),
            "complexion": self._get_complexion(profile_data.get('Profile_complexion')),
            "hobbies": profile_data.get('hobbies', ''),
            "physical_status": "No" if profile_data.get('Pysically_changed', 0) == 0 
                          else "1" if profile_data.get('Pysically_changed', 0) == 1 
                          else profile_data.get('Pysically_changed', 0),
            "eye_wear": profile_data.get('eye_wear', '0'),
            "weight": profile_data.get('weight', '0'),
            "body_type": profile_data.get('body_type', ''),
            "profile_created_by": self._get_profile_creator(profile_data.get('Profile_for'))
        }

    def _prepare_education_details_full(self, profile_data):
        """Maintains all original education_details fields"""
        return {
            "education_level": f"{self._get_education_level(profile_data.get('highest_education'))} {self._get_field_of_study(profile_data.get('field_ofstudy'))}".strip(),
            "education_detail": " ",
            "ug_degeree": get_degree(profile_data.get('ug_degeree', '')),
            "about_education": profile_data.get('about_edu', ''),
            "profession": self._get_profession_name(profile_data.get('profession')),
            "degeree":self._get_degree_name(profile_data.get('degree'),profile_data.get('other_degree')),
            "designation": profile_data.get('designation', ''),
            "company_name": profile_data.get('company_name', ''),
            "business_name": profile_data.get('business_name', ''),
            "business_address": profile_data.get('business_address', ''),
            "annual_income": self._get_annual_income(profile_data.get('anual_income')),
            "gross_annual_income": profile_data.get('actual_income', ''),
            "place_of_stay": get_place_of_work(profile_data)
        }

    def _prepare_family_details_full(self, profile_data):
        """Maintains all original family_details fields"""
        return {
            "about_family": profile_data.get('about_family', ''),
            "father_name": profile_data.get('father_name', ''),
            "father_occupation": profile_data.get('father_occupation', ''),
            "mother_name": profile_data.get('mother_name', ''),
            "mother_occupation": profile_data.get('mother_occupation', ''),
            "family_status": self._get_family_status(profile_data.get('family_status')),
            "no_of_sisters": profile_data.get('no_of_sister', '0'),
            "no_of_brothers": profile_data.get('no_of_brother', '0'),
            "no_of_sis_married": profile_data.get('no_of_sis_married', '0'),
            "no_of_bro_married": profile_data.get('no_of_bro_married', '0'),
            "property_details": profile_data.get('property_details', ''),
            "father_alive": profile_data.get('father_alive'),
            "mother_alive": profile_data.get('mother_alive'),
        }

    def _prepare_horoscope_details_full(self, profile_data, horoscope_permission):
        """Maintains all original horoscope_details fields"""
        details = {
            "rasi": self._get_rasi_name(profile_data.get('birth_rasi_name')),
            "star_name": self._get_star_name(profile_data.get('birthstar_name')),
            "lagnam": self._get_lagnam_didi(profile_data.get('lagnam_didi')),
            "nallikai": profile_data.get('nalikai', ''),
            "didi": profile_data.get('didi', ''),
            "surya_gothram": profile_data.get('suya_gothram', ''),
            "dasa_name": get_dasa_name(profile_data.get('dasa_name', '')),
            "dasa_balance": dasa_format_date(profile_data.get('dasa_balance', '')),
            "chevvai_dosham": self._format_dosham_value(profile_data.get('chevvai_dosaham', 0)),
            "sarpadosham": self._format_dosham_value(profile_data.get('ragu_dosham', 0)),
            "madulamn": profile_data.get('madulamn', '')
        }
        
        if horoscope_permission:
            details.update({
                "rasi_kattam": profile_data.get('rasi_kattam', ''),
                "amsa_kattam": profile_data.get('amsa_kattam', '')
            })
        
        return details



    def _has_vysya_assist(self, profile_from, profile_to):
        """Check if Vysya assist exists with caching"""
        cache_key = f"vys_exists_{profile_from}_{profile_to}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        exists = models.Profile_vysassist.objects.filter(
            profile_from=profile_from,
            profile_to=profile_to
        ).exists()
        cache.set(cache_key, exists, 300)  # Cache for 5 minutes
        return exists

    def _get_vysya_assist_data(self, profile_from, profile_to):
        """Get Vysya assist data with caching"""
        cache_key = f"vys_data_{profile_from}_{profile_to}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            assist = models.Profile_vysassist.objects.filter(
                profile_from=profile_from,
                profile_to=profile_to
            ).prefetch_related(
                Prefetch('followups', 
                    queryset=models.ProfileVysAssistFollowup.objects
                        .order_by('-update_at')[:5]
                )
            ).first()

            if not assist:
                return None

            followups = assist.followups.all()
            data = serializers.ProfileVysAssistFollowupSerializer(
                followups, many=True
            ).data if followups else [{
                "comments": f"{assist.to_message} (Request sent)",
                "update_at": assist.req_datetime
            }]
            
            cache.set(cache_key, data, 300)  # Cache for 5 minutes
            return data
        except Exception as e:
            logger.error(f"Vysya assist error: {str(e)}")
            return None




    def _prepare_contact_details_full(self, profile_data):
        """Maintains all original contact_details fields"""
        return {
            "address": profile_data.get('Profile_address', ''),
            "city": get_city_name(profile_data.get('Profile_city')),
            "district": get_district_name(profile_data.get('Profile_district')),
            "state": get_state_name(profile_data.get('Profile_state')),
            "country": get_country_name(profile_data.get('Profile_country')),
            "phone": profile_data.get('Profile_alternate_mobile', ''),
            "mobile": profile_data.get('Mobile_no', ''),
            "whatsapp": profile_data.get('Profile_whatsapp', ''),
            "email": profile_data.get('EmailId', '')
        }
    
    def _get_profession_name(self, profession_id):
        """Get profession name with caching"""
        if not profession_id:
            return None
        cache_key = f"prof_{profession_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            profession = models.Profespref.objects.filter(
                RowId=profession_id
            ).values_list('profession', flat=True).first()
            cache.set(cache_key, profession, 3600)  # Cache for 1 hour
            return profession
        except Exception:
            return None
    
    def _get_degree_name(self, degree_ids, other_degree):

        # print('degree_ids',degree_ids)
        # print('other_degree',other_degree)
        """Get degree names with caching"""
        if not degree_ids:
            # If only other_degree is provided, return it directly
            return other_degree if other_degree else None

        # Make a consistent cache key
        cache_key = f"prof_{degree_ids}_{other_degree or ''}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            
            # Convert comma-separated IDs into list of integers
            id_list = [int(x) for x in str(degree_ids).split(',') if x.strip().isdigit()]
            id_list = [x for x in id_list if x != 86]

            # Fetch all degree names
            degree_names = list(
                models.Profileedu_degree.objects.filter(id__in=id_list)
                .values_list("degeree_name", flat=True)
            )

            print('degree_names',degree_names)
            


            # Append other_degree if provided
            if other_degree:
                degree_names.append(other_degree)

            
            print('appended other_degree',degree_names)

            # Join into comma-separated string
            final_names = ", ".join(degree_names) if degree_names else None

            # Cache result
            cache.set(cache_key, final_names, 3600)  # Cache for 1 hour
            return final_names

        except Exception:
            return None

    

    def _get_education_level(self, education_id):
        """Get education level with caching"""
        if not education_id:
            return ''
        cache_key = f"edu_{education_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            education = models.Edupref.objects.filter(
                RowId=education_id
            ).values_list('EducationLevel', flat=True).first() or ''
            cache.set(cache_key, education, 3600)
            return education
        except Exception:
            return ''

    def _get_field_of_study(self, field_id):
        """Get field of study with caching"""
        if not field_id:
            return ''
        cache_key = f"field_{field_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            field = models.Profilefieldstudy.objects.filter(
                id=field_id
            ).values_list('field_of_study', flat=True).first() or ''
            cache.set(cache_key, field, 3600)
            return field
        except Exception:
            return ''

    def _get_user_status(self, last_login):
        """Determine user activity status with caching"""
        if not last_login or last_login == '0000-00-00 00:00:00':
            return "Newly registered"
        
        cache_key = f"status_{last_login}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            one_month_ago = timezone.now() - timedelta(days=30)
            status = "Active User" if last_login > one_month_ago else "In Active User"
            cache.set(cache_key, status, 3600)
            return status
        except Exception:
            return "Newly registered"

    def _format_last_visit(self, last_login):
        """Format last visit date with caching"""
        if not last_login or last_login == '0000-00-00 00:00:00':
            return ''
        
        cache_key = f"lastvisit_{last_login}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            formatted = last_login.strftime("(%B %d, %Y)")
            cache.set(cache_key, formatted, 3600)
            return formatted
        except Exception:
            return ''

    def dosham_value_formatter(self,value):
            if isinstance(value, str):
                        return {"0": "Unknown", "1": "Yes", "2": "No"}.get(value, value)
            elif isinstance(value, int):
                        return {0: "Unknown", 1: "Yes", 2: "No"}.get(value, value)
            return value
    
    def _prepare_vysya_assist(self, profile_from, profile_to):
        """Optimized Vysya assist data loading"""
        try:
            assist = models.Profile_vysassist.objects.filter(
                profile_from=profile_from,
                profile_to=profile_to
            ).prefetch_related(
                Prefetch('followups', 
                    queryset=models.ProfileVysAssistFollowup.objects
                        .order_by('-update_at')[:5]  # Limit to 5 most recent
                )
            ).first()

            if not assist:
                return {'vys_assits': False}

            followups = assist.followups.all()
            return {
                'vys_assits': True,
                'vys_list': serializers.ProfileVysAssistFollowupSerializer(
                    followups, many=True
                ).data if followups else [{
                    "comments": f"{assist.to_message} (Request sent)",
                    "update_at": assist.req_datetime
                }]
            }
        except Exception as e:
            logger.error(f"Vysya assist error: {str(e)}")
            return {'vys_assits': False}

    def _get_photo_request_status(self, profile):
        """Efficient photo request check"""
        if profile['Photo_protection'] == 1:
            return 1
        return 1 if not models.Image_Upload.objects.filter(
            profile_id=profile['ProfileId']
        ).exists() else 0
    def _get_profile_images(self, profile_id, gender, photo_viewing_permission, photo_protection):
        """Get profile images with appropriate protection settings"""
        if photo_viewing_permission == 1:
            return get_profile_image_azure_optimized(profile_id, gender, 'all', photo_protection)
        return get_profile_image_azure_optimized(profile_id, gender, 'all', 1)
    
    def _get_marital_status(self, status_id):
        """Get marital status with caching"""
        if not status_id:
            return None
        
        cache_key = f"marital_{status_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            status = models.ProfileMaritalstatus.objects.filter(
                StatusId=status_id
            ).values_list('MaritalStatus', flat=True).first()
            cache.set(cache_key, status, 86400)  # Cache for 24 hours
            return status
        except Exception:
            return None

    def _get_complexion(self, complexion_id):
        """Get complexion description with caching"""
        if not complexion_id:
            return None
        
        cache_key = f"complexion_{complexion_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            complexion = models.Profilecomplexion.objects.filter(
                complexion_id=complexion_id
            ).values_list('complexion_desc', flat=True).first()
            cache.set(cache_key, complexion, 86400)  # Cache for 24 hours
            return complexion
        except Exception:
            return None

    def _get_profile_creator(self, creator_type):
        """Get profile creator type with caching"""
        if not creator_type:
            return None
        
        cache_key = f"creator_{creator_type}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            creator = models.Profileholder.objects.filter(
                Mode=creator_type
            ).values_list('ModeName', flat=True).first()
            cache.set(cache_key, creator, 86400)  # Cache for 24 hours
            return creator
        except Exception:
            return None
    
    def _get_annual_income(self, income_id):
        """Get formatted annual income with caching"""
        if not income_id:
            return ''
        
        cache_key = f"income_{income_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            income = models.Annualincome.objects.filter(
                id=income_id
            ).values_list('income', flat=True).first() or ''
            cache.set(cache_key, income, 86400)  # Cache for 24 hours
            return income
        except Exception:
            return ''

    def _get_family_status(self, status_id):
        """Get family status description with caching"""
        if not status_id:
            return None
        
        cache_key = f"family_status_{status_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            status = models.Familystatus.objects.filter(
                id=status_id
            ).values_list('status', flat=True).first()
            cache.set(cache_key, status, 86400)  # Cache for 24 hours
            return status
        except Exception:
            return None

    def _get_rasi_name(self, rasi_id):
        """Get rasi name with caching"""
        if not rasi_id:
            return None
        
        cache_key = f"rasi_{rasi_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            rasi = models.Rasi.objects.filter(
                id=rasi_id
            ).values_list('name', flat=True).first()
            cache.set(cache_key, rasi, 86400)  # Cache for 24 hours
            return rasi
        except Exception:
            return None

    def _get_star_name(self, star_id):
        """Get birth star name with caching"""
        if not star_id:
            return None
        
        cache_key = f"star_{star_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            star = models.Birthstar.objects.filter(
                id=star_id
            ).values_list('star', flat=True).first()
            cache.set(cache_key, star, 86400)  # Cache for 24 hours
            return star
        except Exception:
            return None

    def _get_lagnam_didi(self, didi_id):
        """Get lagnam didi name with caching"""
        if not didi_id:
            return None
        
        cache_key = f"didi_{didi_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            didi = models.Lagnamdidi.objects.filter(
                id=didi_id
            ).values_list('name', flat=True).first()
            cache.set(cache_key, didi, 86400)  # Cache for 24 hours
            return didi
        except Exception:
            return None

    def _format_dosham_value(self, value):
        """
        Format dosham values consistently
        Converts both string and integer inputs to standardized text
        """
        if value is None:
            return "Unknown"
        
        if isinstance(value, str):
            return {
                "0": "Unknown",
                "1": "Yes", 
                "2": "No"
            }.get(value.strip(), value)
        
        if isinstance(value, int):
            return {
                0: "Unknown",
                1: "Yes",
                2: "No"
            }.get(value, str(value))
        
        return str(value)



def get_place_of_work(profile_details):
        profile = profile_details

        parts = []

        country = get_country_name(profile.get('work_country'))
        if country:
            parts.append(country)

        state = get_state_name(profile.get('work_state'))
        if state:
            parts.append(state)

        district = get_district_name(profile.get('work_district'))
        if district:
            parts.append(district)

        city = get_city_name(profile.get('work_city'))
        if city:
            parts.append(city)

        return " / ".join(parts) if parts else None


def format_date_of_birth(Profile_dob):
        if Profile_dob:
            try:
                return Profile_dob.strftime("%d-%m-%Y")
            except AttributeError:
                return None  # In case dob is not a valid date object
        return None




class UploadImagesView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profile_id = request.data.get('profile_id')
        zip_file = request.FILES.get('zip_file')
        image_files = request.FILES.getlist('image_files')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'Profile ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not image_files:
            return JsonResponse({'status': 'failure', 'message': 'image_files required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate profile existence

        try:
            profile =  models.Registration1.objects.get(ProfileId=profile_id)
        except models.Registration1.DoesNotExist:
            return JsonResponse({'status': 'failure', 'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create directory for the profile if it doesn't exist
        profile_dir = os.path.join(settings.MEDIA_ROOT, f'profile_{profile_id}')
        os.makedirs(profile_dir, exist_ok=True)

        # Process the ZIP file if provided
        if zip_file:
            try:
                with zipfile.ZipFile(zip_file) as z:
                    for file in z.namelist():
                        if file.endswith(('jpg', 'jpeg', 'png')):
                            with z.open(file) as img_file:
                                img = Image.open(BytesIO(img_file.read()))
                                # file_path = self.resize_and_save_image(img, profile_dir, file, watermark_text="vysyamala.com")
                                # models.Image_Upload.objects.create(profile=profile, image=file_path)
            except zipfile.BadZipFile:
                return JsonResponse({'status': 'failure', 'message': 'Invalid zip file.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process individual image files if provided
        for image_file in image_files:
            if image_file.name.endswith(('jpg', 'jpeg', 'png')):
                img = Image.open(image_file)
                file_path = self.resize_and_save_image(img, profile_dir, image_file.name)
                JsonResponse.objects.create(profile=profile, image=file_path)

                print('file_path',file_path)


        return JsonResponse({'status': 'success', 'message': 'Images uploaded and resized successfully.'}, status=status.HTTP_201_CREATED)

    # def resize_and_save_image(self, img, profile_dir, file_name, watermark_text):
    #     # Get the actual file size in bytes
    #     img_byte_array = BytesIO()
    #     img.save(img_byte_array, format=img.format)
    #     img_size = img_byte_array.tell()

    #     # Check if image size exceeds 10MB
    #     if img_size > (10 * 1024 * 1024):
    #         # Resize the image
    #         img.thumbnail((img.width // 2, img.height // 2), Image.ANTIALIAS)
    #     font_path = os.path.join(settings.BASE_DIR, 'fonts', 'timesnewarial.ttf')
    #     font_size = 175
    #     watermark_font = ImageFont.truetype(font_path, font_size)
    #     # Add watermark to the image diagonally
    #     #watermark_font = ImageFont.load_default()  # Default font for watermark
    #     draw = ImageDraw.Draw(img)
    #     watermark_position = (50, img.height - 530)  # Adjust position as needed
    #     draw.text(watermark_position, watermark_text, fill='black', font=watermark_font)

    #     img_path = os.path.join(profile_dir, file_name)
    #     img.save(img_path)
    #     return img_path

    #   def resize_and_save_image(self, img, profile_dir, file_name, logo_path=None):
    #         """
    #         Resizes the image if it exceeds 10MB and overlays a logo watermark.
    #         """
    #         if not logo_path:
    #             logo_path = os.path.join(settings.BASE_DIR, 'vysya_color_logo.png')  # Path to logo

    #         # Get the actual file size in bytes
    #         img_byte_array = BytesIO()
    #         img.save(img_byte_array, format=img.format)
    #         img_size = img_byte_array.tell()

    #         # Resize the image if size exceeds 10MB
    #         if img_size > (10 * 1024 * 1024):  # 10 MB
    #             img.thumbnail((img.width // 2, img.height // 2), Image.Resampling.LANCZOS)

    #         # Add logo watermark
    #         try:
    #             with Image.open(logo_path) as logo:
    #                 # Resize the logo
    #                 logo_width, logo_height = 200, 200
    #                 logo.thumbnail((logo_width, logo_height), Image.Resampling.LANCZOS)

    #                 # Ensure transparency
    #                 logo = logo.convert("RGBA")

    #                 # Position the logo (bottom-right corner)
    #                 img_width, img_height = img.size
    #                 position = (img_width - logo_width - 20, img_height - logo_height - 20)

    #                 # Paste the logo
    #                 img.paste(logo, position, logo)
    #         except Exception as e:
    #             print(f"Error adding logo watermark: {e}")

    #         # Save the final image
    #         img_path = os.path.join(profile_dir, file_name)
    #         img.save(img_path, format="PNG", quality=95)

    #         return img_path



class ListProfileImagesView(APIView):

 def post(self, request, *args, **kwargs):
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'Profile ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate profile existence
        try:
            #profile =  models.Registration1.objects.get(profile_id=profile_id)
            profile = models.Registration1.objects.get(ProfileId=profile_id)
        except models.Registration1.DoesNotExist:
            return JsonResponse({'status': 'failure', 'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all images related to the profile
        profile_images =  models.Image_Upload.objects.filter(profile_id=profile_id,image_approved=1,is_deleted=0)
        media_root_len = len(settings.MEDIA_ROOT)
        
        # Define the URL prefix
        url_prefix = settings.MEDIA_URL
        
        # Update the list comprehension to include the URL prefix
        image_urls = [url_prefix + image.image.path[media_root_len:].lstrip('/') for image in profile_images]
        
        return JsonResponse({'status': 'success', 'images': image_urls}, status=status.HTTP_200_OK)
 


 #photo request module code

class Send_photo_request(APIView):
    def post(self, request):
        serializer = serializers.PhotorequestSerializer(data=request.data)

        print('serializer',serializer)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')


            get_access=can_send_photoreq(profile_from)

            if get_access is True: 

                # print('profile_from',profile_from)
                # print('profile_to',profile_to)
                
                # Check if an entry with the same profile_from and profile_to already exists
                existing_entry = models.Photo_request.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
                
                if existing_entry:
                    # Update the status to 0 if the entry already exists
                    #existing_entry.status = 0
                    existing_entry.status = int_status
                    existing_entry.req_datetime = timezone.now()
                    existing_entry.save()
                                                
                    
                    return JsonResponse({"Status": 0, "message": "Photo interests updated"}, status=status.HTTP_200_OK)
                
                
                else:
                    # Create a new entry with status 1
                    serializer.save(status=1)
                    
                    models.Profile_notification.objects.create(
                        profile_id=profile_to,
                        from_profile_id=profile_from,
                        notification_type='photo_request',
                        to_message='You received a photo request from profile ID '+profile_from,
                        is_read=0,
                        created_at=timezone.now()
                    )

                    return JsonResponse({"Status": 1, "message": "Photo interests sent successfully"}, status=status.HTTP_200_OK)
            
            else:
                return JsonResponse({"Status": 0, "message": "Get full access - upgrade your package today!"}, status=status.HTTP_200_OK)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class Get_photo_request_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:
                
                all_profiles = models.Photo_request.objects.filter(profile_to=profile_id,status__in=[1, 2, 3])
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_from', flat=True))}

                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page
                
                
                fetch_data = models.Photo_request.objects.filter(profile_to=profile_id,status__in=[1, 2, 3])[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_from', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender

                    my_status=profile_data.Status

                    # print('fetch_data',fetch_data)
                    # print('profile_ids',profile_ids)

                    # print('profile_details length',len(profile_details))
                    # print('profile_details',(profile_details))

                    
                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status !=0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)
                    
                    restricted_profile_details = [
                        {
                            "req_profileid": detail.get("ProfileId"),
                            "req_profile_name": detail.get("Profile_name"),
                            #"req_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            # "req_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "req_Profile_img": image_function(detail),
                            "req_profile_age": calculate_age(detail.get("Profile_dob")),
                            "response_message": fetch_data[index].response_message,
                            "req_status": fetch_data[index].status,
                            "req_verified":detail.get('Profile_verified'),
                            "req_height":detail.get("Profile_height"),
                            "req_star":detail.get("star_name"),
                            "req_profession":getprofession(detail.get("profession")),
                            "req_city":detail.get("Profile_city"),
                            "req_degree":get_degree(detail.get("ug_degeree")),
                            "req_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "req_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "req_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "req_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "req_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "req_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                        }
                        # for detail in profile_details
                        for index, detail in enumerate(profile_details)
                    ]

                    #print('fetch_data',fetch_data)
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched Photo request and profile details successfully", "data": combined_data, "photoreq_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No photo request found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Photo_request.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No photo request found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class Update_photo_request(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')

        # Initialize serializer with the incoming data
        serializer = serializers.Update_PhotorequestSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_from')
            profile_to = serializer.validated_data.get('profile_id')
            #status = serializer.validated_data.get('status')

            try:
                # Get the instance to be updated
                instance = models.Photo_request.objects.get(profile_from=profile_from, profile_to=profile_to)
            except models.Photo_request.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Photo request entry not found"}, status=status.HTTP_200_OK)
            
            # Update the instance using the serializer's update method
            serializer.update(instance, serializer.validated_data)

            return JsonResponse({"Status": 1, "message": "Photo request updated successfully"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        

class Get_notification_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:

                now = timezone.now()

                # Calculate the date 30 days ago
                last_60_days = now - timedelta(days=60)

                all_profiles = models.Profile_notification.objects.filter(profile_id=profile_id, created_at__gte=last_60_days)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_id', flat=True))}

                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page

                notify_count=models.Profile_notification.objects.filter(profile_id=profile_id, is_read=0).count()

                notification_list=models.Profile_notification.objects.filter(profile_id=profile_id, created_at__gte=last_60_days).order_by('-id')[start:end]

                notifications_data = [
                    {
                        "id": notification.id,
                        "notify_img": 'https://vysyamala.com/images/heading_icon.png',
                        "profile_image": Get_image_profile(notification.from_profile_id),
                        "from_profile_id": notification.from_profile_id,
                        "notify_profile_name": notification.from_profile_id,
                        "message_titile":notification.message_titile,
                        "notification_type": notification.notification_type,
                        "to_message": notification.to_message,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at,
                        "time_ago": time_ago(notification.created_at),
                        
                    }
                    for notification in notification_list
                ]
                if notifications_data:
                    return JsonResponse({
                        "Status": 1,
                        "message": "Fetched notification lists successfully",
                        "notifiy_count":notify_count,
                        "data": notifications_data,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({
                        "Status": 0,
                        "message": "No notifications found",
                        "data": []
                    }, status=status.HTTP_200_OK)



            except models.Profile_notification.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Fetched notofication lists successfully","data":notifications_data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class Read_notifications(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')

        # Initialize serializer with the incoming data
        serializer = serializers.ReadNotificationSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
           
            try:
                # Perform a bulk update on all notifications for the given profile_id
                updated_count = models.Profile_notification.objects.filter(profile_id=profile_id, is_read=0).update(is_read=1)

                if updated_count > 0:
                    return JsonResponse({"Status": 1, "message": f"{updated_count} notifications updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No unread notifications found"}, status=status.HTTP_200_OK)

            except Exception as e:
                return JsonResponse({"Status": 0, "message": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class User_change_password(APIView):
    
    def post(self, request):
        
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['ProfileId']
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            #print('old_password',make_password(old_password))

            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)
                
                # if not check_password(old_password,user.Password):
                if old_password != user.Password:

                
                    return JsonResponse({"status": "error", "message": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)

                # user.Password = make_password(new_password)
                user.Password = new_password
                user.save()
                return JsonResponse({"status": "success", "message": "Password updated successfully"})
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Customize the error response format
        errors = serializer.errors
        custom_errors = {field: ", ".join(error_messages) for field, error_messages in errors.items()}
        return JsonResponse(custom_errors, status=status.HTTP_400_BAD_REQUEST)
    


def time_ago(created_at):
    now = timezone.now()
    diff = now - created_at

    if diff.days == 0:
        if diff.seconds < 60:
            return "just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds // 3600} hours ago"
    elif diff.days == 1:
        return "1 day ago"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        return f"{diff.days // 7} weeks ago"
    elif diff.days < 365:
        return f"{diff.days // 30} months ago"
    else:
        return f"{diff.days // 365} years ago"
    


class ImageSetEdit(APIView):
    def post(self, request, *args, **kwargs):
        profile_id = request.data.get('profile_id')
        replace_image_ids = request.data.getlist('replace_image_ids')
        replace_files = request.FILES.getlist('replace_image_files')
        new_files = request.FILES.getlist('new_image_files')
        image_objects = []

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that either replace_files or new_files is provided
        if not replace_files and not new_files:
            return JsonResponse({"error": "Either replace_images or new_images must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # If replace_files is provided, replace_image_ids must be provided and match in count
        if replace_files and not replace_image_ids:
            return JsonResponse({"error": "replace_image_ids is required when replace_images is provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(replace_image_ids) != len(replace_files):
            return JsonResponse({"error": "Mismatch between replace_image_ids and replace_files."}, status=status.HTTP_400_BAD_REQUEST)

        # Get current number of images for the profile
        current_image_count = models.Image_Upload.objects.filter(profile_id=profile_id).count()

        # Check if the total number of images exceeds the limit
        if current_image_count - len(replace_image_ids) + len(new_files) > 10:
            return JsonResponse({"error": "Upload limit exceeded. You can only have a maximum of 10 images."}, status=status.HTTP_400_BAD_REQUEST)

        # def process_and_save_image(file, image_instance=None):
        #     valid_extensions = ['png', 'jpeg', 'jpg']
        #     file_extension = os.path.splitext(file.name)[1][1:].lower()
        #     if file_extension not in valid_extensions:
        #         return JsonResponse({"error": "Invalid file type. Accepted formats are: png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)
            
        #     # Image processing (resize, watermark, etc.)
        #     img = PILImage.open(file)
        #     img = img.resize((201, 200))  # Resize the main image

        #     # Load watermark logo
        #     logo_path = os.path.join('vysya_color_logo.png')  # Path to your watermark logo
        #     try:
        #         watermark_logo = PILImage.open(logo_path).convert("RGBA")
        #     except FileNotFoundError:
        #         return JsonResponse({"error": "Watermark logo file not found."}, status=status.HTTP_400_BAD_REQUEST)

        #     # Resize watermark logo proportionally (e.g., 1/4 of the main image size)
        #     #logo_size = (img.width // 4, img.height // 4)
        #     logo_size = (68, 18)
        #     watermark_logo = watermark_logo.resize(logo_size, PILImage.LANCZOS)

        #     # Position the logo (e.g., bottom-right corner)
        #     #position = (img.width - logo_size[0] - 10, img.height - logo_size[1] - 10)  # 10px padding

        #     position = (img.width - logo_size[0] - 10, 10)

        #     # Overlay the watermark logo
        #     img = img.convert("RGBA")
        #     watermarked = PILImage.new("RGBA", img.size, (255, 255, 255, 0))
        #     watermarked.paste(img, (0, 0), img)
        #     watermarked.paste(watermark_logo, position, watermark_logo)

        #     # Convert to RGB and save
        #     output = io.BytesIO()
        #     watermarked = watermarked.convert("RGB")
        #     watermarked.save(output, format='JPEG')
        #     output.seek(0)

        #     # Unlink (delete) the existing image if replacing
        #     if image_instance:
        #         if os.path.isfile(image_instance.image.path):
        #             os.remove(image_instance.image.path)
        #         image_instance.image.save(os.path.join(file.name), ContentFile(output.read()), save=True)
        #     else:
        #         image_instance = models.Image_Upload(profile_id=profile_id)
        #         image_instance.image.save(os.path.join(file.name), ContentFile(output.read()), save=True)
            
        #     image_objects.append(image_instance)

        def process_and_save_image(file, image_instance=None):
            valid_extensions = ['png', 'jpeg', 'jpg']
            file_extension = os.path.splitext(file.name)[1][1:].lower()
            if file_extension not in valid_extensions:
                return JsonResponse({"error": "Invalid file type. Accepted formats are: png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

            # Image processing (resize, watermark, etc.)
            img = PILImage.open(file)
            img = img.resize((201, 200))  # Resize the main image

            logo_path = 'vysya_color_logo.png'
            try:
                watermark_logo = PILImage.open(logo_path).convert("RGBA")
            except FileNotFoundError:
                return JsonResponse({"error": "Watermark logo file not found."}, status=status.HTTP_400_BAD_REQUEST)

            logo_size = (68, 18)
            watermark_logo = watermark_logo.resize(logo_size, PILImage.LANCZOS)
            position = (img.width - logo_size[0] - 10, 10)

            img = img.convert("RGBA")
            watermarked = PILImage.new("RGBA", img.size, (255, 255, 255, 0))
            watermarked.paste(img, (0, 0), img)
            watermarked.paste(watermark_logo, position, watermark_logo)

            output = io.BytesIO()
            watermarked.convert("RGB").save(output, format='JPEG')
            output.seek(0)

            if image_instance:
                # Delete the old file from Azure Storage
                if image_instance.image:
                    image_instance.image.delete(save=False)  # Use delete() method to remove the file safely

                # Save the new file
                image_instance.image.save(file.name, ContentFile(output.read()), save=True)
            else:
                image_instance = models.Image_Upload(profile_id=profile_id)
                image_instance.image.save(file.name, ContentFile(output.read()), save=True)

            image_objects.append(image_instance)


        # Process replacement images
        for idx, image_id in enumerate(replace_image_ids):
            image_instance = models.Image_Upload.objects.get(id=image_id, profile_id=profile_id)
            process_and_save_image(replace_files[idx], image_instance)

        # Process new images
        for file in new_files:
            process_and_save_image(file)
        
        serializer = serializers.ImageSerializer(image_objects, many=True)
        
        
        #update in notification table
        notification_titile='Profile Image'
        notification_message = " Profile Image "
        
        if notification_message:
                    # print('12345')
             #notify_related_profiles(profile_id,'Profile_update',notification_titile,notification_message)
             addto_notification_queue(profile_id,'Profile_update',notification_titile,notification_message)
        
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    


# class Remove_profile_img(APIView):
#     def delete_image(self, instance):
#         if instance.image:
#             image_path = instance.image.path
#             if os.path.exists(image_path):
#                 os.remove(image_path)
#             instance.image = None
#             instance.save()

#     def post(self, request, *args, **kwargs):
#         try:
#             # Get the profile_id from the POST data
#             profile_id = request.POST.get('profile_id')
#             image_id = request.POST.get('image_id')

#             # Ensure profile_id is provided
#             if not profile_id:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'profile_id is required.'
#                 }, status=400)
            
#             if not image_id:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'image_id is required.'
#                 }, status=400)

#             # Get the object by profile_id
#             instance = get_object_or_404(models.Image_Upload, profile_id=profile_id,id=image_id)

#             # Delete the image file and clear the database field
#             self.delete_image(instance)
#             instance.delete()
            
#             return JsonResponse({
#                 'success': 1,
#                 'message': 'Image deleted successfully.'                
#             },status=status.HTTP_200_OK)
#         except Exception as e:
#             return JsonResponse({
#                 'success': 0,
#                 'message': str(e)
#             }, status=status.HTTP_200_OK)

class Remove_profile_img(APIView):
    def delete_image(self, instance):
        if instance.image:
            try:
                # Delete the file from Azure Storage
                instance.image.delete(save=False)
            except Exception as e:
                raise Exception(f"Failed to delete image from Azure Storage: {str(e)}")

        # Remove the reference from the database
        instance.image = None
        instance.save()

    def post(self, request, *args, **kwargs):
        try:
            # Get the profile_id and image_id from the POST data
            profile_id = request.POST.get('profile_id')
            image_id = request.POST.get('image_id')

            if not profile_id:
                return JsonResponse({
                    'success': False,
                    'message': 'profile_id is required.'
                }, status=400)
            
            if not image_id:
                return JsonResponse({
                    'success': False,
                    'message': 'image_id is required.'
                }, status=400)

            # Fetch the image instance by profile_id and image_id
            instance = get_object_or_404(models.Image_Upload, profile_id=profile_id, id=image_id)

            # Delete the image from Azure Storage and clear the field in the database
            self.delete_image(instance)
            
            # Delete the instance from the database
            instance.delete()
            
            return JsonResponse({
                'success': 1,
                'message': 'Image deleted successfully.'                
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({
                'success': 0,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class Get_profile_images(APIView):
    def post(self, request, *args, **kwargs):
        
        profile_id = request.data.get('profile_id')
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():

            # Get images for the specified profile
            # images = models.Image_Upload.objects.filter(profile_id=profile_id,image_approved=1,is_deleted=0)

            images = models.Image_Upload.objects.filter(profile_id=profile_id)
            
            if not images.exists():
                return JsonResponse({"message": "No images found for this profile."}, status=status.HTTP_200_OK)

            image_serializer = serializers.ImageSerializer(images, many=True)
                # Convert the serialized data to a list of dictionaries
            image_data = image_serializer.data

                # Return a JSON response with status and data
            return JsonResponse({"Status": 1,"message": "Images details fetched successfully","data": image_data }, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class Set_photo_password(APIView):
    
    def post(self, request):
        
        
        photo_password = request.data.get('photo_password')
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'profile_id is filed is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not photo_password:
            return JsonResponse({'status': 'failure', 'message': 'photo_password field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializers.Profile_idValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            
            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)
                user.Photo_password = photo_password
                user.save()
                return JsonResponse({"status": "success", "message": "Photo Password updated successfully"},status=status.HTTP_200_OK)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Customize the error response format
        errors = serializer.errors
        custom_errors = {field: ", ".join(error_messages) for field, error_messages in errors.items()}
        return JsonResponse(custom_errors, status=status.HTTP_400_BAD_REQUEST)
    


class Get_photo_bypassword(APIView):
    
    def post(self, request):

        serializer = serializers.PhotobypasswordSerializer(data=request.data)
        #base_url='http://103.214.132.20:8000'
        base_url = settings.MEDIA_URL
        
        
        if serializer.is_valid():
            profile_to = serializer.validated_data['profile_to']

            get_entry = models.Image_Upload.objects.filter(profile_id=profile_to,image_approved=1,is_deleted=0)[:10]
            if get_entry.exists():
                # Serialize the single instance
                serializer = serializers.ImageGetSerializer(get_entry,many=True)
                # Return only the status
                images_dict = {
                    # str(index + 1): base_url + entry['image']
                    str(index + 1): entry['image']
                    for index, entry in enumerate(serializer.data)
                }
                image_data={"user_images":images_dict}
                return JsonResponse({"status": "success", "message": "Photo fetched successfully","data":image_data,"photo_protection":0},status=status.HTTP_200_OK)
                #print(images_dict)
                #return images_dict
            else:
                return JsonResponse({"status": "Failed", "message": "No Photos found"},status=status.HTTP_200_OK)
            
            #main function will br here
           
                
           
        # Customize the error response format
        else:
            errors = serializer.errors
            custom_errors = {field: ", ".join(error_messages) for field, error_messages in errors.items()}
            return JsonResponse({"status": "Failed", "errors": custom_errors}, status=status.HTTP_200_OK)
        

class Get_common_details(APIView):
    
    def post(self, request):
            
        serializer = serializers.Profile_idValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            
            try:
                logindetails=models.Registration1.objects.filter(ProfileId=profile_id).first()
                profile_for = logindetails.Profile_for
                try:
                        Profile_owner = models.Profileholder.objects.get(Mode=profile_for).ModeName
                except models.Profileholder.DoesNotExist:
                        Profile_owner = None
                
                #get first image for the profile icon
                profile_images=models.Image_Upload.objects.filter(profile_id=profile_id,image_approved=1,is_deleted=0).first()
                
                plan_id = logindetails.Plan_id
                plan_limits_json=''
                if plan_id:
                    plan_limits=models.PlanFeatureLimit.objects.filter(plan_id=plan_id)
                
                    serializer = serializers.PlanFeatureLimitSerializer(plan_limits, many=True)
                    plan_limits_json = serializer.data

                gender = logindetails.Gender
                profile_icon=''
                profile_completion=0
                height = logindetails.Profile_height
                marital_status=logindetails.Profile_marital_status
                age=calculate_age(logindetails.Profile_dob)


                if profile_images:
                    profile_icon=profile_images.image.url
                #default image icon
                else:
                    
                    profile_icon = 'men.jpg' if gender == 'male' else 'women.jpg'
                    
                base_url = settings.MEDIA_URL
                profile_image = base_url+profile_icon


                # logindetails_exists=models.Registration1.objects.filter(ProfileId=username,Profile_address !='').first()


                logindetails_exists = models.Registration1.objects.filter(ProfileId=profile_id).filter(Profile_address__isnull=False).exclude(Profile_address__exact='').first()

                family_details_exists=models.Familydetails.objects.filter(profile_id=profile_id).first()
                horo_details_exists=models.Horoscope.objects.filter(profile_id=profile_id).first()
                education_details_exists=models.Edudetails.objects.filter(profile_id=profile_id).first()
                partner_details_exists=models.Partnerpref.objects.filter(profile_id=profile_id).first()

                #check the address is exists for the contact s page contact us details stored in the logindetails page only
                if not logindetails_exists:
                    
                    profile_completion=1     #contact details not exists   

                elif not family_details_exists:
                    
                    profile_completion=2    #Family details not exists   

                elif not horo_details_exists:
                    profile_completion=3    #Horo details not exists   

                elif not education_details_exists:
                    profile_completion=4        #Edu details not exists   

                elif not partner_details_exists:
                    profile_completion=5            #Partner details not exists   

                return JsonResponse({'status': 1,'message': 'Details fetched sucessfully',"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,'gender':gender,'height':height,'marital_status':marital_status,'age':age,"Profile_owner":Profile_owner,"plan_limits":plan_limits_json}, status=200)
                                       
                # return JsonResponse({"status": "success", "message": "Photo Password updated successfully"},status=status.HTTP_200_OK)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Customize the error response format
        errors = serializer.errors
        custom_errors = {field: ", ".join(error_messages) for field, error_messages in errors.items()}
        return JsonResponse(custom_errors, status=status.HTTP_400_BAD_REQUEST)
    

class Get_addon_packages(APIView):
    def post(self, request):
        try:
            addonpackages = models.Addonpackages.objects.all()
            serializer = serializers.CustomAddOnPackSerializer(addonpackages, many=True)
            # return JsonResponse(serializer.data, safe=False)
            return JsonResponse({"status": "success", "message": "Photo fetched successfully","data":serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
        



def render_pdf_view(request, user_profile_id, filename="Horoscope_withbirthchart"):

                print('1234567')
  
                # Retrieve the Horoscope object based on the provided profile_id
                horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
                education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)
                
                # family details
                family_details = models.Familydetails.objects.filter(profile_id=user_profile_id)
                if family_details.exists():
                    family_detail = family_details.first()  

                    father_name = family_detail.father_name  
                    father_occupation = family_detail.father_occupation
                    family_status = family_detail.family_status
                    mother_name = family_detail.mother_name
                    mother_occupation = family_detail.mother_occupation
                    no_of_sis_married = family_detail.no_of_sis_married
                    no_of_bro_married = family_detail.no_of_bro_married
                    suya_gothram = family_detail.suya_gothram
                else:
                    # Handle case where no family details are found
                    father_name = father_occupation = family_status = ""
                    mother_name = mother_occupation = ""
                    no_of_sis_married = no_of_bro_married = 0

                # Education and profession details
                highest_education = education_details.highest_education
                annual_income = education_details.anual_income
                profession = education_details.profession

                # personal details
                name = login_details.Profile_name  # Assuming a Profile_name field exists
                dob = login_details.Profile_dob
                complexion = login_details.Profile_complexion
                user_profile_id = login_details.ProfileId
                height = login_details.Profile_height 

                # Fetch star name from BirthStar model
                try:
                    star = models.Birthstar.objects.get(pk=horoscope.birthstar_name)
                    star_name = star.star  # Or use star.tamil_series, telugu_series, etc. as per your requirement
                except models.Birthstar.DoesNotExist:
                    star_name = "N/A"

                # Fetch rasi name from Rasi model
                try:
                    if horoscope.birth_rasi_name:
                        rasi = models.Rasi.objects.get(pk=horoscope.birth_rasi_name)
                        rasi_name = rasi.name  # Or use rasi.tamil_series, telugu_series, etc. as per your requirement
                    else:
                        rasi_name="N/A"
                except models.Rasi.DoesNotExist:
                    rasi_name = "N/A"

                time_of_birth = horoscope.time_of_birth
                place_of_birth = horoscope.place_of_birth
                lagnam_didi = horoscope.lagnam_didi
                nalikai =  horoscope.nalikai

                # Planet mapping dictionary
                # planet_mapping = {
                #     "1": "Sun",
                #     "2": "Moo",
                #     "3": "Mar",
                #     "4": "Mer",
                #     "5": "Jup",
                #     "6": "Ven",
                #     "7": "Sat",
                #     "8": "Rahu",
                #     "9": "Kethu",
                #     "10": "Lagnam",
                # }

                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }

                # Define a default placeholder for empty values
                default_placeholder = '-'

                def parse_data(data):
                    # Clean up and split data
                    items = data.strip('{}').split(', ')
                    parsed_items = []
                    for item in items:
                        parts = item.split(':')
                        if len(parts) > 1:
                            values = parts[-1].strip()
                            # Handle multiple values separated by comma
                            if ',' in values:
                                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                            else:
                                values = planet_mapping.get(values, default_placeholder)
                        else:
                            values = default_placeholder
                        parsed_items.append(values)
                    return parsed_items

                # Clean up and parse the rasi_kattam and amsa_kattam data
                if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                    rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                    amsa_kattam_data = parse_data(horoscope.amsa_kattam)

                else:
                    rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                    amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')

                # Ensure that we have exactly 12 values for the grid
                rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
                amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))

                    # Dynamic HTML content including Rasi and Amsam charts

                html_content = rf"""
                <html>
                    <head>
                        <style>
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                display: flex; 
                                text-align: left;
                                margin-bottom: 20px;
                            }}

                            .header-logo img {{
                                width: 150px;
                                height: auto;
                            }}
                        
                            .header-info {{
                                text-align: right;
                            }}

                            .header-info p {{
                                color: #ed1e24;
                            }}

                            p {{
                                font-size: 10px;
                                margin: 5px 0;
                                padding: 0;
                                color: #333;
                            }}

                            .details-section {{
                                margin-bottom: 20px;
                            }}

                            .details-section p {{
                                margin: 2px 0;
                            }}

                            table.outer {{
                                width: 100%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                            }}

                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #ffffff;
                            }}

                            .inner td {{
                                border: 1px solid #000;
                                padding: 10px;
                                font-weight: bold;
                                font-size: 12px;
                                background-color: #f0f8ff;
                                white-space: pre-line; /* Ensures new lines are respected */
                            }}

                            .inner .highlight {{
                                background-color: #fffacd;
                            }}

                            .spacer {{
                                width: 5%;
                                display: inline-block;
                                background-color: transparent;
                            }}

                            .table-div{{
                                padding: 10px 10px;
                                border-collapse: collapse;
                            }}

                            .table-div p {{
                                font-size: 12px;
                            }}

                            .note-text {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 50px auto;
                            }}

                            .note-text1 {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 30px auto;
                                text-align: right;
                            }}


                        </style>
                    </head>

                    <body>

                        <table class="logo-header">
                                <tr>
                                    <td>
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/newvysyamalalogo2.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>

                                    <td>
                                        <div class="header-info">
                                            <p><strong>Mobile : </strong> 9944851550</p>
                                            <p><strong>E-mail : </strong> vysyamala.com</p>
                                            <p><strong>Website : </strong> www.vysyamala.com</p>
                                            <p><strong>WhatsApp : </strong> 9043085524</p>
                                        </div>
                                    </td>
                                </tr>
                        </table>

                    <div class="details-section">
                        <h1>Personal Details</h1>
                        
                <table class="table-div">
                            <tr>
                                <td>
                                    <p><strong>Name : </strong>{name}</p>
                                    <p><strong>DOB / POB : </strong> {dob} / {place_of_birth}</p>
                                    <p><strong>Complexion : </strong>{complexion}</p>
                                    <p><strong>Education : </strong>{highest_education}</p>
                                    <p><strong>Sisters/Married : </strong> {no_of_sis_married}</p>
                                </td>
                                
                                <td>
                                    <p><strong>Vysyamala Id : </strong>{user_profile_id}</p>
                                    <p><strong>Height / Photos : </strong>{height} / Not specified</p>
                                    <p><strong>Annual Income : </strong>{annual_income}</p>
                                    <p><strong>Profession : </strong>{profession}</p>
                                    <p><strong>Brothers/Married : </strong> {no_of_bro_married}</p>
                                </td>
                            </tr>
                        </table>


                        <table class="table-div">
                            <tr>
                                <td>
                                    <p><strong>Father Name : </strong> {father_name}</p>
                                    <p><strong>Father Occupation : </strong> {father_occupation}</p>
                                    <p><strong>Family Status : </strong> {family_status}</p>
                                </td>

                                <td>
                                    <p><strong>Mother Name : </strong> {mother_name}</p>
                                    <p><strong>Mother Occupation : </strong> {mother_occupation}</p>
                                </td>
                            </tr>
                        </table>
                        <table class="table-div">
                            <tr>
                                <td>
                                    <p><strong>Star/Rasi : </strong> {star_name}, {rasi_name}</p>
                                    <p><strong>Lagnam/Didi : </strong> {lagnam_didi}</p>
                                    <p><strong>Nalikai : </strong> {nalikai}</p>
                                </td>

                                <td>
                                    <p><strong>Surya Gothram : </strong> {suya_gothram}</p>
                                    <p><strong>Madhulam : </strong> N/A</p>
                                    <p><strong>Birth Time : </strong> {time_of_birth}</p>
                                </td>
                            </tr>
                        </table>
                    
                    </div>


                            <table class="outer">
                            <tr>
                                <td>
                                    <table class="inner">
                                        <tr>
                                            <td>{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                            <td colspan="2" rowspan="2" class="highlight">Rasi</td>
                                            <td>{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                            <td>{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                        </tr>
                                    </table>
                                </td>
                                <td class="spacer"></td>
                                <td>
                                    <table class="inner">
                                        <tr>
                                            <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                            <td colspan="2" rowspan="2" class="highlight">Amsam</td>
                                            <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                        </tr>
                                        <tr>
                                            <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                            <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>


                    <div>
                        <p class="note-text">Note : No commissions / charges will be collected, if marriage settled through Vysyamala. Please verify the profile by yourself.</p>
                    </div>
                    

                    <div>
                        <p class="note-text1">www.vysyamala.com | vysyamala@gmail.com | 9944851550</p>
                    </div>


                </body>
                </html>
                """

                # Create a Django response object and specify content_type as pdf
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                # Create the PDF using xhtml2pdf
                pisa_status = pisa.CreatePDF(html_content, dest=response)

                # If there's an error, log it and return an HTML response with an error message
                if pisa_status.err:
                    logger.error(f"PDF generation error: {pisa_status.err}")
                    return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

                return response






class GetMyProfilePersonal(APIView):
    def post(self, request):

        profile_id = request.data.get('profile_id')
        
        try:
            registration = models.Registration1.objects.get(ProfileId=profile_id)
            horoscope = models.Horoscope.objects.get(profile_id=profile_id)
            familydetails = models.Familydetails.objects.get(profile_id=profile_id)
            education_details = models.Edudetails.objects.get(profile_id=profile_id)
            profileplan_details = models.Profile_PlanFeatureLimit.objects.get(profile_id=profile_id,status=1)
            
            # Get the Profile_for value and lookup the corresponding ModeName
            profile_for_mode = models.Profileholder.objects.get(Mode=registration.Profile_for)
            profile_for_name = profile_for_mode.ModeName

            try:
                marital_status = models.ProfileMaritalstatus.objects.get(StatusId=registration.Profile_marital_status)
                marital_status_name = marital_status.MaritalStatus
            except models.ProfileMaritalstatus.DoesNotExist:
                marital_status_name = None

            try:
                if registration.Profile_complexion not in (None, '', 0):
                    complexion = models.Profilecomplexion.objects.get(complexion_id=registration.Profile_complexion)
                    complexion_name = complexion.complexion_desc
                else:
                    complexion_name = None
            except models.Profilecomplexion.DoesNotExist:
                complexion_name = None
            
            # Look up Profile_for value and get corresponding ModeName
            profile_for_name = None
            if registration.Profile_for is not None:
                try:
                    profile_for_mode = models.Profileholder.objects.get(Mode=registration.Profile_for)
                    profile_for_name = profile_for_mode.ModeName
                except models.Profileholder.DoesNotExist:
                    profile_for_name = None


            registration_serializer = serializers.PersonalRegistrationSerializer(registration)
            horoscope_serializer = serializers.PersonalHoroscopeSerializer(horoscope)
            familydetails_serializer = serializers.PersonalFamilydetailsSerializer(familydetails)
            education_details_serializer = serializers.PersonalEdudetailsSerializer(education_details)

            plan_id=registration_serializer.data.get("Plan_id")
            # plan_name=models.PlanDetails.objects.get(id=plan_id).plan_name
            
            
            if plan_id in (6, 7, 8, 9):
                plan_name='Free'
                valid_upto = profileplan_details.membership_todate.date() if profileplan_details.membership_todate else None
            
            
            
            elif  plan_id:
                try:
                    plan_name = models.PlanDetails.objects.get(id=plan_id).plan_name
                    valid_upto=registration_serializer.data.get("PaymentExpire")
                    if valid_upto is None:
                        # if date_of_join is not None:
                            date_of_join=registration_serializer.data.get("DateOfJoin")
                            date_of_join = datetime.strptime(date_of_join, '%Y-%m-%d %H:%M:%S').date()   # Adjust format as needed
                            # valid_upto = date_of_join + timedelta(days=365)  # Add one year
                    valid_upto = profileplan_details.membership_todate.date() if profileplan_details.membership_todate else ''
                        # else :
                        #      valid_upto=None
                        
                except models.PlanDetails.DoesNotExist:
                    plan_name = ''  # Return empty value if plan not found
                    #valid_upto='No validity on you current plan'

                    valid_upto = profileplan_details.membership_todate.date() if profileplan_details.membership_todate else ''
            else:
                plan_name = 'Basic'  # Return empty value if plan_id is empty
                #valid_upto='No validity on you current plan'

                valid_upto = profileplan_details.membership_todate.date() if profileplan_details.membership_todate else ''


            



            
            birth_star=horoscope_serializer.data.get("birthstar_name")
            # try:
            #     birth_starname=models.Birthstar.objects.get(id=birth_star).star
            # except models.Birthstar.DoesNotExist:
            #         birth_starname = None

            try:
                # Validate the ID is not empty or invalid
                if birth_star:
                    birth_starname = models.Birthstar.objects.get(id=int(birth_star)).star
                else:
                    birth_starname = None  # Default value for empty or invalid ID
            except models.Birthstar.DoesNotExist:
                birth_starname = None  # Handle case where Birthstar object does not exist
            
            try:
                if education_details_serializer.data.get('highest_education'):
                    Profile_high_edu = models.Edupref.objects.get(RowId=education_details_serializer.data.get('highest_education')).EducationLevel
                else:
                    Profile_high_edu=None                    
            except models.Edupref.DoesNotExist:
                Profile_high_edu = None

            
            #field_ofstudy
            try:
                if education_details_serializer.data.get('field_ofstudy'):
                    Profile_field_edu = models.Profilefieldstudy.objects.get(id=education_details_serializer.data.get('field_ofstudy')).field_of_study
                else:
                    Profile_field_edu=''                    
            except models.Profilefieldstudy.DoesNotExist:
                Profile_field_edu = ''
            
            about_edu =education_details_serializer.data.get('about_edu')
            
            try:
                    
                if education_details_serializer.data.get('profession'):
                    Profile_prosession = models.Profespref.objects.get(RowId=education_details_serializer.data.get('profession')).profession
                else:
                    Profile_prosession=''
            except models.Profespref.DoesNotExist:
                Profile_prosession = ''
            
            result_percen=calculate_points_and_get_empty_fields(profile_id)

            highest_qualification_name = safe_get_by_id(models.Edupref, education_details_serializer.data.get('highest_education'), 'EducationLevel')
            field_of_study_name = safe_get_by_id(models.Profilefieldstudy, education_details_serializer.data.get('field_ofstudy'), 'field_of_study')
            #city_name = safe_get_by_id(models.Profilecity, education_details_serializer.data.get('work_city'), 'city_name')
            
            country_name=get_country_name(education_details_serializer.data.get('work_country'))
            state_name=get_country_name(education_details_serializer.data.get('work_state'))
            district_name=get_country_name(education_details_serializer.data.get('work_district'))
            city_name=get_city_name(education_details_serializer.data.get('work_city'))

            location_name = next((name for name in [city_name, district_name, state_name, country_name] if name),None)

            # qualification_name=  highest_qualification_name +' '+field_of_study_name

            qualification_name_1=  get_degree_name(education_details_serializer.data.get('degree'),education_details_serializer.data.get('other_degree'))
            # print('qualification_name',qualification_name)
            if not qualification_name_1:
                # print('Not qualification_name',qualification_name)
                qualification_name=  field_of_study_name
            else :
                qualification_name=qualification_name_1

            # print('Highest edu Name ',education_details_serializer.data.get('highest_education'))
            # print('Work city Name ',education_details_serializer.data.get('work_city'))
            # print(qualification_name)
            # print(city_name)
            
            myself = familydetails_serializer.data.get("about_self")

            if myself is None or myself == "":
                profile = {
                    "name": registration_serializer.data.get("Profile_name"),
                    "profession": Profile_prosession,
                    "company": education_details_serializer.data.get('company_name'),
                    "designation": education_details_serializer.data.get('designation'),
                    "business": education_details_serializer.data.get('business_name'),
                    "qualification": qualification_name,
                    "location": location_name,
                    "profile_type": education_details_serializer.data.get('profession')
                }
                myself = generate_about_myself_summary(profile)

            
            familydetails_serializer.data.get("about_self")

            data = {
                "personal_profile_name": registration_serializer.data.get("Profile_name"),
                "personal_gender": registration_serializer.data.get("Gender"),
                "personal_age": registration_serializer.data.get("age"),
                "personal_profile_dob": registration_serializer.data.get("Profile_dob"),
                "personal_place_of_birth": horoscope_serializer.data.get("place_of_birth"),
                "personal_time_of_birth": horoscope_serializer.data.get("time_of_birth"),
                "personal_time_of_birth_str": format_time_am_pm(horoscope_serializer.data.get("time_of_birth")),
                "personal_profile_height": registration_serializer.data.get("Profile_height"),
                "personal_profile_marital_status_id": registration_serializer.data.get("Profile_marital_status"),
                "personal_profile_marital_status_name": marital_status_name,
                "personal_blood_group": familydetails_serializer.data.get("blood_group"),
                #"personal_about_self": familydetails_serializer.data.get("about_self"),
                "personal_about_self": myself,
                "personal_about_self_original": familydetails_serializer.data.get("about_self"),
                "personal_profile_complexion_id": registration_serializer.data.get("Profile_complexion"),
                "personal_profile_complexion_name": complexion_name,
                "personal_hobbies": familydetails_serializer.data.get("hobbies"),
                # "personal_pysically_changed": familydetails_serializer.data.get("Pysically_changed"),
                "personal_pysically_changed":'Yes' if familydetails_serializer.data.get("Pysically_changed") == 1 else 'No' if familydetails_serializer.data.get("Pysically_changed") == "0" else familydetails_serializer.data.get("Pysically_changed") ,
                "personal_profile_for_id":  registration_serializer.data.get("Profile_for"),
                "personal_video_url":  registration_serializer.data.get("Video_url"),
                "personal_profile_for_name": profile_for_name,
                "personal_weight": familydetails_serializer.data.get("weight"),
                # "personal_eye_wear":  familydetails_serializer.data.get("eye_wear"),
                "personal_eye_wear":'Yes' if familydetails_serializer.data.get("eye_wear") == "1" else 'No' if familydetails_serializer.data.get("eye_wear") == "0" else familydetails_serializer.data.get("eye_wear"),
                "personal_body_type": familydetails_serializer.data.get("body_type"),
                "personal_verify":registration_serializer.data.get("Profile_verified"),
                "package_name":plan_name,
                "valid_upto":valid_upto,
                #"profile_completion":calculate_profile_completion(profile_id),
                #"profile_completion":result_percen['completion_percentage'],
                "profile_completion":int(result_percen['completion_percentage']),
                "empty_fields":result_percen['empty_fields'],
                "profile_id":registration_serializer.data.get("ProfileId"),
                "star":birth_starname,
                # "gothram":registration_serializer.data.get("Profile_gothras"),
                "gothram":familydetails_serializer.data.get("suya_gothram"),
                "uncle_gothram":familydetails_serializer.data.get("uncle_gothram"),
                # "heightest_education":Profile_high_edu,
                "heightest_education": f"{Profile_high_edu} {Profile_field_edu} {qualification_name_1} {about_edu}",
                "prosession":Profile_prosession,
                "mobile_no":registration.Mobile_no
            }

            response = {
                "status": "success",
                "message": "Personal details fetched successfully",
                "data": data
            }

            return JsonResponse(response, status=status.HTTP_200_OK)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Horoscope.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Horoscope not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Profileholder.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile mode not found"}, status=status.HTTP_404_NOT_FOUND)



def generate_about_myself_summary(profile):
    name = profile.get("name", "Name")
    profession = profile.get("profession", "your profession")
    business = profile.get("business", "your business")
    company = profile.get("company", "your company")
    designation =  profile.get("designation", "your designation")
    qualification = profile.get("qualification", "your qualification")
    institution = profile.get("institution", None)
    location = profile.get("location", "your location")
    profile_type = profile.get("profile_type")  # 'employee', 'business', or 'not_working'

    if profile_type == "1":
        summary = (
            f"I am {name}, currently working as a {designation} at {company}. "
            f"I hold a degree in {qualification}"
        )
        #if institution:
            #summary += f" and have completed my education from {institution}."
        summary += f" I reside in {location}."

    elif profile_type == "2":
        summary = (
            f"I am {name}, a business professional engaged in {business}. "
            f"I hold a degree in {qualification}"
        )
        #if institution:
            #summary += f" from {institution}."
        summary += f" I operate my business from {location}."

    else:  # Not working or student, etc.
        summary = (
            f"I am {name}, currently not working. "
            f"I have completed my education in {qualification}"
        )
        #if institution:
            #summary += f" from {institution}."
        summary += f" I live in {location}."

    return summary





def safe_get_by_id(model, pk_value, return_field):
    if not pk_value:
        return ""
    try:
        obj = model.objects.get(pk=pk_value)
        return getattr(obj, return_field)
    except model.DoesNotExist:
        return ""
    except Exception as e:
        print(f"[ERROR] {e}")
        return ""

class UpdateMyProfilePersonal(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        
        try:
            # Check if request data is empty
            if not request.data:
                return JsonResponse({"status": "error", "message": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the instances by profile_id
            registration = models.Registration1.objects.get(ProfileId=profile_id)
            horoscope = models.Horoscope.objects.get(profile_id=profile_id)
            familydetails = models.Familydetails.objects.get(profile_id=profile_id)
            
            # Update registration data
            registration_serializer = serializers.PersonalRegistrationSerializer(registration, data=request.data, partial=True)
            if registration_serializer.is_valid():
                registration_serializer.save()
            else:
                return JsonResponse({"status": "error", "message": registration_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update horoscope data
            horoscope_serializer = serializers.PersonalHoroscopeSerializer(horoscope, data=request.data, partial=True)
            if horoscope_serializer.is_valid():
                horoscope_serializer.save()
            else:
                return JsonResponse({"status": "error", "message": horoscope_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update family details data
            familydetails_serializer = serializers.PersonalFamilydetailsSerializer(familydetails, data=request.data, partial=True)
            if familydetails_serializer.is_valid():
                familydetails_serializer.save()
            else:
                return JsonResponse({"status": "error", "message": familydetails_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Success response
            return JsonResponse({
                "status": "success",
                "message": "Profile updated successfully"
            }, status=status.HTTP_200_OK)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Horoscope.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Horoscope not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
        




def GetMarsRahuKethuDoshamDetails(raw_input):
    # def post(self, request):
        # Get the input data from the single text field
        # raw_input = request.data.get('input_data', '')
        # if not raw_input:
        #     raw_input = request.POST.get('input_data', '')
        # if not raw_input:
        #     raw_input = request.query_params.get('input_data', '')

        # Parse the input string to create the rasi_grid_data dictionary

        # print('1234mars')
        rasi_grid_data = {}
        pattern = r"Grid (\d+):\s*([\d,]*|empty)"
        matches = re.findall(pattern, raw_input)

        for match in matches:
            grid_number = int(match[0])
            if match[1].lower() == "empty" or match[1].strip() == "":
                rasi_grid_data[f'Grid {grid_number}'] = []
            else:
                rasi_grid_data[f'Grid {grid_number}'] = [
                    int(x) for x in match[1].split(',') if x.strip()
                ]

        # Planet mapping dictionary
        # planet_mapping = {
        #     1: "Sun",
        #     2: "Moon",
        #     3: "Mars",
        #     4: "Mercury",
        #     5: "Jupiter",
        #     6: "Venus",
        #     7: "Saturn",
        #     8: "Rahu",
        #     9: "Kethu",
        #     10: "Lagnam",
        # }

        planet_mapping = {
                    "1": "Sun",
                    "2": "Moon",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mars",
                    "6": "Venus",
                    "7": "Jupiter",
                    "8": "Mercury",
                    "9": "Saturn",
                    "10": "Lagnam",
                }

        # Create a grid of 12 cells with mapped planet names
        grid = []
        for i in range(1, 13):
            if f'Grid {i}' in rasi_grid_data:
                planets = [planet_mapping.get(x, '') for x in rasi_grid_data[f'Grid {i}']]
                grid.append(", ".join(planets))
            else:
                grid.append("")

        # Calculation for identifying the positions
        mars_position = None
        rahu_positions = []
        kethu_positions = []
        lagnam_position = None

        for grid_num, planets in rasi_grid_data.items():
            if 5 in planets:  # Mars
                mars_position = int(grid_num.split()[1])
            if 3 in planets:  # Rahu
                rahu_positions.append(int(grid_num.split()[1]))
            if 4 in planets:  # Kethu
                kethu_positions.append(int(grid_num.split()[1]))
            if 10 in planets:  # Lagnam
                lagnam_position = int(grid_num.split()[1])

        def calculate_position(from_position, to_position):
            if from_position is None or to_position is None:
                return None
            if to_position >= from_position:
                return to_position - from_position + 1
            else:
                return 12 - from_position + to_position + 1

        # Calculate positions relative to Lagnam
        rahu_positions_from_lagnam = [
            calculate_position(lagnam_position, pos) for pos in rahu_positions
        ]
        kethu_positions_from_lagnam = [
            calculate_position(lagnam_position, pos) for pos in kethu_positions
        ]

        print('rahu_positions_from_lagnam',rahu_positions_from_lagnam)
        print('kethu_positions_from_lagnam',kethu_positions_from_lagnam)


        # Calculate mars position from lagnam
        mars_position_from_lagnam = calculate_position(lagnam_position, mars_position)


        print('mars_position_from_lagnam',mars_position_from_lagnam)

        # Determine if there is Mars dosham
        mars_dosham = False
        # if mars_position_from_lagnam in {1, 2, 4, 7, 8, 12}:
        if mars_position_from_lagnam in {2, 4, 7, 8, 12}:
            mars_dosham = True

        # Determine if there is Rahu-Kethu dosham
        critical_positions = {1, 2, 7, 8}
        rahu_kethu_dosham = False

        # Check if any Rahu or Kethu position falls within the critical positions
        if any(pos in critical_positions for pos in rahu_positions_from_lagnam) or \
           any(pos in critical_positions for pos in kethu_positions_from_lagnam):
            rahu_kethu_dosham = True

        # Debugging: Print positions and dosham status
        # print(f"Lagnam position: {lagnam_position}")
        # print(f"Rahu positions from Lagnam: {rahu_positions_from_lagnam}")
        # print(f"Kethu positions from Lagnam: {kethu_positions_from_lagnam}")
        # print(f"Rahu-Kethu Dosham: {rahu_kethu_dosham}")
        # print(f"mars_position_from_lagnam: {mars_position_from_lagnam}")
        # print(f"mars_dosham: {mars_dosham}")

        # Generate the HTML directly in the API with the .format() method
        html_content = """
        <table border="1" style="width: 100%; height: 400px; border-collapse: collapse; text-align: center; font-family: Arial, sans-serif;">
            <tr>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{0}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{1}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{2}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{3}</td>
            </tr>
            <tr>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{4}</td>
                <td colspan="2" rowspan="2" style="background-color: #fffacd; width: 50%; height: 50%; padding: 20px; font-weight: bold; font-size: 18px;">Center</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{5}</td>
            </tr>
            <tr>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{6}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{7}</td>
            </tr>
            <tr>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{8}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{9}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{10}</td>
                <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{11}</td>
            </tr>
        </table>
        """.format(
            grid[0],
            grid[1],
            grid[2],
            grid[3],
            grid[11],
            grid[4],
            grid[10],
            grid[5],
            grid[9],
            grid[8],
            grid[7],
            grid[6]
        )

        return mars_dosham, rahu_kethu_dosham


class Save_plan_package(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        plan_id = request.data.get('plan_id')
        addon_package_id = request.data.get('addon_package_id')
        total_amount = request.data.get('total_amount')
        order_id = request.data.get('order_id')
        
        try:
            # Check if request data is empty
            if not profile_id or not plan_id:
                return JsonResponse({"status": "error", "message": "profile_id and plan_id are required"}, status=status.HTTP_400_BAD_REQUEST)


            if not request.data:
                return JsonResponse({"status": "error", "message": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the instances by profile_id
            registration = models.Registration1.objects.get(ProfileId=profile_id)
             # Update the fields
            
            registration.Plan_id = plan_id if plan_id != 0 else registration.Plan_id  #if in case the plan_id come as 0 it shoult update as 0 
            #registration.Plan_id = plan_id
            registration.secondary_status = 30   # newly registered and the Premium
            registration.plan_status = plan_id
            registration.Addon_package = addon_package_id
            registration.Payment= total_amount

            addon_package_ids = addon_package_id

            #update vysassist in profilePlanfeatiretable
            if addon_package_ids:
                # Split comma-separated string into list of ints
                addon_package_id_list = [int(pk.strip()) for pk in addon_package_ids.split(",") if pk.strip().isdigit()]

                # Check if ID 1 is in the list
                if 1 in addon_package_id_list:
                    # print("Addon Package ID 1 found. Updating Profile_plan_feature...")

                    # Example: update all rows (or filter if needed)
                    models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id).update(vys_assist=1,vys_assist_count=10)

            # Save the changes
            registration.save() 

            user, created = User.objects.get_or_create(username=profile_id)
            if created:
                # Handle user creation logic if needed
                pass
              
            # Authentication successful, create token
            token, created = Token.objects.get_or_create(user=user)

            notify_count=models.Profile_notification.objects.filter(profile_id=profile_id, is_read=0).count()

            logindetails=models.Registration1.objects.filter(ProfileId=profile_id).first()

            profile_for=logindetails.Profile_for
            try:
                    Profile_owner = models.Profileholder.objects.get(Mode=profile_for).ModeName
            except models.Profileholder.DoesNotExist:
                    Profile_owner = None
            
            logindetails.Last_login_date=timezone.now()
            logindetails.save()

        
            horodetails=models.Horoscope.objects.filter(profile_id=profile_id).first()
            
            #get first image for the profile icon
            profile_images=models.Image_Upload.objects.filter(profile_id=profile_id).first()  

            plan_id = logindetails.Plan_id
            plan_limits_json=''
            if plan_id:
                plan_limits=models.PlanFeatureLimit.objects.filter(plan_id=plan_id)
            
                serializer = serializers.PlanFeatureLimitSerializer(plan_limits, many=True)
                plan_limits_json = serializer.data


            membership_fromdate = date.today() #same date of the payment date
            membership_todate = membership_fromdate + timedelta(days=365)

            models.PlanSubscription.objects.create(
            profile_id=profile_id,              # e.g., '123'
            plan_id=plan_id,               # e.g., 7
            paid_amount=total_amount,             # e.g., Decimal('499.99')
            payment_mode='Online',     # e.g., 'UPI'
            status=1,   
            payment_by='user_self',                             # e.g., 1 for success, or your own logic
            payment_date=datetime.now(),          # current timestamp
            order_id=order_id  )

            plan_features = models.PlanFeatureLimit.objects.filter(plan_id=plan_id).values().first()

            if plan_features:
                # Remove the 'id' field if present
                plan_features.pop('id', None)
                plan_features.pop('plan_id', None)  # optional, if you don't want to override plan_id

                # Add membership dates
                plan_features.update({
                    'plan_id': plan_id,
                    'membership_fromdate': membership_fromdate,
                    'membership_todate': membership_todate,
                    'status':1
                })

                # Update the profile_plan_features row for profile_id
                models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id).update(**plan_features)
    
            gender = logindetails.Gender
            height = logindetails.Profile_height
            marital_status=logindetails.Profile_marital_status
            quick_reg=logindetails.quick_registration
            if not quick_reg:
                quick_reg=0

            profile_icon=''
            profile_completion=0
            birth_star_id=''
            birth_rasi_id=''
            if horodetails:
                birth_star_id=horodetails.birthstar_name
                birth_rasi_id=horodetails.birth_rasi_name

            if profile_images:
                profile_image = profile_images.image.url
            #default image icon
            else:
            
                profile_icon = 'men.jpg' if gender == 'male' else 'women.jpg'
                base_url = settings.MEDIA_URL
                profile_image = base_url+profile_icon


            logindetails_exists = models.Registration1.objects.filter(ProfileId=profile_id).filter(Profile_address__isnull=False).exclude(Profile_address__exact='').first()

            family_details_exists=models.Familydetails.objects.filter(profile_id=profile_id).first()
            horo_details_exists=models.Horoscope.objects.filter(profile_id=profile_id).first()
            education_details_exists=models.Edudetails.objects.filter(profile_id=profile_id).first()
            partner_details_exists=models.Partnerpref.objects.filter(profile_id=profile_id).first()

            profile_planfeature = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id, status=1).first()
            valid_till = profile_planfeature.membership_todate if profile_planfeature else None

            #check the address is exists for the contact s page contact us details stored in the logindetails page only
            if not logindetails_exists:
            
                profile_completion=1     #contact details not exists   

            elif not family_details_exists:
                
                profile_completion=2    #Family details not exists   

            elif not horo_details_exists:
                profile_completion=3    #Horo details not exists   

            elif not education_details_exists:
                profile_completion=4        #Edu details not exists   

            elif not partner_details_exists:
                profile_completion=5            #Partner details not exists             

             
            # Success response
            return JsonResponse({
                    "status": "success",
                    "message": "Plans and packages updated successfully",
                    "data_message": f"Thank you for registering in Vysyamala. Your profile has been successfully submitted.Your Profile Id is  {profile_id} . We truly appreciate you taking the time to join Vysyamala—it means a lot to us! Our customer support team will review your details and get in touch with you shortly to complete the approval process. Welcome to the Vysyamala family!",
                    'token':token.key ,'profile_id':profile_id ,'message': 'Login Successful',"notification_count":notify_count,"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,"gender":gender,"height":height,"marital_status":marital_status,"custom_message":1,"birth_star_id":birth_star_id,"birth_rasi_id":birth_rasi_id,"profile_owner":Profile_owner,"quick_reg":quick_reg,"plan_limits":plan_limits_json,"valid_till":valid_till }, status=status.HTTP_200_OK)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        

# def GetMarsRahuKethuDoshamDetails(raw_input):
#     # def post(self, request):
#         # Get the input data from the single text field
#         # raw_input = request.data.get('input_data', '')
#         # if not raw_input:
#         #     raw_input = request.POST.get('input_data', '')
#         # if not raw_input:
#         #     raw_input = request.query_params.get('input_data', '')

#         # Parse the input string to create the rasi_grid_data dictionary
#         rasi_grid_data = {}
#         pattern = r"Grid (\d+):\s*([\d,]*|empty)"
#         matches = re.findall(pattern, raw_input)

#         for match in matches:
#             grid_number = int(match[0])
#             if match[1].lower() == "empty" or match[1].strip() == "":
#                 rasi_grid_data[f'Grid {grid_number}'] = []
#             else:
#                 rasi_grid_data[f'Grid {grid_number}'] = [
#                     int(x) for x in match[1].split(',') if x.strip()
#                 ]

#         # Planet mapping dictionary
#         planet_mapping = {
#             1: "Sun",
#             2: "Moon",
#             3: "Mars",
#             4: "Mercury",
#             5: "Jupiter",
#             6: "Venus",
#             7: "Saturn",
#             8: "Rahu",
#             9: "Kethu",
#             10: "Lagnam",
#         }

#         # Create a grid of 12 cells with mapped planet names
#         grid = []
#         for i in range(1, 13):
#             if f'Grid {i}' in rasi_grid_data:
#                 planets = [planet_mapping.get(x, '') for x in rasi_grid_data[f'Grid {i}']]
#                 grid.append(", ".join(planets))
#             else:
#                 grid.append("")

#         # Calculation for identifying the positions
#         mars_position = None
#         rahu_positions = []
#         kethu_positions = []
#         lagnam_position = None

#         for grid_num, planets in rasi_grid_data.items():
#             if 3 in planets:  # Mars
#                 mars_position = int(grid_num.split()[1])
#             if 8 in planets:  # Rahu
#                 rahu_positions.append(int(grid_num.split()[1]))
#             if 9 in planets:  # Kethu
#                 kethu_positions.append(int(grid_num.split()[1]))
#             if 10 in planets:  # Lagnam
#                 lagnam_position = int(grid_num.split()[1])

#         def calculate_position(from_position, to_position):
#             if from_position is None or to_position is None:
#                 return None
#             if to_position >= from_position:
#                 return to_position - from_position + 1
#             else:
#                 return 12 - from_position + to_position + 1

#         # Calculate positions relative to Lagnam
#         rahu_positions_from_lagnam = [
#             calculate_position(lagnam_position, pos) for pos in rahu_positions
#         ]
#         kethu_positions_from_lagnam = [
#             calculate_position(lagnam_position, pos) for pos in kethu_positions
#         ]

#         # Calculate mars position from lagnam
#         mars_position_from_lagnam = calculate_position(lagnam_position, mars_position)

#         # Determine if there is Mars dosham
#         mars_dosham = False
#         if mars_position_from_lagnam in {1, 2, 4, 7, 8, 12}:
#             mars_dosham = True

#         # Determine if there is Rahu-Kethu dosham
#         critical_positions = {1, 2, 7, 8}
#         rahu_kethu_dosham = False

#         # Check if any Rahu or Kethu position falls within the critical positions
#         if any(pos in critical_positions for pos in rahu_positions_from_lagnam) or \
#            any(pos in critical_positions for pos in kethu_positions_from_lagnam):
#             rahu_kethu_dosham = True

#         # Debugging: Print positions and dosham status
#         print(f"Lagnam position: {lagnam_position}")
#         print(f"Rahu positions from Lagnam: {rahu_positions_from_lagnam}")
#         print(f"Kethu positions from Lagnam: {kethu_positions_from_lagnam}")
#         print(f"Rahu-Kethu Dosham: {rahu_kethu_dosham}")
#         print(f"mars_position_from_lagnam: {mars_position_from_lagnam}")
#         print(f"mars_dosham: {mars_dosham}")

#         # Generate the HTML directly in the API with the .format() method
#         html_content = """
#         <table border="1" style="width: 100%; height: 400px; border-collapse: collapse; text-align: center; font-family: Arial, sans-serif;">
#             <tr>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{0}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{1}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{2}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{3}</td>
#             </tr>
#             <tr>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{4}</td>
#                 <td colspan="2" rowspan="2" style="background-color: #fffacd; width: 50%; height: 50%; padding: 20px; font-weight: bold; font-size: 18px;">Center</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{5}</td>
#             </tr>
#             <tr>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{6}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{7}</td>
#             </tr>
#             <tr>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{8}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{9}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{10}</td>
#                 <td style="width: 25%; height: 25%; padding: 20px; background-color: #f0f8ff; font-weight: bold; font-size: 16px;">{11}</td>
#             </tr>
#         </table>
#         """.format(
#             grid[0],
#             grid[1],
#             grid[2],
#             grid[3],
#             grid[11],
#             grid[4],
#             grid[10],
#             grid[5],
#             grid[9],
#             grid[8],
#             grid[7],
#             grid[6]
#         )

#         return mars_dosham, rahu_kethu_dosham

        # Returning both HTML content, grid data, and calculated flags in JSON
        # return JsonResponse({
        #     "input_data": raw_input,
        #     "html_content": html_content,
        #     "grid_values": grid,
        #     "rasi_grid_data": rasi_grid_data,
        #     "mars_position_from_lagnam": mars_position_from_lagnam,
        #     "rahu_positions_from_lagnam": rahu_positions_from_lagnam,
        #     "kethu_positions_from_lagnam": kethu_positions_from_lagnam,
        #     "mars_dosham": mars_dosham,
        #     "rahu_kethu_dosham": rahu_kethu_dosham
        # })






# class GetMyProfileFamily(APIView):
#     def post(self, request):
#         profile_id = request.data.get('profile_id')  
#         if not profile_id:
#             return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             family_details = models.Familydetails.objects.get(profile_id=profile_id)
#             serializer = serializers.PersonalFamilySerializer(family_details)

#             family_status_id = serializer.data.get("family_status")
#             family_status = models.Familystatus.objects.get(id=family_status_id)
#             family_status_serializer = serializers.FamilyStatusSerializer(family_status)

#             data = {
#                 "personal_about_fam": serializer.data.get("about_family"),
#                 "personal_father_name": serializer.data.get("father_name"),
#                 "persoanl_father_occu": serializer.data.get("father_occupation"),
#                 "persoanl_mother_name": serializer.data.get("mother_name"),
#                 "persoanl_mother_occu": serializer.data.get("mother_occupation"),
#                 "persoanl_fam_sta_id": family_status_id,
#                 "persoanl_fam_sta_name": family_status_serializer.data.get("status"),
#                 "persoanl_sis": serializer.data.get("no_of_sister"),
#                 "presoanl_sis_married": serializer.data.get("no_of_sis_married"),
#                 "persoanl_bro": serializer.data.get("no_of_brother"),
#                 "persoanl_bro_married": serializer.data.get("no_of_bro_married"),
#                 "persoanl_prope_det": serializer.data.get("property_details"),
#             }

#             response = {
#                 "status": "success",
#                 "message": "Family details fetched successfully",
#                 "data": data
#             }

#             return JsonResponse(response, status=status.HTTP_200_OK)

#         except models.Familydetails.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
#         except models.Familystatus.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Family status not found"}, status=status.HTTP_404_NOT_FOUND)


class GetMyProfileFamily(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')  
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            family_details = models.Familydetails.objects.get(profile_id=profile_id)
            serializer = serializers.PersonalFamilySerializer(family_details)

            # Handling family status
            try:
                family_status_id = serializer.data.get("family_status")
                if family_status_id and family_status_id.isdigit():
                    family_status = models.Familystatus.objects.get(id=family_status_id)
                    family_status_name = family_status.status  # Extract the field for JSON response
                else:
                    family_status_name = None
            except models.Familystatus.DoesNotExist:
                family_status_name = None

            # Handling father occupation
            # try:
            #     father_occupation_id = serializer.data.get("father_occupation")
            #     if father_occupation_id and father_occupation_id.isdigit():
            #         father_occupation = models.Parentoccupation.objects.get(id=father_occupation_id)
            #         father_occupation_name = father_occupation.occupation  # Extract the field
            #     else:
            #         father_occupation_name = None
            # except models.Parentoccupation.DoesNotExist:
            #     father_occupation_name = None

            # Handling mother occupation
            # try:
            #     mother_occupation_id = serializer.data.get("mother_occupation")
            #     if mother_occupation_id and mother_occupation_id.isdigit():
            #         mother_occupation = models.Parentoccupation.objects.get(id=mother_occupation_id)
            #         mother_occupation_name = mother_occupation.occupation  # Extract the field
            #     else:
            #         mother_occupation_name = None
            # except models.Parentoccupation.DoesNotExist:
            #     mother_occupation_name = None

            # Constructing the response data
            mother_occupation_name=serializer.data.get("mother_occupation")
            father_occupation_name=serializer.data.get("father_occupation")
            data = {
                "personal_about_fam": serializer.data.get("about_family"),
                "personal_father_name": serializer.data.get("father_name"),
                "personal_father_occu_id": father_occupation_name,
                "personal_father_occu_name": father_occupation_name,  
                "personal_mother_name": serializer.data.get("mother_name"),
                "personal_mother_occu_id": mother_occupation_name,
                "personal_mother_occu_name": mother_occupation_name,  
                "personal_fam_sta_id": family_status_id,
                "personal_fam_sta_name": family_status_name,
                "personal_sis": serializer.data.get("no_of_sister"),
                "personal_sis_married": serializer.data.get("no_of_sis_married"),
                "personal_bro": serializer.data.get("no_of_brother"),
                "personal_bro_married": serializer.data.get("no_of_bro_married"),
                "personal_prope_det": serializer.data.get("property_details"),
                "personal_property_worth": serializer.data.get("property_worth"),
                "personal_family": serializer.data.get("family_name"),
                "personal_ancestor_origin": serializer.data.get("ancestor_origin"),
                "personal_family_value":serializer.data.get("family_value"),
                "personal_family_type":serializer.data.get("family_type"),
                "personal_uncle_gothram":serializer.data.get("uncle_gothram"),
                "personal_no_of_children":serializer.data.get("no_of_children"),
                "father_alive": serializer.data.get("father_alive"),
                "mother_alive": serializer.data.get("mother_alive"),
            }

            response = {
                "status": "success",
                "message": "Family details fetched successfully",
                "data": data
            }

            return JsonResponse(response, status=status.HTTP_200_OK)

        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Familystatus.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family status not found"}, status=status.HTTP_404_NOT_FOUND)

        
class UpdateMyProfileFamily(APIView):
    def post(self, request):
        try:
            profile_id = request.data.get('profile_id')
            if not profile_id:
                return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            family_details = models.Familydetails.objects.get(profile_id=profile_id)

            serializer = serializers.PersonalFamilySerializer(family_details, data=request.data, partial=True)
            notification_message=None
            notification_titile="Change In "

            if serializer.is_valid():
                
                family_status_id = request.data.get("family_status")
                if family_status_id:
                    family_status = models.Familystatus.objects.get(id=family_status_id)
                    # family_details.family_status = family_status_id
                    # print('123456',False)
                    # print('family_details.family_status:', family_details.family_status, type(family_details.family_status))
                    # print('family_status_id:', family_status_id, type(family_status_id))
                    

                    # print('family_status_value:', family_status_value, type(family_status_value))
                    if not family_details.family_status or not str(family_details.family_status).isdigit() or int(family_details.family_status) != int(family_status_id):
                        # if family_details.family_status.strip() != family_status_id.strip():

                            # print('123456')
                            family_details.family_status = family_status_id
                            notification_message = "Family Status "
                            notification_titile +=" Family Status "
                    

                    serializer.save()
                    family_details.save()
                    
                    if notification_message:
                    # print('12345')
                       #notify_related_profiles(profile_id,'Profile_update',notification_titile,notification_message)
                        addto_notification_queue(profile_id,'Profile_update',notification_titile,notification_message)
                serializer.save()
                family_details.save()
                
                response = {
                    "status": "success",
                    "message": "Family details updated successfully"
                }
                return JsonResponse(response, status=status.HTTP_200_OK)
                

            return JsonResponse({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)

        except models.Familystatus.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family status not found"}, status=status.HTTP_404_NOT_FOUND)


def format_time_am_pm(time_str):
    if not time_str:  # Handles None or empty strings
        return "N/A"
    try:
        time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
        return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
    except ValueError:
        return str(time_str)



def dasa_format_date(value):
        """
        Format the date based on the input format.
        If input is like "12/7/5", convert to "day:12, month:7, year:5".
        If already in desired format, return as-is.
        """
        if isinstance(value, str) and '/' in value:
            parts = value.split('/')
            if len(parts) == 3:
                day, month, year = parts
                #return f"{day} Days, {month} Months , {year} Years"
                return f"{day} Years, {month} Months, {year} Days"
        return value



class GetMyProfileHoroscope(APIView):

    def post(self, request):
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            horoscope = models.Horoscope.objects.get(profile_id=profile_id)
            horoscope_serializer = serializers.HoroscopeSerializer(horoscope)

            family_details = models.Familydetails.objects.get(profile_id=profile_id)
            family_serializer = serializers.PersonalFamSerilizer(family_details)

            # birthstar_id = horoscope.birthstar_name  
            # birthstar = models.Birthstar.objects.get(id=birthstar_id)
            # birthstar_name = birthstar.star

            # rasi_id = horoscope.birth_rasi_name  
            # rasi = models.Rasi.objects.get(id=rasi_id)
            # rasi_name = rasi.name

            # lagnam_didi_id = horoscope_serializer.data.get("lagnam_didi")
            # lagnam_didi = models.Lagnamdidi.objects.get(id=lagnam_didi_id)
            # lagnam_didi_name = lagnam_didi.name


            try:
                birthstar_id = horoscope.birthstar_name
                if birthstar_id:
                    birthstar = models.Birthstar.objects.get(id=birthstar_id)
                    birthstar_name = birthstar.star
                else:
                    birthstar_name = None  # Default value if null or empty
            except models.Birthstar.DoesNotExist:
                birthstar_name = None  # Handle case where object doesn't exist

            try:
                rasi_id = horoscope.birth_rasi_name
                if rasi_id:
                    rasi = models.Rasi.objects.get(id=rasi_id)
                    rasi_name = rasi.name
                else:
                    rasi_name = None  # Default value if null or empty
            except models.Rasi.DoesNotExist:
                rasi_name = None  # Handle case where object doesn't exist

            try:
                lagnam_didi_id = horoscope_serializer.data.get("lagnam_didi")
                if lagnam_didi_id:
                    lagnam_didi = models.Lagnamdidi.objects.get(id=lagnam_didi_id)
                    lagnam_didi_name = lagnam_didi.name
                else:
                    lagnam_didi_name = None  # Default value if null or empty
            except models.Lagnamdidi.DoesNotExist:
                lagnam_didi_name = None  # Handle case where object doesn't exist

            
            
            def dosham_value_formatter(value):
                if isinstance(value, str):
                    return {"0": "Unknown", "1": "Yes", "2": "No"}.get(value, value)
                elif isinstance(value, int):
                    return {0: "Unknown", 1: "Yes", 2: "No"}.get(value, value)
                return value
            
            if(horoscope_serializer.data.get("rasi_kattam")):
                    mars_dosham, rahu_kethu_dosham=GetMarsRahuKethuDoshamDetails(horoscope_serializer.data.get("rasi_kattam"))

                    print(rahu_kethu_dosham)
                    print(mars_dosham)



            data = {
                "personal_bthstar_id": birthstar_id,
                "personal_bthstar_name": birthstar_name,
                "personal_bth_rasi_id": rasi_id,
                "personal_bth_rasi_name": rasi_name,
                "personal_lagnam_didi_id": lagnam_didi_id,
                "personal_lagnam_didi_name": lagnam_didi_name,
                "personal_didi":horoscope_serializer.data.get("didi"),
                "personal_chevvai_dos": dosham_value_formatter(horoscope_serializer.data.get("chevvai_dosaham")),
                "personal_ragu_dos": dosham_value_formatter(horoscope_serializer.data.get("ragu_dosham")),
                "personal_nalikai": horoscope_serializer.data.get("nalikai"),
                "personal_surya_goth": family_serializer.data.get("suya_gothram"),
                "personal_madulamn": family_serializer.data.get("madulamn"),
                "personal_dasa": get_dasa_name(horoscope_serializer.data.get("dasa_name")),
                "personal_dasa_bal": dasa_format_date(horoscope_serializer.data.get("dasa_balance")),
                "personal_rasi_katt": horoscope_serializer.data.get("rasi_kattam"),
                "personal_amsa_katt": horoscope_serializer.data.get("amsa_kattam"),
                "personal_horoscope_hints": horoscope_serializer.data.get("horoscope_hints")
            }

            response = {
                "status": "success",
                "message": "Horoscope details fetched successfully",
                "data": data
            }
            return JsonResponse(response, status=status.HTTP_200_OK)

        except models.Horoscope.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Horoscope details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Birthstar.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Birthstar details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Rasi.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Rasi details not found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateMyProfileHoroscope(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        rasi_kattam = request.data.get('rasi_kattam')
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            horoscope = models.Horoscope.objects.get(profile_id=profile_id)
            family_details = models.Familydetails.objects.get(profile_id=profile_id)

            horoscope_serializer = serializers.HoroscopeSerializer(horoscope, data=request.data, partial=True)
            
            
            calc_chevvai_dhosham, calc_raguketu_dhosham=GetMarsRahuKethuDoshamDetails(rasi_kattam)
            
            if horoscope_serializer.is_valid():
                horoscope_serializer.save(
                    calc_chevvai_dhosham=calc_chevvai_dhosham,
                    calc_raguketu_dhosham=calc_raguketu_dhosham
                )
            else:
                return JsonResponse({"status": "error", "message": "Invalid horoscope data", "errors": horoscope_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            family_serializer = serializers.PersonalFamSerilizer(family_details, data=request.data, partial=True)
            if family_serializer.is_valid():
                family_serializer.save()
            else:
                return JsonResponse({"status": "error", "message": "Invalid family details data", "errors": family_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({"status": "success", "message": "Profile updated successfully"}, status=status.HTTP_200_OK)

        except models.Horoscope.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Horoscope details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Familydetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Family details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class GetMyProfileEducation(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')  
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            education_details = models.Edudetails.objects.get(profile_id=profile_id)
            education_serializer = serializers.PersonalEdudetailsSerializer(education_details)

            highest_education_id = education_serializer.data.get("highest_education")
            try:
                if highest_education_id:
                    education_level = models.Edupref.objects.get(RowId=highest_education_id)
                    education_level_name = education_level.EducationLevel
                else:
                    education_level=None
                    education_level_name=''
            
            except models.Edupref.DoesNotExist:
                education_level_name = None

            annual_income_id = education_serializer.data.get("anual_income")
            try:
                if annual_income_id:
                    annual_income = models.Annualincome.objects.get(id=annual_income_id)
                    annual_income_name = annual_income.income
                else:
                    annual_income=None
                    annual_income_name=''
            except models.Annualincome.DoesNotExist:
                annual_income_name = None

            work_country_id = education_serializer.data.get("work_country")
            try:
                work_country = models.Profilecountry.objects.get(id=work_country_id) if work_country_id else None
                work_country_name = work_country.name if work_country else None
            except models.Profilecountry.DoesNotExist:
                work_country_name = None

            work_state_id = education_serializer.data.get("work_state")

            if work_state_id is None:
                work_state_name = None
            elif isinstance(work_state_id, str) and not work_state_id.isdigit():
                # If it's a string and not a number, assign it directly
                work_state_name = work_state_id.strip()  # Remove accidental spaces
            else:
                try:
                    # Convert to int only if it's a valid number
                    work_state = models.Profilestate.objects.filter(id=int(work_state_id)).first()
                    work_state_name = work_state.name if work_state else None
                except (ValueError, TypeError):
                    work_state_name = None  # Handle invalid ID

            

            # work_city_id = education_serializer.data.get("work_city")
            # try:
            #     work_city = models.Profilecity.objects.get(id=work_city_id) if work_city_id else None
            #     work_city_name = work_city.name if work_state else None
            # except models.Profilecity.DoesNotExist:
            #     work_city_name = None
        
            data = {
                "personal_edu_id": highest_education_id,
                "personal_edu_name": education_level_name,
                "persoanl_edu_details": education_serializer.data.get("education_details"),
                # "persoanl_field_ofstudy": education_serializer.data.get("field_ofstudy"),
                "persoanl_field_ofstudy":education_serializer.data.get("field_ofstudy"),
                "persoanl_field_ofstudy_name": get_field_of_study_display(education_serializer.data.get("field_ofstudy")),
                "persoanl_degree": education_serializer.data.get("degree"),
                "persoanl_degree_name":  get_field_of_degree_display(education_serializer.data.get("degree")),
                "persoanl_edu_other": education_serializer.data.get("other_degree"),
                "personal_about_edu": education_serializer.data.get("about_edu"),
                "personal_profession": education_serializer.data.get("profession"),
                "personal_profession_name": getprofession(education_serializer.data.get("profession")),
                "personal_ann_inc_id": annual_income_id, 
                "personal_ann_inc_name": annual_income_name, 
                "personal_gross_ann_inc": education_serializer.data.get("actual_income"),
                "personal_work_coun_id": work_country_id,
                "personal_work_coun_name": work_country_name,
                "personal_work_sta_id": work_state_id,
                "personal_work_sta_name": work_state_name,
                "personal_work_district": get_district_name(education_serializer.data.get("work_district")),
                "personal_work_district_id":education_serializer.data.get("work_district"),
                "personal_work_city_name": get_city_name(education_serializer.data.get("work_city")),
                "personal_work_city_id": education_serializer.data.get("work_city"),
                "personal_work_place": education_serializer.data.get("work_place"),
                "personal_work_pin": education_serializer.data.get("work_pincode"),
                "personal_career_plans": education_serializer.data.get("career_plans"),

                "personal_incom_currency": education_serializer.data.get("currency"),
                "personal_company_name": education_serializer.data.get("company_name"),
                "personal_designation": education_serializer.data.get("designation"),
                "personal_profess_details": education_serializer.data.get("profession_details"),
                "personal_business_name": education_serializer.data.get("business_name"),
                "personal_business_addresss": education_serializer.data.get("business_address"),
                "personal_nature_of_business": education_serializer.data.get("nature_of_business"),

                "personal_business_name": education_serializer.data.get("business_name"),
                "personal_business_addresss": education_serializer.data.get("business_address"),
                "personal_nature_of_business": education_serializer.data.get("nature_of_business"),
                

            }

            response = {
                "status": "success",
                "message": "Eduvation details fetched successfully",
                "data": data
            }

            return JsonResponse(response, status=status.HTTP_200_OK)
        
        except models.Edudetails.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Education details not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Edupref.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Education level not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Annualincome.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Annual income not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Profilecountry.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Work country not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.Profilestate.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Work state not found"}, status=status.HTTP_404_NOT_FOUND)


def get_field_of_study_display(value):
    """
    Returns a comma-separated string of FieldOfStudy names based on ID input.
    If the input is already a non-numeric string, it returns it as-is.

    Args:
        value (str): Comma-separated ID string or label string.

    Returns:
        str: Comma-separated FieldOfStudy names or original string.
    """
    if not value:
        return ""

    parts = [p.strip() for p in value.split(',') if p.strip()]

    if all(p.isdigit() for p in parts):
        ids = [int(p) for p in parts]
        fields = models.Profilefieldstudy.objects.filter(id__in=ids).values_list('field_of_study', flat=True)
        return ", ".join(fields)
    
    # If it's not numeric, assume it's already display text
    return value


def get_field_of_degree_display(value):
    """
    Returns a comma-separated string of FieldOfStudy names based on ID input.
    If the input is already a non-numeric string, it returns it as-is.

    Args:
        value (str): Comma-separated ID string or label string.

    Returns:
        str: Comma-separated FieldOfStudy names or original string.
    """
    if not value:
        return ""

    parts = [p.strip() for p in value.split(',') if p.strip()]

    if all(p.isdigit() for p in parts):
        ids = [int(p) for p in parts]
        fields = models.Profileedu_degree.objects.filter(id__in=ids).values_list('degeree_name', flat=True)
        return ", ".join(fields)
    
    # If it's not numeric, assume it's already display text
    return value


class UpdateMyProfileEducation(APIView):
    def post(self, request):
        try:
            profile_id = request.data.get('profile_id')

            if not profile_id:
                return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            education = models.Edudetails.objects.get(profile_id=profile_id)

            education_serializer = serializers.PersonalEdudetailsSerializer(education, data=request.data, partial=True)
            notification_message=""
            notification_titile="Change In "
            print('notification','dfsdf')
            if education_serializer.is_valid():
                validated_data = education_serializer.validated_data

                highest_education_id = request.data.get('education_level')
                print('highest_education_id',highest_education_id)
                if highest_education_id is not None:
                    print("education is not none")
                    try:
                        highest_education_id = int(highest_education_id)
                        if models.Edupref.objects.filter(RowId=highest_education_id).exists():
                            # education.highest_education = highest_education_id
                            
                            #  print('education.highest_education',education.highest_education)
                            #  print('highest_education_id',highest_education_id)
                            if not education.highest_education or not str(education.highest_education).isdigit() or int(education.highest_education) != highest_education_id:

                                # print('Not eaual is true')

                                education.highest_education = highest_education_id
                                notification_message = "Highest education "
                                notification_titile +=" Highest Education "
                                # print('Not equal is false')

                        else:
                            return JsonResponse({"status": "error", "message": "Invalid education level ID"}, status=status.HTTP_400_BAD_REQUEST)
                    except ValueError:
                        return JsonResponse({"status": "error", "message": "Education level ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
                
                anual_income_id = request.data.get('annual_income')
                print("come to actual income1")
                if anual_income_id is not None:
                    # print("come to actual income2")
                    try:
                        # print("come to actual income3")
                        anual_income_id = int(anual_income_id)
                        print("come to actual income3",anual_income_id)
                        if models.Annualincome.objects.filter(id=anual_income_id).exists():
                          
                            # education.anual_income = anual_income_id

                            if education.anual_income != anual_income_id:
                             
                                education.anual_income = anual_income_id
                                
                                notification_message += "Annual income "
                                notification_titile +=" Annual income "
                              
                            
                            else:
                                print('else part is printing')
                            
                        else:
                            return JsonResponse({"status": "error", "message": "Invalid annual income ID"}, status=status.HTTP_400_BAD_REQUEST)
                    except ValueError:
                        return JsonResponse({"status": "error", "message": "Annual income ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
                
               
                education_serializer.save()
                
                # print('notify_message',notification_message)

                if notification_message:
                    # print('12345')
                    # notify_related_profiles(profile_id,'Profile_update',notification_titile,notification_message)
                      print('add to notification queue')
                      addto_notification_queue(profile_id,'Profile_update',notification_titile,notification_message)

                return JsonResponse({
                    "status": "success",
                    "message": "Education details updated successfully"
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Validation error",
                    "errors": education_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except models.Edudetails.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Education details not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # print("Exception:", e)
            return JsonResponse({
                "status": "error",
                "message": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Update_profile_visibility(APIView):
    def post(self, request):
        serializer = serializers.ProfileVisibilitySerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')

            try:
                # Check if the profile_id exists in Registration1 table
                models.Registration1.objects.get(ProfileId=profile_id)

                # Check if profile visibility preferences already exist for the profile_id
                try:
                    profile_visibility = models.ProfileVisibility.objects.get(profile_id=profile_id)
                    # Update existing profile visibility preferences
                    for key, value in serializer.validated_data.items():
                        setattr(profile_visibility, key, value)
                    profile_visibility.save()
                    return JsonResponse({"Status": 1, "message": "Profile visibility details updated successfully"}, status=status.HTTP_200_OK)
                
                except models.ProfileVisibility.DoesNotExist:
                    # Create new profile visibility preferences
                    serializer.save()
                    return JsonResponse({"Status": 1, "message": "Profile visibility details saved successfully"}, status=status.HTTP_201_CREATED)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "Invalid Profile_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_profile_visibility(APIView):
    def post(self, request):
        #profile_id = request.query_params.get('profile_id', None)
        profile_id = request.data.get('profile_id')
        
        if profile_id:
            profile_visibility = models.ProfileVisibility.objects.filter(profile_id=profile_id)
            
            if not profile_visibility.exists():
                return JsonResponse({"Status": 0, "message": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            profile_visibility = models.ProfileVisibility.objects.all()
        
        serializer = serializers.ProfileVisibilityListSerializer(profile_visibility, many=True)
        
        return JsonResponse({"data": serializer.data}, status=status.HTTP_200_OK)



def addto_notification_queue(profile_id, update_type, message_title, message_text):
    """
    Add a single notification to the NotificationQueue for a specific profile.
    """
    try:
        # Get the profile details       
        # Add the notification to the NotificationQueue
        models.NotificationQueue.objects.create(
            profile_id=profile_id,           # The profile that will receive the notification
            notification_type=update_type,   # E.g., "Profile Update"
            message_title=message_title,     # Title of the notification
            message_text=message_text,  # Detailed message for the notification
            is_processed=0,  
            is_taken=0,            # Mark the notification as unprocessed
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # print(f"Notification queued for Profile ID: {profile_id}")
    except Exception as e:
        print(f"Error while adding to notification queue: {str(e)}")




class notify_to_profiles(APIView):
      
        def get(self, request):
            
            

                
                current_time = timezone.now().replace(microsecond=0)

                # Update notifications to mark them as taken where is_taken is False and timestamp <= current time
                models.NotificationQueue.objects.filter(
                    is_taken=0
                ).filter(
                    Q(take_datetime__isnull=True) | ~Q(take_datetime=current_time)
                ).update(
                    is_taken=1, take_datetime=current_time
                )
                print('current_time',current_time)
                
                unprocessed_notifications = models.NotificationQueue.objects.filter(is_processed=0,is_taken=1,take_datetime=current_time)

                print(unprocessed_notifications)

                for notification in unprocessed_notifications:
                # print(profile_id,update_type, message_title)
                        print('notification ',notification)
                        related_profiles = set()

                        # Add profiles from wishlist
                        related_profiles.update(get_wishlist_related_profiles(notification.profile_id))

                        user_profile=models.Registration1.objects.get(ProfileId=notification.profile_id)
                        profile_name=user_profile.Profile_name
                        # Add profiles from visitor logs
                        visitor_profiles = get_profile_visitor_related_profiles(notification.profile_id)

                        # Add visitor_profiles to related_profiles
                        related_profiles.update(visitor_profiles)

                        #  Add profiles from private notes
                        related_profiles.update(get_private_notes_related_profiles(notification.profile_id))

                        #  Add profiles from expressint
                        related_profiles.update(get_expressint_related_profiles(notification.profile_id))

                        # Remove the profile itself from the list (they shouldn't receive a notification about their own update)
                        if notification.profile_id in related_profiles:
                            related_profiles.remove(notification.profile_id)

                        to_message=f"{profile_name} the profile you have visited has changed the{notification.message_text} . Check it out !"

                        # Add notifications for each related profile

                        
                        for related_profile_id in related_profiles:
                            try:
                                # Log each profile being processed
                                print(f"Processing related_profile_id: {related_profile_id}")
                                models.Profile_notification.objects.create(
                                    profile_id=related_profile_id,  # The profile that will receive the notification
                                    from_profile_id=notification.profile_id,  # The profile that triggered the update
                                    notification_type=notification.notification_type,  # E.g., "Profile Update"
                                    message_titile=notification.message_title,  # Title of the notification
                                    to_message=to_message,  # Detailed message
                                    is_read=0,  # Mark as unread
                                    created_at=timezone.now(),
                                    updated_at=timezone.now()
                                )
                                from_profile_id=notification.profile_id
                                to_profile=models.Registration1.objects.get(ProfileId=related_profile_id)
                                choosen_medium=to_profile.Notifcation_enabled
                                message_title=notification.message_title
                                
                                
                                if(choosen_medium):
                                                            
                                        chosen_alert_types = [int(alert_type) for alert_type in choosen_medium.split(',')]
                                        
                                        # Fetch alert settings based on chosen_alert_types
                                        alert_settings = models.ProfileAlertSettings.objects.filter(id__in=chosen_alert_types,notification_type='update_profile' , status=1)
                                        
                                        print(alert_settings)
                                        
                                        send_email = False
                                        send_sms = False

                                        for alert_setting in alert_settings:
                                            if alert_setting.alert_type == 1:  # Assuming '1' is for email
                                                send_email = True
                                            elif alert_setting.alert_type == 2:  # Assuming '2' is for SMS
                                                send_sms = True

                                        # print('send_email',send_email)
                                        # print('send_sms',send_sms)
                                        notification_type='update_profile'
                                        if send_email:
                                            send_email_notification(from_profile_id,profile_name,to_profile.Profile_name,to_profile.EmailId, message_title, to_message,notification_type)

                                        # Send SMS notification if the user has enabled SMS notifications
                                        # if send_sms:
                                        #     send_sms_notification(from_profile_id,profile_name,to_profile.Profile_name,to_profile.Mobile_no, message_title, to_message)
                            
                            except Exception as e:
                                  print(f"Error processing profile {related_profile_id}: {str(e)}")
                                    # Continue processing the next profile
                                  continue


                        notification.is_processed = 1
                        notification.updated_at = timezone.now()
                        notification.save()
            

            
                return JsonResponse({
                    "status": "success",
                    "message": "Notification send successfully"
                }, status=status.HTTP_200_OK)       
                    

# def send_email_notification(from_profile_id,from_profile_name,to_name,to_email, message_title, to_message,notification_type):
#         print('from_profile_id',from_profile_id,notification_type)
#         subject = message_title
        
        
#         if (notification_type=='update_profile'):
        
#             context = {
#                 'recipient_name': to_name,
#                 'profile_name': from_profile_name,
#                 'updated_details':to_message,
#                 'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id
#             }

#             html_content = render_to_string('user_api/authentication/profile_update_notification.html', context)
        
#         elif(notification_type=='express_interests'):

#             context = {
#                 'recipient_name': to_name,
#                 'profile_name': from_profile_name,
#                 'from_profile_id': from_profile_id,
#                 'updated_details':to_message,
#                 'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id
#             }

#         elif(notification_type=='express_interests_update'):

#             context = {
#                 'recipient_name': to_name,
#                 'profile_name': from_profile_name,
#                 'from_profile_id': from_profile_id,
#                 'updated_details':to_message,
#                 'profile_link':'http://matrimonyapp.rainyseasun.com/ProfileDetails?'+ from_profile_id
#             }

#             html_content = render_to_string('user_api/authentication/send_express_Interests.html', context)

#         recipient_list = [to_email]

#         # send_mail(subject,settings.DEFAULT_FROM_EMAIL,recipient_list,fail_silently=False,html_message=html_content)
#         from_email = settings.DEFAULT_FROM_EMAIL

#         send_mail(
#                 subject,
#                 '',  # No plain text version
#                 from_email,
#                 recipient_list,  # Recipient list should be a list
#                 fail_silently=False,
#                 html_message=html_content
#             )
#         print('Email send sucessfully')

def get_private_notes_related_profiles(profile_id):
    
    return models.Profile_personal_notes.objects.filter(profile_to=profile_id).values_list('profile_id', flat=True)



def get_wishlist_related_profiles(profile_id):
    """Get profiles that have this profile in their wishlist"""
    return models.Profile_wishlists.objects.filter(profile_from=profile_id).values_list('profile_to', flat=True)


# def get_profile_visitor_related_profiles(profile_id):
#     """Get profiles that have visited or been visited by this profile"""
#     return models.Profile_visitors.objects.filter(
#         models.Q(profile_id=profile_id) | models.Q(viewed_profile=profile_id)
#     ).values_list('profile_id', 'viewed_profile')

def get_profile_visitor_related_profiles(profile_id):
   
    """Get profiles that have either visited this profile or were visited by this profile."""
    # Check who viewed this profile
    viewed_visitors = models.Profile_visitors.objects.filter(viewed_profile=profile_id).values_list('profile_id', flat=True)
    print(f"Profiles who viewed {profile_id}: {viewed_visitors}")

    # Check profiles that this profile has visited
    visiting_profiles = models.Profile_visitors.objects.filter(profile_id=profile_id).values_list('viewed_profile', flat=True)
    print(f"Profiles visited by {profile_id}: {visiting_profiles}")

    # Combine and return unique profiles
    unique_profiles = set(viewed_visitors).union(set(visiting_profiles))
    print(f"Unique Profiles: {unique_profiles}")
    return unique_profiles

def get_expressint_related_profiles(profile_id):
   
    """Get profiles that have either visited this profile or were visited by this profile."""
    # Check who viewed this profile
    intr_sent = models.Express_interests.objects.filter(profile_from=profile_id,status=2).values_list('profile_to', flat=True)
    print(f"Profiles intrests sent {profile_id}: {intr_sent}")

    # Check profiles that this profile has visited
    intr_rece = models.Express_interests.objects.filter(profile_to=profile_id,status=2).values_list('profile_from', flat=True)
    print(f"Profiles intrests receive {profile_id}: {intr_rece}")

    # Combine and return unique profiles
    unique_profiles = set(intr_sent).union(set(intr_rece))
    print(f"Unique Profiles: {unique_profiles}")
    return unique_profiles




      
    # return visitors
    # print('1223423434dfsdfsdfg')
    # # Check if the query returned any data
    # if not visitors:
    #     print(f"No visitors found for profile ID: {profile_id}")
    #     return set()  # Return empty set if no visitors found
    
    # print('1223423434dfsdfsdfg')

    # # Flatten the tuples and return a set of unique profile IDs
    # unique_profiles = set()
    # for visitor in visitors:
    #     print(f"Visitor Tuple: {visitor}")  # Debug print to check each visitor tuple
    #     profile_id, viewed_profile = visitor
    #     unique_profiles.add(profile_id)
    #     unique_profiles.add(viewed_profile)  # Ensure both values are added

    # print(f"Unique Profiles: {unique_profiles}")
    # return unique_profiles




class GetMyProfileContact(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch contact details
        contact_details = models.Registration1.objects.filter(ProfileId=profile_id).first()
        
        if not contact_details:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        contact_serializer = serializers.Registration1ContactSerializer(contact_details)

        country_id = contact_serializer.data.get("Profile_country")
        state_id = contact_serializer.data.get("Profile_state")

        # country_name = models.Profilecountry.objects.filter(id=country_id).first().name if country_id else "Country not found"
        # state_name = models.Profilestate.objects.filter(id=state_id).first().name if state_id else "State not found"
        
        data = {
            "personal_prof_addr": contact_serializer.data.get("Profile_address"),
            "personal_prof_city": contact_serializer.data.get("Profile_city"),
            "personal_prof_stat_id": contact_serializer.data.get("Profile_state"),
            "personal_prof_stat_name": get_state_name(contact_serializer.data.get("Profile_state")),
            "personal_prof_count_id": contact_serializer.data.get("Profile_country"),
            "personal_prof_count_name": get_country_name(contact_serializer.data.get("Profile_country")),
            "personal_prof_district_id": contact_serializer.data.get("Profile_district"),
            "personal_prof_district_name": get_district_name(contact_serializer.data.get("Profile_district")),
            "personal_prof_city_id": contact_serializer.data.get("Profile_city"),
            "personal_prof_city_name": get_city_name(contact_serializer.data.get("Profile_city")),
            "personal_prof_pin": contact_serializer.data.get("Profile_pincode"),
            "personal_prof_phone": contact_serializer.data.get("Profile_alternate_mobile"),
            "personal_prof_mob_no": contact_serializer.data.get("Profile_mobile_no"),
            "personal_prof_whats": contact_serializer.data.get("Profile_whatsapp"),
            "personal_email": contact_serializer.data.get("EmailId"),
            "admin_use_email":contact_serializer.data.get("Profile_emailid")
        }

        return JsonResponse({
            "status": "success",
            "message": "Contact details fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)


class UpdateMyProfileContact(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contact_details = models.Registration1.objects.get(ProfileId=profile_id)
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        contact_serializer = serializers.Registration1ContactSerializer(contact_details, data=request.data, partial=True)

        if contact_serializer.is_valid():
            validated_data = contact_serializer.validated_data

            country_id = validated_data.get('Profile_country')
            state_id = validated_data.get('Profile_state')

            if country_id is not None:
                if models.Profilecountry.objects.filter(id=country_id).exists():
                    contact_details.Profile_country = country_id
                else:
                    return JsonResponse({"status": "error", "message": "Invalid country ID"}, status=status.HTTP_400_BAD_REQUEST)

            if state_id:
                if models.Profilestate.objects.filter(id=state_id).exists():
                    contact_details.Profile_state = state_id
                else:
                    return JsonResponse({"status": "error", "message": "Invalid state ID"}, status=status.HTTP_400_BAD_REQUEST)
            contact_serializer.save()

            return JsonResponse({
                "status": "success",
                "message": "Contact details updated successfully"
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Validation error",
                "errors": contact_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        




class GetAlertSettings(APIView):
    def post(self, request):
        alert_settings = models.ProfileAlertSettings.objects.all()
        
        email_alerts = []
        sms_alerts = []
        
        for alert in alert_settings:
            if alert.status == 1:
                alert_data = {
                    "id": alert.id,
                    "alert_name": alert.alert_name
                }
                
                if alert.alert_type == 1:
                    email_alerts.append(alert_data)
                elif alert.alert_type == 2:
                    sms_alerts.append(alert_data)

        response_data = {
            "status": "1",  
            "message": "Alert settings fetched successfully",
            "data": {
                "Email Alerts": email_alerts,
                "SMS Alerts": sms_alerts
            }
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)




class GetAlertSettingsByProfile(APIView):
    def post(self, request):
        # Retrieve ProfileId from the request data
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({
                "status": "0",  
                "message": "profile_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile = models.Registration1.objects.filter(ProfileId=profile_id).first()
        
        if not profile:
            return JsonResponse({
                "status": "0",
                "message": "Profile not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if not profile.Notifcation_enabled:
            return JsonResponse({
                "status": "0",
                "message": "No notifications enabled for this profile."
            }, status=status.HTTP_200_OK)

        notification_ids = profile.Notifcation_enabled.split(",")

        alerts = models.ProfileAlertSettings.objects.filter(id__in=notification_ids, status=1)
        alert_data = [
            {"id": alert.id, "alert_name": alert.alert_name}
            for alert in alerts
        ]

        return JsonResponse({
            "status": "1",  
            "message": "Alert settings fetched successfully",
            "data": alert_data
        }, status=status.HTTP_200_OK)


class UpdateNotificationSettings(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        notification_enabled = request.data.get('Notifcation_enabled')
        
        if not profile_id or not notification_enabled:
            return JsonResponse({
                "status": "0", 
                "message": "ProfileId and Notifcation_enabled are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile = models.Registration1.objects.filter(ProfileId=profile_id).first()
        if not profile:
            return JsonResponse({
                "status": "0",
                "message": "Profile not found."
            }, status=status.HTTP_404_NOT_FOUND)

        profile.Notifcation_enabled = notification_enabled
        profile.save()

        return JsonResponse({
            "status": "1",  
            "message": "Notification settings updated successfully"
        }, status=status.HTTP_200_OK)
    


class GetMyProfilePartner(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        partner_preferences = models.Partnerpref.objects.filter(profile_id=profile_id).first()
        
        if not partner_preferences:
            return JsonResponse({"status": "error", "message": "Partner preferences not found for this profile ID"}, status=status.HTTP_404_NOT_FOUND)

        partner_serializer = serializers.ParPrefSerializer(partner_preferences)

        education_ids = partner_serializer.data.get("pref_education", "").split(',')
        education_names = []

        for education_id in education_ids:
            if education_id:
                try:
                    education = models.Edupref.objects.get(RowId=education_id)
                    education_names.append(education.EducationLevel)
                except models.Edupref.DoesNotExist:
                    education_names.append("Education level not found")

        education_names_str = ', '.join(education_names)

        data = {
            "partner_age": partner_serializer.data.get("pref_age_differences"),
            "partner_height_from": partner_serializer.data.get("pref_height_from"),
            "partner_height_to": partner_serializer.data.get("pref_height_to"),
            "partner_edu_id": partner_serializer.data.get("pref_education"),
            "partner_edu_names": education_names_str,  
            "partner_profe": partner_serializer.data.get("pref_profession"),
            "partner_ann_inc": partner_serializer.data.get("pref_anual_income"),
            "partner_rahu_kethu": partner_serializer.data.get("pref_ragukethu"),
            "partner_chev_dho": partner_serializer.data.get("pref_chevvai"),
            "partner_porutham_ids": partner_serializer.data.get("pref_porutham_star"),
            "partner_porutham_star_rasi": partner_serializer.data.get("pref_porutham_star_rasi"),
            "partner_marital_status": partner_serializer.data.get("pref_marital_status"),
            "partner_forign_int": partner_serializer.data.get("pref_foreign_intrest"),
            "partner_ann_inc_max": partner_serializer.data.get("pref_anual_income_max")
        }

        return JsonResponse({
            "status": "success",
            "message": "Partner preferences fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)

class UpdateMyProfilePartner(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner_preferences = models.Partnerpref.objects.get(profile_id=profile_id)
        except models.Partnerpref.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Partner preferences not found for this profile ID"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()

        pref_star_ids = data.get('pref_porutham_star')
        if pref_star_ids:
            try:
                id_list = [int(i.strip()) for i in pref_star_ids.split(',') if i.strip().isdigit()]
 
                matches = models.MatchingStarPartner.objects.filter(id__in=id_list)
 
                star_rasi_pairs = [f"{m.dest_star_id}-{m.dest_rasi_id}" for m in matches]
 
                # Add to the mutable copy
                data['pref_porutham_star_rasi'] = ",".join(star_rasi_pairs)
 
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Invalid pref_porutham_star input. Error: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        # serializer = serializers.ParPrefSerializer(partner_preferences, data=request.data, partial=True)
        serializer = serializers.ParPrefSerializer(partner_preferences, data=data, partial=True)


        if serializer.is_valid():
            serializer.save()  
            return JsonResponse({
                "status": "success",
                "message": "Partner preferences updated successfully",
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "error", "message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class GetSearchResults(APIView):

    def post(self, request):
        # Extract the input data from the JSON body (POST request)
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'Profile ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        # Need to get gender from logindetails table
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Gender FROM logindetails WHERE ProfileId = %s", [profile_id])
                gender = cursor.fetchone()
                if not gender:
                    return JsonResponse({'status': 'failure', 'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
                gender = gender[0]

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract input values from request data (POST request)
        from_age = request.data.get('from_age')
        to_age = request.data.get('to_age')
        from_height = request.data.get('from_height')
        to_height = request.data.get('to_height')
        marital_status = request.data.get('search_marital_status')
        profession = request.data.get('search_profession')
        education = request.data.get('search_education')
        income = request.data.get('search_income')
        max_income = request.data.get('max_income')
        min_income = request.data.get('min_income')
        field_ofstudy = request.data.get('field_ofstudy')
        star = request.data.get('search_star')
        native_state = request.data.get('search_nativestate')
        search_worklocation = request.data.get('search_worklocation')
        search_profilephoto = request.data.get('search_profilephoto')
        people_withphoto = request.data.get('people_withphoto')
        chevvai_dhosam = request.data.get('chevvai_dhosam')
        ragukethu_dhosam = request.data.get('ragukethu_dhosam')
        
        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')


        if not any([
            from_age, to_age, from_height, to_height, marital_status, profession, 
            education, income, star, native_state, search_worklocation, 
            search_profilephoto, people_withphoto, chevvai_dhosam, ragukethu_dhosam
        ]):
            return JsonResponse({'status': 'failure', 'message': "At least one search criterion must be provided."}, status=status.HTTP_200_OK)




        # Set default values if not provided
        if received_per_page is None:
            per_page = 10
        else:
            try:
                per_page = int(received_per_page)
            except (ValueError, TypeError):
                per_page = 10  # Fall back to default if conversion fails

        if received_page_number is None:
            page_number = 1
        else:
            try:
                page_number = int(received_page_number)
            except (ValueError, TypeError):
                page_number = 1  # Fall back to default if conversion fails

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        # Initialize the query with the base structure
        base_query = """
        SELECT distinct(a.ProfileId),a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income , e.birthstar_name , e.birth_rasi_name
                       ,a.Photo_protection,a.Gender        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        JOIN profile_images  pi ON pi.profile_id=a.ProfileId
        WHERE a.gender != %s AND a.ProfileId != %s  AND a.plan_status NOT IN (16, 17, 3) AND a.status=1
        """

        # Prepare the query parameters
        query_params = [gender, profile_id]

        # Check if additional filters are provided, and add them to the query
        if from_age or to_age or from_height or to_height or marital_status or profession or education or income or star:
            # Add age filter
            age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=" if from_age else "<=" if to_age else None
            if age_condition_operator:
                base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
                if from_age and to_age:
                    query_params.extend([from_age, to_age])
                else:
                    query_params.append(from_age or to_age)
            
            # Add marital status filter
            if marital_status:
                # base_query += " AND a.Profile_marital_status = %s"
                base_query += " AND FIND_IN_SET(%s, a.Profile_marital_status)"
                query_params.append(marital_status)

            # Add profession filter
            if profession:
                # base_query += " AND f.profession = %s"
                base_query += " AND FIND_IN_SET(%s, f.profession)"
                query_params.append(profession)

            # Add education filter
            if education:
                base_query += " AND f.highest_education = %s"
                query_params.append(education)

            if field_ofstudy:
                base_query += " AND f.field_ofstudy = %s"
                query_params.append(field_ofstudy)

            if people_withphoto:
                base_query += " AND pi.profile_id IS NOT NULL AND pi.image_approved=1"
                
            # Add income filter
            if income:
                base_query += " AND h.income >= %s"
                query_params.append(income)

            # Add star filter
            if star:
                base_query += " AND d.star = %s"
                query_params.append(star)

            # if chevvai_dhosam:
            #     base_query += " AND e.chevvai_dosaham = %s"
            #     query_params.append(chevvai_dhosam)
            
            # if ragukethu_dhosam:
            #     base_query += " AND e.ragu_dosham = %s"
            #     query_params.append(ragukethu_dhosam)

            if chevvai_dhosam and chevvai_dhosam.lower() == 'yes':
                base_query += " AND LOWER(e.ragu_dosham) = 'yes'"
            elif chevvai_dhosam and chevvai_dhosam.lower() == 'no':
                base_query += " AND LOWER(e.ragu_dosham) = 'no'"

            if ragukethu_dhosam and ragukethu_dhosam.lower() == 'yes':
                base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
            elif ragukethu_dhosam and ragukethu_dhosam.lower() == 'no':
                base_query += " AND LOWER(e.chevvai_dosaham) = 'no'"

            if native_state:
                base_query += " AND a.Profile_state = %s"
                query_params.append(native_state)

            if search_worklocation:
                base_query += " AND f.work_state = %s"
                query_params.append(search_worklocation)

            if min_income and max_income:
                    base_query += " AND a.anual_income BETWEEN %s AND %s"
                    query_params.extend([min_income, max_income])
    
            # Handle height conditions
            if from_height and to_height:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([from_height, to_height])
            elif from_height:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(from_height)
            elif to_height:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(to_height)


        try:
            with connection.cursor() as cursor:
                    cursor.execute(base_query, query_params)
                    all_profile_ids = [row[0] for row in cursor.fetchall()]

                # Log or store all_profile_ids as needed
            #print("All Profile IDs:", all_profile_ids)

                # Get the total count of profiles
            total_count = len(all_profile_ids)

            # profile_with_indices = [{"index": i + 1, "profile_id": profile_id} for i, profile_id in enumerate(all_profile_ids)]
            profile_with_indices={str(i + 1): profile_id for i, profile_id in enumerate(all_profile_ids)}

        


        # count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_query"

        #         # Execute the count query to get the total number of records
        # with connection.cursor() as cursor:
        #     cursor.execute(count_query, query_params)
        #     total_count = cursor.fetchone()[0]  # Fetch the count


        # print('total_count',total_count)
            print('why not print')

            # Add pagination to the query
            # Modify the query to use LIMIT with start and count
            base_query += f" LIMIT %s, %s"
            query_params.extend([start, per_page])

            try:
                print('iam  print')
                with connection.cursor() as cursor:
                    cursor.execute(base_query, query_params)
                    print("Executing SQL:", cursor.mogrify(base_query, query_params))
                    rows = cursor.fetchall()

                    if rows:
                        print('iam  to printing')
                        columns = [col[0] for col in cursor.description]
                        results = [dict(zip(columns, row)) for row in rows]

                        # Log or return the full query for debugging
                        full_query = cursor.mogrify(base_query, query_params)
                        print(full_query,'full_query')

                        profilehoro_data =  models.Horoscope.objects.get(profile_id=profile_id)
                
                        source_rasi_id=profilehoro_data.birth_rasi_name
                        source_star_id=profilehoro_data.birthstar_name


                        transformed_results = [transform_data(result,profile_id,gender,source_rasi_id,source_star_id) for result in results]

                        return JsonResponse({
                            'status': 'success',
                            'total_count':total_count,
                            # 'data': results,
                            'data': transformed_results,
                            # 'query': full_query,  # Include the formatted query in the response
                            'received_per_page': received_per_page,
                            'received_page_number': received_page_number,
                            'calculated_per_page': per_page,
                            'calculated_page_number': page_number,
                            'all_profile_ids':profile_with_indices
                        }, status=status.HTTP_200_OK)
                    else:
                        print('iam  executing')
                        # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)
                        return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print('why print')
                return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('its print')
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def get_city_name(city_id):
#     # Check if the city_id is a valid integer (number)
#     if isinstance(city_id, int):
#         try:
#             # Attempt to retrieve the city object
#             city = models.Profilecity.objects.get(id=city_id)
#             return city.city_name  # Return the city name if found
#         except models.Profilecity.DoesNotExist:
#             return city_id  # Return city_id if the city does not exist
#     else:
#         # If city_id is not a number, return it directly
#         return city_id

def get_city_name(city_id):
    try:
        # Attempt to retrieve the city object using the string city_id
        city = models.Profilecity.objects.get(id=city_id)
        return city.city_name  # Return the city name if found
    except models.Profilecity.DoesNotExist:
        return city_id  # Return city_id if the city does not exist
    except Exception as e:
        return city_id 

def get_state_name(state_id):
    try:
        # Attempt to retrieve the city object using the string city_id
        state = models.Profilestate.objects.get(id=state_id)
        return state.name  # Return the city name if found
    except models.Profilestate.DoesNotExist:
        return state_id  # Return city_id if the city does not exist
    except Exception as e:
        return state_id 

def get_district_name(district_id):
    try:
        # Attempt to retrieve the city object using the string city_id
        district = models.Profiledistrict.objects.get(id=district_id)
        return district.name  # Return the city name if found
    except models.Profiledistrict.DoesNotExist:
        return district_id  # Return city_id if the city does not exist
    except Exception as e:
        return district_id 

def get_dasa_name(dasa_id):
    # print('dasa_id',dasa_id)
    try:
        # Attempt to retrieve the city object using the string city_id
        print('dasa_id',dasa_id)
        dasa =  models.Dasaname.objects.get(id=dasa_id)
        print('dasa name',dasa.name)
        return dasa.name  # Return the city name if found
    except models.Dasaname.DoesNotExist:
        return dasa_id  # Return city_id if the city does not exist
    except Exception as e:
        return dasa_id 
    
def get_country_name(country_id):
    try:
        # Attempt to retrieve the city object using the string city_id
        country = models.Profilecountry.objects.get(id=country_id)
        return country.name  # Return the city name if found
    except models.Profilecountry.DoesNotExist:
        return country_id  # Return city_id if the city does not exist
    except Exception as e:
        return country_id 


class GetFeaturedList(APIView):

    def post(self, request):
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'profile_id is required.'}, status=400)

        # --- Get gender and DOB ---
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Gender, Profile_dob FROM logindetails WHERE ProfileId = %s", [profile_id])
                result = cursor.fetchone()
                if not result:
                    return JsonResponse({'status': 'failure', 'message': 'Profile not found'}, status=404)
                gender, profile_dob = result
                profile_age = calculate_age(profile_dob)
        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=500)

        # --- Pagination ---
        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')
        per_page = int(received_per_page) if received_per_page else 10
        page_number = int(received_page_number) if received_page_number else 1
        per_page = max(1, per_page)
        start = (page_number - 1) * per_page

        # --- Filters from request ---
        from_age = request.data.get('from_age')
        to_age = request.data.get('to_age')
        from_height = request.data.get('from_height')
        to_height = request.data.get('to_height')

        # STEP 1: Get Matching (Partner Preference) IDs
        partner_results = models.Get_profiledata.get_profile_list_for_pref_type(profile_id=profile_id, use_suggested=False)
        partner_ids = set(str(p['ProfileId']) for p in partner_results)
        
        # STEP 2: Get All Featured IDs with Filters
        query = """
            SELECT ProfileId FROM logindetails
            WHERE gender != %s
            AND ProfileId != %s
            AND Plan_id IN (2, 15)
            AND Profile_dob IS NOT NULL AND status =1
        """
        params = [gender, profile_id]

        if from_age:
            query += " AND TIMESTAMPDIFF(YEAR, Profile_dob, CURDATE()) >= %s"
            params.append(int(from_age))
        if to_age:
            query += " AND TIMESTAMPDIFF(YEAR, Profile_dob, CURDATE()) <= %s"
            params.append(int(to_age))
        if from_height:
            query += " AND Profile_height >= %s"
            params.append(int(from_height))
        if to_height:
            query += " AND Profile_height <= %s"
            params.append(int(to_height))

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                featured_ids = set(str(row[0]) for row in cursor.fetchall())
        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=500)

        # STEP 3: Subtract Matching from Featured IDs
        unique_ids = list(featured_ids - partner_ids)

        if not unique_ids:
            return JsonResponse({'status': 'failure', 'message': 'No unique featured profiles found.'}, status=404)

        # STEP 4: Fetch Full Data with JOINs
        placeholders = ','.join(['%s'] * len(unique_ids))
        details_query = f"""
            SELECT DISTINCT a.ProfileId, a.Plan_id, a.DateOfJoin, a.Photo_protection, a.Profile_city,
                   a.Profile_verified, a.Profile_name, a.Profile_dob, a.Profile_height,
                   e.birthstar_name, e.birth_rasi_name,
                   f.ug_degeree, f.profession, f.highest_education,
                   g.EducationLevel, d.star, h.income,
                   IF(i.id IS NOT NULL, 1, 0) AS has_image
            FROM logindetails a
            JOIN profile_horoscope e ON a.ProfileId = e.profile_id
            JOIN masterbirthstar d ON d.id = e.birthstar_name
            JOIN profile_edudetails f ON a.ProfileId = f.profile_id
            JOIN mastereducation g ON f.highest_education = g.RowId
            JOIN masterannualincome h ON h.id = f.anual_income
            LEFT JOIN profile_images i ON a.ProfileId = i.profile_id
                AND i.image_approved = 1 AND i.is_deleted = 0
            WHERE a.ProfileId IN ({placeholders})
            ORDER BY has_image DESC, a.DateOfJoin DESC
            LIMIT %s OFFSET %s
        """

        count_query = f"""
            SELECT COUNT(*) FROM (
                SELECT ProfileId FROM logindetails
                WHERE ProfileId IN ({placeholders})
            ) AS count_alias
        """

        query_params = unique_ids + [per_page, start]
        count_params = unique_ids

        try:
            with connection.cursor() as cursor:
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]

                cursor.execute(details_query, query_params)
                rows = cursor.fetchall()
                if not rows:
                    return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=404)

                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': f'DB Error: {str(e)}'}, status=500)

        # STEP 5: Apply transformation (e.g., horoscope logic)
        try:
            profile_horo = models.Horoscope.objects.get(profile_id=profile_id)
            source_rasi_id = profile_horo.birth_rasi_name
            source_star_id = profile_horo.birthstar_name
        except models.Horoscope.DoesNotExist:
            source_rasi_id = None
            source_star_id = None

        final_data = [
            transform_data(entry, profile_id, gender, source_rasi_id, source_star_id)
            for entry in results
        ]

        return JsonResponse({
            'status': 'success',
            'total_count': total_count,
            'data': final_data,
            'received_per_page': received_per_page,
            'received_page_number': received_page_number,
            'calculated_per_page': per_page,
            'calculated_page_number': page_number,
        }, status=200)

class SuggestedProfiles1(APIView):

    def post(self, request):
            # Extract the input data from the JSON body (POST request)
        profile_id = request.data.get('profile_id')

        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')
        per_page = int(received_per_page) if received_per_page else 10
        page_number = int(received_page_number) if received_page_number else 1

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        if not profile_id:
                return JsonResponse({'status': 'failure', 'message': 'profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        
        profile = get_object_or_404(models.Registration1, ProfileId=profile_id)
        gender = profile.Gender
        suggested_results = models.Get_profiledata.get_profile_list_for_pref_type(
            profile_id=profile_id,
            use_suggested=True
        )
        suggested_ids = set([r['ProfileId'] for r in suggested_results])

        # print('suggested_ids',suggested_ids)

        # Get all user preference profile IDs
        partner_results = models.Get_profiledata.get_profile_list_for_pref_type(
            profile_id=profile_id,
            use_suggested=False
        )
        partner_ids = set([r['ProfileId'] for r in partner_results])
        # print('partner_ids',partner_ids)

        # Subtract
        unique_ids = list(suggested_ids - partner_ids)

        if not unique_ids:

            return JsonResponse({'status': 'failure', 'message': 'No unique suggested profiles found.'}, status=status.HTTP_404_NOT_FOUND)


        # Use raw query to fetch final result details using profile ID list
        placeholders = ','.join(['%s'] * len(unique_ids))
        base_query = f"""
            SELECT DISTINCT a.ProfileId,a.Plan_id ,a.DateOfJoin,a.Photo_protection,a.Profile_city,a.Profile_verified,a.Profile_name,a.Profile_dob,a.Profile_height,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
            WHERE a.ProfileId IN ({placeholders}) 
            ORDER BY a.DateOfJoin DESC LIMIT %s OFFSET %s
        """
        count_query = f"SELECT COUNT(*) FROM ({base_query.replace('LIMIT %s OFFSET %s', '')}) AS count_query"
        count_query_params = list(unique_ids)  # Only the profile_ids for count

        with connection.cursor() as cursor:
            cursor.execute(count_query, count_query_params)
            total_count = cursor.fetchone()[0]


        query_params = list(unique_ids) + [per_page, start]

        try:
            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]                    

                    full_query = cursor.mogrify(base_query, query_params)

                    profilehoro_data =  models.Horoscope.objects.get(profile_id=profile_id)
                    source_rasi_id=profilehoro_data.birth_rasi_name
                    source_star_id=profilehoro_data.birthstar_name
                    transformed_results = [transform_data(result,profile_id,gender,source_rasi_id,source_star_id) for result in results]

                    
                    # print('transformed_results',transformed_results)

                    # print(full_query)  
                    return JsonResponse({
                        'status': 'success',
                        'total_count':total_count,
                        'data':transformed_results,
                        'received_per_page': received_per_page,
                        'received_page_number': received_page_number,
                        'calculated_per_page': per_page,
                        'calculated_page_number': page_number
                    }, status=status.HTTP_200_OK)
                else:
                    full_query = cursor.mogrify(base_query, query_params)
                    print(full_query) 
                    return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class SuggestedProfiles1(APIView):

#     def post(self, request):
#         # Extract the input data from the JSON body (POST request)
#         profile_id = request.data.get('profile_id')

#         if not profile_id:
#             return JsonResponse({'status': 'failure', 'message': 'profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Get gender from logindetails table
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT Gender,Profile_dob FROM logindetails WHERE ProfileId = %s", [profile_id])
#                 result = cursor.fetchone()
                
#                 if result:
#                     gender, profile_dob = result  # unpack the tuple
#                 else:
#                     # Handle no result found
#                     gender = None
#                     profile_dob = None
#                 profile_age=calculate_age(profile_dob)
#         except Exception as e:
#             return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Extract input values from request data (POST request)
#         from_age = request.data.get('from_age')
#         to_age = request.data.get('to_age')
#         from_height = request.data.get('from_height')
#         to_height = request.data.get('to_height')

#         received_per_page = request.data.get('per_page')
#         received_page_number = request.data.get('page_number')

#         # Set default values if not provided
#         per_page = int(received_per_page) if received_per_page else 10
#         page_number = int(received_page_number) if received_page_number else 1

#         # Ensure valid values for pagination
#         per_page = max(1, per_page)
#         page_number = max(1, page_number)

#         # Calculate the starting record for the SQL LIMIT clause
#         start = (page_number - 1) * per_page

#         # Initialize the query with the base structure
        
#         if gender.lower() == 'male':
#             age_condition_operator = '<'
#         else:
#             age_condition_operator = '>'
        
#         base_query = """
#         SELECT DISTINCT b.profile_id,a.*, 
#                f.profession, f.highest_education, g.EducationLevel, d.star, h.income ,d.star as star_name , e.birthstar_name ,e.birth_rasi_name ,
#                IF(i.id IS NOT NULL, 1, 0) AS has_image
#         FROM logindetails a 
#         JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
#         JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
#         JOIN masterbirthstar d ON d.id = e.birthstar_name 
#         JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
#         JOIN mastereducation g ON f.highest_education = g.RowId 
#         JOIN masterannualincome h ON h.id = f.anual_income

#         LEFT JOIN profile_images i 
#         ON a.ProfileId = i.profile_id 
#         AND a.Plan_id !=16
#         AND i.image_approved = 1 
#         AND i.is_deleted = 0

#         WHERE a.gender != %s AND a.ProfileId != %s AND Plan_id IN (2, 3, 15)
#         """

#         base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator} %s   ORDER BY has_image DESC"


#         # Prepare the query parameters
#         query_params = [gender, profile_id, profile_age]
        

#         # Check if additional filters are provided, and add them to the query
#         # if from_age or to_age or from_height or to_height:
#         #     # Add age filter
#         #     age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=" if from_age else "<=" if to_age else None
#         #     if age_condition_operator:
#         #         base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
#         #         if from_age and to_age:
#         #             query_params.extend([from_age, to_age])
#         #         else:
#         #             query_params.append(from_age or to_age)
            
#         #     if from_height and to_height:
#         #         base_query += " AND a.Profile_height BETWEEN %s AND %s"
#         #         query_params.extend([from_height, to_height])
#         #     elif from_height:
#         #         base_query += " AND a.Profile_height >= %s"
#         #         query_params.append(from_height)
#         #     elif to_height:
#         #         base_query += " AND a.Profile_height <= %s"
#         #         query_params.append(to_height)

#         count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_query"

#                     # Execute the count query to get the total number of records
#         with connection.cursor() as cursor:
#                 cursor.execute(count_query, query_params)
#                 total_count = cursor.fetchone()[0]  # Fetch the count




#         base_query += " LIMIT %s, %s"
#         query_params.extend([start, per_page])

#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(base_query, query_params)
#                 rows = cursor.fetchall()

#                 if rows:
#                     columns = [col[0] for col in cursor.description]
#                     results = [dict(zip(columns, row)) for row in rows]
                    

#                     full_query = cursor.mogrify(base_query, query_params)

#                     profilehoro_data =  models.Horoscope.objects.get(profile_id=profile_id)
#                     source_rasi_id=profilehoro_data.birth_rasi_name
#                     source_star_id=profilehoro_data.birthstar_name


#                     # print(source_rasi_id,'source_rasi_id')
#                     # print(source_star_id,'source_star_id')
#                     # print(profile_id,'profile_id')
#                     # print(gender,'gender')

#                     transformed_results = [transform_data(result,profile_id,gender,source_rasi_id,source_star_id) for result in results]

                    
#                     # print('transformed_results',transformed_results)

#                     # print(full_query)  
#                     return JsonResponse({
#                         'status': 'success',
#                         'total_count':total_count,
#                         # 'data': results,
#                         'data':transformed_results,
#                         # 'query': full_query,  
#                         'received_per_page': received_per_page,
#                         'received_page_number': received_page_number,
#                         'calculated_per_page': per_page,
#                         'calculated_page_number': page_number
#                     }, status=status.HTTP_200_OK)
#                 else:
#                     full_query = cursor.mogrify(base_query, query_params)
#                     print(full_query) 
#                     return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Photo_Id_Settings(APIView):

    def post(self, request):
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
          
        horoscope_file = request.FILES.get('horoscope_file') 
        horoscope_file_admin = request.FILES.get('horoscope_file_admin')
        idproof_file = request.FILES.get('idproof_file')
        divorcepf_file = request.FILES.get('divorcepf_file')
        photo_password = request.data.get('photo_password')
        photo_protection = request.data.get('photo_protection')
        Video_url = request.data.get('Video_url')

        if not any([horoscope_file, idproof_file, divorcepf_file, photo_password, photo_protection,horoscope_file_admin]):
            return JsonResponse({"error": "At least one of 'horoscope_file', 'idproof_file', 'divorcepf_file', 'photo_password', or 'photo_protection' or 'Video_url' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch or create the necessary instances
            horoscope_instance, _ = models.Horoscope.objects.get_or_create(profile_id=profile_id)
            registration_instance = models.Registration1.objects.get(ProfileId=profile_id)

            # File validation parameters
            max_file_size = 10 * 1024 * 1024  # 10MB
            valid_extensions = ['doc', 'docx', 'pdf', 'png', 'jpeg', 'jpg']

            # Update the respective fields if provided
            if horoscope_file:
                if horoscope_file.size > max_file_size:
                    return JsonResponse({"error": "Horoscope file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(horoscope_file.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid horoscope file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                horoscope_instance.horoscope_file.save(horoscope_file.name, ContentFile(horoscope_file.read()), save=True)
                horoscope_instance.horo_file_updated = timezone.now()
                horoscope_instance.save()

            if horoscope_file_admin:
                if horoscope_file_admin.size > max_file_size:
                    return JsonResponse({"error": "Horoscope file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(horoscope_file_admin.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid horoscope file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                horoscope_instance.horoscope_file_admin.save(horoscope_file_admin.name, ContentFile(horoscope_file_admin.read()), save=True)
                horoscope_instance.horo_file_updated = timezone.now()
                horoscope_instance.save()

            if idproof_file:
                if idproof_file.size > max_file_size:
                    return JsonResponse({"error": "ID proof file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(idproof_file.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid ID proof file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                registration_instance.Profile_idproof.save(idproof_file.name, ContentFile(idproof_file.read()), save=True)
                registration_instance.save()

            if divorcepf_file:
                if divorcepf_file.size > max_file_size:
                    return JsonResponse({"error": "Divorce proof file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(divorcepf_file.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid divorce proof file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                registration_instance.Profile_divorceproof.save(divorcepf_file.name, ContentFile(divorcepf_file.read()), save=True)
                registration_instance.save()

            if photo_password or photo_protection is not None:
                if photo_protection == 1 and photo_password:
                    registration_instance.Photo_password = photo_password
                registration_instance.Photo_protection = photo_protection
                registration_instance.save()
            
            if Video_url or Video_url is not None:
                registration_instance.Video_url = Video_url
                registration_instance.save()

            # Serialize and respond
            response_data = {
                "horoscope_data": serializers.HorosuploadSerializer(horoscope_instance).data,
                "registration_data": serializers.IdproofuploadSerializer(registration_instance).data,
            }

            return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)

        except models.Registration1.DoesNotExist:
            return JsonResponse({"error": "Profile with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PhotoProtectionView(APIView):
    def post(self, request):
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({"status": "0", "error": "Profile ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = models.Registration1.objects.get(ProfileId=profile_id)
            
            serializer = serializers.PhotoProtectionSerializer(profile)
            
            return JsonResponse({
                "status": "1",
                "message": "Protection fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "0", "error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
class UpdatePhotoPasswordView(APIView):
    def post(self, request):
        serializer = serializers.UpdatePhotoPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            photo_password = serializer.validated_data['photo_password']
            photo_protection = serializer.validated_data['photo_protection']
            
            try:
                profile = models.Registration1.objects.get(ProfileId=profile_id)
                
                if(photo_protection==1):
                    profile.Photo_password = photo_password

                profile.Photo_protection = photo_protection
                profile.save()
                
                return JsonResponse({"status": 1, "message": "Photo password updated successfully."}, status=status.HTTP_200_OK)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": 0, "error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return JsonResponse({"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    





def transform_data2(original_data,my_gender):

    # print('original_data',original_data)

    transformed_data = {
        "profile_id": original_data.get("ProfileId"),
        "profile_name": original_data.get("Profile_name"),
        "profile_age": calculate_age(original_data.get("Profile_dob")),
        "profile_gender": original_data.get("Gender"),
        "profile_img": Get_profile_image(original_data.get("ProfileId"),my_gender,1,original_data.get("Photo_protection")),
        "profile_height": original_data.get("Profile_height"),
        "weight": original_data.get("weight"),  # You need to add this if you have this information
        "degree": original_data.get("EducationLevel"),
        "star": original_data.get("star"),
        # "profession": original_data.get("profession"),
        "profession": getprofession(original_data.get("profession")),
        "location": original_data.get("Profile_city"),      # Default value

    }
    return transformed_data







def transform_data(original_data,my_profile_id,my_gender,source_rasi_id,source_star_id):

    # print('original_data',original_data)
    # print('birthstar_name',original_data.get("birthstar_name"))
    # print('birth_rasi_name',original_data.get("birth_rasi_name"))

    photo_viewing=get_permission_limits(my_profile_id,'photo_viewing')

    # print(original_data.get("Photo_protection"),'photo protecion')
    # print(my_gender,'my_gender')
    # print(my_profile_id,'my_profile_id')

    
    profile_data =  models.Registration1.objects.get(ProfileId=my_profile_id)


    my_status=profile_data.Status
    
    
    
    if photo_viewing == 1 and my_status!= 0:
                # print("Execution time before image starts ",datetime.now())
                image_function = lambda detail: get_profile_image_azure_optimized(original_data.get("ProfileId"), my_gender, 1, original_data.get("Photo_protection"))
    else:
                # print("Execution time before blur image starts ",datetime.now())
                image_function = lambda detail: get_profile_image_azure_optimized(original_data.get("ProfileId"), my_gender, 1,1)

    transformed_data = {
        "profile_id": original_data.get("ProfileId"),
        "profile_name": original_data.get("Profile_name"),
        "profile_age": calculate_age(original_data.get("Profile_dob")),
        "profile_gender": original_data.get("Gender"),
        # "profile_img": Get_profile_image(original_data.get("ProfileId"),my_gender,1,original_data.get("Photo_protection")),
        "profile_img":image_function(original_data),
        "profile_height": original_data.get("Profile_height"),
        "weight": None,  # You need to add this if you have this information
        "degree": original_data.get("EducationLevel"),
        "star": original_data.get("star"),
        # "profession": original_data.get("profession"),
        "profession": getprofession(original_data.get("profession")),
        "location": original_data.get("Profile_city"),
        "photo_protection": original_data.get("Photo_protection"),  # Default value
        "matching_score":Get_matching_score(source_star_id,source_rasi_id,original_data.get("birthstar_name"),original_data.get("birth_rasi_name"),my_gender),    # Default value
        "wish_list": Get_wishlist(my_profile_id,original_data.get("ProfileId")),          # Default value

    }
    return transformed_data


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class CreateOrderView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)

            required_fields = ["profile_id", "amount"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=400
                )

            amount = int(data.get("amount")) * 100  # Convert to paise
            # amount = 1*100
            currency = "INR"
            profile_id=data.get("profile_id")
            plan_id=data.get("plan_id", "")
            addon_package=data.get("addon_package", "")

            order_data = {
                "amount": amount,
                "currency": currency,
                "payment_capture": "1",  # Auto-capture payment
            }

            order = client.order.create(data=order_data)

            # Save order details in the database
            models.PaymentTransaction.objects.create(
                profile_id=profile_id,  # Assuming you have user authentication
                order_id=order["id"],
                amount=amount / 100,  # Save in INR
                plan_id=plan_id,
                addon_package=addon_package,
                payment_type='Online',
                status=1,
                created_at=timezone.now()
            )
            
            #return JsonResponse(order)
            return JsonResponse({"status": "success" , "message": "Order Created Sucessfully", "order": order})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def profile_preview(request: HttpRequest, profile_id):
    profile = get_object_or_404(models.Registration1, ProfileId=profile_id)
    profile_images = models.Image_Upload.objects.filter(profile_id=profile,image_approved=1,is_deleted=0).first()
    profile_horo = get_object_or_404(models.Horoscope, profile_id=profile_id)
    profile_edu = get_object_or_404(models.Edudetails, profile_id=profile_id)
    
    profile_image_url = request.build_absolute_uri(profile_images.image.url) if profile_images else ""
    
    profileId=[profile_id]

    profile_details = get_profile_details(profileId)


    try:
            Profile_high_edu = models.Edupref.objects.get(RowId=profile_details[0]['highest_education']).EducationLevel
    except models.Edupref.DoesNotExist:
            Profile_high_edu = None

    try:
            Profile_profession = models.Profespref.objects.get(RowId=profile_details[0]['profession']).profession
    except models.Profespref.DoesNotExist:
            Profile_profession = None

    try:
            Profile_owner = models.Profileholder.objects.get(Mode=profile_details[0]['Profile_for']).ModeName
    except models.Profileholder.DoesNotExist:
            Profile_owner = None

    try:
            Profile_marital_status = models.ProfileMaritalstatus.objects.get(StatusId=profile_details[0]['Profile_marital_status']).MaritalStatus
    except models.ProfileMaritalstatus.DoesNotExist:
            Profile_marital_status = None

    # print(f"Profile details: {profile_details}")
    my_gender=profile_details[0]['Gender']
    if my_gender=="male":
        my_gender="female"
        looking_for="Bride"
        my_status="Groom"
    else :
        my_gender="male"
        looking_for="Groom"
        my_status="Bride"

    Get_profile_image(profile_details[0]['ProfileId'],my_gender,1,0)

    context = {
        "profile_id": profile.ProfileId,
        "profile_name": profile.Profile_name,
        "profile_age":calculate_age(profile.Profile_dob),
        "profile_dob":profile.Profile_dob,
        "profile_height":profile.Profile_height,
        "profile_education":Profile_high_edu,
        "profile_profession":Profile_profession,
        "profile_image_url":Get_profile_image(profile_details[0]['ProfileId'],my_gender,1,0),
        "looking_for":looking_for,
        "star":  profile_details[0]['star_name'],
        "rasi":profile_details[0]['rasi_name'],
        "suya_gothram":profile_details[0]['suya_gothram'],
        "profile_owner":Profile_owner,
        "anual_incom":profile_details[0]['actual_income'],
        "height":profile_details[0]['Profile_height'],
        "working_location":profile_details[0]['Profile_height'],
        "company_name":profile_details[0]['company_name'],
        "marital_status":Profile_marital_status,
        "state":get_state_name(profile_details[0]['Profile_state']),
        "city":get_city_name(profile_details[0]['Profile_city']),
        "address":get_city_name(profile_details[0]['Profile_address']),
        "mobile": profile_details[0]['Mobile_no'],
        "whatsapp": profile_details[0]['Profile_whatsapp'],
        "my_status":my_status
    }
    return render(request, "profile_preview.html", context)



def profile_preview_withouphoto(request: HttpRequest, profile_id):
    profile = get_object_or_404(models.Registration1, ProfileId=profile_id)
    profile_images = models.Image_Upload.objects.filter(profile_id=profile,image_approved=1,is_deleted=0).first()
    profile_horo = get_object_or_404(models.Horoscope, profile_id=profile_id)
    profile_edu = get_object_or_404(models.Edudetails, profile_id=profile_id)
    
    profile_image_url = request.build_absolute_uri(profile_images.image.url) if profile_images else ""
    
    profileId=[profile_id]

    profile_details = get_profile_details(profileId)


    try:
            Profile_high_edu = models.Edupref.objects.get(RowId=profile_details[0]['highest_education']).EducationLevel
    except models.Edupref.DoesNotExist:
            Profile_high_edu = None

    try:
            Profile_profession = models.Profespref.objects.get(RowId=profile_details[0]['profession']).profession
    except models.Profespref.DoesNotExist:
            Profile_profession = None

    try:
            Profile_owner = models.Profileholder.objects.get(Mode=profile_details[0]['Profile_for']).ModeName
    except models.Profileholder.DoesNotExist:
            Profile_owner = None

    try:
            Profile_marital_status = models.ProfileMaritalstatus.objects.get(StatusId=profile_details[0]['Profile_marital_status']).MaritalStatus
    except models.ProfileMaritalstatus.DoesNotExist:
            Profile_marital_status = None

    # print(f"Profile details: {profile_details}")
    my_gender=profile_details[0]['Gender']
    base_url = settings.MEDIA_URL
    default_img_bride='default_bride.png'
    default_img_groom='default_groom.png'
    if my_gender=="male":
        my_gender="female"
        looking_for="Bride"
        my_status="Groom"
        image_url=base_url+default_img_groom
    else :
        my_gender="male"
        looking_for="Groom"
        my_status="Bride"
        image_url= base_url+default_img_bride

    # Get_profile_image(profile_details[0]['ProfileId'],my_gender,1,1)
    
    context = {
        "profile_id": profile.ProfileId,
        "profile_name": profile.Profile_name,
        "profile_age":calculate_age(profile.Profile_dob),
        "profile_dob":profile.Profile_dob,
        "profile_height":profile.Profile_height,
        "profile_education":Profile_high_edu,
        "profile_profession":Profile_profession,
        "profile_image_url":image_url,
        "looking_for":looking_for,
        "star":  profile_details[0]['star_name'],
        "rasi":profile_details[0]['rasi_name'],
        "suya_gothram":profile_details[0]['suya_gothram'],
        "profile_owner":Profile_owner,
        "anual_incom":profile_details[0]['actual_income'],
        "height":profile_details[0]['Profile_height'],
        "working_location":profile_details[0]['Profile_height'],
        "company_name":profile_details[0]['company_name'],
        "marital_status":Profile_marital_status,
        "state":get_state_name(profile_details[0]['Profile_state']),
        "city":get_city_name(profile_details[0]['Profile_city']),
        "address":get_city_name(profile_details[0]['Profile_address']),
        "mobile": profile_details[0]['Mobile_no'],
        "whatsapp": profile_details[0]['Profile_whatsapp'],
        "my_status":my_status
    }
    return render(request, "profile_preview.html", context)





        
# @method_decorator(csrf_exempt, name="dispatch")
# class RazorpayWebhookView(APIView):
#     def post(self, request):
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             signature = request.headers.get("X-Razorpay-Signature")
#             client.utility.verify_webhook_signature(request.body, signature, settings.RAZORPAY_KEY_SECRET)

#             payment_id = data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#             order_id = data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")

#             order = models.PaymentTransaction.objects.get(order_id=order_id)
#             order.payment_id = payment_id
#             order.status = 2
#             order.save()

#             return JsonResponse({"status": "success"})
#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({"status": "error", "message": "Signature verification failed"}, status=400)
#         except models.PaymentTransaction.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Order not found"}, status=404)
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)

# @method_decorator(csrf_exempt, name="dispatch")
# class RazorpayWebhookView(APIView):
#     def post(self, request):
#         try:
#             # Ensure body is not empty
#             if not request.body:
#                 return JsonResponse({"status": "error", "message": "Empty request body"}, status=400)

#             # Decode and parse JSON data
#             data = json.loads(request.body.decode("utf-8"))

#             # Extract required fields
#             # signature = request.headers.get("X-Razorpay-Signature")
#             # if not signature:
#             #     return JsonResponse({"status": "error", "message": "Signature missing"}, status=400)
#             profile_id = data.get("profile_id")
#             payment_id = data.get("payment_id")
#             order_id = data.get("order_id")
#             signature = data.get("signature")

#             client.utility.verify_webhook_signature(request.body, signature, settings.RAZORPAY_KEY_SECRET)

#             #order_id = data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")

#             if not order_id or not payment_id:
#                 return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

#             # Update order status in the database
#             order = models.PaymentTransaction.objects.get(order_id=order_id)
#             order.payment_id = payment_id
#             order.status = 2  # Assuming 2 means 'Payment Captured'
#             order.save()

#             return JsonResponse({"status": "success","message":"PaymentCaptured sucessfully"})
        
#         except json.JSONDecodeError:
#             return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({"status": "error", "message": "Signature verification failed"}, status=400)

#         except models.PaymentTransaction.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Order not found"}, status=404)

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)


# @method_decorator(csrf_exempt, name="dispatch")
# class RazorpayWebhookView(APIView):
#     def post(self, request):
#         try:
#             # Ensure body is not empty
#             if not request.body:
#                 return JsonResponse({"status": "error", "message": "Empty request body"}, status=400)
        
#             # Decode request body properly
#             body_unicode = request.body.decode('utf-8')  # Decode bytes to string
#             data = json.loads(body_unicode)  # Convert string to JSON

#             print('data',data)

#             required_fields = ["profile_id", "order_id", "payment_id"]
#             missing_fields = [field for field in required_fields if field not in data]

#             if missing_fields:
#                 return JsonResponse(
#                     {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"},
#                     status=400
#                 )
            
#             # Extract required fields
#             payment_id = data.get("payment_id")
#             order_id = data.get("order_id")
#             signature = data.get("signature")

#             generated_signature = hmac.new(
#             settings.RAZORPAY_KEY_SECRET.encode(),
#             request.body,  # Use raw request body
#             hashlib.sha256 ).digest()

#             expected_signature = base64.b64encode(generated_signature).decode()

#             print(f"Expected Signature: {expected_signature}")
#             print(f"Received Signature: {signature}")


#             # Validate presence of required fields
#             if not order_id or not payment_id or not signature:
#                 return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

#             # Verify Razorpay signature
#             client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#             client.utility.verify_webhook_signature(body_unicode, expected_signature, settings.RAZORPAY_KEY_SECRET)

#             print("Print the client Responses")
#             print(client)

#             # Fetch and update order status
#             order = models.PaymentTransaction.objects.get(order_id=order_id)
#             order.payment_id = payment_id
#             order.status = 2  # Assuming 2 means 'Payment Captured'
#             order.save()

#             return JsonResponse({"status": "success", "message": "Payment Captured successfully"})
        
#         except json.JSONDecodeError:
#             return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({"status": "error", "message": "Signature verification failed"}, status=400)

#         except models.PaymentTransaction.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Order not found"}, status=404)

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(APIView):
    def post(self, request):
        try:
            # Ensure body is not empty
            if not request.body:
                return JsonResponse({"status": "error", "message": "Empty request body"}, status=400)

            # Parse JSON
            data = json.loads(request.body)
            #print('Received Data:', data)

            # Check required fields
            required_fields = ["order_id", "payment_id", "signature"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse({"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)

            # Extract fields
            order_id = data.get("order_id")
            payment_id = data.get("payment_id")
            received_signature = data.get("signature")

            # Generate the expected signature (order_id|payment_id)
            message = f"{order_id}|{payment_id}".encode()
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message,
                hashlib.sha256
            ).hexdigest()  # Convert to hex

            # print(f"Expected Signature: {generated_signature}")
            # print(f"Received Signature: {received_signature}")

            if generated_signature != received_signature:
                return JsonResponse({"status": "error", "message": "Signature verification failed"}, status=400)

            # Fetch and update order status
            order = models.PaymentTransaction.objects.get(order_id=order_id)
            order.payment_id = payment_id
            order.status = 2  # Payment Captured
            order.save()

            return JsonResponse({"status": "success", "message": "Payment Captured successfully"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

        except models.PaymentTransaction.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"}, status=404)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)






@method_decorator(csrf_exempt, name="dispatch")
class UpdatePaymentStatusView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            required_fields = ["profile_id", "order_id", "status"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=400
                )
            
            order_id = data.get("order_id")
            status = data.get("status")

            #order = models.PaymentTransaction.objects.get(order_id=order_id,status!=2)
            order = models.PaymentTransaction.objects.filter(Q(order_id=order_id) & ~Q(status=2)).first()
            order.status = status
            order.save()
            
            #return JsonResponse({"status": "success", "message": f"Order {order_id} updated to {status}"})
            return JsonResponse({"status": "success", "message": "Order Updated Sucessfully"})
        except models.PaymentTransaction.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        


class Get_Profession(APIView):

    def post(self, request):
        try:
            professions = models.MasterProfession.objects.filter(is_deleted=0)
            serializer = serializers.CustomProfessionSerializer(professions, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except models.MasterProfession.DoesNotExist:
            return JsonResponse({'error': 'Professions not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgetPassword(APIView):
    def post(self, request):
        serializer = serializers.ForgetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            profile_id = serializer.validated_data.get('profile_id')
            
            try:
                if profile_id:
                    # Fetch user by profile_id to get the associated email
                    user = models.Registration1.objects.get(ProfileId=profile_id,Status=1)
                    email = user.EmailId  # Override email with the one from the user record
                else:
                    # Fetch user by email
                    user = models.Registration1.objects.get(EmailId=email,Status=1)

                otp = str(secrets.randbelow(1000000)).zfill(6)
                logging.debug(f"Generated OTP: {otp}")

                user.Reset_OTP = otp
                # user.Reset_OTP_Time = timezone.now() 
                user.Reset_OTP_Time = timezone.now() 
                logging.debug(f"Setting OTP: {otp} for user with ProfileId: {user.ProfileId}")
                user.save()
                logging.debug(f"Saved OTP: {user.Reset_OTP} for user with ProfileId: {user.ProfileId}")

                context = {
                    'profile_id': user.ProfileId,
                    'otp': otp,
                    'logo_url': 'https://vysyamat.blob.core.windows.net/vysyamala/newvysyamalalogo2.png',
                }

                subject = "Your Password Reset OTP"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [email]
                html_content = render_to_string('user_api/authentication/forget_password.html', context)

                email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()
                
                return JsonResponse({"message": "OTP sent to your email.","forget_profile_id":user.ProfileId}, status=status.HTTP_200_OK)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=status.HTTP_200_OK)
            
            except Exception as e:
                logging.error(f"Error sending OTP: {e}")
                return JsonResponse({"error": f"An error occurred while sending the OTP. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def is_otp_valid(user):
    reset_otp_time = user.Reset_OTP_Time  # Get the Reset_OTP_Time

    if reset_otp_time is None:  # Check if it's None
        return False  # OTP is invalid if there's no Reset_OTP_Time

    otp_expiry_time = reset_otp_time + timedelta(minutes=5)  # Add 5 minutes
    current_time = timezone.now()

    if current_time > otp_expiry_time:
        return False  # OTP has expired
    return True  # OTP is still valid


class ForgetPassword_otpverify(APIView):
    def post(self, request):
        #serializer = serializers.ResetPasswordSerializer(data=request.data)
        
        # if serializer.is_valid():
        #     profile_id = serializer.validated_data['profile_id']
        #     otp = serializer.validated_data['otp']
            
        profile_id=request.data.get('profile_id')
        otp=request.data.get('otp')
        if profile_id and otp is not None:

            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)

                if user.Reset_OTP != otp:
                    return JsonResponse({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

                if not is_otp_valid(user):
                    return JsonResponse({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

                
                logging.debug(f"Resetting password for user with ProfileId: {user.ProfileId}. OTP Time: {user.Reset_OTP_Time}")

                #user.save()

                return JsonResponse({"message": "Otp verified successfully.","status":1,"profile_id":profile_id}, status=status.HTTP_200_OK)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"error": "User not found or invalid OTP."}, status=status.HTTP_404_NOT_FOUND)
            
            except Exception as e:
                logging.error(f"Error resetting password: {e}")
                return JsonResponse({"error": "An error occurred while resetting the password."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JsonResponse({"error": "profile_id and otp is required"}, status=status.HTTP_400_BAD_REQUEST)




class ResetPassword(APIView):
    def post(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            # otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            reenter_new_password = serializer.validated_data['new_password']
            if new_password!=reenter_new_password:
                return JsonResponse({"error": "New password and reenter new password is not the same","status":0}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)

                # user.Password = make_password(new_password) 
                user.Password = new_password
                user.Reset_OTP = '' 
                user.Reset_OTP_Time = timezone.now()  
                
                logging.debug(f"Resetting password for user with ProfileId: {user.ProfileId}. OTP Time: {user.Reset_OTP_Time}")

                user.save()

                return JsonResponse({"message": "Password successfully reset."}, status=status.HTTP_200_OK)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"error": "User not found or invalid OTP."}, status=status.HTTP_404_NOT_FOUND)
            
            except Exception as e:
                logging.error(f"Error resetting password: {e}")
                return JsonResponse({"error": "An error occurred while resetting the password."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# def calculate_profile_completion(profile_id):
#     total_points = 0
#     completed_points = 0

#     # Define field weights
#     field_weights = {
#         'logindetails': {'Profile_idproof': 2, 'Profile_gothras': 2 , 'Profile_country':1,'Profile_state':1,'Profile_district':1,'Profile_city':1,'Profile_pincode':1},
#         'profile_familydetails': {'family_status': 2, 'property_worth': 1},
#         'profile_horoscope': {'birthstar_name': 2, 'birth_rasi_name': 2,'horoscope_file':1},
# 		'profile_images': {'image': 2},
# 		'profile_partner_pref': {'pref_age_differences': 2, 'pref_height_from': 2,'pref_height_to':2,'pref_marital_status':2,'pref_profession':2,'pref_porutham_star':2,'pref_education':2,'pref_anual_income':2,'pref_chevvai':2,'pref_ragukethu':2,'pref_foreign_intrest':2},
# 		'profile_edudetails': {'highest_education': 2, 'profession': 2,'anual_income':2,'career_plans':2},
#     }

#     # Fetch logindetails Data
#     logindetails = models.Registration1.objects.filter(ProfileId=profile_id).first()
#     if logindetails:
#         for field, weight in field_weights['logindetails'].items():
#             total_points += weight
#             if getattr(logindetails, field):
#                 completed_points += weight
#         print('loginpoints',completed_points)

#     # Fetch profile_familydetails Data
#     profile_familydetails = models.Familydetails.objects.filter(profile_id=profile_id).first()
#     if profile_familydetails:
#         for field, weight in field_weights['profile_familydetails'].items():
#             total_points += weight
#             if getattr(profile_familydetails, field):
#                 completed_points += weight
#         print('profile_familydetail points',completed_points)

#     # Fetch profile_horoscope Data
#     profile_horoscope = models.Horoscope.objects.filter(profile_id=profile_id).first()
#     if profile_horoscope:
#         for field, weight in field_weights['profile_horoscope'].items():
#             total_points += weight
#             if getattr(profile_horoscope, field):
#                 completed_points += weight
#         print('profile_horoscope points',completed_points)

	
# 	# Fetch profile_images Data
#     if models.Image_Upload.objects.filter(profile_id=profile_id).exists():
#         profile_images = models.Image_Upload.objects.filter(profile_id=profile_id).first()
#         for field, weight in field_weights['profile_images'].items():
#             total_points += weight
#             if getattr(profile_images, field):
#                 completed_points += weight
#     else:
#         # If no images exist, handle the case (optional)
#         for weight in field_weights['profile_images'].values():
#             total_points += weight  # Add the weights for missing image fields

	
# 	# Fetch profile_partner_pref Data
#     profile_partner_pref = models.Partnerpref.objects.filter(profile_id=profile_id).first()
#     if profile_partner_pref:
#         for field, weight in field_weights['profile_partner_pref'].items():
#             total_points += weight
#             if getattr(profile_partner_pref, field):
#                 completed_points += weight
#         print('profile_partner_pref points',completed_points)
	
# 	# Fetch profile_edudetails Data
#     profile_edudetails = models.Edudetails.objects.filter(profile_id=profile_id).first()
#     if profile_edudetails:
#         for field, weight in field_weights['profile_edudetails'].items():
#             total_points += weight
#             if getattr(profile_edudetails, field):
#                 completed_points += weight
#         print('profile_edudetails points',completed_points)
	

#     # Calculate percentage
#     if total_points == 0:
#         return 0
#     print('total_points',total_points)
#     print('completed_points',completed_points)
#     return round((completed_points / total_points) * 100)

def calculate_profile_completion(profile_id):
    total_points = 0
    completed_points = 0
    empty_fields = []

    # Define field weights
    field_weights = {
        'logindetails': {'Profile_idproof': 15},  # ID Proof Upload - 15%
        'profile_images': {'image': 15},  # Photo Upload - 15%
        'profile_horoscope': {'horoscope_file': 15},  # Horoscope Upload - 15%
        'logindetails_additional': {'EmailId': 5},  # Email Verification - 5%
        'profile_familydetails': {'property_worth': 5},  # Property Worth - 5%
        'about_myself': {'about_self': 10},  # About Myself - 10%
        'about_my_family': {'about_family': 10},  # About My Family - 10%
        'profile_edudetails': {'career_plans': 10, 'anual_income': 5},  # Career Plan (10%), Annual Income (5%)
        'profile_videos': {'Video_url': 10},  # Videos - 10%
    }

    # 1. ID Proof Upload
    logindetails = models.Registration1.objects.filter(ProfileId=profile_id).first()
    if logindetails:
        for field, weight in field_weights['logindetails'].items():
            total_points += weight
            if getattr(logindetails, field):
                completed_points += weight

    # 2. Photo Upload
    profile_images = models.Image_Upload.objects.filter(profile_id=profile_id,image_approved=1,is_deleted=0).first()
    if profile_images:
        for field, weight in field_weights['profile_images'].items():
            total_points += weight
            if getattr(profile_images, field):
                completed_points += weight

    # 3. Horoscope Upload
    profile_horoscope = models.Horoscope.objects.filter(profile_id=profile_id).first()
    if profile_horoscope:
        for field, weight in field_weights['profile_horoscope'].items():
            total_points += weight
            if getattr(profile_horoscope, field):
                completed_points += weight

    # 4. Email Verification
    if logindetails:
        for field, weight in field_weights['logindetails_additional'].items():
            total_points += weight
            if getattr(logindetails, field):
                completed_points += weight

    # 5. Property Worth
    profile_familydetails = models.Familydetails.objects.filter(profile_id=profile_id).first()
    if profile_familydetails:
        for field, weight in field_weights['profile_familydetails'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight

    # 6. About Myself
    if profile_familydetails:
        for field, weight in field_weights['about_myself'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight

    # 7. About My Family
    if profile_familydetails:
        for field, weight in field_weights['about_my_family'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight

    # 8. Career Plan and Annual Income
    profile_edudetails = models.Edudetails.objects.filter(profile_id=profile_id).first()
    if profile_edudetails:
        for field, weight in field_weights['profile_edudetails'].items():
            total_points += weight
            if getattr(profile_edudetails, field):
                completed_points += weight

    # 9. Videos
    profile_videos = models.Registration1.objects.filter(ProfileId=profile_id).first()
    if profile_videos:
        for field, weight in field_weights['profile_videos'].items():
            total_points += weight
            if getattr(profile_videos, field):
                completed_points += weight

    # Calculate completion percentage
    if total_points == 0:
        return 0

    return round((completed_points / total_points) * 100)




def calculate_points_and_get_empty_fields(profile_id):
    total_points = 0
    completed_points = 0
    empty_fields = []  # List to store empty fields

    # Define field weights
    field_weights = {
        'logindetails': {'Profile_idproof': 15},  # ID Proof Upload - 15%
        'profile_images': {'image': 15},  # Photo Upload - 15%
        'profile_horoscope': {'horoscope_file': 15},  # Horoscope Upload - 15%
        'logindetails_additional': {'EmailId': 5},  # Email Verification - 5%
        'profile_familydetails': {'property_worth': 5},  # Property Worth - 5%
        'about_myself': {'about_self': 10},  # About Myself - 10%
        'about_my_family': {'about_family': 10},  # About My Family - 10%
        'profile_edudetails': {'career_plans': 10, 'anual_income': 5},  # Career Plan (10%), Annual Income (5%)
        'profile_videos': {'Video_url': 10},  # Videos - 10%
    }

    # 1. ID Proof Upload
    logindetails = models.Registration1.objects.filter(ProfileId=profile_id).first()
    if logindetails:
        for field, weight in field_weights['logindetails'].items():
            total_points += weight
            if getattr(logindetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'Personal_info', 'field': field})
                
    # 2. Photo Upload
    profile_images = models.Image_Upload.objects.filter(profile_id=profile_id).first()
    if profile_images:
        for field, weight in field_weights['profile_images'].items():
            total_points += weight
            if getattr(profile_images, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'profile_images', 'field': field})
    else:
        for field, weight in field_weights['profile_images'].items():
            total_points += weight
        empty_fields.append({'tab': 'profile_images', 'field': field})

                
    # 3. Horoscope Upload
    profile_horoscope = models.Horoscope.objects.filter(profile_id=profile_id).first()
    if profile_horoscope:
        for field, weight in field_weights['profile_horoscope'].items():
            total_points += weight
            if getattr(profile_horoscope, field):
                completed_points += weight
            else:
                # empty_fields.append(field)
                empty_fields.append({'tab': 'profile_horoscope', 'field': field})


    # 4. Email Verification
    if logindetails:
        for field, weight in field_weights['logindetails_additional'].items():
            total_points += weight
            if getattr(logindetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'Personal_info', 'field': field})


    # 5. Property Worth
    profile_familydetails = models.Familydetails.objects.filter(profile_id=profile_id).first()
    if profile_familydetails:
        for field, weight in field_weights['profile_familydetails'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'profile_familydetails', 'field': field})

    # 6. About Myself
    if profile_familydetails:  # Assuming "about_self" is in logindetails
        for field, weight in field_weights['about_myself'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'Personal_info', 'field': field})

    # 7. About My Family
    if profile_familydetails:
        for field, weight in field_weights['about_my_family'].items():
            total_points += weight
            if getattr(profile_familydetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'profile_familydetails', 'field': field})

    # 8. Career Plan and Annual Income
    profile_edudetails = models.Edudetails.objects.filter(profile_id=profile_id).first()
    if profile_edudetails:
        for field, weight in field_weights['profile_edudetails'].items():
            total_points += weight
            if getattr(profile_edudetails, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'profile_edudetails', 'field': field})

    # 9. Videos
    profile_videos = models.Registration1.objects.filter(ProfileId=profile_id).first()
    if profile_videos:
        for field, weight in field_weights['profile_videos'].items():
            total_points += weight
            if getattr(profile_videos, field):
                completed_points += weight
            else:
                #empty_fields.append(field)
                empty_fields.append({'tab': 'Personal_info', 'field': field})

    # Calculate completion percentage
    completion_percentage = (completed_points / total_points) * 100 if total_points else 0

    return {
        'total_points': total_points,
        'completed_points': completed_points,
        'completion_percentage': completion_percentage,
        'empty_fields': empty_fields
    }


    # # Example Usage
    # profile_id = 123  # Replace with your profile ID
    # result = calculate_points_and_get_empty_fields(profile_id)

    # print("Total Points:", result['total_points'])
    # print("Completed Points:", result['completed_points'])
    # print("Completion Percentage:", result['completion_percentage'])
    # print("Empty Fields:", result['empty_fields'])


class FeaturedProfile(APIView):
    def post(self, request):
        gender = request.query_params.get('gender') or request.data.get('gender')

        if not gender:
            return JsonResponse({"Status": 0, "message": "Gender is required"}, status=status.HTTP_400_BAD_REQUEST)

        normalized_gender = gender.strip().lower()
        photo_gender = 'female' if normalized_gender == 'male' else 'male'


        # oposi_gender=''
        # if((photo_gender=='male') or (photo_gender =='Male')):
        #     oposi_gender='female'
        # else:
        #     oposi_gender='male'

        try:
            # Raw SQL query to fetch random profiles
            query = """
            SELECT 
                    ld.ProfileId,ld.Profile_name,  ld.Gender,  ld.Profile_dob, ld.Profile_height, ld.Profile_city, ld.Photo_protection FROM (
                    SELECT ProfileId
                    FROM logindetails
                    WHERE LOWER(Gender) = LOWER(%s)
                    AND Status = 1
                    AND Plan_id IN (2, 15)
                    ORDER BY RAND()
                    LIMIT 10
                ) AS rand_ld
                JOIN logindetails ld ON ld.ProfileId = rand_ld.ProfileId
                JOIN (
                    SELECT pi1.*
                    FROM profile_images pi1
                    INNER JOIN (
                        SELECT profile_id, MIN(id) AS min_id
                        FROM profile_images
                        WHERE image_approved = 1 
                        AND is_deleted = 0
                        GROUP BY profile_id
                    ) AS pi2 ON pi1.id = pi2.min_id
                ) AS i ON i.profile_id = ld.ProfileId;
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [normalized_gender])
                columns = [col[0] for col in cursor.description]
                profile_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Check if any profiles were found (use len() for lists)
            if not profile_details:  # Replaces .exists()
                return JsonResponse({"Status": 0, "message": "No featured profiles found"}, status=status.HTTP_200_OK)

            # Extract ProfileIds from the raw SQL results
            profile_ids = [profile['ProfileId'] for profile in profile_details]

            # Fetch education details for these profiles
            edu_details = models.Edudetails.objects.filter(profile_id__in=profile_ids)
            profession_id_mapping = {edu.profile_id: edu.profession for edu in edu_details}
            highest_education_mapping = {edu.profile_id: edu.highest_education for edu in edu_details}

            # Prefetch profession and degree mappings
            professions = models.Profespref.objects.all()
            degrees = models.Highesteducation.objects.all()
            profession_mapping = {str(prof.RowId): prof.profession for prof in professions}
            degree_mapping = {str(degree.id): degree.degree for degree in degrees}

            # Build the response
            restricted_profile_details = []
            for profile in profile_details:
                profile_id = profile['ProfileId']

                profile_img = Get_profile_image(profile_id, photo_gender, 1, profile['Photo_protection'])
                # Skip if image is 'not found'
                if profile_img == "not_found_image_url" or profile_img.endswith("not-found.jpg"):  # Adjust the condition as needed
                    continue


                restricted_profile_details.append({
                    "profile_id": profile_id,
                    "profile_name": profile['Profile_name'],
                    "profile_img":profile_img,
                    "profile_age": calculate_age(profile['Profile_dob']),
                    "profile_gender": profile['Gender'],
                    "height": profile['Profile_height'],
                    "degree": degree_mapping.get(str(highest_education_mapping.get(profile_id, "")), ""),
                    "profession": profession_mapping.get(str(profession_id_mapping.get(profile_id, "")), ""),
                    "location": profile['Profile_city']
                })

            return JsonResponse({
                "Status": 1,
                "message": "Featured profiles fetched successfully",
                "profiles": restricted_profile_details
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # print(f"Error: {e}")
            return JsonResponse({"Status": 0, "message": f"An error occurred: {e}"}, status=status.HTTP_200_OK)
        








class Search_byprofile_id(APIView):


    def post(self, request):
        # Extract the input data from the JSON body (POST request)
        profile_id = request.data.get('profile_id')
        search_profile_id = request.data.get('search_profile_id')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not search_profile_id:
            return JsonResponse({'status': 'failure', 'message': 'search_profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Need to get gender from logindetails table
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Gender FROM logindetails WHERE ProfileId = %s", [profile_id])
                gender = cursor.fetchone()
                if not gender:
                    return JsonResponse({'status': 'failure', 'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
                gender = gender[0]

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract input values from request data (POST request)
        from_age = request.data.get('from_age')
       
        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')

        # Set default values if not provided
        if received_per_page is None:
            per_page = 10
        else:
            try:
                per_page = int(received_per_page)
            except (ValueError, TypeError):
                per_page = 10  # Fall back to default if conversion fails

        if received_page_number is None:
            page_number = 1
        else:
            try:
                page_number = int(received_page_number)
            except (ValueError, TypeError):
                page_number = 1  # Fall back to default if conversion fails

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        # Initialize the query with the base structure
        base_query = """
        SELECT a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income , e.birthstar_name , e.birth_rasi_name
                       ,a.Photo_protection,a.Gender        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        WHERE a.gender != %s AND a.ProfileId != %s AND a.plan_status NOT IN (16, 17, 3) AND (a.ProfileId = %s
       OR a.Profile_name LIKE CONCAT('%%', %s, '%%'));
        """
        
        # Prepare the query parameters
        query_params = [gender, profile_id , search_profile_id , search_profile_id]

        try:
            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]

                    # Log or return the full query for debugging
                    full_query = cursor.mogrify(base_query, query_params)

                    profilehoro_data =  models.Horoscope.objects.get(profile_id=profile_id)
            
                    source_rasi_id=profilehoro_data.birth_rasi_name
                    source_star_id=profilehoro_data.birthstar_name


                    transformed_results = [transform_data(result,profile_id,gender,source_rasi_id,source_star_id) for result in results]

                    return JsonResponse({
                        'status': 'success',
                        # 'data': results,
                        'data': transformed_results,
                        # 'query': full_query,  # Include the formatted query in the response
                        'received_per_page': received_per_page,
                        'received_page_number': received_page_number,
                        'calculated_per_page': per_page,
                        'page_name': '1',
                        'calculated_page_number': page_number
                    }, status=status.HTTP_200_OK)
                else:
                    # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)
                    return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_200_OK)




#Vysassists list



class Send_vysassist_request(APIView):
    def post(self, request):
        serializer = serializers.VysassistrequestSerializer(data=request.data)

        # print('serializer',serializer)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')
            to_message = serializer.validated_data.get('to_message')

            get_limits=can_get_vysassist_profile(profile_from)

            # print('get_limits',get_limits)

            if get_limits is True: 
        

                # print('profile_from',profile_from)
                # print('profile_to',profile_to)
                
                # Check if an entry with the same profile_from and profile_to already exists
                existing_entry = models.Profile_vysassist.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
                
                if existing_entry:
                    # Update the status to 0 if the entry already exists
                    #existing_entry.status = 0
                    existing_entry.status = int_status
                    existing_entry.req_datetime = timezone.now()
                    existing_entry.save() 

                    return JsonResponse({"Status": 0, "message": "Vysassist updated"}, status=status.HTTP_200_OK)
                
                
                else:
                    # Create a new entry with status 1
                    serializer.save(status=1)
                    
                    models.Profile_notification.objects.create(
                        profile_id=profile_to,
                        from_profile_id=profile_from,
                        notification_type='Vys_assists',
                        to_message=to_message,
                        is_read=0,
                        created_at=timezone.now()
                    )

                    return JsonResponse({"Status": 1, "message": "Vysassist sent successfully"}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"Status": 0, "message": "No access to Vysyassis request"}, status=status.HTTP_200_OK)
            
        return JsonResponse(serializer.errors, status=status.HTTP_200_OK)


class Click_call_request(APIView):
    def post(self, request):
        serializer = serializers.CallactionSerializer(data=request.data)

        # print('serializer',serializer)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')

            get_limits=can_call_profile(profile_from)

            if get_limits is True: 
        
                # print('profile_from',profile_from)
                # print('profile_to',profile_to)
                
                # Check if an entry with the same profile_from and profile_to already exists
                existing_entry = models.Profile_callogs.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
                
                if existing_entry:
                    # Update the status to 0 if the entry already exists
                    #existing_entry.status = 0
                    int_status=1
                    existing_entry.status = int_status
                    existing_entry.req_datetime = timezone.now()
                    existing_entry.save() 
                    toprofile_details = models.Registration1.objects.filter(ProfileId=profile_to).first()
                    toprofile_mobile_no = toprofile_details.Mobile_no
                    return JsonResponse({"Status": 1, "message": "Call action updated successfully","toprofile_mobile_no": toprofile_mobile_no}, status=status.HTTP_200_OK)
                
                
                else:
                    # Create a new entry with status 1
                    serializer.save(status=1)
                    
                    models.Profile_notification.objects.create(
                        profile_id=profile_to,
                        from_profile_id=profile_from,
                        notification_type='CalL_request',
                        is_read=0,
                        created_at=timezone.now()
                    )
                    
                toprofile_details = models.Registration1.objects.filter(ProfileId=profile_to).first()

                if toprofile_details:
                    toprofile_mobile_no = toprofile_details.Mobile_no
                    return JsonResponse(
                        {"Status": 1, "message": "Call action saved successfully", "toprofile_mobile_no": toprofile_mobile_no}, 
                        status=status.HTTP_200_OK
                    )
                else:
                    return JsonResponse(
                        {"Status": 0, "message": "To Profile not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                    return JsonResponse({"Status": 0, "message": "No access to call to the profile"}, status=status.HTTP_200_OK)
            
        return JsonResponse(serializer.errors, status=status.HTTP_200_OK)


class My_vysassist_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            page = int(request.data.get('page_number', 1))
            per_page = int(request.data.get('per_page', 10))  
            try:
                
                all_profiles = models.Profile_vysassist.objects.filter(profile_from=profile_id,status=1)
                all_profile_ids = {str(index + 1): profile_id for index, profile_id in enumerate(all_profiles.values_list('profile_to', flat=True))}

                total_records = all_profiles.count()

                start = (page - 1) * per_page
                end = start + per_page
                              
                
                fetch_data = models.Profile_vysassist.objects.filter(profile_from=profile_id,status=1)[start:end]
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_to', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender
                    my_status=profile_data.Status

                    photo_viewing=get_permission_limits(profile_id,'photo_viewing')
               
                    if photo_viewing == 1 and my_status != 0:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1, detail.get("Photo_protection"))
                    else:
                        image_function = lambda detail: get_profile_image_azure_optimized(detail.get("ProfileId"), my_gender, 1,1)

                    # vysassist_cond = {'status': 1,'profile_from':profile_id}
                    # vysassist_count = count_records(models.Profile_vysassist, vysassist_cond)
                    
                    restricted_profile_details = [
                        {
                            "vys_profileid": detail.get("ProfileId"),
                            "vys_profile_name": detail.get("Profile_name"),
                            #"vys_Profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                            "vys_Profile_img": image_function(detail),
                            "vys_profile_age": calculate_age(detail.get("Profile_dob")),
                            "vys_verified":detail.get("Profile_verified"),
                            "vys_height":detail.get("Profile_height"),
                            "vys_star":detail.get("star_name"),
                            "vys_profession":getprofession(detail.get("profession")),
                            "vys_city":detail.get("Profile_city"),
                            "vys_degree":get_degree(detail.get("ug_degeree")),
                            "vys_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "vys_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "vys_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "vys_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "vys_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            "vys_profile_wishlist":Get_wishlist(profile_id,detail.get("ProfileId")),
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids":all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched Vysassist and profile details successfully", "data": combined_data , "vysassist_count":total_records}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"Status": 0, "message": "No Vysassist found for the given profile ID"}, status=status.HTTP_200_OK)
            except models.Express_interests.DoesNotExist:
                return JsonResponse({"Status": 0, "message": "No Vysassist found for the given profile ID"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_200_OK)
        



def get_user_statusandlastvisit(lastlogindate):

    now = timezone.now()
    # Convert now to a naive datetime
    now_naive = now.replace(tzinfo=None)
    one_month_ago = now_naive - timedelta(days=30)


    Profile_status_active = ''
    last_login_date=lastlogindate
    last_visit=''

    if last_login_date:
    # Check if the date is the default invalid value
        if last_login_date == '0000-00-00 00:00:00':
            last_login_date = None
            Profile_status_active = "Newly registered"
            # print(last_login_date,'last_login_date0000')
        else:
                # print('Hai')
                # if isinstance(last_login_date, str):
                #     print(last_login_date,'last_login_date123')
                try:
                        # Convert string to datetime
                        # print(last_login_date,'last_login_date12345')                          

                        last_visit =lastlogindate.strftime("(%B %d, %Y)") 
                            

                        #last_login_date = datetime.strptime(last_login_date, "%Y-%m-%d %H:%M:%S")


                except ValueError:
                    # print(last_login_date,'8521478523')
                    last_login_date = None
                # elif not isinstance(last_login_date, datetime):
                # print(last_login_date,'878787878')
                last_login_date = None

            # Compare the last_login_date with one_month_ago
                if last_login_date and last_login_date < one_month_ago:
                        Profile_status_active = "In Active User"  # Mark as inactive if last login is older than one month
                else:
                        Profile_status_active = "Active User"
    else:
            Profile_status_active = "Newly registered"  # Handle case where Last_login_date is None or empty


    return last_visit , Profile_status_active








#Happy stories api

class SuccessStoryListView(APIView):
    def post(self, request):
        # Get page number and page size from the request data
        page = int(request.data.get('page_number', 1))
        per_page = int(request.data.get('per_page', 9))

        # Calculate start and end indices
        start = (page - 1) * per_page
        end = start + per_page

        # Filter the queryset and apply pagination
        queryset = models.SuccessStory.objects.filter(deleted=False)[start:end]

        # Calculate the total number of records without pagination
        total_records = models.SuccessStory.objects.filter(deleted=False).count()

       
        # Serialize the results
        serializer = serializers.SuccessStoryListSerializer(queryset, many=True)

        #base_url = 'http://103.214.132.20:8000'
        base_url = settings.MEDIA_URL

        # Modify the serialized data to include the full image URL
        serialized_data = serializer.data
        for item in serialized_data:
            item['photo'] = f"{item['photo']}"
        
        # Prepare response data
        response_data = {
            'data': serializer.data,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_records + per_page - 1) // per_page,  # Calculate total pages
            'total_records': total_records,
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)




class AwardListView(APIView):
    def post(self, request):
        page = int(request.data.get('page_number', 1))
        per_page = int(request.data.get('per_page', 9))

        start = (page - 1) * per_page
        end = start + per_page

        queryset = models.Award.objects.filter(deleted=False, status=1)[start:end]

        total_records = models.Award.objects.filter(deleted=False, status=1).count()

        serializer = serializers.AwardListSerializer(queryset, many=True)

        #base_url = 'http://103.214.132.20:8000'
        base_url = settings.MEDIA_URL

        serialized_data = serializer.data
        for item in serialized_data:
            item['image'] = f"{item['image']}"
        
        # Prepare response data
        response_data = {
            'data': serialized_data,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_records + per_page - 1) // per_page, 
            'total_records': total_records,
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    


class TestimonialListView(APIView):
    def post(self, request):
        page = int(request.data.get('page_number', 1))
        per_page = int(request.data.get('per_page', 9))

        start = (page - 1) * per_page
        end = start + per_page

        queryset = models.Testimonial.objects.filter(deleted=False, status=1)[start:end]

        total_records = models.Testimonial.objects.filter(deleted=False, status=1).count()

        serializer = serializers.TestimonialListSerializer(queryset, many=True)

        #base_url = 'http://103.214.132.20:8000'
        base_url = settings.MEDIA_URL

        serialized_data = serializer.data
        for item in serialized_data:
            item['user_image'] = f"{item['user_image']}"
        
        response_data = {
            'data': serialized_data,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_records + per_page - 1) // per_page, 
            'total_records': total_records,
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)


# class Findsomeonespecial(APIView):

#     def post(self, request): 
#         # Need to get gender from logindetails table
#         # Extract input values from request data (POST request)
#         from_age = request.data.get('from_age')
#         to_age = request.data.get('to_age')
#         gender = request.data.get('gender')
#         native_state = request.data.get('search_nativestate')
#         profession = request.data.get('profession')
#         received_per_page = request.data.get('per_page')
#         received_page_number = request.data.get('page_number')
        


#         if not any([
#             from_age, to_age, native_state]):
#             return JsonResponse({'status': 'failure', 'message': "At least one search criterion must be provided."}, status=status.HTTP_200_OK)
        
#         # Set default values if not provided
#         if received_per_page is None:
#             per_page = 10
#         else:
#             try:
#                 per_page = int(received_per_page)
#             except (ValueError, TypeError):
#                 per_page = 10  # Fall back to default if conversion fails

#         if received_page_number is None:
#             page_number = 1
#         else:
#             try:
#                 page_number = int(received_page_number)
#             except (ValueError, TypeError):
#                 page_number = 1  # Fall back to default if conversion fails

#         # Ensure valid values for pagination
#         per_page = max(1, per_page)
#         page_number = max(1, page_number)

#         # Calculate the starting record for the SQL LIMIT clause
#         start = (page_number - 1) * per_page

#         # Initialize the query with the base structure
#         base_query = """
#         SELECT a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, 
#                f.profession, f.highest_education, g.EducationLevel, d.star, h.income , e.birthstar_name , e.birth_rasi_name ,a.Photo_protection,a.Gender FROM logindetails a 
#         JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
#         JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
#         JOIN masterbirthstar d ON d.id = e.birthstar_name 
#         JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
#         JOIN mastereducation g ON f.highest_education = g.RowId 
#         JOIN masterannualincome h ON h.id = f.anual_income
#         WHERE a.gender = %s """

#         # Prepare the query parameters
#         query_params = [gender]

#         # Check if additional filters are provided, and add them to the query
#         if from_age or to_age or profession :
#             # Add age filter
#             age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=" if from_age else "<=" if to_age else None
#             if age_condition_operator:
#                 base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
#                 if from_age and to_age:
#                     query_params.extend([from_age, to_age])
#                 else:
#                     query_params.append(from_age or to_age)
            
#             # Add marital status filter

#             # Add profession filter
#             if profession:
#                 base_query += " AND f.profession = %s"
#                 query_params.append(profession)

#         try:
#             with connection.cursor() as cursor:
#                     cursor.execute(base_query, query_params)
#                     all_profile_ids = [row[0] for row in cursor.fetchall()]

#                 # Log or store all_profile_ids as needed
#             #print("All Profile IDs:", all_profile_ids)

#                 # Get the total count of profiles
#             total_count = len(all_profile_ids)

#             # profile_with_indices = [{"index": i + 1, "profile_id": profile_id} for i, profile_id in enumerate(all_profile_ids)]
#             profile_with_indices={str(i + 1): profile_id for i, profile_id in enumerate(all_profile_ids)}

#             # Add pagination to the query
#             # Modify the query to use LIMIT with start and count
#             base_query += f" LIMIT %s, %s"
#             query_params.extend([start, per_page])

#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute(base_query, query_params)
#                     rows = cursor.fetchall()

#                     if rows:
#                         columns = [col[0] for col in cursor.description]
#                         results = [dict(zip(columns, row)) for row in rows]

#                         # Log or return the full query for debugging
#                         full_query = cursor.mogrify(base_query, query_params)

                       
#                         transformed_results = [transform_data2(result,gender) for result in results]

#                         return JsonResponse({
#                             'status': 'success',
#                             'total_count':total_count,
#                             'data': transformed_results,
#                             'received_per_page': received_per_page,
#                             'received_page_number': received_page_number,
#                             'calculated_per_page': per_page,
#                             'calculated_page_number': page_number,
#                             'all_profile_ids':profile_with_indices
#                         }, status=status.HTTP_200_OK)
#                     else:
#                         # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)
#                         return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)
#             except Exception as e:
#                 return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         except Exception as e:
#             return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Searchbeforelogin(APIView):

    def post(self, request): 
        # Extract input values from request data (POST request)
        from_age = request.data.get('from_age')
        to_age = request.data.get('to_age')
        gender = request.data.get('gender')
        native_state = request.data.get('search_nativestate')
        city = request.data.get('search_city')
        profession = request.data.get('profession')
        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')
        
        if not any([gender,from_age, to_age, native_state,profession,city]):
            return JsonResponse({'status': 'failure', 'message': "At least one search criterion must be provided."}, status=status.HTTP_200_OK)
        
        # Set default values if not provided
        per_page = int(received_per_page) if received_per_page and received_per_page.isdigit() else 10
        page_number = int(received_page_number) if received_page_number and received_page_number.isdigit() else 1

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        # Initialize the query with the base structure
        base_query = """
        SELECT a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income , e.birthstar_name , e.birth_rasi_name ,a.Photo_protection,a.Gender 
        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        WHERE a.gender = %s
        """

        # Prepare the query parameters
        query_params = [gender]

        # Add age filter
        if from_age or to_age:
            age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=%s" if from_age else "<=%s"
            base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
            if from_age and to_age:
                query_params.extend([from_age, to_age])
            else:
                query_params.append(from_age or to_age)
        
        # Add profession filter
        if profession:
            base_query += " AND f.profession = %s"
            query_params.append(profession)

                # Add profession filter
        if native_state:
            base_query += " AND a.Profile_state = %s"
            query_params.append(native_state)
        

        # print('search before login 173', city)
        if city:
            if city != '173':
                # print('search before login 173', city)
                base_query += " AND a.Profile_district = %s"
                query_params.append(city)
            else:
                base_query += " AND a.Profile_district NOT IN (3, 28, 62, 96, 97, 15)"

        # print('base_query',base_query)
        try:
            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                all_profile_ids = [row[0] for row in cursor.fetchall()]
                total_count = len(all_profile_ids)

            # Add pagination to the query
            base_query += " LIMIT %s, %s"
            query_params.extend([start, per_page])

            try:
                with connection.cursor() as cursor:
                    cursor.execute(base_query, query_params)
                    rows = cursor.fetchall()

                    if rows:
                        columns = [col[0] for col in cursor.description]
                        results = [dict(zip(columns, row)) for row in rows]

                        if gender == 'male':
                            opposite_gender = 'female'
                        else:
                            opposite_gender = 'male'
                        
                        transformed_results = [transform_data2(result, opposite_gender) for result in results]

                        return JsonResponse({
                            'status': 'success',
                            'total_count': total_count,
                            'data': transformed_results,
                            'received_per_page': received_per_page,
                            'received_page_number': received_page_number,
                            'calculated_per_page': per_page,
                            'calculated_page_number': page_number,
                            'all_profile_ids': {str(i + 1): profile_id for i, profile_id in enumerate(all_profile_ids)}
                        }, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_200_OK)


class GetPageDetails(APIView):

    def post(self, request):
        page_id = request.data.get('page_id')
        
        try:
            page = models.Page.active_objects.get(id=page_id, status='active', deleted=False)
            serializer = serializers.PageSerializer(page)
            return JsonResponse({
                "status": 1,
                "message": "page details fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except models.Page.DoesNotExist:
            return JsonResponse({
                "status": 0,
                "message": "page id not found"
            }, status=status.HTTP_200_OK)
            
            
            
            
            
class ActiveProfilesAndHappyCustomersAPIView(APIView):
    def post(self, request):
        active_profiles_count = models.Registration1.objects.filter(status=1).count()

        happy_customers_count = 56555  
        
        return JsonResponse({
            "status": "success",
            "message": "Active profiles and happy customers fetched successfully",
            "data": {
                "active_profiles_count": active_profiles_count,
                "happy_customers_count": happy_customers_count
            }
        })
        
        

class JustRegisteredAPIView(APIView):
    def post(self, request):
        recent_users = models.Registration1.objects.all().order_by('-DateOfJoin')[:10]
        active_profiles_count = models.Registration1.objects.filter(Status=1).count()
        happy_customers_count = 56555
 
 
        users_data = []
        today = now().date()
 
        for user in recent_users:
            dob = user.Profile_dob
 
            if isinstance(dob, str):
                dob = datetime.strptime(dob, "%Y-%m-%d").date()  
            elif isinstance(dob, datetime):
                dob = dob.date()  
 
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
 
            education = models.Edudetails.objects.filter(profile_id=user.ProfileId).first()
            if education is not None:
                field_id = getattr(education, 'field_ofstudy', None)
 
                if field_id:
                    try:
                        education_field_obj = models.Profilefieldstudy.objects.get(id=field_id)
                        education_field= education_field_obj.field_of_study
                    except models.Profilefieldstudy.DoesNotExist:
                        education_field = "Not available"
                else:
                    education_field = "Not available"
 
            horoscope = models.Horoscope.objects.filter(profile_id=user.ProfileId).first()
 
            if horoscope and horoscope.birthstar_name:
                birthstar_obj = models.Birthstar.objects.filter(id=horoscope.birthstar_name).first()
                birthstar_name = birthstar_obj.star if birthstar_obj else "Not available"
            else:
                birthstar_name = "Not available"
 
            users_data.append({
                "profile_id": user.ProfileId,
                "age": age,
                "birthstar": birthstar_name,
                "education": education_field,
                "gender": user.Gender,
            })
 
        return JsonResponse({
            "status": "success",
            "message": "Just registered users fetched successfully",
            "data": users_data,
            "active_profiles_count": active_profiles_count,
            "happy_customers_count": happy_customers_count
        })
        
    
        
        
        
class GetFooterView(APIView):
    def get(self, request):
        settings = models.AdminSettings.objects.first()
        if settings:
            serializer = serializers.AdminSettingsSerializer(settings)
            return JsonResponse({
                "status": "success",
                "message": "Footer settings fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return JsonResponse({
            "status": "error",
            "message": "Settings not found"
        }, status=status.HTTP_200_OK)        
    



# def get_blurred_image(image_name):
#     # Construct the image path
#     #print('image_name',image_name)

#     image_name = image_name[len('/'):]
    
#     image_path = os.path.join(settings.MEDIA_URL,image_name)

#     # print('image_path',image_path)
    
#     # Check if the file exists
#     if not os.path.isfile(image_path):
#         return settings.MEDIA_URL+'default_img.png'
    
#     try:
#         # Open the image using Pillow
#         with Image.open(image_path) as img:
#             # Apply blur effect
#             blurred_image = img.filter(ImageFilter.GaussianBlur(10))  # Adjust the blur radius if needed
            
#             # Save the blurred image to a BytesIO object
#             buffered = BytesIO()
#             blurred_image.save(buffered, format="JPEG")
            
#             # Encode the image in base64
#             img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
#             # Return the base64 encoded image in a JSON response
#             return 'data:image/jpeg;base64,'+img_base64
    
#     except Exception as e:
#         return settings.MEDIA_URL+'default_img.png'


#Commanded by vinoth by 19-05-25

# def get_blurred_image(image_name):
#     # print('Inside Blur Images')
#     # print("Original image URL:", image_name)

#     try:
#         # Parse URL and extract path
#         parsed_url = urlparse(image_name)
#         full_path = parsed_url.path.lstrip('/')  # Remove leading slash
        
#         # Remove container name from the path
#         container_name = settings.AZURE_CONTAINER
#         if full_path.startswith(container_name + '/'):
#             blob_path = full_path[len(container_name)+1:]  # Remove "vysyamala/"
#         else:
#             blob_path = full_path
        
#         print('Container:', container_name)
#         print('Blob path:', blob_path)

#         if not blob_path:
#             raise ValueError("Blob path is empty")

#         # Initialize BlobServiceClient
#         blob_service = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        
#         # Check if the blurred image already exists
#         blurred_blob_name = f"blurred/{os.path.basename(blob_path)}"
#         blurred_blob_client = blob_service.get_blob_client(
#             container=container_name,
#             blob=blurred_blob_name
#         )

#         # If blurred image exists, return the URL immediately
#         if blurred_blob_client.exists():
#             print("Blurred image already exists.")
#             return f"https://{blob_service.account_name}.blob.core.windows.net/{container_name}/{blurred_blob_name}"

#         # Get blob client for original image
#         blob_client = blob_service.get_blob_client(
#             container=container_name,
#             blob=blob_path
#         )

#         # Verify blob exists
#         if not blob_client.exists():
#             raise FileNotFoundError(f"Blob {blob_path} not found in container {container_name}")

#         # Download and process image
#         image_bytes = blob_client.download_blob().readall()

#         with Image.open(BytesIO(image_bytes)) as img:
#             # Resize image for faster processing (optional)
#             img = img.resize((img.width // 2, img.height // 2))

#             # Apply blur
#             blurred_image = img.filter(ImageFilter.GaussianBlur(5))
            
#             # Save blurred image to memory (in memory, avoiding disk I/O)
#             output_buffer = BytesIO()
#             blurred_image.save(output_buffer, format="JPEG", quality=70)
#             output_buffer.seek(0)  # Rewind the buffer
            
#             # Upload blurred image to Azure
#             blurred_blob_client.upload_blob(output_buffer, overwrite=True, content_settings=ContentSettings(content_type="image/jpeg"))
            
#             print(f"Blurred image uploaded as: {blurred_blob_name}")
            
#             # Return the URL of the blurred image
#             return f"https://{blob_service.account_name}.blob.core.windows.net/{container_name}/{blurred_blob_name}"

#     except FileNotFoundError as fnf_error:
#         logger.error(f"Image not found: {fnf_error}")
#         return settings.MEDIA_URL + 'default_img.png'

#     except Exception as e:
#         logger.exception(f"Error processing image: {e}")
#         return settings.MEDIA_URL + 'default_img.png'






def get_blurred_images_updated(image_names, return_multiple=False):
    """
    Get blurred image URLs from Azure Blob Storage
    Args:
        image_names: Single image path (str) or list of paths
        return_multiple: Always return dict even for single image
    Returns:
        Single URL (str) or dict of {original_path: blurred_url}
    """
    if not image_names:
        return {} if return_multiple else settings.MEDIA_URL + 'default_img.png'

    # Convert single image to list for uniform processing
    single_mode = not isinstance(image_names, list)
    if single_mode:
        image_names = [image_names]

    results = {}
    container_name = settings.AZURE_CONTAINER
    blob_service = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)

    for original_url in image_names:
        try:
            parsed_url = urlparse(original_url)
            full_path = parsed_url.path.lstrip('/')
            
            # Extract blob path
            if full_path.startswith(container_name + '/'):
                blob_path = full_path[len(container_name)+1:]
            else:
                blob_path = full_path

            if not blob_path:
                raise ValueError("Empty blob path")

            # Construct blurred image path
            blurred_blob_name = f"blurred_images/{os.path.basename(blob_path)}"
            blurred_blob_client = blob_service.get_blob_client(
                container=container_name,
                blob=blurred_blob_name
            )

            if blurred_blob_client.exists():
                results[original_url] = (
                    f"https://{blob_service.account_name}.blob.core.windows.net/"
                    f"{container_name}/{blurred_blob_name}"
                )
            else:
                results[original_url] = settings.MEDIA_URL + 'default_img.png'

        except Exception as e:
            logger.error(f"Error processing {original_url}: {str(e)}")
            results[original_url] = settings.MEDIA_URL + 'default_img.png'

    if single_mode and not return_multiple:
        return results.get(image_names[0], settings.MEDIA_URL + 'default_img.png')
    return results



def get_blurred_image(image_name):
    try:
        # Parse the URL and get the blob path
        parsed_url = urlparse(image_name)
        full_path = parsed_url.path.lstrip('/')  # Remove leading slash

        container_name = settings.AZURE_CONTAINER
        if full_path.startswith(container_name + '/'):
            blob_path = full_path[len(container_name) + 1:]  # Remove container name
        else:
            blob_path = full_path

        if not blob_path:
            raise ValueError("Blob path is empty")

        # Get the blurred image blob path
        blurred_blob_name = f"blurred_images/{os.path.basename(blob_path)}"

        # Initialize BlobServiceClient and get the blob client for blurred image
        blob_service = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        blurred_blob_client = blob_service.get_blob_client(container=container_name, blob=blurred_blob_name)

        # Check if blurred image exists
        if blurred_blob_client.exists():
            return f"https://{blob_service.account_name}.blob.core.windows.net/{container_name}/{blurred_blob_name}"
        else:
            return settings.MEDIA_URL + 'default_img.png'

    except Exception as e:
        logger.exception(f"Error processing image: {e}")
        return settings.MEDIA_URL + 'default_img.png'


  
def can_send_express_interest(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    # print('current_datetime',timezone.now())
    # print('current_date',current_date)

    

    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired

    # Check if the plan allows sending express interests
    if plan and plan.exp_int_lock and plan.express_int_count is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.exp_int_lock == 0:
            return False  # Not allowed to send express interests
        elif plan.exp_int_lock == 2:
            return True  # Unlimited express interests
        else:
                        # Check how many express interests the user has sent today
            #print('894563')

            
            start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            
            # print('date',date.today())
            sent_interests_count = models.Express_interests.objects.filter(
                profile_from=profile_id, 
                # req_datetime__date=current_date, 
                req_datetime__gte=start_of_day, 
                req_datetime__lt=end_of_day,
                status__in=[1, 2, 3]
            ).count()

            # print('sent_interests_count',sent_interests_count)
            # print('express_int_count',plan.express_int_count)

            if sent_interests_count < plan.express_int_count:
                return True  # Within the express interest limit
            else:
                return False  # Reached the limit

    return False  # If no plan or plan is restricted






def can_send_photoreq(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired


    # Check if the plan allows sending express interests
    if plan and plan.photo_req is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.photo_req == 0:
            return False  # Not allowed to send express interests
        elif plan.photo_req == 1:
            return True  # Unlimited express interests

    return False  # If no plan or plan is restricted

def can_save_personal_notes(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    # Check if the plan allows sending express interests
    if plan and plan.private_notes is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.private_notes == 0:
            return False  # Not allowed to send express interests
        elif plan.private_notes == 1:
            return True  # Unlimited express interests

    return False  # If no plan or plan is restricted


def can_save_bookmark(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    # Check if the plan allows sending express interests
    if plan and plan.book_mark is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.book_mark == 0:
            return False  # Not allowed to send express interests
        elif plan.book_mark == 1:
            return True  # Unlimited express interests

    return False  # If no plan or plan is restricted



def can_call_profile(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired


    # print('current_datetime',timezone.now())
    # print('current_date',current_date)

    # print(plan)
   
    # Check if the plan allows sending express interests
    if plan and plan.click_to_call is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.click_to_call == 0:
            return False  # Not allowed to send express interests
        elif plan.click_to_call == 2:
            return True  # Unlimited click to call action
        else:
                        # Check how many express interests the user has sent today
            #print('894563')

            
            # start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # end_of_day = start_of_day + timedelta(days=1)
            
            
            # print('date',date.today())
            call_action_count = models.Profile_callogs.objects.filter(
                profile_from=profile_id, 
                # req_datetime__date=current_date, 
                # req_datetime__gte=start_of_day, 
                # req_datetime__lt=end_of_day,
                status__in=[1]
            ).count()

            # print('sent_interests_count',sent_interests_count)
            # print('express_int_count',plan.express_int_count)

            if call_action_count < plan.click_to_call_count:
                return True  # Within the express interest limit
            else:
                return False  # Reached the limit

    return False  # If no plan or plan is restricted


def can_get_vysassist_profile(profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    # current_date = now().date()
    current_time = timezone.now()
    current_date = current_time.date()

    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired

    
    # print('current_datetime',timezone.now())
    # print('current_date',current_date)

    # print(plan)
      
    # Check if the plan allows sending express interests
    if plan and plan.vys_assist is not None:
        # print('123456')
        # print('datetime',datetime.today())
        if plan.vys_assist == 0:
            return False  # Not allowed to send vysyrequest interests
        elif plan.vys_assist == 2:
            return True  # Unlimited click to vysassist request
        else:
                 
                 
                        # Check how many express interests the user has sent today
            #print('894563')

            
            # start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # end_of_day = start_of_day + timedelta(days=1)
            
            
            # print('date',date.today())
            vysyassist_action_count = models.Profile_vysassist.objects.filter(
                profile_from=profile_id, 
                # req_datetime__date=current_date, 
                # req_datetime__gte=start_of_day, 
                # req_datetime__lt=end_of_day,
                status__in=[1]
            ).count()

            # print('sent_interests_count',sent_interests_count)
            # print('express_int_count',plan.express_int_count)
            # print('vysyassist_action_count',vysyassist_action_count)
            if vysyassist_action_count < plan.vys_assist_count:
                return True  # Within the express interest limit
            else:
                return False  # Reached the limit

    return False  # If no plan or plan is restricted





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



def can_see_compatability_report(profile_id,req_profile_id):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id   
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    current_time = timezone.now()
    current_date = current_time.date()

    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired


    # Check if the plan allows sending express interests
    if plan and plan.compatability_report is not None:
        if plan.compatability_report == 0:
            return False  # Not allowed to send express interests
        elif plan.compatability_report == 1:
            return True  # Unlimited express interests
        else:
                        # Check how many express interests the user has sent today
            #print('894563')           
            
            # print('date',date.today())
            sent_pdf_count = models.Profile_docviewlogs.objects.filter(
                profile_id=profile_id, 
                type=3
            ).exclude(viewed_profile=req_profile_id).count()

            if sent_pdf_count < plan.compatability_report:
                return True  # Within the express interest limit
            else:
                return False  # Reached the limit

    return False  # If no plan or plan is restricted


def can_see_horoscope_report(profile_id,req_profile_id,lang):

    registration=models.Registration1.objects.filter(ProfileId=profile_id).first()
    plan_id = registration.Plan_id    
    
    plan = models.Profile_PlanFeatureLimit.objects.filter(profile_id=profile_id,plan_id=plan_id,status=1).first()

    # Check if the plan allows sending express interests
    
    current_time = timezone.now()
    current_date = current_time.date()
    
    if not plan:
        return 0  # No active plan found
    
    if getattr(plan, 'membership_todate', None) and plan.membership_todate.date() < current_date:
        return 0  # Membership expired
    
    if lang is 'english':
        if plan and plan.eng_print is not None:
            if plan.eng_print == 0:
                return False  # Not allowed to send express interests
            elif plan.eng_print == 1:
                return True  # Unlimited express interests
            else:
                            # Check how many express interests the user has sent today
                #print('894563')           
                
                # print('date',date.today())
                sent_pdf_count = models.Profile_docviewlogs.objects.filter(
                    profile_id=profile_id, 
                    type=2
                ).exclude(viewed_profile=req_profile_id).count()

                if sent_pdf_count < plan.eng_print:
                    return True  # Within the express interest limit
                else:
                    return False  # Reached the limit

        return False  # If no plan or plan is restricted
    else :
        if plan and plan.tamil_print is not None:
            if plan.tamil_print == 0:
                return False  # Not allowed to send express interests
            elif plan.tamil_print == 1:
                return True  # Unlimited express interests
            else:
                            # Check how many express interests the user has sent today
                #print('894563')           
                
                # print('date',date.today())
                sent_pdf_count = models.Profile_docviewlogs.objects.filter(
                    profile_id=profile_id, 
                    type=2
                ).exclude(viewed_profile=req_profile_id).count()

                if sent_pdf_count < plan.tamil_print:
                    return True  # Within the express interest limit
                else:
                    return False  # Reached the limit

        return False  # If no plan or plan is restricted


class Profile_other_fields(APIView):
    def post(self, request):
        # Required field
        profile_id = request.POST.get('profile_id')
        
        # Check if profile_id is provided
        if not profile_id:
            return JsonResponse({
                "status": 0,
                "message": "The 'profile_id' field is required."
            }, status=400)
        
        # List of optional fields
        optional_fields = [
            ('image', request.FILES.get('image')),  # Check image file
            ('horoscope_file', request.FILES.get('horoscope_file')),  # Check horoscope_file
            ('Profile_idproof', request.FILES.get('Profile_idproof')),
            ('EmailId', request.POST.get('EmailId')),
            ('property_worth', request.POST.get('property_worth')),
            ('about_self', request.POST.get('about_self')),
            ('about_family', request.POST.get('about_family')),
            ('career_plans', request.POST.get('career_plans')),
            ('Video_url', request.POST.get('Video_url')),
            ('anual_income', request.POST.get('anual_income'))
        ]
        
        # Check if at least one optional field is provided
        if not any(field_value for field_name, field_value in optional_fields):
            return JsonResponse({
                "status": 0,
                "message": "At least one of the following fields is required: "
                           "image, horoscope_file, Profile_idproof,EmailId, property_worth, "
                           "about_self, about_family, career_plans, Video_url , anual_income"
            }, status=400)

        
        image = request.FILES.get('image')
        horoscope_file = request.FILES.get('horoscope_file')
        Profile_idproof = request.FILES.get('Profile_idproof')
        EmailId = request.POST.get('EmailId')
        property_worth  = request.POST.get('property_worth')
        about_self   = request.POST.get('about_self')
        about_family   = request.POST.get('about_family')
        career_plans = request.POST.get('career_plans')
        Video_url  = request.POST.get('Video_url')
        anual_income  = request.POST.get('anual_income')
        #try:
            # Fetch or create the necessary instances
        horoscope_instance, _ = models.Horoscope.objects.get_or_create(profile_id=profile_id)
        image_instance = models.Image_Upload.objects.create(profile_id=profile_id)
        registration_instance = models.Registration1.objects.get(ProfileId=profile_id)
        education_instance = models.Edudetails.objects.get(profile_id=profile_id)
        family_instance = models.Familydetails.objects.get(profile_id=profile_id)

        # File validation parameters
        max_file_size = 10 * 1024 * 1024  # 10MB
        valid_extensions = ['doc', 'docx', 'pdf', 'png', 'jpeg', 'jpg']
        valid_image_extensions = ['png', 'jpeg', 'jpg']

        # Update the respective fields if provided
        try:
            if horoscope_file:
                if horoscope_file.size > max_file_size:
                    return JsonResponse({"error": "Horoscope file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(horoscope_file.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid horoscope file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                horoscope_instance.horoscope_file.save(horoscope_file.name, ContentFile(horoscope_file.read()), save=True)
                horoscope_instance.horo_file_updated = timezone.now()
                horoscope_instance.save()

            if Profile_idproof:
                if Profile_idproof.size > max_file_size:
                    return JsonResponse({"error": "ID proof file size should be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(Profile_idproof.name)[1][1:].lower()
                if file_extension not in valid_extensions:
                    return JsonResponse({"error": "Invalid ID proof file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                registration_instance.Profile_idproof.save(Profile_idproof.name, ContentFile(Profile_idproof.read()), save=True)
                registration_instance.save()
            
            if image:
                if image.size > max_file_size:
                    return JsonResponse({"error": "Uploded Images"}, status=status.HTTP_400_BAD_REQUEST)

                file_extension = os.path.splitext(image.name)[1][1:].lower()
                if file_extension not in valid_image_extensions:
                    return JsonResponse({"error": "Invalid ID proof file type. Accepted formats are: doc, docx, pdf, png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)

                image_instance.image.save(image.name, ContentFile(image.read()), save=True)
                image_instance.save()
        
            if Video_url or Video_url is not None:
                registration_instance.Video_url = Video_url
                registration_instance.save()
            
            if EmailId or EmailId is not None:
                registration_instance.EmailId = EmailId
                registration_instance.save()
            
            if career_plans or career_plans is not None:
                education_instance.career_plans = career_plans
                education_instance.save()
            
            if anual_income  or anual_income is not None:
                education_instance.anual_income = anual_income
                education_instance.save()
            
            if property_worth  or property_worth is not None:
                family_instance.property_worth = property_worth
                family_instance.save()
            
            if about_self  or about_self is not None:
                family_instance.about_self = about_self
                family_instance.save()

            if about_family  or about_family is not None:
                family_instance.about_family = about_family
                family_instance.save()

            # Serialize and respond
            # response_data = {
            #     "horoscope_data": serializers.HorosuploadSerializer(horoscope_instance).data,
            #     "registration_data": serializers.IdproofuploadSerializer(registration_instance).data,
            # }        
            # Proceed with logic if validation passes
            return JsonResponse({"status": 1, "message": "Updated Sucessfully"}, status=200)
        except:
            return JsonResponse({"status": 0, "message": "Error In update"}, status=200)
        


def get_unread_messages_count(profile_id):
    # Find all rooms the user is part of
    rooms = models.Room.objects.filter(user_ids__contains=profile_id)

    # If no rooms exist, return 0
    if not rooms.exists():
        return 0

    # Count unread messages in those rooms, not sent by the user
    unread_count = models.Message.objects.filter(
        room__in=rooms,
        read_msg=False
    ).exclude(user=profile_id).count()

    return unread_count

class UnreadMessagesCountView(APIView):
    def post(self, request):
        profile_id = request.POST.get('profile_id')

        if not profile_id:
            return JsonResponse({"error": "Profile ID is required"}, status=400)

        if not models.Registration1.objects.filter(ProfileId=profile_id).exists():
            return JsonResponse({"error": "Profile ID does not exist"}, status=404)

        unread_count = get_unread_messages_count(profile_id)
        return JsonResponse({"unread_count": unread_count}, status=200)


def mark_messages_as_read(request, room_name):
    if request.method == 'POST':
        user = request.user
        room = models.Room.objects.get(name=room_name)
        messages = models.Message.objects.filter(room=room, user=user, read_msg=False)
        messages.update(read_msg=True)  # Mark all unread messages as read
        return JsonResponse({"success": True, "message": "Messages marked as read."})



class CreateOrRetrieveChat(APIView):
    def post(self, request):
        user1_id = request.data.get('profile_id')
        user2_id = request.data.get('profile_to')

        # serializer = serializers.Profile_idValidationSerializer(data=request.data)
        serializer2 = serializers.Profile_toValidationSerializer(data=request.data)

        if serializer2.is_valid():
            user_ids=user1_id+','+user2_id
            
            if not user1_id or not user2_id:
                return JsonResponse({'error': 'Both profile_id and profile_to are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate the room ID based on the two user IDs
            room_id_name = generate_room_id(user1_id, user2_id)

            # Check if the room already exists
            room = models.Room.objects.filter(name=room_id_name).first()

            if room:
                # Room already exists, return the room ID
                return JsonResponse({'statue':1,'room_id_name': room.name, 'created': False}, status=status.HTTP_200_OK)
            else:
                # Room doesn't exist, create a new one
                new_room = models.Room.objects.create(name=room_id_name,user_ids=user_ids)
                return JsonResponse({'statue':1,'room_id_name': new_room.name, 'created': True}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer2.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserChat(APIView):
    def post(self, request):
        user_id = request.data.get('profile_id')

        if not user_id:
            return JsonResponse({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Querying Room objects where user_id exists in the user_ids column
        # Query Room objects where user_id exists in user_ids column
        rooms = models.Room.objects.filter(Q(user_ids__contains=user_id))

        # Prepare the list to store the result
        result_data = []

        # Iterate through the rooms and handle comma-separated user_ids
        if rooms:
            for room in rooms:
                # Split the user_ids field to get all user IDs
                user_ids_list = room.user_ids.split(',')

                # print('user_ids_list',user_ids_list)
                
                # Remove the searched user_id from the list
                remaining_ids = [uid for uid in user_ids_list if uid != user_id]


                remaining_user_id = remaining_ids[0] if remaining_ids else None

                
                # profile_id =[remaining_ids]

                profile_details = get_profile_details(remaining_ids)

                # print('profile_details',profile_details)

                oposi_gender=''
                if((profile_details[0]['Gender']=='male') or (profile_details[0]['Gender']=='Male')):
                    oposi_gender='female'
                else:
                    oposi_gender='male'

                profile_image = Get_profile_image(profile_details[0]['ProfileId'], oposi_gender, 1,profile_details[0]['Photo_protection'])

                # print('profile_image',profile_image)
                
                get_last_mesaage = models.Message.objects.filter(room=room.id).order_by('-date').first()

                last_mesaage=''
                if get_last_mesaage:
                    
                    last_mesaage=get_last_mesaage.value # Replace 'content' with the actual field you want to access
                    
                    if(get_last_mesaage.user!=user_id):
                        last_mesaage_seen=get_last_mesaage.read_msg
                    else:
                        last_mesaage_seen=True
                    
                    message_time=time_ago(get_last_mesaage.date)
                    

                else:
                    last_mesaage=''
                    message_time=''
                    last_mesaage_seen=True

                # print('remaining_user_ids:', remaining_user_id)
                
                # print('remaining_ids',remaining_ids)
                
                # Prepare the result with room_name_id and remaining user_ids
                result_data.append({
                    "room_name_id": room.name,      # Assuming 'name' is the room name column
                    "profile_user_id": remaining_user_id,
                    "profile_user_name": profile_details[0]['Profile_name'],
                    "profile_image":profile_image , # List of user_ids excluding the searched one
                    "last_mesaage":last_mesaage,
                    "last_mesaage_seen":last_mesaage_seen,
                    "message_time":message_time,
                    "profile_lastvist": get_user_statusandlastvisit(profile_details[0]['Last_login_date'])[0],
                })

            return JsonResponse({"status":1,"mesaage":"Message Lists Fectched Sucessfully",'data':result_data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": 0, "mesaage":"No message lists"}, status=status.HTTP_200_OK)
        

class GetUserChat_search(APIView):
    def post(self, request):
        user_id = request.data.get('profile_id')
        search_id = request.data.get('search_id')  # This is the ID you're searching for in the user_ids field

        if not user_id:
            return JsonResponse({'error': 'profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not search_id:
            return JsonResponse({'error': 'search_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Fetch all rooms where user_id is part of user_ids
        rooms = models.Room.objects.filter(Q(user_ids__icontains=user_id))

        result_data = []
        if rooms:
            for room in rooms:
                user_ids_list = room.user_ids.split(',')

                # Step 2: Partial match with search_id
                if search_id in room.user_ids:
                    remaining_ids = [uid for uid in user_ids_list if uid != user_id]
                else:
                    remaining_ids = []

                # Only process if there are remaining IDs
                if remaining_ids:
                    remaining_user_id = remaining_ids[0] if remaining_ids else None

                    # Get profile details for the remaining user IDs
                    profile_details = get_profile_details(remaining_ids)
                    oposi_gender=''
                    if((profile_details[0]['Gender']=='male') or (profile_details[0]['Gender']=='Male')):
                        oposi_gender='female'
                    else:
                        oposi_gender='male'

                    if profile_details:
                        profile_image = Get_profile_image(profile_details[0]['ProfileId'], oposi_gender, 1, profile_details[0]['Photo_protection'])

                        # Get the last message in the room
                        get_last_message = models.Message.objects.filter(room=room.id).order_by('-date').first()

                        last_message = ''
                        message_time = ''

                        if get_last_message:
                            last_message = get_last_message.value  # Replace 'value' with the actual field you want to access
                            message_time = time_ago(get_last_message.date)

                        # Prepare the result data
                        result_data.append({
                            "room_name_id": room.name,  # Assuming 'name' is the room name column
                            "profile_user_id": remaining_user_id,
                            "profile_user_name": profile_details[0]['Profile_name'],
                            "profile_image": profile_image,
                            "last_message": last_message,
                            "message_time": message_time,
                            "profile_last_visit": get_user_statusandlastvisit(profile_details[0]['Last_login_date'])[0],
                        })

            return JsonResponse({"status": 1,"mesaage":"Message Lists Fectched Sucessfully",'data': result_data}, status=status.HTTP_200_OK)
        else:
             return JsonResponse({"status": 0, "mesaage":"No message lists"}, status=status.HTTP_200_OK)


class HomepageListView(APIView):
    def get(self, request):
        # Fetching all homepage entries
        homepages = models.Homepage.objects.filter(deleted=False)

        if not homepages.exists():
            return JsonResponse({'status': 'error', 'message': 'No homepage entries found.'}, status=status.HTTP_404_NOT_FOUND)

        # Serializing the data
        serializer = serializers.HomepageSerializer(homepages, many=True)

        # Return a structured response
        return JsonResponse({
            'status': 'success',
            'message': 'Homepage fetched successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        # Fetching the homepage entry (assuming there should be only one active homepage entry)
        try:
            homepage = models.Homepage.objects.get(deleted=False)
        except models.Homepage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Homepage entry not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Update the existing entry with the new data
        serializer = serializers.HomepageSerializer(homepage, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Homepage updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def get_degree_name(degree_ids, other_degree):
        if not degree_ids:
            # If only other_degree is provided, return it directly
            return other_degree if other_degree else None

        try:
            id_list = [int(x) for x in str(degree_ids).split(',') if x.strip().isdigit()]
            id_list = [x for x in id_list if x != 86]
            degree_names = list(
                models.Profileedu_degree.objects.filter(id__in=id_list)
                .values_list("degeree_name", flat=True)
            )
            if other_degree:
                degree_names.append(other_degree)
            final_names = ", ".join(degree_names) if degree_names else None
            return final_names
        except Exception:
            return None

def My_horoscope_generate(request, user_profile_id, filename="Horoscope_withbirthchart"):

                # print('1234567')
  
                # Retrieve the Horoscope object based on the provided profile_id
                horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
                education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)

                if all(not str(val).strip() for val in [
                    login_details.Profile_address,
                    get_district_name(login_details.Profile_district),
                    get_city_name(login_details.Profile_city),
                    login_details.Profile_pincode
                ]):
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>N/A</p>"""
                else:
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>{login_details.Profile_address}</p>
                        <p>{get_district_name(login_details.Profile_district)}, {get_city_name(login_details.Profile_city)}</p>
                        <p>{login_details.Profile_pincode}.</p>
                    """

            
                mobile_email_content = f"""
                        <p>Mobile: {login_details.Mobile_no or 'N/A'}</p>
                        <p>Alternate Mobile: {login_details.Profile_alternate_mobile or 'N/A'}</p>
                        <p>WhatsApp: {login_details.Profile_whatsapp or 'N/A'}</p>
                        <p>Email: {login_details.EmailId or 'N/A'}</p>
                """
                try:
                    degree= get_degree_name(education_details.degree,education_details.other_degree)  
                except Exception as e:
                    degree = None
                # family details
                family_details = models.Familydetails.objects.filter(profile_id=user_profile_id)
                if family_details.exists():
                    family_detail = family_details.first()  

                    father_name = family_detail.father_name  
                    father_occupation = family_detail.father_occupation
                    family_status = family_detail.family_status
                    mother_name = family_detail.mother_name 
                    mother_occupation = family_detail.mother_occupation
                    no_of_sis_married = family_detail.no_of_sis_married
                    no_of_bro_married = family_detail.no_of_bro_married
                    suya_gothram = family_detail.suya_gothram
                    madulamn = family_detail.madulamn if family_detail.madulamn != None else "N/A" 
                    no_of_sister = family_detail.no_of_sister
                    no_of_brother = family_detail.no_of_brother
                else:
                    # Handle case where no family details are found
                    father_name = father_occupation = family_status = " "
                    mother_name = mother_occupation = " "
                    no_of_sis_married = no_of_bro_married = 0
                
                try:
                    num_sisters_married = int(no_of_sis_married)
                except ValueError:
                    num_sisters_married = 0     
            
                try:
                    num_brothers_married = int(no_of_bro_married)
                except ValueError:
                    num_brothers_married = 0   
                if int(num_sisters_married) == 0:
                    no_of_sis_married = "No"

                if  int(num_brothers_married) == 0:
                    no_of_bro_married="No"


                if no_of_sister=="0" or no_of_sister =='':
                    no_of_sis_married='No'
                    no_of_sister ='No'

                if no_of_brother=="0" or no_of_brother =='':
                    no_of_bro_married='No'
                    no_of_brother ='No'
                

                # Education and profession details
                highest_education = education_details.highest_education

                annual_income = "Unknown"
                actual_income = str(education_details.actual_income).strip()
                annual_income_id = education_details.anual_income

                if not actual_income or actual_income in ["", "~"]:
                    if annual_income_id and str(annual_income_id).isdigit():
                        annual_income = models.Annualincome.objects.filter(id=int(annual_income_id)).values_list('income', flat=True).first() or "Unknown"
                else:
                    annual_income = actual_income

                # personal details
                name = login_details.Profile_name  # Assuming a Profile_name field exists
                date =  format_date_of_birth(login_details.Profile_dob)
                dob = date
                complexion = login_details.Profile_complexion
                user_profile_id = login_details.ProfileId
                height = cm_to_feet_inches(login_details.Profile_height)

                                # Safely convert to integer only if value is digit and non-empty
                def safe_get_value(model, pk_field, value, name_field='name', default='N/A'):
                    try:
                        if value and str(value).isdigit():
                            return model.objects.filter(**{pk_field: value}).values_list(name_field, flat=True).first() or default
                    except Exception:
                        pass
                    return default

                # Complexion
                complexion_id = login_details.Profile_complexion
                complexion = safe_get_value(models.Profilecomplexion, 'complexion_id', complexion_id, 'complexion_desc')

                # Highest Education
                highest_education_id = education_details.highest_education
                highest_education = "Unknown"
                if highest_education_id:
                    highest_education = models.Edupref.objects.filter(RowId=highest_education_id).values_list('EducationLevel', flat=True).first() or "Unknown"

                

                field_ofstudy_id = education_details.field_ofstudy
                fieldof_study=" "
                if field_ofstudy_id:
                    fieldof_study = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id).values_list('field_of_study', flat=True).first() or "Unknown"
                
                about_edu=education_details.about_edu
                
                final_education = (highest_education + ' ' + fieldof_study).strip() or about_edu

                
                # Annual Income
                # annual_income_id = education_details.anual_income
                # annual_income = safe_get_value(models.Annualincome, 'id', annual_income_id, 'income')

                # Profession
                profession_id = education_details.profession
                profession = safe_get_value(models.Profespref, 'RowId', profession_id, 'profession')

                # Work place and occupation details
                work_place = education_details.work_city or "N/A"
                occupation_title = ''
                occupation = ''

                try:
                    prof_id_int = int(profession_id)
                    if prof_id_int == 1:
                        occupation_title = 'Employment Details'
                        occupation = f"{education_details.company_name or ''} / {education_details.designation or ''}"
                    elif prof_id_int == 2:
                        occupation_title = 'Business Details'
                        occupation = f"{education_details.business_name or ''} / {education_details.nature_of_business or ''}"
                except (ValueError, TypeError):
                    occupation_title = 'Other'
                    occupation = ''

                def get_model_instance_name(model, pk, field="name", default="N/A"):
                    try:
                        if pk and str(pk).isdigit():
                            return getattr(model.objects.get(pk=int(pk)), field)
                    except (model.DoesNotExist, ValueError, TypeError):
                        pass
                    return default
                # Family fields
                father_occupation = family_detail.father_occupation or "N/A"
                mother_occupation = family_detail.mother_occupation or "N/A"
                father_name = family_detail.father_name or "N/A"
                mother_name = family_detail.mother_name or "N/A"
                family_status_id = family_detail.family_status
                family_status = safe_get_value(models.Familystatus, 'id', family_status_id, 'status')

                star_name = get_model_instance_name(models.Birthstar, horoscope.birthstar_name, "star")
                rasi_name = get_model_instance_name(models.Rasi, horoscope.birth_rasi_name, "name")
                # lagnam = get_model_instance_name(models.Rasi, horoscope.lagnam_didi, "name")

                try:
                    if horoscope.birth_rasi_name :
                        rasi = models.Rasi.objects.get(pk=horoscope.birth_rasi_name)
                        rasi_name = get_primary_sign(str(rasi.name))  # Or use rasi.tamil_series, telugu_series, etc. as per your requirement
                    else :
                        rasi_name="N/A"
                except models.Rasi.DoesNotExist:
                    rasi_name = "N/A"
                lagnam="N/A"
                try:
                    if horoscope.lagnam_didi and str(horoscope.lagnam_didi).isdigit() and int(horoscope.lagnam_didi) > 0:
                        lagnam = models.Rasi.objects.filter(pk=int(horoscope.lagnam_didi)).first()
                        lagnam= get_primary_sign(str(lagnam.name))
                except models.Rasi.DoesNotExist:
                    lagnam = "N/A"
                # Time & location
                time_of_birth = horoscope.time_of_birth or "N/A"
                place_of_birth = horoscope.place_of_birth or "N/A"
                didi = horoscope.didi or "N/A"
                nalikai = horoscope.nalikai or "N/A"
                def format_time_am_pm(time_str):
                    if not time_str:  # Handles None or empty strings
                        return "N/A"
                    try:
                        time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                        return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
                    except ValueError:
                        return str(time_str)
                    
                birth_time=format_time_am_pm(time_of_birth)
                # Age calculation
                age = calculate_age(login_details.Profile_dob) if login_details.Profile_dob else "N/A"
                # Planet mapping dictionary
                # planet_mapping = {
                #     "1": "Sun",
                #     "2": "Moo",
                #     "3": "Mar",
                #     "4": "Mer",
                #     "5": "Jup",
                #     "6": "Ven",
                #     "7": "Sat",
                #     "8": "Rahu",
                #     "9": "Kethu",
                #     "10": "Lagnam",
                # }

                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }

                # Define a default placeholder for empty values
                default_placeholder = '-'

                def parse_data(data):
                    # Clean up and split data
                    items = data.strip('{}').split(', ')
                    parsed_items = []
                    for item in items:
                        parts = item.split(':')
                        if len(parts) > 1:
                            values = parts[-1].strip()
                            # Handle multiple values separated by comma
                            if ',' in values:
                                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                            else:
                                values = planet_mapping.get(values, default_placeholder)
                        else:
                            values = default_placeholder
                        parsed_items.append(values)
                    return parsed_items

                # Clean up and parse the rasi_kattam and amsa_kattam data
                if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                    rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                    amsa_kattam_data = parse_data(horoscope.amsa_kattam)

                else:
                    rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                    amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')

                # Ensure that we have exactly 12 values for the grid
                rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
                amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))
                
                def is_grid_data_empty(grid_data):
                    return all(cell == default_placeholder for cell in grid_data)

                hide_charts = is_grid_data_empty(rasi_kattam_data) and is_grid_data_empty(amsa_kattam_data)

                horoscope_data = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
    
                if horoscope_data.horoscope_file_admin:
                    horoscope_image_url = horoscope_data.horoscope_file_admin.url
            
                    if horoscope_image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        horoscope_content = f'<img src="{horoscope_image_url}" alt="Horoscope Image" style="max-width: 200%; height: auto;">'
                    else:
                        horoscope_content = f'<a href="{horoscope_image_url}" download>Download Horoscope File</a>'
                else:
                    horoscope_content = 'empty'
                    
                show_horo_file = "yes"
                if horoscope_content == 'empty':
                    show_horo_file="No"
                # Get matching stars data
                birth_star_id = horoscope.birthstar_name
                birth_rasi_id = horoscope.birth_rasi_name
                gender = login_details.Gender
                porutham_data = models.MatchingStarPartner.get_matching_stars_pdf(birth_rasi_id, birth_star_id, gender)

                horo_hint = horoscope_data.horoscope_hints or "N/A"
                #print(porutham_data)
            
                # Prepare the Porutham sections for the PDF
                def format_star_names(poruthams):
                    #return ', '.join([item['matching_starname'] for item in poruthams])
                    return ', '.join([f"{item['matching_starname']} - {item['matching_rasiname'].split('/')[0]}" for item in poruthams])

                profile_url = f"https://polite-pond-0783ff91e.1.azurestaticapps.net/ProfileDetails?id={user_profile_id}&rasi={horoscope.birth_rasi_name}"

                dasa_day = dasa_month = dasa_year = 0
                # Try to split if format is correct
                # dasa_date_str = horoscope.dasa_balance.strip()
                # if dasa_date_str.startswith("day:") and "," in dasa_date_str:
                #     # Split and extract numbers
                #     try:
                #         day_str, month_str, year_str = dasa_date_str.split(',')
                #         dasa_day = int(day_str.split(':')[1].strip())
                #         dasa_month = int(month_str.split(':')[1].strip())
                #         dasa_year = int(year_str.split(':')[1].strip())
                #     except (ValueError, IndexError):
                #         dasa_day = dasa_month = dasa_year = 0

                dasa_balance_str=dasa_format_date(horoscope.dasa_balance)
                match = re.match(r"(\d+)\s+Years,\s+(\d+)\s+Months,\s+(\d+)\s+Days", dasa_balance_str or "")
                if match:
                    dasa_year, dasa_month, dasa_day = match.groups()

                #print(dasa_balance_str,'dasa_balance_str')


                dasa_name = get_dasa_name(horoscope_data.dasa_name)
                image_status = models.Image_Upload.get_image_status(profile_id=user_profile_id)
                
                charts_html = ""
                horo_file=""
                if show_horo_file == "yes":
                    horo_file = f"""
                    

                        <div class="upload-horo-bg" >
                            <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" >
                        </div>

               
                             <table class="upload-horo-image">
                                <tr>
                                <td>
                                    {horoscope_content}
                                </td>
                                </tr>
                                </table>
                    """

                if not hide_charts:
                    charts_html = f"""
                    <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td class="spacer">
                                <table class="table-div dasa-table">
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Name</strong></p>
                                            <p>{dasa_name}</p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Balance</strong></p>
                                            <p>{dasa_year} Years</p>
                                            <p>{dasa_month} Months</p>
                                            <p>{dasa_day} Days</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Amsam
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    
                <div>
                <table class="add-info"> 
                    <tr>
                        <td>
                            <p><b>Horoscope Hints: </b>{horo_hint}</p>
                        </td>
                    </tr>
                    <tr>
                    <td>
                    <table>
                    """

                html_content = rf"""
                <html>
                    <head>
                        <style>
                        @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: auto;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                            .score-box {{
                                float: right;
                                text-align: center;
                                background-color: #fffbcc;
                                border: 1px solid #d4d4d4;
                                width:100%;
                               margin-bottom:1.5rem !important;
                            }}

                             .score-box p {{
                                font-size: 2rem;
                                font-weight: bold;
                                padding: 10px 30px 10px !important;
                                color: #333;
                                margin: 0px auto !important;
                                padding-top:1.3rem !important;
                            }}

                            p {{
                                font-size: 10px;
                                margin: 5px 0;
                                padding: 0;
                                color: #333;
                            }}

                            .details-div {{
                                margin-bottom: 20px;
                            }}

                            .details-section p {{
                                margin: 2px 0;
                            }}

                            .details-section td {{
                                  border: none;
                            }}
                             .personal-detail-header{{
                                font-size: 2rem;
                                font-weight: bold;
                                margin-bottom: 1rem;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin:0;
                                padding:0;
                                margin-bottom:10px;

                            }}
                            .outer tr td{{
                            padding:0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff9c7;
                            }}
                            .inner-tabledata{{
                                 width:25%;
                                height:80px;
                                
                            }}
                            .inner td {{
                                width:25%;
                                height:80px;
                                border:2px solid #d6d6d6;
                                padding: 10px;
                                color: #008000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line; /* Ensures new lines are respected */
                            }}

                            .inner-table tr td p{{
                                white-space: pre-line;
                               word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow:hidden;
                                
                            }}

                            .inner .highlight {{
                                    background-color: #ffffff;
                                    text-align: center;
                                    width: 100%;
                                    height: 100%;
                                   font-size:24px;
                                    font-weight: 700;
                                    color: #008000;

                            }}

                            .inner .highlight p{{
                                font-size: 16px;
                                font-weight: 400;
                                color: #008000;
                            }}

                            .spacer {{
                                width: 14%;
                                display: inline-block;
                                background-color: transparent;
                            }}

                            .table-div{{
                                border-collapse: collapse;
                                padding:5px 20px;
                                margin-bottom:1rem;
                            }}
                            .table-div tr {{
                                padding: 10px 10px;
                            }}
                            .table-div tr .border-right{{
                                border-right:1px solid #008000;
                            }}
                            .table-div td{{
                                background-color: #fff9c7;
                                width:50%;
                                padding: 10px 10px;
                                text-align:left;
                            }}
                            .table-div p {{
                                   font-size:14px;
                                font-weight:400;
                                color: #008000;
                            }}
                            .inner-table tr td{{
                                padding:0px;
                                margin-bottom:0px;
                            }}
                            .dasa-table td{{
                                width:100%;
                                background-color:#fff;
                                 padding:0px;
                            }}
                            .dasa-table td p{{
                                font-size:14px;
                                font-weight:400;
                                text-align:center;
                            }}
                            .note-text {{
                                color: red;
                                font-size:12px;
                                font-weight: 500;
                                margin: 50px auto;
                            }}

                            .note-text1 {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 30px auto;
                                text-align: right;
                            }}
 
                            .add-info tr {{
                           padding:5px 20px ;
                            }}
                        
                            .add-info td {{
                                background-color: #fff9c7;
                                padding: 5px 5px;
                            }}
                          .add-info td p{{
                            font-size: 14px;
                            font-weight: 400;
                            color: #008000;
                            padding:0 10px;
                           }}
                           .click-here{{
                            color:#318f9a;
                           text-decoration: none;

                           }}

                            .porutham-page{{
                                padding: 0px 20px;
                            }}
                            .porutham-header {{
                                margin: 20px 0px;
                            }}

                            .porutham-header img{{
                                width: 130px;
                                height: auto;
                            }}
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}
                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            porutham-table{{
                                border:1px solid #bcbcbc;
                                border-collapse: collapse;
                                margin-bottom: 24px;
                            }}
                            .porutham-table td {{
                                border:1px solid #bcbcbc;
                            }}
                            .porutham-table td p{{
                                color: #000;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 10px 0;
                            }}
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}


                            .upload-horo-bg img{{
                               width:100%;
                               height:auto;
                           }}
                            .upload-horo-image{{
                                margin: 10px 0px;
                                text-align: center;
                                height: 800px;
                           
                            }}
                            .upload-horo-image tr{{
                                height: 800px;
                            }}
                            .upload-horo-image tr td{{
                                height: 800px;
                            }}
                            .upload-horo-image img{{
                                width:400px;
                                height:800px;
                                object-fit: cover;
                             
                            }}
                            

                        </style>
                    </head>

                    <body>

                        <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>
                        
                    <div class="details-section">
                    
                <table class="table-div">
                            <tr>
                                <td class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Name</strong></p></td>
                                        <td><p><strong>{name}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>DOB / POB</p></td>
                                        <td><p>{dob} / {place_of_birth}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Complexion</p></td>
                                        <td><p>{complexion}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Education</p></td>
                                        <td><p>{final_education}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Degree</p></td>
                                        <td><p>{degree}</p></td>
                                    </tr>
                                    </table>
                                    
                                </td>
                                
                                <td>
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Vysyamala Id :</strong></p></td>
                                        <td><p><strong>{user_profile_id}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Height / Photos </p></td>
                                        <td><p>{height} / {image_status}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Annual Income </p></td>
                                        <td><p>{annual_income}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Profession / Place of stay </p></td>
                                        <td><p>{profession} / {work_place}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>{occupation_title}</p></td>
                                        <td><p>{occupation}</p></td>
                                    </tr>
                                </table>
                                </td>
                            </tr>
                        </table>

                        


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td><p><strong>Father Name</strong></p></td>
                                            <td><p><strong>{father_name}</strong></p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Father Occupation</p></td>
                                            <td><p>{father_occupation}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Family Status</p></td>
                                            <td><p>{family_status}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Brothers/Married</p></td>
                                            <td><p>{no_of_brother}/{no_of_bro_married}</p></td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Mother Name </strong> </p>
                                                <p>Mother Occupation </p>
                                                <p>Sisters/Married </p>
                                            </td>
                                            <td>
                                                <p><strong>{mother_name}</strong></p>
                                                <p>{mother_occupation}</p>
                                                <p>{no_of_sister}/{no_of_sis_married}</p>
                                            </td>
                                        </tr>
                                    </table>
                               

                                </td>
                            </tr>
                        </table>
                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Star/Rasi </strong> </p>
                                                <p>Lagnam/Didi </p>
                                                <p>Nalikai </p>
                                            </td>
                                            <td>
                                                <p style="font-size:12px"><strong>{star_name}, {rasi_name}</strong></p>
                                                <p>{lagnam}/{didi}</p>
                                                <p>{nalikai}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Surya Gothram : </strong></p>
                                                <p>Madhulam </p>
                                                <p>Birth Time </p>
                                            </td>
                                            <td>
                                                <p><strong>{suya_gothram}</strong></p>
                                                <p>{madulamn}</p>
                                                <p>{birth_time}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>
                            </tr>
                        </table>
                    
                    </div>
                    {charts_html}


                        <tr>
                            <td>
                                {address_content}
                            </td>
                            <td>
                                {mobile_email_content}
                            </td>
                        </tr>
                    </table>
                    </td>
                    </tr>
                    <tr>
                        <td>
                            <p>Note: Please verify this profile yourself. No hidden charges or commissions if marriage is fixed through Vysyamala. For more details of this profile: <a href="{profile_url}" target="_blank" class="click-here">click here</a></p>
                        </td>
                    </tr>
                </table>
                </div>

                <table class="porutham-page">
                <tr>
                <td>
                <br>
                <table class="porutham-header">
                    <tr>
                        <td>
                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/newvysyamalalogo2.png">
                        </td>
                        <td>
                            <p>www.vysyamala.com</p>
                        </td>
                    </tr>
                </table>

                <h2 class="porutham-table-title">Matching Stars Report</h2>
                <table class="porutham-table">
                     <tr>
                        <td><p>Name</p></td>
                        <td><p>{name}</p></td>
                        <td><p>Vysyamala ID</p></td>
                        <td><p>{user_profile_id}</p></td>
                    </tr>
                    <tr>
                        <td><p>Birth Star</p></td>
                        <td><p>{star_name}</p></td>
                        <td><p>Age</p></td>
                        <td><p>{age}</p></td>
                    </tr>
                </table>

                <h2 class="porutham-table-title">Matching Stars (9 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["9 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (8 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["8 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (7 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["7 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (6 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["6 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (5 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["5 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>

                <p class="porutham-note">Note: This is system generated report, please confirm the same with your astrologer.</p>
                </td>
                </tr>
                </table>

                {horo_file}
                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/uploadHoroFooter.png" >
                </div>

                    </body>
                </html>
                """
                
                # Create a Django response object and specify content_type as pdf
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'


                # Create the PDF using xhtml2pdf
                pisa_status = pisa.CreatePDF(html_content, dest=response)

                # If there's an error, log it and return an HTML response with an error message
                if pisa_status.err:
                    logger.error(f"PDF generation error: {pisa_status.err}")
                    return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

                return response



# Function to fetch porutham details
# def fetch_porutham_details(profile_from, profile_to):
#     try:
#         # Fetch horoscope details for both profiles
#         horoscope_from = models.Horoscope.objects.get(profile_id=profile_from)
#         horoscope_to = models.Horoscope.objects.get(profile_id=profile_to)

#         # Fetch star and rasi ids
#         source_star_id = horoscope_from.birthstar_name
#         source_rasi_id = horoscope_from.birth_rasi_name
#         dest_star_id = horoscope_to.birthstar_name
#         dest_rasi_id = horoscope_to.birth_rasi_name

#         # Fetch the gender from the Registration1 model
#         profile_to_details = models.Registration1.objects.get(ProfileId=profile_to)
#         gender_to = profile_to_details.Gender.lower()

#         # Check porutham match from MatchingStarPartner
#         matching_star_partner = models.MatchingStarPartner.objects.filter(
#             source_star_id=source_star_id,
#             source_rasi_id=source_rasi_id,
#             dest_star_id=dest_star_id,
#             dest_rasi_id=dest_rasi_id,
#             gender=gender_to
#         ).first()

#         if not matching_star_partner:
#             porutham_names = models.Matchingporutham.objects.all()
#             porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO'} for porutham in porutham_names]
#             return {'porutham_results': porutham_results, 'matching_score': '0/10'}

#         # Parse the matching porutham IDs
#         try:
#             matching_porutham_ids = set(
#                 int(porutham_id) for porutham_id in matching_star_partner.matching_porutham.split(',') if porutham_id.strip().isdigit()
#             )
#         except ValueError:
#             matching_porutham_ids = set()

#         porutham_names = models.Matchingporutham.objects.all()
#         porutham_results = [
#             {'porutham_name': porutham.protham_name, 'status': 'YES ✔' if porutham.id in matching_porutham_ids else 'NO ✖'}
#             for porutham in porutham_names
#         ]

#         # Calculate matching score as a fraction out of 10
#         max_score = 10
#         matching_score = matching_star_partner.match_count
#         if matching_score == 0:
#             porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO'} for porutham in porutham_names]
#             matching_score_fraction = '0/10'
#         else:
#             matching_score_fraction = f'{min(matching_score, max_score)}/10'

#         return {'porutham_results': porutham_results, 'matching_score': matching_score_fraction}

#     except models.Horoscope.DoesNotExist:
#         porutham_names = models.Matchingporutham.objects.all()
#         porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO'} for porutham in porutham_names]
#         return {'porutham_results': porutham_results, 'matching_score': '0/10'}

def fetch_porutham_details(profile_from, profile_to):
    try:
        # Fetch horoscope details for both profiles
        horoscope_from = models.Horoscope.objects.get(profile_id=profile_from)
        horoscope_to = models.Horoscope.objects.get(profile_id=profile_to)

        # Fetch star and rasi ids, ensuring they are not None
        source_star_id = horoscope_from.birthstar_name or ''
        source_rasi_id = horoscope_from.birth_rasi_name or ''
        dest_star_id = horoscope_to.birthstar_name or ''
        dest_rasi_id = horoscope_to.birth_rasi_name or ''

        # Fetch the gender from the Registration1 model
        profile_from_details = models.Registration1.objects.get(ProfileId=profile_from)
        gender_to = profile_from_details.Gender.lower() if profile_from_details.Gender else 'unknown'

        # Check porutham match from MatchingStarPartner
        matching_star_partner = models.MatchingStarPartner.objects.filter(
            source_star_id=source_star_id,
            source_rasi_id=source_rasi_id,
            dest_star_id=dest_star_id,
            dest_rasi_id=dest_rasi_id,
            gender=gender_to
        ).first()

        porutham_names = models.Matchingporutham.objects.exclude(id__in=[11, 12])

        if not matching_star_partner:
            porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO ✖'} for porutham in porutham_names]
            return {'porutham_results': porutham_results, 'matching_score': '0/10'}

        # Parse the matching porutham IDs, ensuring the string is not None
        matching_porutham_str = matching_star_partner.matching_porutham or ''
        try:
            matching_porutham_ids = set(
                int(porutham_id.strip()) for porutham_id in matching_porutham_str.split(',') if porutham_id.strip().isdigit()
            )
        except ValueError:
            matching_porutham_ids = set()

        porutham_results = [
            {'porutham_name': porutham.protham_name, 'status': 'YES ✔' if porutham.id in matching_porutham_ids else 'NO ✖'}
            for porutham in porutham_names
        ]

        # Calculate matching score as a fraction out of 10
        max_score = 10
        matching_score = matching_star_partner.match_count or 0
        if matching_score == 0:
            porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO ✖'} for porutham in porutham_names]
            matching_score_fraction = '0/10'
        
        elif matching_score == 15:
             matching_score_fraction=0/10
        
        else:
            matching_score_fraction = f'{min(matching_score, max_score)}/10'

        return {'porutham_results': porutham_results, 'matching_score': matching_score_fraction}

    except models.Horoscope.DoesNotExist:
        porutham_names = models.Matchingporutham.objects.all()
        porutham_results = [{'porutham_name': porutham.protham_name, 'status': 'NO ✖'} for porutham in porutham_names]
        return {'porutham_results': porutham_results, 'matching_score': '0/10'}
    


def parse_data(data):
    planet_mapping = {
        "1": "Sun/Suriyan",
        "2": "Moon/Chandran",
        "3": "Mars/Chevai",
        "4": "Mercury/Budhan",
        "5": "Jupiter/Guru",
        "6": "Venus/Sukran",
        "7": "Saturn/Sani",
        "8": "Raghu/Rahu",
        "9": "Kethu/Ketu",
        "10": "Lagnam",
    }
    default_placeholder = '-'
    items = data.strip('{}').split(', ')
    parsed_items = []
    for item in items:
        parts = item.split(':')
        if len(parts) > 1:
            values = parts[-1].strip()
            if ',' in values:
                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
            else:
                values = planet_mapping.get(values, default_placeholder)
        else:
            values = default_placeholder
        parsed_items.append(values)
    return parsed_items



def My_horoscope(request, user_profile_id, filename="Horoscope_withbirthchart"):

                #print('1234567')
  
                # Retrieve the Horoscope object based on the provided profile_id
                horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
                education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)


                if all(not str(val).strip() for val in [
                    login_details.Profile_address,
                    get_district_name(login_details.Profile_district),
                    get_city_name(login_details.Profile_city),
                    login_details.Profile_pincode
                ]):
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>N/A</p>"""
                else:
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>{login_details.Profile_address}</p>
                        <p>{get_district_name(login_details.Profile_district)}, {get_city_name(login_details.Profile_city)}</p>
                        <p>{login_details.Profile_pincode}.</p>
                    """
                
                mobile_email_content = f"""
                        <p>Mobile: {login_details.Mobile_no or 'N/A'}</p>
                        <p>Alternate Mobile: {login_details.Profile_alternate_mobile or 'N/A'}</p>
                        <p>WhatsApp: {login_details.Profile_whatsapp or 'N/A'}</p>
                        <p>Email: {login_details.EmailId or 'N/A'}</p>
                """
                try:
                    degree= get_degree_name(education_details.degree,education_details.other_degree)
                except Exception:
                    degree=None
                    
                # family details
                family_details = models.Familydetails.objects.filter(profile_id=user_profile_id)
                if family_details.exists():
                    family_detail = family_details.first()  

                    father_name = family_detail.father_name  
                    father_occupation = family_detail.father_occupation
                    family_status = family_detail.family_status
                    mother_name = family_detail.mother_name
                    mother_occupation = family_detail.mother_occupation
                    no_of_sis_married = family_detail.no_of_sis_married
                    no_of_bro_married = family_detail.no_of_bro_married

                    no_of_sister = family_detail.no_of_sister
                    no_of_brother = family_detail.no_of_brother

                    suya_gothram = family_detail.suya_gothram
                    madulamn = family_detail.madulamn if family_detail.madulamn != None else "N/A" 
                else:
                    # Handle case where no family details are found
                    father_name = father_occupation = family_status = ""
                    mother_name = mother_occupation = ""
                    no_of_sis_married = no_of_bro_married = 0
                    
                try:
                    num_sisters_married = int(no_of_sis_married)
                except ValueError:
                    num_sisters_married = 0     
            
                try:
                    num_brothers_married = int(no_of_bro_married)
                except ValueError:
                    num_brothers_married = 0   
                if int(num_sisters_married) == 0:
                    no_of_sis_married = "No"

                if  int(num_brothers_married) == 0:
                    no_of_bro_married="No"

                if no_of_sister=="0" or no_of_sister =='':
                    no_of_sis_married='No'
                    no_of_sister ='No'

                if no_of_brother=="0" or no_of_brother =='':
                    no_of_bro_married='No'
                    no_of_brother ='No'
               

                # Education and profession details
                highest_education = education_details.highest_education
                
                annual_income = "Unknown"
                actual_income = str(education_details.actual_income).strip()
                annual_income_id = education_details.anual_income

                if not actual_income or actual_income in ["", "~"]:
                    if annual_income_id and str(annual_income_id).isdigit():
                        annual_income = models.Annualincome.objects.filter(id=int(annual_income_id)).values_list('income', flat=True).first() or "Unknown"
                else:
                    annual_income = actual_income
                # personal details
                name = login_details.Profile_name  # Assuming a Profile_name field exists
                date =  format_date_of_birth(login_details.Profile_dob)
                dob = date
                complexion = login_details.Profile_complexion
                user_profile_id = login_details.ProfileId
                height = cm_to_feet_inches(login_details.Profile_height)

                # Safely handle complexion
                complexion_id = login_details.Profile_complexion
                complexion = "Unknown"
                if complexion_id:
                    complexion = models.Profilecomplexion.objects.filter(complexion_id=complexion_id).values_list('complexion_desc', flat=True).first() or "Unknown"

                # Safely handle education level
                highest_education_id = education_details.highest_education
                highest_education = "Unknown"
                if highest_education_id:
                    highest_education = models.Edupref.objects.filter(RowId=highest_education_id).values_list('EducationLevel', flat=True).first() or "Unknown"
                
                field_ofstudy_id = education_details.field_ofstudy
                fieldof_study=" "
                if field_ofstudy_id:
                    fieldof_study = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id).values_list('field_of_study', flat=True).first() or "Unknown"
                
                about_edu=education_details.about_edu
                
                final_education = (highest_education + ' ' + fieldof_study).strip() or about_edu

                # Safely handle profession
                profession_id = education_details.profession
                profession = "Unknown"
                if profession_id:
                    profession = models.Profespref.objects.filter(RowId=profession_id).values_list('profession', flat=True).first() or "Unknown"

                # Workplace logic
                work_place = education_details.work_city or ""
                occupation_title = ''
                occupation = ''

                try:
                    prof_id_int = int(profession_id)
                    if prof_id_int == 1:
                        occupation_title = 'Employment Details'
                        occupation = f"{education_details.company_name or ''} / {education_details.designation or ''}"
                    elif prof_id_int == 2:
                        occupation_title = 'Business Details'
                        occupation = f"{education_details.business_name or ''} / {education_details.nature_of_business or ''}"
                except (ValueError, TypeError):
                    occupation_title = 'Other'
                    occupation = ''

                dasa_day = dasa_month = dasa_year = 0
                # Try to split if format is correct
                dasa_balance_str=dasa_format_date(horoscope.dasa_balance)
                match = re.match(r"(\d+)\s+Years,\s+(\d+)\s+Months,\s+(\d+)\s+Days", dasa_balance_str or "")
                if match:
                    dasa_year, dasa_month, dasa_day = match.groups()
                
                
                #father_occupation_id = family_detail.father_occupation
                father_occupation = family_detail.father_occupation or "N/A"

                 #mother_occupation_id = family_detail.mother_occupation
                mother_occupation = family_detail.mother_occupation or "N/A"
                father_name = family_detail.father_name or "N/A"
                mother_name = family_detail.mother_name or "N/A"
                family_status = "Unknown"
                family_status_id = family_detail.family_status

                if family_status_id:
                    family_status = models.Familystatus.objects.filter(id=family_status_id).values_list('status', flat=True).first() or "Unknown"

                # Fetch star name from BirthStar model
                def get_model_instance(model, pk):
                    if not pk or not str(pk).isdigit():
                        return None
                    try:
                        return model.objects.get(pk=pk)
                    except model.DoesNotExist:
                        return None
                    except ValueError:
                        return None

                star_obj = get_model_instance(models.Birthstar, horoscope.birthstar_name)
                star_name = star_obj.star if star_obj else "Unknown"

                rasi_obj = get_model_instance(models.Rasi, horoscope.birth_rasi_name)
                rasi_name = get_primary_sign(str(rasi_obj.name)) if rasi_obj else "Unknown"

                lagnam_obj = get_model_instance(models.Rasi, horoscope.lagnam_didi)
                lagnam = get_primary_sign(str(lagnam_obj.name)) if lagnam_obj else "Unknown"

                time_of_birth = horoscope.time_of_birth
                place_of_birth = horoscope.place_of_birth


                didi = horoscope.didi or "N/A"
                nalikai =  horoscope.nalikai or "N/A"
                
                def format_time_am_pm(time_str):
                    if not time_str:  # Handles None or empty strings
                        return "N/A"
                    try:
                        time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                        return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
                    except ValueError:
                        return str(time_str)
                birth_time=format_time_am_pm(time_of_birth)
                # Age calculation
                age = calculate_age(login_details.Profile_dob) or "N/A"

                # Planet mapping dictionary
                # planet_mapping = {
                #     "1": "Sun",
                #     "2": "Moo",
                #     "3": "Mar",
                #     "4": "Mer",
                #     "5": "Jup",
                #     "6": "Ven",
                #     "7": "Sat",
                #     "8": "Rahu",
                #     "9": "Kethu",
                #     "10": "Lagnam",
                # }

                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }

                # Define a default placeholder for empty values
                default_placeholder = '-'

                def parse_data(data):
                    # Clean up and split data
                    items = data.strip('{}').split(', ')
                    parsed_items = []
                    for item in items:
                        parts = item.split(':')
                        if len(parts) > 1:
                            values = parts[-1].strip()
                            # Handle multiple values separated by comma
                            if ',' in values:
                                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                            else:
                                values = planet_mapping.get(values, default_placeholder)
                        else:
                            values = default_placeholder
                        parsed_items.append(values)
                    return parsed_items

                # Clean up and parse the rasi_kattam and amsa_kattam data
                if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                    rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                    amsa_kattam_data = parse_data(horoscope.amsa_kattam)

                else:
                    rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                    amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')

                # Ensure that we have exactly 12 values for the grid
                rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
                amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))

                horoscope_data = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
    
                
                if horoscope_data.horoscope_file_admin:
                    horoscope_image_url = horoscope_data.horoscope_file_admin.url

                    print(horoscope_image_url)

                    if horoscope_image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        horoscope_content = f'<img src="{horoscope_image_url}" alt="Horoscope Image" style="max-width: 200%; height: auto;">'
                    else:
                        horoscope_content = f'<a href="{horoscope_image_url}" download>Download Horoscope File</a>'
                else:
                    horoscope_content = '<p>No horoscope uploaded</p>'
                dasa_name = get_dasa_name(horoscope_data.dasa_name)
                
                horo_hint = horoscope_data.horoscope_hints or "N/A"
                # image status
                image_status = models.Image_Upload.get_image_status(profile_id=user_profile_id)
                # Get matching stars data
                birth_star_id = horoscope.birthstar_name
                birth_rasi_id = horoscope.birth_rasi_name
                gender = login_details.Gender
                porutham_data = models.MatchingStarPartner.get_matching_stars_pdf(birth_rasi_id, birth_star_id, gender)
                # print("fathername:",father_name)
                # Prepare the Porutham sections for the PDF
                def format_star_names(poruthams):
                    return ', '.join([f"{item['matching_starname']} - {item['matching_rasiname'].split('/')[0]}" for item in poruthams])
                
                profile_url = f"https://polite-pond-0783ff91e.1.azurestaticapps.net/ProfileDetails?id={user_profile_id}&rasi={horoscope.birth_rasi_name}"
                
                def is_grid_data_empty(grid_data):
                    return all(cell == default_placeholder for cell in grid_data)
                
                hide_charts = is_grid_data_empty(rasi_kattam_data) and is_grid_data_empty(amsa_kattam_data)
                

                    # Dynamic HTML content including Rasi and Amsam charts
                    
                    
                charts_html = ""
                # print("hide",hide_charts)
                if not hide_charts:
                    charts_html = f"""
                    <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td class="spacer">
                                <table class="table-div dasa-table">
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Name</strong></p>
                                            <p>{dasa_name}</p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Balance</strong></p>
                                            <p>{dasa_year} Years</p>
                                            <p>{dasa_month} Months</p>
                                            <p>{dasa_day} Days</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Amsam
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <div>
                <table class="add-info"> 
                    <tr>
                        <td>
                            <p><b>Horoscope Hints: </b>{horo_hint}</p>
                       <hr class="divider">

                        </td>
                    </tr>
                    <tr>
                    <td>
                    <table>
                    """

                html_content = rf"""
                <html>
                    <head>
                        <style>
                        @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: 300px;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                            .score-box {{
                                float: right;
                                text-align: center;
                                background-color: #fffbcc;
                                border: 1px solid #d4d4d4;
                                width:100%;
                               margin-bottom:1.5rem !important;
                            }}

                             .score-box p {{
                                font-size: 2rem;
                                font-weight: bold;
                                padding: 10px 30px 10px !important;
                                color: #333;
                                margin: 0px auto !important;
                                padding-top:1.3rem !important;
                            }}

                            p {{
                                font-size: 10px;
                                margin: 5px 0;
                                padding: 0;
                                color: #333;
                            }}

                            .details-div {{
                                margin-bottom: 20px;
                            }}

                            .details-section p {{
                                margin: 2px 0;
                            }}

                            .details-section td {{
                                  border: none;
                            }}
                             .personal-detail-header{{
                                font-size: 2rem;
                                font-weight: bold;
                                margin-bottom: 1rem;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin:0;
                                padding:0;
                            margin-bottom:10px;


                            }}
                            .outer tr td{{
                            padding:0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff;
                            }}
                            .inner-tabledata{{
                                 width:25%;
                                height:80px;
                                
                            }}
                            .inner td {{
                                width:25%;
                                height:70px;
                                border:2px solid #d6d6d6;
                                padding: 10px;
                                color: #000000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line; /* Ensures new lines are respected */
                            }}

                            .inner .highlight {{
                                    background-color: #ffffff;
                                    text-align: center;
                                    width: 100%;
                                    height: 100%;
                                    font-size:24px;
                                    font-weight: 700;
                                    color: #000000;

                            }}
                            .inner-table tr td p{{
                                white-space: pre-line;
                               word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow:hidden;
                                
                            }}
                            .inner .highlight p{{
                                font-size: 16px;
                                font-weight: 400;
                                color: #000;
                            }}

                           
                            .table-div{{
                                padding: 5px 10px;
                                border-collapse: collapse;
                                padding:5px 20px;
                                margin-bottom:15px;
                            }}
                            .table-div tr {{
                                padding: 0px 10px;
                            }}
                            .table-div tr .border-right{{
                                border-right:1px solid #000000;
                            }}
                            .table-div td{{
                                background-color: #ffffff;
                                width:50%;
                                padding: 10x  20px;
                                text-align:left;
                            }}
                            .table-div p {{
                                   font-size:14px;
                                font-weight:400;
                                color: #000;
                            }}
                            .divider{{
                            margin:10px 0 !important;
                            }}
                            .inner-table tr td{{
                                padding:0px;
                                margin-bottom:0px;
                            }}
                             .spacer {{
                                width: 14%;
                                display: inline-block;
                                background-color: transparent;
                                padding:0px 0px !important;
                                margin:0px 0px !important;
                            }}
                            .dasa-table {{
                                width: 100%;
                                padding:0px;
                            }}
                            .dasa-table td{{
                                width:100%;
                                background-color:#fff;
                                padding:0px;
                            }}
                            .dasa-table td p{{
                                width: 100%;
                                font-size:12px;
                                font-weight:400;
                                text-align:center;
                                color:#000000;
                            }}
                            .note-text {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 50px auto;
                            }}

                            .note-text1 {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 30px auto;
                                text-align: right;
                            }}

                             .add-info tr {{
                            padding:5px 20px ;
                            }}
                        
                            .add-info td {{
                                background-color: #ffffff;
                                padding: 5px 5px;
                            }}
                          .add-info td p{{
                            font-size: 14px;
                            font-weight: 400;
                            color: #000000;
                            padding:0 10px;
                           }}
                          
                           .click-here{{
                            color:#000;
                            font-weight:700 ;
                           text-decoration: none;

                           }}

                            .porutham-page{{
                                padding: 0px 20px;
                            }}
                            .porutham-header {{
                                margin: 20px 0px;
                            }}

                            .porutham-header img{{
                                width: 130px;
                                height: auto;
                            }}
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}
                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            porutham-table{{
                                border:1px solid #bcbcbc;
                                border-collapse: collapse;
                                margin-bottom: 24px;
                            }}
                            .porutham-table td {{
                                border:1px solid #bcbcbc;
                            }}
                            .porutham-table td p{{
                                color: #000;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 10px 0;
                            }}
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}



                           .upload-horo-bg img{{
                               width:100%;
                               height:auto;
                           }}
                            .upload-horo-image{{
                                margin: 10px 0px;
                                text-align: center;
                                height: 800px;
                           
                            }}
                            .upload-horo-image tr{{
                                height: 800px;
                            }}
                            .upload-horo-image tr td{{
                                height: 800px;
                            }}
                            .upload-horo-image img{{
                                width:400px;
                                height:800px;
                                object-fit: cover;
                             
                            }}
                            

                        </style>
                    </head>

                    <body>

                        <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader-bg-white.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>
                        
                    <div class="details-section">
                    
                <table class="table-div">
                            <tr>
                                <td class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Name</strong></p></td>
                                        <td><p><strong>{name}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>DOB / POB</p></td>
                                        <td><p>{dob} / {place_of_birth}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Complexion</p></td>
                                        <td><p>{complexion}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Education</p></td>
                                        <td><p>{final_education}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Degree</p></td>
                                        <td><p>{degree}</p></td>
                                    </tr>
                                    </table>
                                    
                                </td>
                                
                                <td>
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Vysyamala Id :</strong></p></td>
                                        <td><p><strong>{user_profile_id}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Height / Photos </p></td>
                                        <td><p>{height} / {image_status}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Annual Income </p></td>
                                        <td><p>{annual_income}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Profession / Place of stay </p></td>
                                        <td><p>{profession} / {work_place}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>{occupation_title}</p></td>
                                        <td><p>{occupation}</p></td>
                                    </tr>
                                </table>
                                </td>
                            </tr>
                        </table>

                       <hr class="divider">


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td><p><strong>Father Name</strong></p></td>
                                            <td><p><strong>{father_name}</strong></p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Father Occupation</p></td>
                                            <td><p>{father_occupation}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Family Status</p></td>
                                            <td><p>{family_status}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Brothers/Married</p></td>
                                            <td><p>{no_of_brother}/{no_of_bro_married}</p></td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Mother Name </strong> </p>
                                                <p>Mother Occupation </p>
                                                <p>Sisters/Married </p>
                                            </td>
                                            <td>
                                                <p><strong>{mother_name}</strong></p>
                                                <p>{mother_occupation}</p>
                                                <p>{no_of_sister}/{no_of_sis_married}</p>
                                            </td>
                                        </tr>
                                    </table>
                               

                                </td>
                            </tr>
                        </table>

                       <hr class="divider">


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Star/Rasi </strong> </p>
                                                <p>Lagnam/Didi </p>
                                                <p>Nalikai </p>
                                            </td>
                                            <td>
                                                <p style="font-size:12px"><strong>{star_name}/{rasi_name}</strong></p>
                                                <p>{lagnam}/{didi}</p>
                                                <p>{nalikai}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Surya Gothram : </strong></p>
                                                <p>Madhulam </p>
                                                <p>Birth Time </p>
                                            </td>
                                            <td>
                                                <p><strong>{suya_gothram}</strong></p>
                                                <p>{madulamn}</p>
                                                <p>{birth_time}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>
                            </tr>
                        </table>
                    
                    </div>
                    
                    {charts_html}
                
                        <tr>
                            <td>
                               {address_content}
                            </td>
                            <td>
                               {mobile_email_content}
                            </td>
                        </tr>
                    </table>
                    </td>
                    </tr>
                    <tr>
                        <td>
                            <p>Note: Please verify this profile yourself. No hidden charges or commissions if marriage is fixed through Vysyamala. For more details of this profile: <a href="{profile_url}" target="_blank" class="click-here">click here</a></p>
                        </td>
                    </tr>
                </table>
                </div>

                <table class="porutham-page">
                <tr>
                <td>
                <br>
                <table class="porutham-header">
                    <tr>
                        <td>
                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/newvysyamalalogo2.png">
                        </td>
                        <td>
                            <p>www.vysyamala.com</p>
                        </td>
                    </tr>
                </table>

                <h2 class="porutham-table-title">Matching Stars Report</h2>
                <table class="porutham-table">
                                        <tr>
                            <td><p>Name</p></td>
                            <td><p>{name}</p></td>
                            <td><p>Vysyamala ID</p></td>
                            <td><p>{user_profile_id}</p></td>
                        </tr>
                        <tr>
                            <td><p>Birth Star</p></td>
                            <td><p>{star_name}</p></td>
                            <td><p>Age</p></td>
                            <td><p>{age}</p></td>
                        </tr>
                </table>

                <h2 class="porutham-table-title">Matching Stars (9 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["9 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (8 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["8 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (7 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["7 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (6 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["6 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>
                <h2 class="porutham-table-title">Matching Stars (5 Poruthams)</h2>
                <table class="porutham-table porutham-stars">
                    <tr>
                        <td>
                            <p>{format_star_names(porutham_data["5 Poruthams"])}</p>
                        </td>
                    </tr>
                </table>

                <p class="porutham-note">Note: This is system generated report, please confirm the same with your astrologer.</p>
                </td>
                </tr>
                </table>


                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" >
                </div>

               <table class="upload-horo-image">
                <tr>
                <td>
                         {horoscope_content}
 
                </td>
                </tr>
                </table>
                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/uploadHoroFooter.png" >
                </div>


                   

                    </body>
                </html>
                """

                # Create a Django response object and specify content_type as pdf
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'

                # Create the PDF using xhtml2pdf
                pisa_status = pisa.CreatePDF(html_content, dest=response)

                # If there's an error, log it and return an HTML response with an error message
                if pisa_status.err:
                    logger.error(f"PDF generation error: {pisa_status.err}")
                    return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

                return response


def render_to_pdf(html_content):
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

def safe_str(value):
    return value.strip() if isinstance(value, str) else ''

@csrf_exempt
def generate_porutham_pdf(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            profile_from = data.get('profile_from')
            profile_to = data.get('profile_to')
        else:
            profile_from = request.GET.get('profile_from')
            profile_to = request.GET.get('profile_to')

        if not profile_from or not profile_to:
            return JsonResponse({'status': 'error', 'message': 'profile_from and profile_to are required'}, status=400)

        if can_see_compatability_report(profile_from, profile_to) is not True:
            return JsonResponse({'status': 'failure', 'message': 'Get full access - upgrade your package today!'}, status=400)

        # Fetch required data
        profile_from_details = models.Registration1.objects.get(ProfileId=profile_from)
        profile_to_details = models.Registration1.objects.get(ProfileId=profile_to)
        horoscope_from = models.Horoscope.objects.get(profile_id=profile_from)
        horoscope_to = models.Horoscope.objects.get(profile_id=profile_to)
        education_from_details = models.Edudetails.objects.get(profile_id=profile_from)
        education_to_details = models.Edudetails.objects.get(profile_id=profile_to)

        try:
            degree_from= get_degree_name(education_from_details.degree,education_from_details.other_degree)  
        except Exception as e:
            degree_from = None
            
        try:
            degree_to= get_degree_name(education_to_details.degree,education_to_details.other_degree)  
        except Exception as e:
            degree_to = None
        # Defensive check for null fields
        if not horoscope_from.birthstar_name or not horoscope_to.birthstar_name:
            return JsonResponse({'status': 'error', 'message': 'Missing birth star data'}, status=400)

        if not horoscope_from.birth_rasi_name or not horoscope_to.birth_rasi_name:
            return JsonResponse({'status': 'error', 'message': 'Missing rasi data'}, status=400)

        if not education_from_details.highest_education or not education_to_details.highest_education:
            return JsonResponse({'status': 'error', 'message': 'Missing education data'}, status=400)

        # Fetch from master tables
        birth_star_from = models.Birthstar.objects.get(id=horoscope_from.birthstar_name)
        birth_star_to = models.Birthstar.objects.get(id=horoscope_to.birthstar_name)
        rasi_from = models.Rasi.objects.get(id=horoscope_from.birth_rasi_name)
        rasi_to = models.Rasi.objects.get(id=horoscope_to.birth_rasi_name)
        highest_education_from = models.Edupref.objects.get(RowId=education_from_details.highest_education)
        highest_education_to = models.Edupref.objects.get(RowId=education_to_details.highest_education) 

        field_ofstudy_id_from = education_from_details.field_ofstudy
        fieldof_study_from=" "
        if field_ofstudy_id_from:
            fieldof_study_from = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_from).values_list('field_of_study', flat=True).first() or "Unknown"
        
        about_edu_from=education_from_details.about_edu
        
        final_education_from = (highest_education_from.EducationLevel + ' ' + fieldof_study_from).strip() or about_edu_from
                
        field_ofstudy_id_to = education_to_details.field_ofstudy
        fieldof_study_to=" "
        if field_ofstudy_id_to:
            fieldof_study_to = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_to).values_list('field_of_study', flat=True).first() or "Unknown"
        
        about_edu_to=education_to_details.about_edu
        
        final_education_to = (highest_education_to.EducationLevel + ' ' + fieldof_study_to).strip() or about_edu_to
        
        def format_time_am_pm(time_str):
            if not time_str:  # Handles None or empty strings
                return "N/A"
            try:
                time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
            except ValueError:
                return str(time_str)
            
        horo_from_time = format_time_am_pm(horoscope_from.time_of_birth)
        horo_to_time = format_time_am_pm(horoscope_to.time_of_birth)
        
        horo_from_date = format_date_of_birth(profile_from_details.Profile_dob)
        horo_to_date = format_date_of_birth(profile_to_details.Profile_dob)
        # Handle Gender safely
        gender_from = safe_str(profile_from_details.Gender).lower()
        gender_to = safe_str(profile_to_details.Gender).lower()
        if gender_from == gender_to:
            return JsonResponse({'status': 'error', 'message': 'Profiles have the same gender. Matching is not applicable.'}, status=400)

        # Parse Rasi Kattam data
        rasi_kattam_from = parse_data(horoscope_from.rasi_kattam or "")
        rasi_kattam_to = parse_data(horoscope_to.rasi_kattam or "")
        rasi_kattam_from.extend(['-'] * (12 - len(rasi_kattam_from)))
        rasi_kattam_to.extend(['-'] * (12 - len(rasi_kattam_to)))
        if horoscope_from.rasi_kattam or  horoscope_from.amsa_kattam:
            rasi_kattam_data_from = parse_data(horoscope_from.rasi_kattam)
        else:
            rasi_kattam_data_from=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
        rasi_kattam_data_from.extend([default_placeholder] * (12 - len(rasi_kattam_data_from)))

        if horoscope_to.rasi_kattam or  horoscope_to.amsa_kattam:
            rasi_kattam_data_to = parse_data(horoscope_to.rasi_kattam)
        else:
            rasi_kattam_data_to=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
        rasi_kattam_data_to.extend([default_placeholder] * (12 - len(rasi_kattam_data_to)))     
        # Get porutham data
        porutham_data = fetch_porutham_details(profile_from, profile_to)


            # Define the HTML content with custom styles
        porutham_rows = ""
        for idx, porutham in enumerate(porutham_data['porutham_results']):
            extra_td = ""
            if idx == 0:
                extra_td = (
                    f"<td rowspan='{len(porutham_data['porutham_results'])}'>"
                    f"<p class='matching-score' style='font-size:40px;'>{porutham_data['matching_score']}</p>"
                    f"<p style='font-weight:300;'>Please check with your astrologer for detailed compatibility.</p>"
                    f"<p>Jai Vasavi</p>"
                    f"</td>"
                )
            porutham_rows += (
                f"<tr>"
                f"<td>{porutham['porutham_name']}</td>"
                f"<td><span style='color: {'green' if porutham['status'].startswith('YES') else 'red'};'>{porutham['status']}</span></td>"
                f"{extra_td}"
                f"</tr>"
            )



            # Define the HTML content with custom styles
        html_content = f"""
            <html>
            <head>
                <style>
                   @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: auto;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                           
                           
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}

                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            .porutham-table{{
                                border:1px solid #538135;
                                border-collapse: collapse;
                                margin-bottom: 10px;
                            }}
                            .porutham-table th {{
                                padding: 5px 0;
                                  background-color: #538135;
                                  color:#f4c542;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0 0 0;
                            }}
                            .porutham-table td {{
                                border:1px solid #538135;
                                color: #538135;
                                font-size:15px;
                                font-weight:400;
                                text-align:center;
                                padding: 8px 5px;
                            }}
                            .porutham-table tr td p{{
                                color: #538135;
                                font-size:15px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0;
                            }}
                          
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}


                            .matching-score{{
                                font-size:30px ;
                                font-weight:700;
                            }}
                        

                            .compatibility-page-wrapper {{
                                 margin:0px auto;
                                text-align:center;
                                width:100%;
                            }}
                            .compatibility-page-wrapper tr {{
                                margin: auto;
                                text-align:center;
                                width:100%;
                            }}
                            
                            .compatibility-page-wrapper tr td{{
                                background-color: #ffd966;
                                width:100%;
                                text-align:center;
                                margin: auto;
                               
                            }}

                            .report-title {{
                                background-color: #ffd966;
                                color: #538135;
                                font-weight: bold;
                                text-align: center;
                                padding: 10px 0px 0px;
                                font-size: 16px;
                            }}
                             .report-table {{
                                width: 100%;
                                border-collapse: collapse;
                                background-color: #538135;
                                
                            }}
                             .report-table  tr {{
                                background-color: #538135;

                             }}
                             .report-table  tr  td{{
                                background-color: #538135;
                                color:#ffd966;
                                border:1px solid #ffd966;

                             }}
                             .report-table  tr  td p{{
                                background-color: #538135;
                                color:#ffd966;
                                font-size:14px;
                                width:100%;

                             }}
                             .profile-name{{
                                color:#ffd966;
                             }}
                            .header-cell {{
                                background-color: #538135;
                                color: #fff;
                                font-weight: bold;
                                text-align: center;
                                padding: 6px;
                            }}
                            .sub-header {{
                                background-color:#538135;
                                color: #000;
                                text-align: center;
                                padding: 4px;
                            }}
                            .profile-addtional-info{{
                                width: 100%;
                                background-color: #ffd966;
                                border:1px solid #538135;

                            }}
                              .profile-addtional-info  tr {{
                                background-color: #ffd966;
                                border:none;

                             }}
                            
                             .profile-addtional-info  tr  td p{{
                                background-color: #ffd966;
                                color:#538135;
                                font-size:14px;
                                width:100%;

                             }}
                            .data-row {{
                                padding: 2px 0px;
                            }}
                            .data-label {{
                                font-weight: bold;
                                width: 40%;
                                padding: 4px;
                            }}
                            .data-value {{
                                padding: 4px;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                                margin-bottom: 10px;
                            }}
                            .outer tr td {{
                                padding: 0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff9c7;
                            }}

                            .inner-tabledata {{
                                width: 25%;
                                height: 80px;

                            }}

                            .inner td {{
                                width: 25%;
                                height: 80px;
                                border: 2px solid #d6d6d6;
                                padding: 10px;
                                color: #008000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line;
                                /* Ensures new lines are respected */
                            }}

                            .inner-table tr td p {{
                                white-space: pre-line;
                                word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow: hidden;

                            }}

                            .inner .highlight {{
                                background-color: #ffd966;
                                text-align: center;
                                width: 100%;
                                height: 100%;
                                font-size: 24px;
                                font-weight: 700;
                                color: #008000;
                                vertical-align: middle;
                                padding: 10px;

                            }}

                            .inner .highlight p {{
                                font-size: 16px;
                                font-weight: 400;
                                color: #008000;
                            }}
        
                </style>
            </head>
        <body>
                               
                <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>

            <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
            <h2 class="report-title">Marriage Compatibility Report</h2>
        
            <table class="report-table" border="0">
                <tr>
                <td class="header-cell">
                    <p class="profile-name">{profile_from_details.Profile_name} - {profile_from_details.ProfileId}</p>
                </td>
                <td class="header-cell">
                    <p class="profile-name"> {profile_to_details.Profile_name} - {profile_to_details.ProfileId}</p>   
                 </td>
                </tr>
                <tr>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_from.name} - {birth_star_from.star}</p>
                </td>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_to.name} - {birth_star_to.star}</p>
                </td>
                </tr>
            </table>
            <br>
        
            <table class="profile-addtional-info" >
                <tr>
                <td class="data-row">
                     <p> Place of Birth : {horoscope_from.place_of_birth}</p>
                </td>
                <td class="data-row">
                    <p> Place of Birth : {horoscope_to.place_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Time of Birth : {horo_from_time}</p>
                </td>
                <td class="data-row">
                    <p>  Time of Birth : {horo_to_time}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Date Of Birth : {horo_from_date}</p>
                </td>
                <td class="data-row">
                    <p> Date Of Birth : {horo_to_date}</p>
                </td>
                </tr>
            </table>
            <br>
        
              <table class="profile-addtional-info">
                <tr>
                <td class="data-row">
                    <p> Height : {profile_from_details.Profile_height}</p>
                </td>
                <td class="data-row">
                        <p> Height : {profile_to_details.Profile_height}</p>
        
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> {final_education_from}</p>
                    <p> {degree_from} </p>
                </td>
                <td class="data-row">
                    <p> {final_education_to}</p>
                    <p> {degree_to} </p>
                </td>
                </tr>
            </table>
            <br>
            
            <br>

            <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{rasi_kattam_data_to[0].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[1].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[2].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{rasi_kattam_data_to[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[10].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[9].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[8].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[7].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
            <br>
                    
            <br>
                    
            </td>
            </tr>
            </table>
             <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
                
            <h2 class="report-title" >Nakshatra Porutham & Rasi Porutham</h2>
           <table class="porutham-table">
                <tr>
                    <th>Porutham Name</th>
                    <th>Status</th>
                    <th>Matching Score</th>
                </tr>
                 {porutham_rows}
                 </table>        
              <table class="profile-addtional-info">
                <tr >
                <td class="data-row"  style="width:100%;">
                <p>
                Our best wishes for finding your soulmate in Vyasyamala soon. Please inform Vyasyamala if your marriage is fixed. Share your engagement photo and receive a surprise gift. No commissions / hidden charges. Jai Vasavi!
                </p>
                </td>
                </tr>
                </table>
                <br>
            </td>
            </tr>
            </table>
        </body>
        </html>"""

            # Log profile view
        
        save_logs, created = models.Profile_docviewlogs.objects.get_or_create(
            profile_id=profile_from,
            viewed_profile=profile_to,
            type=3,
            defaults={
                'viewed_profile': profile_to,
                'datetime': timezone.now(),
                'type': 3,
                'status': 1
            }
        )
        if not created:
            save_logs.datetime = timezone.now()
            save_logs.save()

        # Render and return PDF
        return render_to_pdf(html_content)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except models.Registration1.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=404)
    except models.Horoscope.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Horoscope not found'}, status=404)
    except models.Edudetails.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Education details not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def generate_porutham_pdf_mobile(request, profile_from, profile_to):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Only GET method is allowed'}, status=405)

    try:
        # if request.content_type == 'application/json':
        #     data = json.loads(request.body)
        #     profile_from = data.get('profile_from')
        #     profile_to = data.get('profile_to')
        # else:
        #     profile_from = request.GET.get('profile_from')
        #     profile_to = request.GET.get('profile_to')

        if not profile_from or not profile_to:
            return JsonResponse({'status': 'error', 'message': 'profile_from and profile_to are required'}, status=400)

        if can_see_compatability_report(profile_from, profile_to) is not True:
            return JsonResponse({'status': 'failure', 'message': 'No access to see the compatibility report'}, status=400)

        # Fetch required data
        profile_from_details = models.Registration1.objects.get(ProfileId=profile_from)
        profile_to_details = models.Registration1.objects.get(ProfileId=profile_to)
        horoscope_from = models.Horoscope.objects.get(profile_id=profile_from)
        horoscope_to = models.Horoscope.objects.get(profile_id=profile_to)
        education_from_details = models.Edudetails.objects.get(profile_id=profile_from)
        education_to_details = models.Edudetails.objects.get(profile_id=profile_to)

        try:
            degree_from= get_degree_name(education_from_details.degree,education_from_details.other_degree)  
        except Exception as e:
            degree_from = None
        try:
            degree_to= get_degree_name(education_to_details.degree,education_to_details.other_degree)  
        except Exception as e:
            degree_to = None

        # Defensive check for null fields
        if not horoscope_from.birthstar_name or not horoscope_to.birthstar_name:
            return JsonResponse({'status': 'error', 'message': 'Missing birth star data'}, status=400)

        if not horoscope_from.birth_rasi_name or not horoscope_to.birth_rasi_name:
            return JsonResponse({'status': 'error', 'message': 'Missing rasi data'}, status=400)

        if not education_from_details.highest_education or not education_to_details.highest_education:
            return JsonResponse({'status': 'error', 'message': 'Missing education data'}, status=400)

        # Fetch from master tables
        birth_star_from = models.Birthstar.objects.get(id=horoscope_from.birthstar_name)
        birth_star_to = models.Birthstar.objects.get(id=horoscope_to.birthstar_name)
        rasi_from = models.Rasi.objects.get(id=horoscope_from.birth_rasi_name)
        rasi_to = models.Rasi.objects.get(id=horoscope_to.birth_rasi_name)
        highest_education_from = models.Edupref.objects.get(RowId=education_from_details.highest_education)
        highest_education_to = models.Edupref.objects.get(RowId=education_to_details.highest_education)
        
        field_ofstudy_id_from = education_from_details.field_ofstudy
        fieldof_study_from=" "
        if field_ofstudy_id_from:
            fieldof_study_from = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_from).values_list('field_of_study', flat=True).first() or "Unknown"
        
        about_edu_from=education_from_details.about_edu
        
        final_education_from = (highest_education_from.EducationLevel + ' ' + fieldof_study_from).strip() or about_edu_from
                
        field_ofstudy_id_to = education_to_details.field_ofstudy
        fieldof_study_to=" "
        if field_ofstudy_id_to:
            fieldof_study_to = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_to).values_list('field_of_study', flat=True).first() or "Unknown"
        
        about_edu_to=education_to_details.about_edu
        
        final_education_to = (highest_education_to.EducationLevel + ' ' + fieldof_study_to).strip() or about_edu_to
        
        def format_time_am_pm(time_str):
            if not time_str:  # Handles None or empty strings
                return "N/A"
            try:
                time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
            except ValueError:
                return str(time_str)
            
        horo_from_time = format_time_am_pm(horoscope_from.time_of_birth)
        horo_to_time = format_time_am_pm(horoscope_to.time_of_birth)
        
        horo_from_date = format_date_of_birth(profile_from_details.Profile_dob)
        horo_to_date = format_date_of_birth(profile_to_details.Profile_dob)

        # Handle Gender safely
        gender_from = safe_str(profile_from_details.Gender).lower()
        gender_to = safe_str(profile_to_details.Gender).lower()
        if gender_from == gender_to:
            return JsonResponse({'status': 'error', 'message': 'Profiles have the same gender. Matching is not applicable.'}, status=400)

        # Parse Rasi Kattam data
        rasi_kattam_from = parse_data(horoscope_from.rasi_kattam or "")
        rasi_kattam_to = parse_data(horoscope_to.rasi_kattam or "")
        rasi_kattam_from.extend(['-'] * (12 - len(rasi_kattam_from)))
        rasi_kattam_to.extend(['-'] * (12 - len(rasi_kattam_to)))
        if horoscope_from.rasi_kattam or  horoscope_from.amsa_kattam:
            rasi_kattam_data_from = parse_data(horoscope_from.rasi_kattam)
        else:
            rasi_kattam_data_from=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
        rasi_kattam_data_from.extend([default_placeholder] * (12 - len(rasi_kattam_data_from)))

        if horoscope_to.rasi_kattam or  horoscope_to.amsa_kattam:
            rasi_kattam_data_to = parse_data(horoscope_to.rasi_kattam)
        else:
            rasi_kattam_data_to=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
        rasi_kattam_data_to.extend([default_placeholder] * (12 - len(rasi_kattam_data_to)))     
        # Get porutham data
        porutham_data = fetch_porutham_details(profile_from, profile_to)


        porutham_rows = ""
        for idx, porutham in enumerate(porutham_data['porutham_results']):
            extra_td = ""
            if idx == 0:
                extra_td = (
                    f"<td rowspan='{len(porutham_data['porutham_results'])}'>"
                    f"<p class='matching-score' style='font-size:40px;'>{porutham_data['matching_score']}</p>"
                    f"<p style='font-weight:300;'>Please check with your astrologer for detailed compatibility.</p>"
                    f"<p>Jai Vasavi</p>"
                    f"</td>"
                )
            porutham_rows += (
                f"<tr>"
                f"<td>{porutham['porutham_name']}</td>"
                f"<td><span style='color: {'green' if porutham['status'].startswith('YES') else 'red'};'>{porutham['status']}</span></td>"
                f"{extra_td}"
                f"</tr>"
            )



            # Define the HTML content with custom styles
        html_content = f"""
            <html>
            <head>
                <style>
                   @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: auto;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                           
                           
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}

                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            .porutham-table{{
                                border:1px solid #538135;
                                border-collapse: collapse;
                                margin-bottom: 10px;
                            }}
                            .porutham-table th {{
                                padding: 5px 0;
                                  background-color: #538135;
                                  color:#f4c542;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0 0 0;
                            }}
                            .porutham-table td {{
                                border:1px solid #538135;
                                color: #538135;
                                font-size:15px;
                                font-weight:400;
                                text-align:center;
                                padding: 8px 5px;
                            }}
                            .porutham-table tr td p{{
                                color: #538135;
                                font-size:15px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0;
                            }}
                          
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}


                            .matching-score{{
                                font-size:30px ;
                                font-weight:700;
                            }}
                        

                            .compatibility-page-wrapper {{
                                 margin:0px auto;
                                text-align:center;
                                width:100%;
                            }}
                            .compatibility-page-wrapper tr {{
                                margin: auto;
                                text-align:center;
                                width:100%;
                            }}
                            
                            .compatibility-page-wrapper tr td{{
                                background-color: #ffd966;
                                width:100%;
                                text-align:center;
                                margin: auto;
                               
                            }}

                            .report-title {{
                                background-color: #ffd966;
                                color: #538135;
                                font-weight: bold;
                                text-align: center;
                                padding: 10px 0px 0px;
                                font-size: 16px;
                            }}
                             .report-table {{
                                width: 100%;
                                border-collapse: collapse;
                                background-color: #538135;
                                
                            }}
                             .report-table  tr {{
                                background-color: #538135;

                             }}
                             .report-table  tr  td{{
                                background-color: #538135;
                                color:#ffd966;
                                border:1px solid #ffd966;

                             }}
                             .report-table  tr  td p{{
                                background-color: #538135;
                                color:#ffd966;
                                font-size:14px;
                                width:100%;

                             }}
                             .profile-name{{
                                color:#ffd966;
                             }}
                            .header-cell {{
                                background-color: #538135;
                                color: #fff;
                                font-weight: bold;
                                text-align: center;
                                padding: 6px;
                            }}
                            .sub-header {{
                                background-color:#538135;
                                color: #000;
                                text-align: center;
                                padding: 4px;
                            }}
                            .profile-addtional-info{{
                                width: 100%;
                                background-color: #ffd966;
                                border:1px solid #538135;

                            }}
                              .profile-addtional-info  tr {{
                                background-color: #ffd966;
                                border:none;

                             }}
                            
                             .profile-addtional-info  tr  td p{{
                                background-color: #ffd966;
                                color:#538135;
                                font-size:14px;
                                width:100%;

                             }}
                            .data-row {{
                                padding: 2px 0px;
                            }}
                            .data-label {{
                                font-weight: bold;
                                width: 40%;
                                padding: 4px;
                            }}
                            .data-value {{
                                padding: 4px;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                                margin-bottom: 10px;
                            }}
                            .outer tr td {{
                                padding: 0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff9c7;
                            }}

                            .inner-tabledata {{
                                width: 25%;
                                height: 80px;

                            }}

                            .inner td {{
                                width: 25%;
                                height: 80px;
                                border: 2px solid #d6d6d6;
                                padding: 10px;
                                color: #008000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line;
                                /* Ensures new lines are respected */
                            }}

                            .inner-table tr td p {{
                                white-space: pre-line;
                                word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow: hidden;

                            }}

                            .inner .highlight {{
                                background-color: #ffd966;
                                text-align: center;
                                width: 100%;
                                height: 100%;
                                font-size: 24px;
                                font-weight: 700;
                                color: #008000;
                                vertical-align: middle;
                                padding: 10px;

                            }}

                            .inner .highlight p {{
                                font-size: 16px;
                                font-weight: 400;
                                color: #008000;
                            }}
                </style>
            </head>
        <body>
                               
                 <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>

            <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
            <h2 class="report-title">Marriage Compatibility Report</h2>
        
            <table class="report-table" border="0">
                <tr>
                <td class="header-cell">
                    <p class="profile-name">{profile_from_details.Profile_name} - {profile_from_details.ProfileId}</p>
                </td>
                <td class="header-cell">
                    <p class="profile-name"> {profile_to_details.Profile_name} - {profile_to_details.ProfileId}</p>   
                 </td>
                </tr>
                <tr>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_from.name} - {birth_star_from.star}</p>
                </td>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_to.name} - {birth_star_to.star}</p>
                </td>
                </tr>
            </table>
            <br>
        
            <table class="profile-addtional-info" >
                <tr>
                <td class="data-row">
                     <p> Place of Birth : {horoscope_from.place_of_birth}</p>
                </td>
                <td class="data-row">
                    <p> Place of Birth : {horoscope_to.place_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Time of Birth : {horo_from_time}</p>
                </td>
                <td class="data-row">
                    <p>  Time of Birth : {horo_to_time}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Date Of Birth : {horo_from_date}</p>
                </td>
                <td class="data-row">
                    <p> Date Of Birth : {horo_to_date}</p>
                </td>
                </tr>
            </table>
            <br>
        
              <table class="profile-addtional-info">
                <tr>
                <td class="data-row">
                    <p> Height : {profile_from_details.Profile_height}</p>
                </td>
                <td class="data-row">
                        <p> Height : {profile_to_details.Profile_height}</p>
        
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> {final_education_from}</p>
                    <p> {degree_from} </p>
                </td>
                <td class="data-row">
                    <p> {final_education_to}</p>
                    <p> {degree_to} </p>
                </td>
                </tr>
            </table>
            <br>
            
            <br>

            <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data_from[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{rasi_kattam_data_to[0].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[1].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[2].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{rasi_kattam_data_to[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[10].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{rasi_kattam_data_to[9].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[8].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[7].replace('/', '<br>')}</td>
                                        <td>{rasi_kattam_data_to[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
            <br>
                    
            <br>
                    
            </td>
            </tr>
            </table>
             <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
                
            <h2 class="report-title" >Nakshatra Porutham & Rasi Porutham</h2>
           <table class="porutham-table">
                <tr>
                    <th>Porutham Name</th>
                    <th>Status</th>
                    <th>Matching Score</th>
                </tr>
                 {porutham_rows}
                 </table>        
              <table class="profile-addtional-info">
                <tr >
                <td class="data-row"  style="width:100%;">
                <p>
                Our best wishes for finding your soulmate in Vyasyamala soon. Please inform Vyasyamala if your marriage is fixed. Share your engagement photo and receive a surprise gift. No commissions / hidden charges. Jai Vasavi!
                </p>
                </td>
                </tr>
                </table>
                <br>
            </td>
            </tr>
            </table>
        </body>
        </html>"""

            # Log profile view
        save_logs, created = models.Profile_docviewlogs.objects.get_or_create(
            profile_id=profile_from,
            viewed_profile=profile_to,
            type=3,
            defaults={
                'viewed_profile': profile_to,
                'datetime': timezone.now(),
                'type': 3,
                'status': 1
            }
        )
        if not created:
            save_logs.datetime = timezone.now()
            save_logs.save()

        # Render and return PDF
        return render_to_pdf(html_content)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except models.Registration1.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=404)
    except models.Horoscope.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Horoscope not found'}, status=404)
    except models.Edudetails.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Education details not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_primary_sign(value):
    if not value:
        return "N/A"
    return value.split('/')[0]

def cm_to_feet_inches(cm):
    if cm is None or cm == "":
        return "N/A"

    try:
        cm = float(cm)
    except ValueError:
        return "N/A"

    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)

    return f"{feet} ft {inches} in"


class getMessages(APIView):
    
    def post(self, request): 

        room_name = request.data.get('room_name')
        profile_id = request.data.get('profile_id')
        if not room_name:
            
            return JsonResponse({
                "status": "failure",
                "message": "room_name is required"
            }, status=status.HTTP_200_OK)
        
        # search_id = request.data.get('search_id') 
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            
            try:
                room_details = models.Room.objects.get(name=room_name)
            except models.Room.DoesNotExist:
                
                return JsonResponse({
                    "status": "failure",
                    "message": "Room name doesn't exist"
                })
            
            messages = models.Message.objects.filter(room=room_details.id).values('id', 'value', 'date','user')
            return JsonResponse({"messages":list(messages)})
        
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

def generate_room_id(user1_id, user2_id):
    return f"{min(user1_id, user2_id)}{max(user1_id, user2_id)}"




from django.shortcuts import render, redirect, get_object_or_404
# from .models import Room, Message
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Create your views here.
def home(request):

    # print('room')
    return render(request, 'home.html')

def room(request, room):

    try:
        room_details = models.Room.objects.get(name=room)
        messages = models.Message.objects.filter(room=room_details.id)
    except models.Room.DoesNotExist:
        
        # print('room',room)
        # print(request.GET.get('username'))
        return render(request, 'error.html', {'error_message': 'Room does not exist.'})

    return render(request, 'room.html', {
        'room': room,
        'username': request.GET.get('username'),
        'messages': messages
    })

def checkview(request):
    # print('123457')
    room =  request.POST['room_name']
    username =request.POST['username']

    if models.Room.objects.filter(name=room).exists():
        return redirect('/auth/'+room+'/?username='+username)
    else:
        new_room = models.Room.objects.create(name=room)
        new_room.save()  # Ensure the room is saved before redirecting
        return redirect('/auth/'+room+'/?username='+username)

import logging
logger = logging.getLogger(__name__)




def send(request):
    # print('Iam here')
    room_id = request.POST.get('room_id')

    
    # print('Room Id ',room_id)
    
    if not room_id:
        # return HttpResponseBadRequest('Room ID is required')
        return JsonResponse({'error': 'Room ID is required'}, status=400)

    try:
        room = models.Room.objects.get(name=room_id)  # Iam now using room name # Assuming you're using room ID, not name
        # print('room',room)
    except models.Room.DoesNotExist:
        logger.error(f"Room with ID {room_id} does not exist.")
        # return HttpResponseBadRequest('Invalid room ID')
        return JsonResponse({'error': 'Invalid room ID'}, status=400)


    message = request.POST.get('message')
    username = request.POST.get('username')

    # print('message',message)
    # print('username',username)

    if not message or not username:
        # return HttpResponseBadRequest('Message and username are required')
        return JsonResponse({'error': 'Message and username are required'}, status=400)
    # print('skdfgkgfhdfghdsbhgbsdjgbsdfjjgfkhdgfhsdf')
    try:
        new_message = models.Message.objects.create(
            value=message, 
            user=username, 
            room=room,
            date=timezone.now()  # Ensure the message has a timestamp
        )
        new_message.save()
    except Exception as e:
        # print('3486587435684765')
        # print('erorr',{e})
        logger.error(f"Error saving message: {e}")
        return JsonResponse({'error': 'Failed to save message'}, status=500)

    return JsonResponse({'message': 'Message sent successfully'})





# def getMessages(request, room):
#     room_details = models.Room.objects.get(name=room)
#     messages = models.Message.objects.filter(room=room_details.id)
#     return JsonResponse({"messages":list(messages.values())})

@csrf_exempt
def delete_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(models.Message, id=message_id)
        message.delete()
        return JsonResponse({'status': 'Message deleted'})
    return JsonResponse({'status': 'Invalid request'}, status=400)



def generate_pdf_without_address(request, user_profile_id, filename="Horoscope_withbirthchart"):

            print('1234567')

            # Retrieve main objects
            horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
            login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
            education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)

            # === Helper functions ===
            def safe_get_value(model, pk_field, value, name_field='name', default='N/A'):
                try:
                    if value and str(value).isdigit():
                        return model.objects.filter(**{pk_field: value}).values_list(name_field, flat=True).first() or default
                except Exception:
                    pass
                return default

            def clean_value(value):
                """Convert blank/null/'null' to 'N/A'."""
                if value and str(value).strip().lower() not in ['none', 'null', '']:
                    return str(value).strip()
                return "N/A"

            # === Personal details ===
            name = clean_value(login_details.Profile_name)
            dob = clean_value(login_details.Profile_dob)
            height = clean_value(login_details.Profile_height)
            user_profile_id = login_details.ProfileId
            complexion_id = login_details.Profile_complexion
            complexion = clean_value(safe_get_value(models.Profilecomplexion, 'complexion_id', complexion_id, 'complexion_desc'))

            # === Education and income/profession ===
            highest_education_id = education_details.highest_education
            highest_education = clean_value(safe_get_value(models.Highesteducation, 'id', highest_education_id, 'degree'))

            annual_income_id = education_details.anual_income
            annual_income = clean_value(safe_get_value(models.Annualincome, 'id', annual_income_id, 'income'))

            profession_id = education_details.profession
            profession = clean_value(safe_get_value(models.Profespref, 'RowId', profession_id, 'profession'))

            # === Occupation title & text ===
            occupation = "N/A"
            occupation_title = "N/A"
            try:
                prof_id = int(profession_id)
                if prof_id == 1:
                    occupation_title = "Employment Details"
                    occupation = f"{clean_value(education_details.company_name)} / {clean_value(education_details.designation)}"
                elif prof_id == 2:
                    occupation_title = "Business Details"
                    occupation = f"{clean_value(education_details.business_name)} / {clean_value(education_details.nature_of_business)}"
                else:
                    occupation_title = "Other"
            except (ValueError, TypeError):
                occupation_title = "Unknown"
                occupation = "Unknown"

            # === Family details ===
            family_detail = models.Familydetails.objects.filter(profile_id=user_profile_id).first()

            father_name = clean_value(family_detail.father_name if family_detail else "")
            father_occupation = clean_value(family_detail.father_occupation if family_detail else "")
            mother_name = clean_value(family_detail.mother_name if family_detail else "")
            mother_occupation = clean_value(family_detail.mother_occupation if family_detail else "")
            family_status_id = family_detail.family_status if family_detail else ""
            family_status = clean_value(safe_get_value(models.Familystatus, 'id', family_status_id, 'status'))
            suya_gothram = clean_value(family_detail.suya_gothram if family_detail else "")
            no_of_sis_married = clean_value(family_detail.no_of_sis_married if family_detail else "0")
            no_of_bro_married = clean_value(family_detail.no_of_bro_married if family_detail else "0")

            def get_model_display_name(model, pk, field_name='star', default='Unknown'):
                try:
                    return getattr(model.objects.get(pk=int(pk)), field_name)
                except (model.DoesNotExist, ValueError, TypeError):
                    return default
            # === Horoscopic Details ===
            star_name = get_model_display_name(models.Birthstar, horoscope.birthstar_name, 'star')
            rasi_name = get_model_display_name(models.Rasi, horoscope.birth_rasi_name, 'name')

            time_of_birth = clean_value(horoscope.time_of_birth)
            place_of_birth = clean_value(horoscope.place_of_birth)
            lagnam_didi = clean_value(horoscope.lagnam_didi)
            nalikai = clean_value(horoscope.nalikai)
            age = calculate_age(login_details.Profile_dob) if login_details.Profile_dob else "N/A"            # Planet mapping dictionary
            # planet_mapping = {
            #     "1": "Sun",
            #     "2": "Moo",
            #     "3": "Mar",
            #     "4": "Mer",
            #     "5": "Jup",
            #     "6": "Ven",
            #     "7": "Sat",
            #     "8": "Rahu",
            #     "9": "Kethu",
            #     "10": "Lagnam",
            # }
            planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }
            # Define a default placeholder for empty values
            default_placeholder = '-'
            def parse_data(data):
                # Clean up and split data
                items = data.strip('{}').split(', ')
                parsed_items = []
                for item in items:
                    parts = item.split(':')
                    if len(parts) > 1:
                        values = parts[-1].strip()
                        # Handle multiple values separated by comma
                        if ',' in values:
                            values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                        else:
                            values = planet_mapping.get(values, default_placeholder)
                    else:
                        values = default_placeholder
                    parsed_items.append(values)
                return parsed_items
            # Clean up and parse the rasi_kattam and amsa_kattam data
            if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                amsa_kattam_data = parse_data(horoscope.amsa_kattam)
            else:
                rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
            # Ensure that we have exactly 12 values for the grid
            rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
            amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))
            horoscope_data = get_object_or_404(models.Horoscope, profile_id=user_profile_id)

            if horoscope_data.horoscope_file_admin:
                horoscope_image_url = horoscope_data.horoscope_file_admin.url
        
                if horoscope_image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    horoscope_content = f'<img src="{settings.IMAGE_BASEURL}{horoscope_image_url}" alt="Horoscope Image" style="max-width: 200%; height: auto;">'
                else:
                    horoscope_content = f'<a href="{settings.IMAGE_BASEURL}{horoscope_image_url}" download>Download Horoscope File</a>'
            else:
                horoscope_content = '<p>No horoscope uploaded</p>'
            # Get matching stars data
            birth_star_id = horoscope.birthstar_name
            birth_rasi_id = horoscope.birth_rasi_name
            gender = login_details.Gender
            porutham_data = models.MatchingStarPartner.get_matching_stars_pdf(birth_rasi_id, birth_star_id, gender)
        
            # Prepare the Porutham sections for the PDF
            def format_star_names(poruthams):
                return ', '.join([f"{item['matching_starname']} - {item['matching_rasiname'].split('/')[0]}" for item in poruthams])
            profile_url = f"http://matrimonyapp.rainyseasun.com/ProfileDetails?id={user_profile_id}&rasi={horoscope.birth_rasi_name}"
            
                # Dynamic HTML content including Rasi and Amsam charts
            html_content = rf"""
            <html>
                <head>
                    <style>
                    @page {{
                            size: A4;
                            margin: 0;
                        }}
                        body {{
                            background-color: #ffffff;
                        }}
                        .header {{
                            margin-bottom: 10px;
                        }}
                        .header-left img {{
                            width: 100%;
                            height: auto;
                        }}
                        .logo-text{{
                            font-size: 18px;
                            font-weight: 400;
                            color:  #fbf274;
                        }}
                        .header-left {{
                            width: 100%;
                        }}
                        
                        .header-left p{{
                            font-size: 18px;
                            font-weight: 400;
                            color: #ffffff;
                        }}
                        .header-info p {{
                            color:#fbf274;
                            font-size:16px;
                            padding-bottom:5px;
                            text-align:center;
                        }}
                        .score-box {{
                            float: right;
                            text-align: center;
                            background-color: #fffbcc;
                            border: 1px solid #d4d4d4;
                            width:100%;
                           margin-bottom:1.5rem !important;
                        }}
                         .score-box p {{
                            font-size: 2rem;
                            font-weight: bold;
                            padding: 10px 30px 10px !important;
                            color: #333;
                            margin: 0px auto !important;
                            padding-top:1.3rem !important;
                        }}
                        p {{
                            font-size: 10px;
                            margin: 5px 0;
                            padding: 0;
                            color: #333;
                        }}
                        .details-div {{
                            margin-bottom: 20px;
                        }}
                        .details-section p {{
                            margin: 2px 0;
                        }}
                        .details-section td {{
                              border: none;
                        }}
                         .personal-detail-header{{
                            font-size: 2rem;
                            font-weight: bold;
                            margin-bottom: 1rem;
                        }}
                        table.outer {{
                            width: 100%;
                            text-align: center;
                            font-family: Arial, sans-serif;
                            margin:0;
                            padding:0;
                            margin-bottom:10px;
                        }}
                        .outer tr td{{
                        padding:0 20px;
                        }}
                        table.inner {{
                            width: 45%;
                            border-collapse: collapse;
                            text-align: center;
                            font-family: Arial, sans-serif;
                            margin: 10px;
                            display: inline-block;
                            vertical-align: top;
                            background-color: #fff9c7;
                        }}
                        .inner-tabledata{{
                             width:25%;
                            height:80px;
                            
                        }}
                        .inner td {{
                            width:25%;
                           height:85px;
                            border:2px solid #d6d6d6;
                            padding: 10px;
                            color: #008000;
                            font-weight: bold;
                            font-size: 12px;
                            white-space: pre-line; /* Ensures new lines are respected */
                        }}
                        .inner .highlight {{
                                background-color: #ffffff;
                                text-align: center;
                                width: 100%;
                                height: 100%;
                               font-size:24px;
                                font-weight: 700;
                                color: #008000;
                        }}
                        .inner .highlight p{{
                            font-size: 16px;
                            font-weight: 400;
                            color: #008000;
                        }}
                        .spacer {{
                            width: 14%;
                            display: inline-block;
                            background-color: transparent;
                        }}
                        .table-div{{
                            border-collapse: collapse;
                            padding:5px 20px;
                            margin-bottom:2rem;
                        }}
                        .table-div tr {{
                            padding: 10px 10px;
                        }}
                        .table-div tr .border-right{{
                            border-right:1px solid #008000;
                        }}
                        .table-div td{{
                            background-color: #fff9c7;
                            width:50%;
                            padding: 10px 10px;
                            text-align:left;
                        }}
                        .table-div p {{
                               font-size:14px;
                            font-weight:400;
                            color: #008000;
                        }}
                        .inner-table tr td{{
                            padding:0px;
                            margin-bottom:0px;
                        }}
                        .dasa-table td{{
                            width:100%;
                            background-color:#fff;
                             padding:0px;
                        }}
                        .dasa-table td p{{
                            font-size:14px;
                            font-weight:400;
                            text-align:center;
                        }}
                        .note-text {{
                            color: red;
                            font-size:12px;
                            font-weight: 500;
                            margin: 50px auto;
                        }}
                        .note-text1 {{
                            color: red;
                            font-size: 14px;
                            font-weight: 500;
                            margin: 30px auto;
                            text-align: right;
                        }}
                      
                        .add-info tr {{
                       padding:10px 20px ;
                        }}
                    
                        .add-info td {{
                            background-color: #fff9c7;
                            padding: 5px 5px;
                        }}
                      .add-info td p{{
                        font-size: 16px;
                        font-weight: 400;
                        color: #008000;
                        padding:0 20px;
                       }}
                       .click-here{{
                        color:#318f9a;
                       text-decoration: none;
                       }}
                        .porutham-page{{
                            padding: 0px 20px;
                        }}
                        .porutham-header {{
                            margin: 20px 0px;
                        }}
                        .porutham-header img{{
                            width: 130px;
                            height: auto;
                        }}
                        .porutham-header p {{
                            font-size:22px;
                            font-weight: 700;
                            color:#000000;
                        }}
                        h2.porutham-table-title{{
                            font-size: 24px;
                            font-weight: 700;
                            margin-bottom: 20px;
                            padding:0px 0px;
                        }}
                        porutham-table{{
                            border:1px solid #bcbcbc;
                            border-collapse: collapse;
                            margin-bottom: 24px;
                        }}
                        .porutham-table td {{
                            border:1px solid #bcbcbc;
                        }}
                        .porutham-table td p{{
                            color: #000;
                            font-size:16px;
                            font-weight:700;
                            text-align:center;
                            padding: 10px 0;
                        }}
                        .porutham-stars tr td p{{
                            text-align:left;
                            padding: 20px 20px;
                        }}
                        .porutham-note{{
                            font-size: 17px;
                            font-weight:400;
                            color: #000000;
                            padding:20px 0px;
                        }}
                       .upload-horo-bg img{{
                           width:100%;
                           height:auto;
                       }}
                        .upload-horo-image{{
                            margin: 10px 0px;
                            text-align: center;
                        }}
                        .upload-horo-image img{{
                            width:400px;
                            height:800px;
                            object-fit: contain;
                        }}
                        
                    </style>
                </head>
                <body>
                    <table class="header">
                            <tr>
                                <td class="header-left">
                                    <div class="header-logo">
                                        <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" alt="Vysyamala Logo">
                                    </div>
                                </td>
                            </tr>
                    </table>
                    
                <div class="details-section">
                
            <table class="table-div">
                        <tr>
                            <td class="border-right">
                            <table class="inner-table">
                                <tr>
                                <td>
                                <p><strong>Name </strong></p>
                                <p>DOB / POB </p>
                                <p>Complexion </p>
                                <p>Education </p>
                                </td>
                                <td>
                                <p><strong>{name}</strong></p>
                                <p>{dob} / {place_of_birth}</p>
                                <p> {complexion}</p>
                                <p>{highest_education}</p>
                                </td>
                                </tr>
                                </table>
                                
                            </td>
                            
                            <td>
                            <table class="inner-table">
                                <tr>
                                    <td>
                                        <p><strong>Vysyamala Id : </strong></p>
                                        <p>Height / Photos </p>
                                        <p>Annual Income</p>
                                        <p>Profession</p>
                                    </td> 
                                    <td>
                                        <p><strong>{user_profile_id}</strong></p>
                                        <p> {height} / Not specified</p>
                                        <p>{annual_income}</p>
                                        <p>{profession}</p>
                                        <p>{occupation_title}</p>
                                        <p>{occupation}</p>
                                    </td> 
                                </tr>
                            </table>
                            </td>
                        </tr>
                    </table>
                    
                    <table class="table-div">
                        <tr>
                            <td  class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td>
                                            <p><strong>Father Name </strong> </p>
                                            <p>Father Occupation </p>
                                            <p>Family Status </p>
                                            <p>Brothers/Married </p>
                                        </td>
                                        <td>
                                            <p><strong>{father_name}</strong></p>
                                            <p> {father_occupation}</p>
                                            <p>{family_status}</p>
                                            <p>{no_of_bro_married}</p>
                                        </td>
                                    </tr>
                                </table>
                                
                            </td>
                            <td>
                                <table class="inner-table">
                                    <tr>
                                        <td>
                                            <p><strong>Mother Name </strong> </p>
                                            <p>Mother Occupation </p>
                                            <p>Sisters/Married </p>
                                        </td>
                                        <td>
                                            <p><strong>{mother_name}</strong></p>
                                            <p>{mother_occupation}</p>
                                            <p>{no_of_sis_married}</p>
                                        </td>
                                    </tr>
                                </table>
                           
                            </td>
                        </tr>
                    </table>
                    <table class="table-div">
                        <tr>
                            <td  class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td>
                                            <p><strong>Star/Rasi </strong> </p>
                                            <p>Lagnam/Didi </p>
                                            <p>Nalikai </p>
                                        </td>
                                        <td>
                                            <p><strong>{star_name}, {rasi_name}</strong></p>
                                            <p>{lagnam_didi}</p>
                                            <p>{nalikai}</p>
                                        </td>
                                    </tr>
                                </table>
                                
                            </td>
                            <td>
                                <table class="inner-table">
                                    <tr>
                                        <td>
                                            <p><strong>Surya Gothram : </strong></p>
                                            <p>Madhulam </p>
                                            <p>Birth Time </p>
                                        </td>
                                        <td>
                                            <p><strong>{suya_gothram}</strong></p>
                                            <p>N/A</p>
                                            <p>{time_of_birth}</p>
                                        </td>
                                    </tr>
                                </table>
                                
                            </td>
                        </tr>
                    </table>
                
                </div>
                
                        <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                        Rasi
                                        <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td class="spacer">
                                 <table class="table-div dasa-table">
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Name</strong</p>
                                            <p>Moon</p>
                                        </td>
                                    </tr
                                    <tr>
                                    <td>
                                        
                                            <p><strong>Dasa Balance</strong</p>
                                            <p>Years: 01</p>
                                            <p>Months: 8</p>
                                            <p>Days: 23</p>
                                        </td>
                                    </tr>
                                        
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Amsam
                                        <p>vysyamala.com</p>
                                        </td>
                                        <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
						 <tr>
                    <td>
                    <br>
                        <p>Note: Please verify this profile yourself. No hidden charges or commissions if marriage is fixed through Vysyamala. For more details of this profile: <a href="{profile_url}" target="_blank" class="click-here">click here</a></p>
                    </td>
                </tr>
                    </table>
					<table class="porutham-page">
            <tr>
            <td>
            <br>
            <table class="porutham-header">
                <tr>
                    <td>
                        <img src="https://vysyamat.blob.core.windows.net/vysyamala/newvysyamalalogo2.png">
                    </td>
                    <td>
                        <p>www.vysyamala.com</p>
                    </td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars Report</h2>
            <table class="porutham-table">
                 <tr>
                    <td><p>Name</p></td>
                    <td><p>{name}</p></td>
                    <td><p>Vysyamala ID</p></td>
                    <td><p>{user_profile_id}</p></td>
                </tr>
                <tr>
                    <td><p>Birth Star</p></td>
                    <td><p>{star_name}</p></td>
                    <td><p>Age</p></td>
                    <td><p>{age}</p></td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars (9 Poruthams)</h2>
            <table class="porutham-table porutham-stars">
                <tr>
                    <td>
                        <p>{format_star_names(porutham_data["9 Poruthams"])}</p>
                    </td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars (8 Poruthams)</h2>
            <table class="porutham-table porutham-stars">
                <tr>
                    <td>
                        <p>{format_star_names(porutham_data["8 Poruthams"])}</p>
                    </td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars (7 Poruthams)</h2>
            <table class="porutham-table porutham-stars">
                <tr>
                    <td>
                        <p>{format_star_names(porutham_data["7 Poruthams"])}</p>
                    </td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars (6 Poruthams)</h2>
            <table class="porutham-table porutham-stars">
                <tr>
                    <td>
                        <p>{format_star_names(porutham_data["6 Poruthams"])}</p>
                    </td>
                </tr>
            </table>
            <h2 class="porutham-table-title">Matching Stars (5 Poruthams)</h2>
            <table class="porutham-table porutham-stars">
                <tr>
                    <td>
                        <p>{format_star_names(porutham_data["5 Poruthams"])}</p>
                    </td>
                </tr>
            </table>
            <p class="porutham-note">Note: This is system generated report, please confirm the same with your astrologer.</p>
            </td>
            </tr>
            </table>
            <div class="upload-horo-bg" >
                <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" >
            </div>
            <div class="upload-horo-image">
                     {horoscope_content} 
            </div>
            <div class="upload-horo-bg" >
                <img  src="https://vysyamat.blob.core.windows.net/vysyamala/uploadHoroFooter.png" >
            </div>
               
                </body>
            </html>
            """
            # Create a Django response object and specify content_type as pdf
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            # Create the PDF using xhtml2pdf
            pisa_status = pisa.CreatePDF(html_content, dest=response)
            # If there's an error, log it and return an HTML response with an error message
            if pisa_status.err:
                logger.error(f"PDF generation error: {pisa_status.err}")
                return HttpResponse('We had some errors <pre>' + html_content + '</pre>')
            return response
   


class WithoutAddressSendEmailAPI(APIView):
    def post(self, request):
        """API to generate horoscope PDFs (without address) for multiple profiles and send them to a single recipient."""
        profile_ids = request.data.get('profile_id')  # Comma-separated profile IDs
        to_profile_id = request.data.get('to_profile_id')  # Single recipient profile ID

        if not profile_ids or not to_profile_id:
            return JsonResponse({"error": "profile_id and to_profile_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        profile_ids_list = [pid.strip() for pid in profile_ids.split(',') if pid.strip()]
        missing_profiles = []
        pdf_attachments = []
        email_status = "failed"

        # Fetch recipient email for to_profile_id
        recipient_email = LoginDetails.objects.filter(ProfileId__iexact=to_profile_id).values_list('EmailId', flat=True).first()
        if not recipient_email:
            return JsonResponse({"error": "No email found for to_profile_id"}, status=status.HTTP_400_BAD_REQUEST)

        for profile_id in profile_ids_list:
            horoscope = models.Horoscope.objects.filter(profile_id__iexact=profile_id).first()
            login_details = models.Registration1.objects.filter(ProfileId__iexact=profile_id).first()

            if not horoscope or not login_details:
                missing_profiles.append(profile_id)
                continue  # Skip this profile

            # Generate PDF
            pdf_content = generate_pdf_without_address(request, profile_id)
            if not pdf_content:
                missing_profiles.append(profile_id)
                continue  # Skip this profile

            # Ensure pdf_content is bytes, not HttpResponse
            if isinstance(pdf_content, HttpResponse):
                pdf_content = pdf_content.getvalue()  # Extract PDF bytes

            pdf_attachments.append((f"Horoscope_{profile_id}.pdf", pdf_content, "application/pdf"))

        if not pdf_attachments:
            return JsonResponse({"error": f"Failed for all provided Profile IDs: {', '.join(missing_profiles)}"}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send Email
        subject = "Horoscope Profile Details (Without Address)"
        message = "Dear User,\n\nPlease find the attached horoscope details.\n\nBest Regards,\nYour Astrology Team"
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

        for attachment in pdf_attachments:
            email.attach(*attachment)

        try:
            email.send()
            email_status = "sent"
            response_msg = {"message": "Email sent successfully to the recipient!"}
            if missing_profiles:
                response_msg["warning"] = f"Some profiles failed: {', '.join(missing_profiles)}"
        except Exception as e:
            email_status = "failed"
            response_msg = {"error": f"Error sending email: {e}"}

        # Log Email Sending
        SentWithoutAddressEmailLog.objects.create(
            profile_id=profile_ids,
            to_ids=to_profile_id,
            profile_owner=profile_ids_list[0] if profile_ids_list else "Unknown",
            status=email_status,
            sent_datetime=datetime.now() 
        )

        return JsonResponse(response_msg, status=status.HTTP_200_OK if email_status == "sent" else status.HTTP_500_INTERNAL_SERVER_ERROR)




class health_check(APIView):

    def get(self,request):
        return JsonResponse({"status": "ok"}, status=200)


class WithoutAddressPrintPDF(APIView):
    def post(self, request):
        """API to generate and merge horoscope PDFs (without address) into a single response and log the process."""

        profile_ids = request.data.get('profile_id')  # Expecting comma-separated IDs
        action_type = request.data.get('action_type')  # 'print' or 'whatsapp'

        if not profile_ids:
            return JsonResponse({"error": "profile_id is required"}, status=400)

        profile_ids_list = [pid.strip() for pid in profile_ids.split(',') if pid.strip()]
        missing_profiles = []
        pdf_merger = PdfMerger()
        successful_profiles = []
        log_status = "failed"

        for profile_id in profile_ids_list:
            horoscope = models.Horoscope.objects.filter(profile_id__iexact=profile_id).first()
            login_details = models.Registration1.objects.filter(ProfileId__iexact=profile_id).first()

            if not horoscope or not login_details:
                missing_profiles.append(profile_id)
                continue  # Skip this profile

            # Generate PDF for this profile
            pdf_response = generate_pdf_without_address(request, profile_id)

            if not pdf_response or pdf_response.status_code != 200:
                missing_profiles.append(profile_id)
                continue  # Skip this profile

            profile_owner = request.data.get('profile_owner')

            pdf_content = pdf_response.getvalue()  # Extract PDF content

            # Store the PDF content in memory
            pdf_file = io.BytesIO(pdf_content)
            pdf_merger.append(pdf_file)  # Merge PDF into one file
            successful_profiles.append(profile_id)

        if successful_profiles:
            log_status = "sent"

        # Determine the log model based on action_type
        log_model = SentWithoutAddressPrintwpPDFLog if action_type == 'whatsapp' else SentWithoutAddressPrintPDFLog
        
        # Create log entry
        log_model.objects.create(
            profile_id=",".join(profile_ids_list),
            to_ids="self",  # Change this if recipient info is available
            profile_owner=profile_owner if profile_owner else "Unknown",  # Dynamic profile owner
            status=log_status,
            sent_datetime=datetime.now()
        )

        if not successful_profiles:
            return JsonResponse({"error": f"Failed to generate PDF for profiles: {', '.join(missing_profiles)}"}, 
                                status=500)

        # Create a final merged PDF file in memory
        merged_pdf = io.BytesIO()
        pdf_merger.write(merged_pdf)
        pdf_merger.close()
        merged_pdf.seek(0)

        # Return the merged PDF file
        response = HttpResponse(merged_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Merged_Horoscope_Profiles.pdf"'
        return response
 


# Define a default placeholder for empty values
default_placeholder = '-'

# Planet mapping dictionary
# planet_mapping = {
#     "1": "Sun",
#     "2": "Moo",
#     "3": "Mar",
#     "4": "Mer",
#     "5": "Jup",
#     "6": "Ven",
#     "7": "Sat",
#     "8": "Rahu",
#     "9": "Kethu",
#     "10": "Lagnam",
# }

planet_mapping = {
    "1": "Sun",
    "2": "Moo",
    "3": "Rahu",
    "4": "Kethu",
    "5": "Mar",
    "6": "Ven",
    "7": "Jup",
    "8": "Mer",
    "9": "Sat",
    "10": "Lagnam",
}

# Function to parse kattam data
def parse_data(data):
    items = data.strip('{}').split(', ')
    parsed_items = []
    for item in items:
        parts = item.split(':')
        if len(parts) > 1:
            values = parts[-1].strip()
            values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(',')) if ',' in values else planet_mapping.get(values, default_placeholder)
        else:
            values = default_placeholder
        parsed_items.append(values)
    return parsed_items

# class HoroscopeKattamAPI(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             data = request.data
#             profile_id = data.get('profile_id')
#             if not profile_id:
#                 return Response({'error': 'profile_id is required'}, status=400)

#             horoscope = get_object_or_404(models.Horoscope, profile_id=profile_id)
#             login_details = get_object_or_404(models.Registration1, ProfileId=profile_id)
            
#             rasi_kattam_data = parse_data(horoscope.rasi_kattam) if horoscope.rasi_kattam else parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
#             amsa_kattam_data = parse_data(horoscope.amsa_kattam) if horoscope.amsa_kattam else parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
            
#             rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
#             amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))

#             def generate_image(html_content, filename):
#                 """Generate an image from HTML and save it to media folder."""
#                 media_dir = os.path.join(settings.MEDIA_ROOT, 'horoscope')
#                 os.makedirs(media_dir, exist_ok=True)
#                 file_path = os.path.join(media_dir, filename)

#                 options = {
#                     'format': 'png',
#                     'width': '400',
#                     'height': '400',
#                     'quality': '100',
#                     # 'crop-w': '400',  # Crop width
#                     # 'crop-h': '400',  # Crop height
#                 }

#                 imgkit.from_string(html_content, file_path, options=options,config=config)
#                 return file_path  # Return the saved file path

#             base_url = request.build_absolute_uri(settings.MEDIA_URL)

#             rasi_html_content = f"""
#                 <html>
#                     <head>
#                         <style>
#                         @page {{
#                                 size: A4;
#                                 margin: 0;
#                             }}
#                             body {{
#                                 background-color: #ffffff;
#                             }}

#                             .header {{
#                                 margin-bottom: 10px;
#                             }}

#                             .header-left img {{
#                                 width: 100%;
#                                 height: auto;
#                             }}
#                             .logo-text{{
#                                 font-size: 18px;
#                                 font-weight: 400;
#                                 color:  #fbf274;
#                             }}
#                             .header-left {{
#                                 width: 100%;
#                             }}
                            
#                             .header-left p{{
#                                 font-size: 18px;
#                                 font-weight: 400;
#                                 color: #ffffff;
#                             }}
#                             .header-info p {{
#                                 color:#fbf274;
#                                 font-size:16px;
#                                 padding-bottom:5px;
#                                 text-align:center;
#                             }}
#                             .score-box {{
#                                 float: right;
#                                 text-align: center;
#                                 background-color: #fffbcc;
#                                 border: 1px solid #d4d4d4;
#                                 width:100%;
#                                margin-bottom:1.5rem !important;
#                             }}

#                              .score-box p {{
#                                 font-size: 2rem;
#                                 font-weight: bold;
#                                 padding: 10px 30px 10px !important;
#                                 color: #333;
#                                 margin: 0px auto !important;
#                                 padding-top:1.3rem !important;
#                             }}

#                             p {{
#                                 font-size: 10px;
#                                 margin: 5px 0;
#                                 padding: 0;
#                                 color: #333;
#                             }}

#                             .details-div {{
#                                 margin-bottom: 20px;
#                             }}

#                             .details-section p {{
#                                 margin: 2px 0;
#                             }}

#                             .details-section td {{
#                                   border: none;
#                             }}
#                              .personal-detail-header{{
#                                 font-size: 2rem;
#                                 font-weight: bold;
#                                 margin-bottom: 1rem;
#                             }}
#                             table.outer {{
#                                 width: 100%;
#                                 text-align: center;
#                                 font-family: Arial, sans-serif;
#                                 margin:0;
#                                 padding:0;
#                                 margin-bottom:10px;

#                             }}
#                             .outer tr td{{
#                             padding:0 20px;
#                             }}
#                             table.inner {{
#                                 width: 45%;
#                                 border-collapse: collapse;
#                                 text-align: center;
#                                 font-family: Arial, sans-serif;
#                                 margin: 10px;
#                                 display: inline-block;
#                                 vertical-align: top;
#                                 background-color: #fff9c7;
#                             }}
#                             .inner-tabledata{{
#                                  width:25%;
#                                 height:80px;
                                
#                             }}
#                             .inner td {{
#                                 width:25%;
#                                height:85px;
#                                 border:2px solid #d6d6d6;
#                                 padding: 10px;
#                                 color: #008000;
#                                 font-weight: bold;
#                                 font-size: 12px;
#                                 white-space: pre-line; /* Ensures new lines are respected */
#                             }}

#                             .inner .highlight {{
#                                     background-color: #ffffff;
#                                     text-align: center;
#                                     width: 100%;
#                                     height: 100%;
#                                    font-size:24px;
#                                     font-weight: 700;
#                                     color: #008000;

#                             }}

#                             .inner .highlight p{{
#                                 font-size: 16px;
#                                 font-weight: 400;
#                                 color: #008000;
#                             }}

#                             .spacer {{
#                                 width: 14%;
#                                 display: inline-block;
#                                 background-color: transparent;
#                             }}

#                             .table-div{{
#                                 border-collapse: collapse;
#                                 padding:5px 20px;
#                                 margin-bottom:2rem;
#                             }}
#                             .table-div tr {{
#                                 padding: 10px 10px;
#                             }}
#                             .table-div tr .border-right{{
#                                 border-right:1px solid #008000;
#                             }}
#                             .table-div td{{
#                                 background-color: #fff9c7;
#                                 width:50%;
#                                 padding: 10px 10px;
#                                 text-align:left;
#                             }}
#                             .table-div p {{
#                                    font-size:14px;
#                                 font-weight:400;
#                                 color: #008000;
#                             }}
#                             .inner-table tr td{{
#                                 padding:0px;
#                                 margin-bottom:0px;
#                             }}
#                             .dasa-table td{{
#                                 width:100%;
#                                 background-color:#fff;
#                                  padding:0px;
#                             }}
#                             .dasa-table td p{{
#                                 font-size:14px;
#                                 font-weight:400;
#                                 text-align:center;
#                             }}
#                             .note-text {{
#                                 color: red;
#                                 font-size:12px;
#                                 font-weight: 500;
#                                 margin: 50px auto;
#                             }}

#                             .note-text1 {{
#                                 color: red;
#                                 font-size: 14px;
#                                 font-weight: 500;
#                                 margin: 30px auto;
#                                 text-align: right;
#                             }}
                          
#                             .add-info tr {{
#                            padding:10px 20px ;
#                             }}
                        
#                             .add-info td {{
#                                 background-color: #fff9c7;
#                                 padding: 5px 5px;
#                             }}
#                           .add-info td p{{
#                             font-size: 16px;
#                             font-weight: 400;
#                             color: #008000;
#                             padding:0 20px;
#                            }}
#                            .click-here{{
#                             color:#318f9a;
#                            text-decoration: none;

#                            }}

#                             .porutham-page{{
#                                 padding: 0px 20px;
#                             }}
#                             .porutham-header {{
#                                 margin: 20px 0px;
#                             }}

#                             .porutham-header img{{
#                                 width: 130px;
#                                 height: auto;
#                             }}
#                             .porutham-header p {{
#                                 font-size:22px;
#                                 font-weight: 700;
#                                 color:#000000;
#                             }}
#                             h2.porutham-table-title{{
#                                 font-size: 24px;
#                                 font-weight: 700;
#                                 margin-bottom: 20px;
#                                 padding:0px 0px;
#                             }}
#                             porutham-table{{
#                                 border:1px solid #bcbcbc;
#                                 border-collapse: collapse;
#                                 margin-bottom: 24px;
#                             }}
#                             .porutham-table td {{
#                                 border:1px solid #bcbcbc;
#                             }}
#                             .porutham-table td p{{
#                                 color: #000;
#                                 font-size:16px;
#                                 font-weight:700;
#                                 text-align:center;
#                                 padding: 10px 0;
#                             }}
#                             .porutham-stars tr td p{{
#                                 text-align:left;
#                                 padding: 20px 20px;
#                             }}
#                             .porutham-note{{
#                                 font-size: 17px;
#                                 font-weight:400;
#                                 color: #000000;
#                                 padding:20px 0px;
#                             }}



#                            .upload-horo-bg img{{
#                                width:100%;
#                                height:auto;
#                            }}
#                             .upload-horo-image{{
#                                 margin: 10px 0px;
#                                 text-align: center;

#                             }}
#                             .upload-horo-image img{{
#                                 width:400px;
#                                 height:800px;
#                                 object-fit: contain;
#                             }}
                            

#                         </style>
#                     </head>

#                     <body>
                
#                 <table class="outer">
#                     <tr>
#                         <td>
#                             <table class="inner">
#                                 <tr>
#                                     <td>{rasi_kattam_data[0]}</td>
#                                     <td>{rasi_kattam_data[1]}</td>
#                                     <td>{rasi_kattam_data[2]}</td>
#                                     <td>{rasi_kattam_data[3]}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>{rasi_kattam_data[11]}</td>
#                                     <td colspan="2" rowspan="2" class="highlight">Rasi<p>vysyamala.com</p></td>
#                                     <td>{rasi_kattam_data[4]}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>{rasi_kattam_data[10]}</td>
#                                     <td>{rasi_kattam_data[5]}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>{rasi_kattam_data[9]}</td>
#                                     <td>{rasi_kattam_data[8]}</td>
#                                     <td>{rasi_kattam_data[7]}</td>
#                                     <td>{rasi_kattam_data[6]}</td>
#                                 </tr>
#                             </table>
#                         </td>
#                         <td class="spacer"></td>
                        
#                     </tr>
#                 </table>
#                 </body></html>
#             """

#             amsa_html_content = f"""
#                 <html>
#                     <head>
#                         <style>
#                         @page {{
#                                 size: A4;
#                                 margin: 0;
#                             }}
#                             body {{
#                                 background-color: #ffffff;
#                             }}

#                             .header {{
#                                 margin-bottom: 10px;
#                             }}

#                             .header-left img {{
#                                 width: 100%;
#                                 height: auto;
#                             }}
#                             .logo-text{{
#                                 font-size: 18px;
#                                 font-weight: 400;
#                                 color:  #fbf274;
#                             }}
#                             .header-left {{
#                                 width: 100%;
#                             }}
                            
#                             .header-left p{{
#                                 font-size: 18px;
#                                 font-weight: 400;
#                                 color: #ffffff;
#                             }}
#                             .header-info p {{
#                                 color:#fbf274;
#                                 font-size:16px;
#                                 padding-bottom:5px;
#                                 text-align:center;
#                             }}
#                             .score-box {{
#                                 float: right;
#                                 text-align: center;
#                                 background-color: #fffbcc;
#                                 border: 1px solid #d4d4d4;
#                                 width:100%;
#                                margin-bottom:1.5rem !important;
#                             }}

#                              .score-box p {{
#                                 font-size: 2rem;
#                                 font-weight: bold;
#                                 padding: 10px 30px 10px !important;
#                                 color: #333;
#                                 margin: 0px auto !important;
#                                 padding-top:1.3rem !important;
#                             }}

#                             p {{
#                                 font-size: 10px;
#                                 margin: 5px 0;
#                                 padding: 0;
#                                 color: #333;
#                             }}

#                             .details-div {{
#                                 margin-bottom: 20px;
#                             }}

#                             .details-section p {{
#                                 margin: 2px 0;
#                             }}

#                             .details-section td {{
#                                   border: none;
#                             }}
#                              .personal-detail-header{{
#                                 font-size: 2rem;
#                                 font-weight: bold;
#                                 margin-bottom: 1rem;
#                             }}
#                             table.outer {{
#                                 width: 100%;
#                                 text-align: center;
#                                 font-family: Arial, sans-serif;
#                                 margin:0;
#                                 padding:0;
#                                 margin-bottom:10px;

#                             }}
#                             .outer tr td{{
#                             padding:0 20px;
#                             }}
#                             table.inner {{
#                                 width: 45%;
#                                 border-collapse: collapse;
#                                 text-align: center;
#                                 font-family: Arial, sans-serif;
#                                 margin: 10px;
#                                 display: inline-block;
#                                 vertical-align: top;
#                                 background-color: #fff9c7;
#                             }}
#                             .inner-tabledata{{
#                                  width:25%;
#                                 height:80px;
                                
#                             }}
#                             .inner td {{
#                                 width:25%;
#                                height:85px;
#                                 border:2px solid #d6d6d6;
#                                 padding: 10px;
#                                 color: #008000;
#                                 font-weight: bold;
#                                 font-size: 12px;
#                                 white-space: pre-line; /* Ensures new lines are respected */
#                             }}

#                             .inner .highlight {{
#                                     background-color: #ffffff;
#                                     text-align: center;
#                                     width: 100%;
#                                     height: 100%;
#                                    font-size:24px;
#                                     font-weight: 700;
#                                     color: #008000;

#                             }}

#                             .inner .highlight p{{
#                                 font-size: 16px;
#                                 font-weight: 400;
#                                 color: #008000;
#                             }}

#                             .spacer {{
#                                 width: 14%;
#                                 display: inline-block;
#                                 background-color: transparent;
#                             }}

#                             .table-div{{
#                                 border-collapse: collapse;
#                                 padding:5px 20px;
#                                 margin-bottom:2rem;
#                             }}
#                             .table-div tr {{
#                                 padding: 10px 10px;
#                             }}
#                             .table-div tr .border-right{{
#                                 border-right:1px solid #008000;
#                             }}
#                             .table-div td{{
#                                 background-color: #fff9c7;
#                                 width:50%;
#                                 padding: 10px 10px;
#                                 text-align:left;
#                             }}
#                             .table-div p {{
#                                    font-size:14px;
#                                 font-weight:400;
#                                 color: #008000;
#                             }}
#                             .inner-table tr td{{
#                                 padding:0px;
#                                 margin-bottom:0px;
#                             }}
#                             .dasa-table td{{
#                                 width:100%;
#                                 background-color:#fff;
#                                  padding:0px;
#                             }}
#                             .dasa-table td p{{
#                                 font-size:14px;
#                                 font-weight:400;
#                                 text-align:center;
#                             }}
#                             .note-text {{
#                                 color: red;
#                                 font-size:12px;
#                                 font-weight: 500;
#                                 margin: 50px auto;
#                             }}

#                             .note-text1 {{
#                                 color: red;
#                                 font-size: 14px;
#                                 font-weight: 500;
#                                 margin: 30px auto;
#                                 text-align: right;
#                             }}
                          
#                             .add-info tr {{
#                            padding:10px 20px ;
#                             }}
                        
#                             .add-info td {{
#                                 background-color: #fff9c7;
#                                 padding: 5px 5px;
#                             }}
#                           .add-info td p{{
#                             font-size: 16px;
#                             font-weight: 400;
#                             color: #008000;
#                             padding:0 20px;
#                            }}
#                            .click-here{{
#                             color:#318f9a;
#                            text-decoration: none;

#                            }}

#                             .porutham-page{{
#                                 padding: 0px 20px;
#                             }}
#                             .porutham-header {{
#                                 margin: 20px 0px;
#                             }}

#                             .porutham-header img{{
#                                 width: 130px;
#                                 height: auto;
#                             }}
#                             .porutham-header p {{
#                                 font-size:22px;
#                                 font-weight: 700;
#                                 color:#000000;
#                             }}
#                             h2.porutham-table-title{{
#                                 font-size: 24px;
#                                 font-weight: 700;
#                                 margin-bottom: 20px;
#                                 padding:0px 0px;
#                             }}
#                             porutham-table{{
#                                 border:1px solid #bcbcbc;
#                                 border-collapse: collapse;
#                                 margin-bottom: 24px;
#                             }}
#                             .porutham-table td {{
#                                 border:1px solid #bcbcbc;
#                             }}
#                             .porutham-table td p{{
#                                 color: #000;
#                                 font-size:16px;
#                                 font-weight:700;
#                                 text-align:center;
#                                 padding: 10px 0;
#                             }}
#                             .porutham-stars tr td p{{
#                                 text-align:left;
#                                 padding: 20px 20px;
#                             }}
#                             .porutham-note{{
#                                 font-size: 17px;
#                                 font-weight:400;
#                                 color: #000000;
#                                 padding:20px 0px;
#                             }}



#                            .upload-horo-bg img{{
#                                width:100%;
#                                height:auto;
#                            }}
#                             .upload-horo-image{{
#                                 margin: 10px 0px;
#                                 text-align: center;

#                             }}
#                             .upload-horo-image img{{
#                                 width:400px;
#                                 height:800px;
#                                 object-fit: contain;
#                             }}
                            

#                         </style>
#                     </head>

#                     <body>
                
               
#                                     <table class="inner">
#                                         <tr>
#                                             <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
#                                         </tr>
#                                         <tr>
#                                             <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
#                                             <td colspan="2" rowspan="2" class="highlight">Amsam
#                                             <p>vysyamala.com</p>
#                                             </td>
#                                             <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
#                                         </tr>
#                                         <tr>
#                                             <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
#                                         </tr>
#                                         <tr>
#                                             <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
#                                             <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
#                                         </tr>
#                                     </table>
                                
#                 </body></html>
#             """

#             # Generate images
#             rasi_image_path = generate_image(rasi_html_content, f"{profile_id}_rasi.png")
#             amsa_image_path = generate_image(amsa_html_content, f"{profile_id}_amsa.png")

#             # Convert file paths to URLs
#             rasi_image_url = base_url + f'horoscope/{profile_id}_rasi.png'
#             amsa_image_url = base_url + f'horoscope/{profile_id}_amsa.png'

#             return JsonResponse({
#                 "rasi_kattam_url": rasi_image_url,
#                 "amsa_kattam_url": amsa_image_url
#             })

#         except Exception as e:
#             return Response({'error': str(e)}, status=400)


def New_horoscope_color(request, user_profile_id, my_profile_id , filename="Horoscope_withbirthchart"):

                # print('1234567')
                
                # Retrieve the Horoscope object based on the provided profile_id

                attached_horoscope_enable=get_permission_limits(my_profile_id,'attached_horoscope')
                contact_enable=get_permission_limits(my_profile_id,'contact_details')
                print('attached_horoscope_enable',attached_horoscope_enable)


                horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
                education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)
                login_my  = get_object_or_404(models.Registration1, ProfileId=my_profile_id)
                horoscope_my = get_object_or_404(models.Horoscope, profile_id=my_profile_id)
                education_my = get_object_or_404(models.Edudetails, profile_id=my_profile_id)
                if all(not str(val).strip() for val in [
                    login_details.Profile_address,
                    get_district_name(login_details.Profile_district),
                    get_city_name(login_details.Profile_city),
                    login_details.Profile_pincode
                ]):
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>Not Specified</p>"""
                else:
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>{login_details.Profile_address}</p>
                        <p>{get_district_name(login_details.Profile_district)}, {get_city_name(login_details.Profile_city)}</p>
                        <p>{login_details.Profile_pincode}.</p>
                    """
                
                mobile_email_content = f"""
                        <p>Mobile: {login_details.Mobile_no or 'N/A'}</p>
                        <p>Alternate Mobile: {login_details.Profile_alternate_mobile or 'N/A'}</p>
                        <p>WhatsApp: {login_details.Profile_whatsapp or 'N/A'}</p>
                        <p>Email: {login_details.EmailId or 'N/A'}</p>
                """


                if contact_enable:
                    address_content
                    mobile_email_content
                else:
                
                        address_content = f"""<p> Get full access - upgrade your package today </p>"""
                        mobile_email_content = f"""<p> Get full access - upgrade your package today </p>"""


                try:
                    degree= get_degree_name(education_details.degree,education_details.other_degree)
                except Exception:
                    degree=None
                    
                # family details
                family_details = models.Familydetails.objects.filter(profile_id=user_profile_id)
                if family_details.exists():
                    family_detail = family_details.first()  

                    father_name = family_detail.father_name  
                    father_occupation = family_detail.father_occupation
                    family_status = family_detail.family_status
                    mother_name = family_detail.mother_name
                    mother_occupation = family_detail.mother_occupation
                    no_of_sis_married = family_detail.no_of_sis_married
                    no_of_bro_married = family_detail.no_of_bro_married

                    no_of_sister = family_detail.no_of_sister
                    no_of_brother = family_detail.no_of_brother

                    suya_gothram = family_detail.suya_gothram
                    madulamn = family_detail.madulamn if family_detail.madulamn != None else "N/A" 
                else:
                    # Handle case where no family details are found
                    father_name = father_occupation = family_status = ""
                    mother_name = mother_occupation = ""
                    no_of_sis_married = no_of_bro_married = 0

                try:
                    num_sisters_married = int(no_of_sis_married)
                except ValueError:
                    num_sisters_married = 0     
            
                try:
                    num_brothers_married = int(no_of_bro_married)
                except ValueError:
                    num_brothers_married = 0   
                if int(num_sisters_married) == 0:
                    no_of_sis_married = "No"

                if  int(num_brothers_married) == 0:
                    no_of_bro_married="No"


                if no_of_sister=="0" or no_of_sister =='':
                    no_of_sis_married='No'
                    no_of_sister ='No'

                if no_of_brother=="0" or no_of_brother =='':
                    no_of_bro_married='No'
                    no_of_brother ='No'
                
                # Education and profession details
                highest_education = education_details.highest_education
                annual_income = education_details.anual_income
                profession = education_details.profession

                # personal details
                name = login_details.Profile_name  # Assuming a Profile_name field exists
                date =  format_date_of_birth(login_details.Profile_dob)
                dob = date
                complexion = login_details.Profile_complexion
                user_profile_id = login_details.ProfileId
                height =cm_to_feet_inches(login_details.Profile_height) 

                complexion_id = login_details.Profile_complexion
                complexion = "Unknown"
                if complexion_id:
                    complexion = models.Profilecomplexion.objects.filter(complexion_id=complexion_id).values_list('complexion_desc', flat=True).first() or "Unknown"

                # Safely handle education level
                highest_education_id = education_details.highest_education
                highest_education = "Unknown"
                if highest_education_id:
                    highest_education = models.Edupref.objects.filter(RowId=highest_education_id).values_list('EducationLevel', flat=True).first() or "Unknown"


                field_ofstudy_id = education_details.field_ofstudy
                fieldof_study=" "
                if field_ofstudy_id:
                    fieldof_study = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id).values_list('field_of_study', flat=True).first() or "Unknown"
                
                about_edu=education_details.about_edu
                
                final_education = (highest_education + ' ' + fieldof_study).strip() or about_edu
                
                
                
                highest_education_id_my = education_my.highest_education
                highest_education_my="N/A"
                if highest_education_id_my:
                    highest_education_my = models.Edupref.objects.filter(RowId=highest_education_id_my).values_list('EducationLevel', flat=True).first() or "N/A"

                field_ofstudy_id_my = education_my.field_ofstudy
                fieldof_study_my=" "
                if field_ofstudy_id_my:
                    fieldof_study_my = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_my).values_list('field_of_study', flat=True).first() or "N/A"
                
                about_edu=education_my.about_edu
                
                final_education_my = (highest_education_my + ' ' + fieldof_study_my).strip() or about_edu


                annual_income = "Unknown"
                actual_income = str(education_details.actual_income).strip()
                annual_income_id = education_details.anual_income

                if not actual_income or actual_income in ["", "~"]:
                    if annual_income_id and str(annual_income_id).isdigit():
                        annual_income = models.Annualincome.objects.filter(id=int(annual_income_id)).values_list('income', flat=True).first() or "Unknown"
                else:
                    annual_income = actual_income


                profession_id = education_details.profession
                profession = "Unknown"
                if profession_id:
                    profession = models.Profespref.objects.filter(RowId=profession_id).values_list('profession', flat=True).first() or "Unknown"

                work_place=education_details.work_city
                occupation_title=''
                occupation=''

                try:
                    prof_id_int = int(profession_id)
                    if prof_id_int == 1:
                        occupation_title = 'Employment Details'
                        occupation = f"{education_details.company_name or ''} / {education_details.designation or ''}"
                    elif prof_id_int == 2:
                        occupation_title = 'Business Details'
                        occupation = f"{education_details.business_name or ''} / {education_details.nature_of_business or ''}"
                except (ValueError, TypeError):
                    occupation_title = 'Other'
                    occupation = ''
                
          

                #father_occupation_id = family_detail.father_occupation
                father_occupation = family_detail.father_occupation or "N/A"

                 #mother_occupation_id = family_detail.mother_occupation
                mother_occupation = family_detail.mother_occupation or "N/A"
                father_name = family_detail.father_name or "N/A"
                mother_name = family_detail.mother_name or "N/A"
                family_status = "Unknown"
                family_status_id = family_detail.family_status

                if family_status_id:
                    family_status = models.Familystatus.objects.filter(id=family_status_id).values_list('status', flat=True).first() or "Unknown"

                # Fetch star name from BirthStar model
                def get_model_instance(model, pk):
                    if not pk or not str(pk).isdigit():
                        return None
                    try:
                        return model.objects.get(pk=pk)
                    except model.DoesNotExist:
                        return None
                    except ValueError:
                        return None

                star_obj = get_model_instance(models.Birthstar, horoscope.birthstar_name)
                star_name = star_obj.star if star_obj else "N/A"

                star_obj_my = get_model_instance(models.Birthstar, horoscope_my.birthstar_name)
                star_name_my = star_obj_my.star if star_obj_my else "N/A"
                
                rasi_obj = get_model_instance(models.Rasi, horoscope.birth_rasi_name)
                rasi_name = get_primary_sign(str(rasi_obj.name)) if rasi_obj else "N/A"

                rasi_obj_my = get_model_instance(models.Rasi, horoscope_my.birth_rasi_name)
                rasi_name_my = get_primary_sign(str(rasi_obj_my.name)) if rasi_obj_my else "N/A"
                
                lagnam_obj = get_model_instance(models.Rasi, horoscope.lagnam_didi)
                lagnam = get_primary_sign(str(lagnam_obj.name)) if lagnam_obj else "N/A"

                time_of_birth = horoscope.time_of_birth
                place_of_birth = horoscope.place_of_birth
                didi = horoscope.didi  or "N/A"
                nalikai =  horoscope.nalikai  or "N/A"

                def format_time_am_pm(time_str):
                    if not time_str:  # Handles None or empty strings
                        return "N/A"
                    try:
                        time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                        return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
                    except ValueError:
                        return str(time_str)

                birth_time=format_time_am_pm(time_of_birth)
                age = calculate_age(login_details.Profile_dob)   or "N/A"


                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }

                # Define a default placeholder for empty values
                default_placeholder = '-'

                def parse_data(data):
                    # Clean up and split data
                    items = data.strip('{}').split(', ')
                    parsed_items = []
                    for item in items:
                        parts = item.split(':')
                        if len(parts) > 1:
                            values = parts[-1].strip()
                            # Handle multiple values separated by comma
                            if ',' in values:
                                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                            else:
                                values = planet_mapping.get(values, default_placeholder)
                        else:
                            values = default_placeholder
                        parsed_items.append(values)
                    return parsed_items

                # Clean up and parse the rasi_kattam and amsa_kattam data
                if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                    rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                    amsa_kattam_data = parse_data(horoscope.amsa_kattam)

                else:
                    rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                    amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')


                # Ensure that we have exactly 12 values for the grid
                rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
                amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))

                if attached_horoscope_enable:


                    horoscope_data = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
        
                    if horoscope_data.horoscope_file_admin:
                        horoscope_image_url = horoscope_data.horoscope_file_admin.url
                
                        if horoscope_image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            horoscope_content = f'<img src="{horoscope_image_url}" alt="Horoscope Image" style="max-width: 200%; height: auto;">'
                        else:
                            horoscope_content = f'<a href="{horoscope_image_url}" download>Download Horoscope File</a>'
                    else:
                        horoscope_content = '<p>No horoscope uploaded</p>'
                else :
                    
                     horoscope_content = '<p>Get full access - upgrade your package today </p>'

                # Get matching stars data
                birth_star_id = horoscope.birthstar_name
                birth_rasi_id = horoscope.birth_rasi_name
                gender = login_details.Gender
                porutham_data = fetch_porutham_details(user_profile_id, my_profile_id)
            
                horo_hint = horoscope.horoscope_hints or "N/A"
                def is_grid_data_empty(grid_data):
                    return all(cell == default_placeholder for cell in grid_data)

                hide_charts = is_grid_data_empty(rasi_kattam_data) and is_grid_data_empty(amsa_kattam_data)
            
                # Prepare the Porutham sections for the PDF
                def format_star_names(poruthams):
                    return ', '.join([f"{item['matching_starname']} - {item['matching_rasiname'].split('/')[0]}" for item in poruthams])

                profile_url = f"https://polite-pond-0783ff91e.1.azurestaticapps.net/ProfileDetails?id={user_profile_id}&rasi={horoscope.birth_rasi_name}"

                dasa_day = dasa_month = dasa_year = 0
                # Try to split if format is correct
                dasa_balance_str=dasa_format_date(horoscope.dasa_balance)
                match = re.match(r"(\d+)\s+Years,\s+(\d+)\s+Months,\s+(\d+)\s+Days", dasa_balance_str or "")
                if match:
                    dasa_year, dasa_month, dasa_day = match.groups()
                dasa_name = get_dasa_name(horoscope.dasa_name)
                image_status = models.Image_Upload.get_image_status(profile_id=user_profile_id)

                porutham_rows = ""
                for idx, porutham in enumerate(porutham_data['porutham_results']):
                    extra_td = ""
                    if idx == 0:
                        extra_td = (
                            f"<td rowspan='{len(porutham_data['porutham_results'])}'>"
                            f"<p class='matching-score'>{porutham_data['matching_score']}</p>"
                            f"<p style='font-weight:500; font-size:13px;'>Please check with your astrologer for detailed compatibility.</p>"
                            f"<p style='margin-top:10px;'>Jai Vasavi</p>"
                            f"</td>"
                        )
                    porutham_rows += (
                        f"<tr>"
                        f"<td>{porutham['porutham_name']}</td>"
                        f"<td><span style='color: {'green' if porutham['status'].startswith('YES') else 'red'};'>{porutham['status']}</span></td>"
                        f"{extra_td}"
                        f"</tr>")

                charts_html = ""



                if not hide_charts:

                    charts_html = f"""
                    <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td class="spacer">
                                <table class="table-div dasa-table">
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Name</strong></p>
                                            <p>{dasa_name}</p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Balance</strong></p>
                                            <p>{dasa_year} Years</p>
                                            <p>{dasa_month} Months</p>
                                            <p>{dasa_day} Days</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Amsam
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                     <div>
                <table class="add-info"> 
                    <tr>
                        <td>
                            <p><b>Horoscope Hints: </b>{horo_hint}</p>
                        </td>
                    </tr>
                    <tr>
                    <td>
                    <table>
                    """  
                html_content = rf"""
                <html>
                    <head>
                        <style>
                        @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: auto;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                            .score-box {{
                                float: right;
                                text-align: center;
                                background-color: #fffbcc;
                                border: 1px solid #d4d4d4;
                                width:100%;
                               margin-bottom:1.5rem !important;
                            }}

                             .score-box p {{
                                font-size: 2rem;
                                font-weight: bold;
                                padding: 10px 30px 10px !important;
                                color: #333;
                                margin: 0px auto !important;
                                padding-top:1.3rem !important;
                            }}

                            p {{
                                font-size: 10px;
                                margin: 5px 0;
                                padding: 0;
                                color: #333;
                            }}

                            .details-div {{
                                margin-bottom: 20px;
                            }}

                            .details-section p {{
                                margin: 2px 0;
                            }}

                            .details-section td {{
                                  border: none;
                            }}
                             .personal-detail-header{{
                                font-size: 2rem;
                                font-weight: bold;
                                margin-bottom: 1rem;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin:0;
                                padding:0;
                                margin-bottom:10px;

                            }}
                            .outer tr td{{
                            padding:0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff9c7;
                            }}
                            .inner-tabledata{{
                                 width:25%;
                                height:80px;
                                
                            }}
                            .inner td {{
                                width:25%;
                                height:80px;
                                border:2px solid #d6d6d6;
                                padding: 10px;
                                color: #008000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line; /* Ensures new lines are respected */
                            }}

                            .inner-table tr td p{{
                                white-space: pre-line;
                               word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow:hidden;
                                
                            }}

                            .inner .highlight {{
                                    background-color: #ffffff;
                                    text-align: center;
                                    width: 100%;
                                    height: 100%;
                                   font-size:24px;
                                    font-weight: 700;
                                    color: #008000;

                            }}

                            .inner .highlight p{{
                                font-size: 16px;
                                font-weight: 400;
                                color: #008000;
                            }}

                            .spacer {{
                                width: 14%;
                                display: inline-block;
                                background-color: transparent;
                            }}

                            .table-div{{
                                border-collapse: collapse;
                                padding:5px 20px;
                                margin-bottom:1rem;
                            }}
                            .table-div tr {{
                                padding: 10px 10px;
                            }}
                            .table-div tr .border-right{{
                                border-right:1px solid #008000;
                            }}
                            .table-div td{{
                                background-color: #fff9c7;
                                width:50%;
                                padding: 10px 10px;
                                text-align:left;
                            }}
                            .table-div p {{
                                   font-size:14px;
                                font-weight:400;
                                color: #008000;
                            }}
                            .inner-table tr td{{
                                padding:0px;
                                margin-bottom:0px;
                            }}
                            .dasa-table td{{
                                width:100%;
                                background-color:#fff;
                                 padding:0px;
                            }}
                            .dasa-table td p{{
                                font-size:14px;
                                font-weight:400;
                                text-align:center;
                            }}
                            .note-text {{
                                color: red;
                                font-size:12px;
                                font-weight: 500;
                                margin: 50px auto;
                            }}

                            .note-text1 {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 30px auto;
                                text-align: right;
                            }}
 
                            .add-info tr {{
                           padding:5px 20px ;
                            }}
                        
                            .add-info td {{
                                background-color: #fff9c7;
                                padding: 5px 5px;
                            }}
                          .add-info td p{{
                            font-size: 14px;
                            font-weight: 400;
                            color: #008000;
                            padding:0 10px;
                           }}
                           .click-here{{
                            color:#318f9a;
                           text-decoration: none;

                           }}

                            .porutham-page{{
                                padding: 0px 20px;
                            }}
                            .porutham-header {{
                                margin: 20px 0px;
                            }}

                            .porutham-header img{{
                                width: 130px;
                                height: auto;
                            }}
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}
                           
                            .upload-horo-bg img{{
                               width:100%;
                               height:auto;
                           }}
                            .upload-horo-image{{
                                margin: 10px 0px;
                                text-align: center;
                                height: 800px;
                           
                            }}
                            .upload-horo-image tr{{
                                height: 800px;
                            }}
                            .upload-horo-image tr td{{
                                height: 800px;
                            }}
                            .upload-horo-image img{{
                                width:400px;
                                height:800px;
                                object-fit: cover;
                             
                            }}
                            

                            .compatibility-page-wrapper {{
                                 margin:0px auto;
                                text-align:center;
                                width:100%;
                            }}
                            .compatibility-page-wrapper tr {{
                                margin: auto;
                                text-align:center;
                                width:100%;
                            }}
                            
                            .compatibility-page-wrapper tr td{{
                                background-color: #ffd966;
                                width:100%;
                                text-align:center;
                                margin: auto;
                               
                            }}

                            .report-title {{
                                background-color: #ffd966;
                                color: #538135;
                                font-weight: bold;
                                text-align: center;
                                padding: 10px 0px 0px;
                                font-size: 16px;
                            }}
                             .report-table {{
                                width: 100%;
                                border-collapse: collapse;
                                background-color: #538135;
                                
                            }}
                             .report-table  tr {{
                                background-color: #538135;

                             }}
                             .report-table  tr  td{{
                                background-color: #538135;
                                color:#ffd966;
                                border:1px solid #ffd966;

                             }}
                             .report-table  tr  td p{{
                                background-color: #538135;
                                color:#ffd966;
                                font-size:14px;
                                width:100%;

                             }}
                             .profile-name{{
                                color:#ffd966;
                             }}
                            .header-cell {{
                                background-color: #538135;
                                color: #fff;
                                font-weight: bold;
                                text-align: center;
                                padding: 6px;
                            }}
                            .sub-header {{
                                background-color:#538135;
                                color: #000;
                                text-align: center;
                                padding: 4px;
                            }}
                            .profile-addtional-info{{
                                width: 100%;
                                background-color: #ffd966;
                                border:1px solid #538135;

                            }}
                              .profile-addtional-info  tr {{
                                background-color: #ffd966;
                                border:none;

                             }}
                            
                             .profile-addtional-info  tr  td p{{
                                background-color: #ffd966;
                                color:#538135;
                                font-size:14px;
                                width:100%;

                             }}
   .data-row {{
                                padding: 2px 0px;
                            }}
                            .data-label {{
                                font-weight: bold;
                                width: 40%;
                                padding: 4px;
                            }}
                            .data-value {{
                                padding: 4px;
                            }}


                             .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}

                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            .porutham-table{{
                                border:1px solid #538135;
                                border-collapse: collapse;
                                margin-bottom: 10px;
                            }}
                            .porutham-table th {{
                                padding: 5px 0;
                                  background-color: #538135;
                                  color:#f4c542;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0 0 0;
                            }}
                            .porutham-table td {{
                                border:1px solid #538135;
                                color: #538135;
                                font-size:15px;
                                font-weight:400;
                                text-align:center;
                                padding: 8px 5px;
                            }}
                            .porutham-table tr td p{{
                                color: #538135;
                                font-size:15px;
                                font-weight:700;
                                text-align:center;
                                padding: 5px 0;
                            }}
                          
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}


                            .matching-score{{
                                font-size:30px ;
                                font-weight:700;
                            }}
                        

                        </style>
                    </head>

                    <body>

                        <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>
                        
                    <div class="details-section">
                    
                <table class="table-div">
                            <tr>
                                <td class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Name</strong></p></td>
                                        <td><p><strong>{name}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>DOB / POB</p></td>
                                        <td><p>{dob} / {place_of_birth}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Complexion</p></td>
                                        <td><p>{complexion}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Education</p></td>
                                        <td><p>{final_education}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Degree</p></td>
                                        <td><p>{degree}</p></td>
                                    </tr>
                                    </table>
                                    
                                </td>
                                
                                <td>
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Vysyamala Id :</strong></p></td>
                                        <td><p><strong>{user_profile_id}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Height / Photos </p></td>
                                        <td><p>{height} / {image_status}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Annual Income </p></td>
                                        <td><p>{annual_income}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Profession / Place of stay </p></td>
                                        <td><p>{profession} / {work_place}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>{occupation_title}</p></td>
                                        <td><p>{occupation}</p></td>
                                    </tr>
                                </table>
                                </td>
                            </tr>
                        </table>

                        


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td><p><strong>Father Name</strong></p></td>
                                            <td><p><strong>{father_name}</strong></p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Father Occupation</p></td>
                                            <td><p>{father_occupation}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Family Status</p></td>
                                            <td><p>{family_status}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Brothers/Married</p></td>
                                            <td><p>{no_of_brother}/{no_of_bro_married}</p></td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Mother Name </strong> </p>
                                                <p>Mother Occupation </p>
                                                <p>Sisters/Married </p>
                                            </td>
                                            <td>
                                                <p><strong>{mother_name}</strong></p>
                                                <p>{mother_occupation}</p>
                                                <p>{no_of_sister}/{no_of_sis_married}</p>
                                            </td>
                                        </tr>
                                    </table>
                               

                                </td>
                            </tr>
                        </table>
                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Star/Rasi </strong> </p>
                                                <p>Lagnam/Didi </p>
                                                <p>Nalikai </p>
                                            </td>
                                            <td>
                                                <p style="font-size:12px"><strong>{star_name}, {rasi_name}</strong></p>
                                                <p>{lagnam}/{didi}</p>
                                                <p>{nalikai}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Surya Gothram : </strong></p>
                                                <p>Madhulam </p>
                                                <p>Birth Time </p>
                                            </td>
                                            <td>
                                                <p><strong>{suya_gothram}</strong></p>
                                                <p>{madulamn}</p>
                                                <p>{birth_time}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>
                            </tr>
                        </table>
                    
                    </div>
                    
                    {charts_html}   


               
                        <tr>
                            <td>
                               {address_content}
                            </td>
                            <td>
                                {mobile_email_content}
                            </td>
                        </tr>
                    </table>
                    </td>
                    </tr>
                    <tr>
                        <td>
                            <p>Note: Please verify this profile yourself. No hidden charges or commissions if marriage is fixed through Vysyamala. For more details of this profile: <a href="{profile_url}" target="_blank" class="click-here">click here</a></p>
                        </td>
                    </tr>
                </table>
                </div>


                

              
                <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
            <h2 class="report-title">Marriage Compatibility Report</h2>
        
            <table class="report-table" border="0">
                <tr>
                <td class="header-cell">
                    <p class="profile-name">{login_my.Profile_name} - {login_my.ProfileId}</p>
                </td>
                <td class="header-cell">
                    <p class="profile-name"> {login_details.Profile_name} - {login_details.ProfileId}</p>   
                 </td>
                </tr>
                <tr>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_name_my} - {star_name_my}</p>
                </td>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_name} - {star_name}</p>
                </td>
                </tr>
            </table>
            <br>
        
            <table class="profile-addtional-info" >
                <tr>
                <td class="data-row">
                     <p> Place of Birth : {horoscope_my.place_of_birth}</p>
                </td>
                <td class="data-row">
                    <p> Place of Birth : {horoscope.place_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Time of Birth : {horoscope_my.time_of_birth}</p>
                </td>
                <td class="data-row">
                    <p>  Time of Birth : {horoscope.time_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Date Of Birth : {login_my.Profile_dob}</p>
                </td>
                <td class="data-row">
                    <p> Date Of Birth : {login_details.Profile_dob}</p>
                </td>
                </tr>
            </table>
            <br>
        
              <table class="profile-addtional-info">
                <tr>
                <td class="data-row">
                    <p> Height : {cm_to_feet_inches(login_my.Profile_height)}</p>
                </td>
                <td class="data-row">
                        <p> Height : {cm_to_feet_inches(login_details.Profile_height)}</p>
        
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> {final_education_my}</p>
                </td>
                <td class="data-row">
                    <p> {final_education}</p>
                </td>
                </tr>
            </table>
                
            <h2 class="report-title" >Nakshatra Porutham & Rasi Porutham</h2>
           <table class="porutham-table">
                <tr>
                    <th>Porutham Name</th>
                    <th>Status</th>
                    <th>Matching Score</th>
                </tr>
                 {porutham_rows}
                 </table>        
              <table class="profile-addtional-info">
                <tr >
                <td class="data-row"  style="width:100%;">
                <p>
                Our best wishes for finding your soulmate in Vyasyamala soon. Please inform Vyasyamala if your marriage is fixed. Share your engagement photo and receive a surprise gift. No commissions / hidden charges. Jai Vasavi!
                </p>
                </td>
                </tr>
                </table>
                <br>
            </td>
            </tr>
            </table>

                <table class="porutham-page">
                <tr>
                <td>
                <br>
               


                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" >
                </div>

                <table class="upload-horo-image">
                <tr>
                <td>
                         {horoscope_content}
 
                </td>
                </tr>
                </table>
                
                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/uploadHoroFooter.png" >
                </div>

                    </body>
                </html>
                """
                
                # Create a Django response object and specify content_type as pdf
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f' inline; filename="{filename}"'


                # Create the PDF using xhtml2pdf
                pisa_status = pisa.CreatePDF(html_content, dest=response)

                # If there's an error, log it and return an HTML response with an error message
                if pisa_status.err:
                    logger.error(f"PDF generation error: {pisa_status.err}")
                    return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

                return response

def New_horoscope_black(request, user_profile_id, my_profile_id ,  filename="Horoscope_withbirthchart"):

                #print('1234567')
  
                # Retrieve the Horoscope object based on the provided profile_id
                horoscope = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                login_details = get_object_or_404(models.Registration1, ProfileId=user_profile_id)
                education_details = get_object_or_404(models.Edudetails, profile_id=user_profile_id)
                login_my  = get_object_or_404(models.Registration1, ProfileId=my_profile_id)
                horoscope_my = get_object_or_404(models.Horoscope, profile_id=my_profile_id)
                education_my = get_object_or_404(models.Edudetails, profile_id=my_profile_id)

                attached_horoscope_enable=get_permission_limits(my_profile_id,'attached_horoscope')
                contact_enable=get_permission_limits(my_profile_id,'contact_details')
                print("attached_horoscope_enable",attached_horoscope_enable)

                if all(not str(val).strip() for val in [
                    login_details.Profile_address,
                    get_district_name(login_details.Profile_district),
                    get_city_name(login_details.Profile_city),
                    login_details.Profile_pincode
                ]):
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>N/A</p>"""
                else:
                    address_content = f"""
                        <p><b>Address:</b></p>
                        <p>{login_details.Profile_address}</p>
                        <p>{get_district_name(login_details.Profile_district)}, {get_city_name(login_details.Profile_city)}</p>
                        <p>{login_details.Profile_pincode}.</p>
                    """
                
                mobile_email_content = f"""
                        <p>Mobile: {login_details.Mobile_no or 'N/A'}</p>
                        <p>Alternate Mobile: {login_details.Profile_alternate_mobile or 'N/A'}</p>
                        <p>WhatsApp: {login_details.Profile_whatsapp or 'N/A'}</p>
                        <p>Email: {login_details.EmailId or 'N/A'}</p>
                """

                try:
                    degree= get_degree_name(education_details.degree,education_details.other_degree)
                except Exception:
                    degree=None

                if contact_enable:
                    address_content
                    mobile_email_content
                else:
                    address_content = f""" Get full access - upgrade your package today """
                    mobile_email_content = f""" Get full access - upgrade your package today """
                
                # family details
                family_details = models.Familydetails.objects.filter(profile_id=user_profile_id)
                if family_details.exists():
                    family_detail = family_details.first()  

                    father_name = family_detail.father_name  
                    father_occupation = family_detail.father_occupation
                    family_status = family_detail.family_status
                    mother_name = family_detail.mother_name
                    mother_occupation = family_detail.mother_occupation
                    no_of_sis_married = family_detail.no_of_sis_married
                    no_of_bro_married = family_detail.no_of_bro_married

                    no_of_sister = family_detail.no_of_sister
                    no_of_brother = family_detail.no_of_brother

                    suya_gothram = family_detail.suya_gothram
                    madulamn = family_detail.madulamn if family_detail.madulamn != None else "N/A" 
                else:
                    # Handle case where no family details are found
                    father_name = father_occupation = family_status = ""
                    mother_name = mother_occupation = ""
                    no_of_sis_married = no_of_bro_married = 0

                try:
                    num_sisters_married = int(no_of_sis_married)
                except ValueError:
                    num_sisters_married = 0     
            
                try:
                    num_brothers_married = int(no_of_bro_married)
                except ValueError:
                    num_brothers_married = 0   
                if int(num_sisters_married) == 0:
                    no_of_sis_married = "No"

                if  int(num_brothers_married) == 0:
                    no_of_bro_married="No"
                

                if no_of_sister=="0" or no_of_sister =='':
                    no_of_sis_married='No'
                    no_of_sister='No'

                if no_of_brother=="0" or no_of_brother =='':
                    no_of_bro_married='No'
                    no_of_brother ='No'
                # Education and profession details
                highest_education = education_details.highest_education
                annual_income = education_details.anual_income
                profession = education_details.profession

                # personal details
                name = login_details.Profile_name  # Assuming a Profile_name field exists
                date =  format_date_of_birth(login_details.Profile_dob)
                dob = date
                complexion = login_details.Profile_complexion
                user_profile_id = login_details.ProfileId
                height = cm_to_feet_inches(login_details.Profile_height)

                complexion_id = login_details.Profile_complexion
                complexion="N/A"
                if complexion_id:
                    complexion = models.Profilecomplexion.objects.filter(complexion_id=complexion_id).values_list('complexion_desc', flat=True).first() or "N/A"

                highest_education_id = education_details.highest_education
                highest_education="N/A"
                if highest_education_id:
                    highest_education = models.Edupref.objects.filter(RowId=highest_education_id).values_list('EducationLevel', flat=True).first() or "N/A"

                field_ofstudy_id = education_details.field_ofstudy
                fieldof_study=" "
                if field_ofstudy_id:
                    fieldof_study = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id).values_list('field_of_study', flat=True).first() or "N/A"
                
                about_edu=education_details.about_edu
                
                final_education = (highest_education + ' ' + fieldof_study).strip() or about_edu
                
                
                
                highest_education_id_my = education_my.highest_education
                highest_education_my="N/A"
                if highest_education_id_my:
                    highest_education_my = models.Edupref.objects.filter(RowId=highest_education_id_my).values_list('EducationLevel', flat=True).first() or "N/A"

                field_ofstudy_id_my = education_my.field_ofstudy
                fieldof_study_my=" "
                if field_ofstudy_id_my:
                    fieldof_study_my = models.Profilefieldstudy.objects.filter(id=field_ofstudy_id_my).values_list('field_of_study', flat=True).first() or "N/A"
                
                about_edu=education_my.about_edu
                
                final_education_my = (highest_education_my + ' ' + fieldof_study_my).strip() or about_edu



                annual_income_id = education_details.anual_income
                annual_income = "N/A"
                
                if not education_details.actual_income or str(education_details.actual_income).strip() in ["", "~"]:
                    annual_income_id = education_details.anual_income
                    if annual_income_id:
                        annual_income = models.Annualincome.objects.filter(id=annual_income_id).values_list('income', flat=True).first() or "Unknown"

                else:
                    annual_income = education_details.actual_income
                
                profession_id = education_details.profession
                profession="N/A"
                if profession_id:
                    profession = models.Profespref.objects.filter(RowId=profession_id).values_list('profession', flat=True).first() or "Unknown"

                work_place=education_details.work_city
                occupation_title=''
                occupation=''

                try:
                    prof_id_int = int(profession_id)
                    if prof_id_int == 1:
                        occupation_title = 'Employment Details'
                        occupation = f"{education_details.company_name or 'N/A'} / {education_details.designation or 'N/A'}"
                    elif prof_id_int == 2:
                        occupation_title = 'Business Details'
                        occupation = f"{education_details.business_name or 'N/A'} / {education_details.nature_of_business or 'N/A'}"
                except (ValueError, TypeError):
                    occupation_title = 'Other'
                    occupation = ''
                
               
            
                dasa_day = dasa_month = dasa_year = 0
                # Try to split if format is correct
                dasa_balance_str=dasa_format_date(horoscope.dasa_balance)
                match = re.match(r"(\d+)\s+Years,\s+(\d+)\s+Months,\s+(\d+)\s+Days", dasa_balance_str or "")
                if match:
                    dasa_year, dasa_month, dasa_day = match.groups()
                
                #father_occupation_id = family_detail.father_occupation
                father_occupation = family_detail.father_occupation or "N/A"

                 #mother_occupation_id = family_detail.mother_occupation
                mother_occupation = family_detail.mother_occupation or "N/A"
                father_name = family_detail.father_name or "N/A"
                mother_name = family_detail.mother_name or "N/A"
                family_status_id = family_detail.family_status 
                family_status="N/A"
                if family_status_id:
                    family_status = models.Familystatus.objects.filter(id=family_status_id).values_list('status', flat=True).first() or "Unknown"

                # Fetch star name from BirthStar model
                try:
                    star = models.Birthstar.objects.get(pk=horoscope.birthstar_name)
                    star_name = star.star  # Or use star.tamil_series, telugu_series, etc. as per your requirement
                except models.Birthstar.DoesNotExist:
                    star_name = "N/A"

                try:
                    star_my = models.Birthstar.objects.get(pk=horoscope_my.birthstar_name)
                    star_name_my = star_my.star  # Or use star.tamil_series, telugu_series, etc. as per your requirement
                except models.Birthstar.DoesNotExist:
                    star_name_my = "N/A"
                # Fetch rasi name from Rasi model
                try:
                    if horoscope.birth_rasi_name:
                        rasi = models.Rasi.objects.get(pk=horoscope.birth_rasi_name)
                        rasi_name = get_primary_sign(str(rasi.name))  # Or use rasi.tamil_series, telugu_series, etc. as per your requirement
                    else:
                        rasi_name="N/A"
                except models.Rasi.DoesNotExist:
                    rasi_name = "N/As"
                    
                try:
                    if horoscope_my.birth_rasi_name:
                        rasi_my = models.Rasi.objects.get(pk=horoscope_my.birth_rasi_name)
                        rasi_name_my = get_primary_sign(str(rasi_my.name))  # Or use rasi.tamil_series, telugu_series, etc. as per your requirement
                    else:
                        rasi_name_my="N/A"
                except models.Rasi.DoesNotExist:
                    rasi_name_my = "N/A"
                time_of_birth = horoscope.time_of_birth
                place_of_birth = horoscope.place_of_birth
            
                def format_time_am_pm(time_str):
                    if not time_str:  # Handles None or empty strings
                        return "N/A"
                    try:
                        time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
                        return time_obj.strftime("%I:%M %p")  # 12-hour format with AM/PM
                    except ValueError:
                        return str(time_str)
                birth_time=format_time_am_pm(time_of_birth)
                
                try:
                    if horoscope.lagnam_didi and str(horoscope.lagnam_didi).isdigit() and int(horoscope.lagnam_didi) > 0:
                        lagnam = models.Rasi.objects.get(pk=horoscope.lagnam_didi)
                        lagnam = get_primary_sign(str(lagnam.name))
                    else:
                        lagnam="Unknown"
                except models.Rasi.DoesNotExist:
                    lagnam = "Unknown"

                didi = horoscope.didi or "N/A"
                nalikai =  horoscope.nalikai  or "N/A"

                age = calculate_age(login_details.Profile_dob)  or "N/A" 

                # Planet mapping dictionary
                # planet_mapping = {
                #     "1": "Sun",
                #     "2": "Moo",
                #     "3": "Mar",
                #     "4": "Mer",
                #     "5": "Jup",
                #     "6": "Ven",
                #     "7": "Sat",
                #     "8": "Rahu",
                #     "9": "Kethu",
                #     "10": "Lagnam",
                # }

                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Rahu",
                    "4": "Kethu",
                    "5": "Mar",
                    "6": "Ven",
                    "7": "Jup",
                    "8": "Mer",
                    "9": "Sat",
                    "10": "Lagnam",
                }

                # Define a default placeholder for empty values
                default_placeholder = '-'

                def parse_data(data):
                    # Clean up and split data
                    items = data.strip('{}').split(', ')
                    parsed_items = []
                    for item in items:
                        parts = item.split(':')
                        if len(parts) > 1:
                            values = parts[-1].strip()
                            # Handle multiple values separated by comma
                            if ',' in values:
                                values = '/'.join(planet_mapping.get(v.strip(), default_placeholder) for v in values.split(','))
                            else:
                                values = planet_mapping.get(values, default_placeholder)
                        else:
                            values = default_placeholder
                        parsed_items.append(values)
                    return parsed_items

                # Clean up and parse the rasi_kattam and amsa_kattam data
                if horoscope.rasi_kattam or  horoscope.amsa_kattam:
                    rasi_kattam_data = parse_data(horoscope.rasi_kattam)
                    amsa_kattam_data = parse_data(horoscope.amsa_kattam)

                else:
                    rasi_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')
                    amsa_kattam_data=parse_data('{Grid 1: empty, Grid 2: empty, Grid 3: empty, Grid 4: empty, Grid 5: empty, Grid 6: empty, Grid 7: empty, Grid 8: empty, Grid 9: empty, Grid 10: empty, Grid 11: empty, Grid 12: empty}')

                # Ensure that we have exactly 12 values for the grid
                rasi_kattam_data.extend([default_placeholder] * (12 - len(rasi_kattam_data)))
                amsa_kattam_data.extend([default_placeholder] * (12 - len(amsa_kattam_data)))

                
                horoscope_data = get_object_or_404(models.Horoscope, profile_id=user_profile_id)
                
                horo_hint = horoscope_data.horoscope_hints or "N/A"
                if attached_horoscope_enable:
                    if horoscope_data.horoscope_file_admin:
                        horoscope_image_url = horoscope_data.horoscope_file_admin.url

                        # print(horoscope_image_url)

                        if horoscope_image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            horoscope_content = f'<img src="{horoscope_image_url}" alt="Horoscope Image" style="max-width: 200%; height: auto;">'
                        else:
                            horoscope_content = f'<a href="{horoscope_image_url}" download>Download Horoscope File</a>'
                    else:
                        horoscope_content = '<p>No horoscope uploaded</p>'
                else :
                    
                     horoscope_content = '<h2>Get full access - upgrade your package today </h2>'

                # Get matching stars data
                birth_star_id = horoscope.birthstar_name
                birth_rasi_id = horoscope.birth_rasi_name
                gender = login_details.Gender
                porutham_data = fetch_porutham_details(my_profile_id,user_profile_id)
                # Prepare the Porutham sections for the PDF
                def format_star_names(poruthams):
                    return ', '.join([f"{item['matching_starname']} - {item['matching_rasiname'].split('/')[0]}" for item in poruthams])
                
                profile_url = f"https://polite-pond-0783ff91e.1.azurestaticapps.net/ProfileDetails?id={user_profile_id}&rasi={horoscope.birth_rasi_name}"

                def is_grid_data_empty(grid_data):
                    return all(cell == default_placeholder for cell in grid_data)

                hide_charts = is_grid_data_empty(rasi_kattam_data) and is_grid_data_empty(amsa_kattam_data)
                dasa_name = get_dasa_name(horoscope_data.dasa_name)
                    # Dynamic HTML content including Rasi and Amsam charts
                image_status = models.Image_Upload.get_image_status(profile_id=user_profile_id)

                porutham_rows = ""
                for idx, porutham in enumerate(porutham_data['porutham_results']):
                    extra_td = ""
                    if idx == 0:
                        extra_td = (
                            f"<td rowspan='{len(porutham_data['porutham_results'])}'>"
                            f"<p class='matching-score'>{porutham_data['matching_score']}</p>"
                            f"<p style='font-weight:500; font-size:13px;'>Please check with your astrologer for detailed compatibility.</p>"
                            f"<p style='margin-top:10px;'>Jai Vasavi</p>"
                            f"</td>"
                        )
                    porutham_rows += (
                        f"<tr>"
                        f"<td>{porutham['porutham_name']}</td>"
                        f"<td><span style='color: {'#000000' if porutham['status'].startswith('YES') else '#000000'};'>{porutham['status']}</span></td>"
                        f"{extra_td}"
                        f"</tr>")

                charts_html = ""



                if not hide_charts:

                    charts_html = f"""
                    <table class="outer">
                        <tr>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[0].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[1].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[2].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">
                                            Rasi
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td class="inner-tabledata">{rasi_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[10].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td class="inner-tabledata">{rasi_kattam_data[9].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[8].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[7].replace('/', '<br>')}</td>
                                        <td class="inner-tabledata">{rasi_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                            <td class="spacer">
                                <table class="table-div dasa-table">
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Name</strong></p>
                                            <p>{dasa_name}</p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <p><strong>Dasa Balance</strong></p>
                                            <p>{dasa_year} Years</p>
                                            <p>{dasa_month} Months</p>
                                            <p>{dasa_day} Days</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                            <td>
                                <table class="inner">
                                    <tr>
                                        <td>{amsa_kattam_data[0].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[1].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[2].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[3].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[11].replace('/', '<br>')}</td>
                                        <td colspan="2" rowspan="2" class="highlight">Amsam
                                            <p>vysyamala.com</p>
                                        </td>
                                        <td>{amsa_kattam_data[4].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[10].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[5].replace('/', '<br>')}</td>
                                    </tr>
                                    <tr>
                                        <td>{amsa_kattam_data[9].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[8].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[7].replace('/', '<br>')}</td>
                                        <td>{amsa_kattam_data[6].replace('/', '<br>')}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    
                <div>
                <table class="add-info"> 
                    <tr>
                        <td>
                            <p><b>Horoscope Hints: </b>{horo_hint}</p>
                       <hr class="divider">

                        </td>
                    </tr>
                    <tr>
                    <td>
                    <table>
                    """
                html_content = rf"""
                <html>
                    <head>
                        <style>
                        @page {{
                                size: A4;
                                margin: 0;
                            }}
                            body {{
                                background-color: #ffffff;
                            }}

                            .header {{
                                margin-bottom: 10px;
                            }}

                            .header-left img {{
                                width: 100%;
                                height: 300px;
                            }}
                            .logo-text{{
                                font-size: 18px;
                                font-weight: 400;
                                color:  #fbf274;
                            }}
                            .header-left {{
                                width: 100%;
                            }}
                            
                            .header-left p{{
                                font-size: 18px;
                                font-weight: 400;
                                color: #ffffff;
                            }}
                            .header-info p {{
                                color:#fbf274;
                                font-size:16px;
                                padding-bottom:5px;
                                text-align:center;
                            }}
                            .score-box {{
                                float: right;
                                text-align: center;
                                background-color: #fffbcc;
                                border: 1px solid #d4d4d4;
                                width:100%;
                               margin-bottom:1.5rem !important;
                            }}

                             .score-box p {{
                                font-size: 2rem;
                                font-weight: bold;
                                padding: 10px 30px 10px !important;
                                color: #333;
                                margin: 0px auto !important;
                                padding-top:1.3rem !important;
                            }}

                            p {{
                                font-size: 10px;
                                margin: 5px 0;
                                padding: 0;
                                color: #333;
                            }}

                            .details-div {{
                                margin-bottom: 20px;
                            }}

                            .details-section p {{
                                margin: 2px 0;
                            }}

                            .details-section td {{
                                  border: none;
                            }}
                             .personal-detail-header{{
                                font-size: 2rem;
                                font-weight: bold;
                                margin-bottom: 1rem;
                            }}
                            table.outer {{
                                width: 100%;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin:0;
                                padding:0;
                            margin-bottom:10px;


                            }}
                            .outer tr td{{
                            padding:0 20px;
                            }}
                            table.inner {{
                                width: 45%;
                                border-collapse: collapse;
                                text-align: center;
                                font-family: Arial, sans-serif;
                                margin: 10px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #fff;
                            }}
                            .inner-tabledata{{
                                 width:25%;
                                height:80px;
                                
                            }}
                            .inner td {{
                                width:25%;
                                height:60px;
                                border:2px solid #d6d6d6;
                                padding: 10px;
                                color: #000000;
                                font-weight: bold;
                                font-size: 12px;
                                white-space: pre-line; /* Ensures new lines are respected */
                            }}

                            .inner .highlight {{
                                    background-color: #ffffff;
                                    text-align: center;
                                    width: 100%;
                                    height: 100%;
                                    font-size:24px;
                                    font-weight: 700;
                                    color: #000000;

                            }}
                            .inner-table tr td p{{
                                white-space: pre-line;
                               word-break: break-all;
                                word-wrap: normal;
                                word-wrap: break-word;
                                overflow:hidden;
                                
                            }}
                            .inner .highlight p{{
                                font-size: 14px;
                                font-weight: 400;
                                color: #000;
                            }}

                           
                            .table-div{{
                                padding: 5px 10px;
                                border-collapse: collapse;
                                padding:5px 20px;
                                margin-bottom:15px;
                            }}
                            .table-div tr {{
                                padding: 0px 10px;
                            }}
                            .table-div tr .border-right{{
                                border-right:1px solid #000000;
                            }}
                            .table-div td{{
                                background-color: #ffffff;
                                width:50%;
                                padding: 10x  20px;
                                text-align:left;
                            }}
                            .table-div p {{
                                   font-size:14px;
                                font-weight:400;
                                color: #000;
                            }}
                            .divider{{
                            margin:10px 0 !important;
                            }}
                            .inner-table tr td{{
                                padding:0px;
                                margin-bottom:0px;
                            }}
                             .spacer {{
                                width: 14%;
                                display: inline-block;
                                background-color: transparent;
                                padding:0px 0px !important;
                                margin:0px 0px !important;
                            }}
                            .dasa-table {{
                                width: 100%;
                                padding:0px;
                            }}
                            .dasa-table td{{
                                width:100%;
                                background-color:#fff;
                                padding:0px;
                            }}
                            .dasa-table td p{{
                                width: 100%;
                                font-size:12px;
                                font-weight:400;
                                text-align:center;
                                color:#000000;
                            }}
                            .note-text {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 50px auto;
                            }}

                            .note-text1 {{
                                color: red;
                                font-size: 14px;
                                font-weight: 500;
                                margin: 30px auto;
                                text-align: right;
                            }}

                             .add-info tr {{
                            padding:5px 20px ;
                            }}
                        
                            .add-info td {{
                                background-color: #ffffff;
                                padding: 5px 5px;
                            }}
                          .add-info td p{{
                            font-size: 14px;
                            font-weight: 400;
                            color: #000000;
                            padding:0 10px;
                           }}
                          
                           .click-here{{
                            color:#000;
                            font-weight:700 ;
                           text-decoration: none;

                           }}

                            .porutham-page{{
                                padding: 0px 20px;
                            }}
                            .porutham-header {{
                                margin: 20px 0px;
                            }}

                            .porutham-header img{{
                                width: 130px;
                                height: auto;
                            }}
                            .porutham-header p {{
                                font-size:22px;
                                font-weight: 700;
                                color:#000000;
                            }}
                            h2.porutham-table-title{{
                                font-size: 24px;
                                font-weight: 700;
                                margin-bottom: 20px;
                                padding:0px 0px;
                            }}
                            porutham-table{{
                                border:1px solid #bcbcbc;
                                border-collapse: collapse;
                                margin-bottom: 24px;
                            }}
                            .porutham-table td {{
                                border:1px solid #bcbcbc;
                            }}
                            .porutham-table td p{{
                                color: #000;
                                font-size:16px;
                                font-weight:700;
                                text-align:center;
                                padding: 10px 0;
                            }}
                            .porutham-stars tr td p{{
                                text-align:left;
                                padding: 20px 20px;
                            }}
                            .porutham-note{{
                                font-size: 17px;
                                font-weight:400;
                                color: #000000;
                                padding:20px 0px;
                            }}



                           .upload-horo-bg img{{
                               width:100%;
                               height:auto;
                           }}
                            .upload-horo-image{{
                                margin: 10px 0px;
                                text-align: center;
                                height: 800px;
                           
                            }}
                            .upload-horo-image tr{{
                                height: 800px;
                            }}
                            .upload-horo-image tr td{{
                                height: 800px;
                            }}
                            .upload-horo-image img{{
                                width:400px;
                                height:800px;
                                object-fit: cover;
                             
                            }}
                            
.compatibility-page-wrapper {{
    margin:0px auto;
    text-align:center;
    width:100%;
}}
.compatibility-page-wrapper tr {{
    margin: auto;
    text-align:center;
    width:100%;
}}

.compatibility-page-wrapper tr td{{
    background-color: #ffffff;
    width:100%;
    text-align:center;
    margin: auto;
}}

.report-title {{
    background-color: #ffffff;
    color: #000000;
    font-weight: bold;
    text-align: center;
    padding: 10px 0px 0px;
    font-size: 16px;
}}
.report-table {{
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff;
}}
.report-table  tr {{
    background-color: #ffffff;
}}
.report-table  tr  td{{
    background-color: #ffffff;
    color:#000000;
    border:1px solid #000000;
}}
.report-table  tr  td p{{
    background-color: #ffffff;
    color:#000000;
    font-size:14px;
    width:100%;
}}
.profile-name{{
    color:#000000;
}}
.header-cell {{
    background-color: #ffffff;
    color: #000000;
    font-weight: bold;
    text-align: center;
    padding: 6px;
}}
.sub-header {{
    background-color:#000000;
    color: #ffffff;
    text-align: center;
    padding: 4px;
}}
.profile-addtional-info{{
    width: 100%;
    background-color: #ffffff;
    border:1px solid #000000;
}}
.profile-addtional-info  tr {{
    background-color: #ffffff;
    border:none;
}}
.profile-addtional-info  tr  td p{{
    background-color: #ffffff;
    color:#000000;
    font-size:14px;
    width:100%;
}}
.data-row {{
    padding: 2px 0px;
}}
.data-label {{
    font-weight: bold;
    width: 40%;
    padding: 4px;
}}
.data-value {{
    padding: 4px;
}}

.porutham-header p {{
    font-size:22px;
    font-weight: 700;
    color:#000000;
}}

h2.porutham-table-title{{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 20px;
    padding:0px 0px;
}}
.porutham-table{{
    border:1px solid #000000;
    border-collapse: collapse;
    margin-bottom: 10px;
}}
.porutham-table th {{
    padding: 5px 0;
    background-color: #ffffff;
    color:#000000;
    font-size:16px;
    font-weight:700;
    text-align:center;
    padding: 5px 0 0 0;
}}
.porutham-table td {{
    border:1px solid #000000;
    color: #000000;
    font-size:15px;
    font-weight:400;
    text-align:center;
    padding: 8px 5px;
}}
.porutham-table tr td p{{
    color: #000000;
    font-size:15px;
    font-weight:700;
    text-align:center;
    padding: 5px 0;
}}

.porutham-stars tr td p{{
    text-align:left;
    padding: 20px 20px;
}}
.porutham-note{{
    font-size: 17px;
    font-weight:400;
    color: #000000;
    padding:20px 0px;
}}

.matching-score{{
    font-size:30px ;
    font-weight:700;
}}

                        </style>
                    </head>

                    <body>

                        <table class="header">
                                <tr>
                                    <td class="header-left">
                                        <div class="header-logo">
                                            <img src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader-bg-white.png" alt="Vysyamala Logo">
                                        </div>
                                    </td>
                                </tr>
                        </table>
                        
                    <div class="details-section">
                    
                <table class="table-div">
                            <tr>
                                <td class="border-right">
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Name</strong></p></td>
                                        <td><p><strong>{name}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>DOB / POB</p></td>
                                        <td><p>{dob} / {place_of_birth}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Complexion</p></td>
                                        <td><p>{complexion}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Education</p></td>
                                        <td><p>{final_education}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Degree</p></td>
                                        <td><p>{degree}</p></td>
                                    </tr>
                                    </table>
                                    
                                </td>
                                
                                <td>
                                <table class="inner-table">
                                    <tr>
                                        <td><p><strong>Vysyamala Id :</strong></p></td>
                                        <td><p><strong>{user_profile_id}</strong></p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Height / Photos </p></td>
                                        <td><p>{height} / {image_status}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Annual Income </p></td>
                                        <td><p>{annual_income}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>Profession / Place of stay </p></td>
                                        <td><p>{profession} / {work_place}</p></td>
                                    </tr>
                                    <tr>
                                        <td><p>{occupation_title}</p></td>
                                        <td><p>{occupation}</p></td>
                                    </tr>
                                </table>
                                </td>
                            </tr>
                        </table>

                       <hr class="divider">


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td><p><strong>Father Name</strong></p></td>
                                            <td><p><strong>{father_name}</strong></p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Father Occupation</p></td>
                                            <td><p>{father_occupation}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Family Status</p></td>
                                            <td><p>{family_status}</p></td>
                                        </tr>
                                        <tr>
                                            <td><p>Brothers/Married</p></td>
                                            <td><p>{no_of_brother}/{no_of_bro_married}</p></td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Mother Name </strong> </p>
                                                <p>Mother Occupation </p>
                                                <p>Sisters/Married </p>
                                            </td>
                                            <td>
                                                <p><strong>{mother_name}</strong></p>
                                                <p>{mother_occupation}</p>
                                                <p>{no_of_sister}/{no_of_sis_married}</p>
                                            </td>
                                        </tr>
                                    </table>
                               

                                </td>
                            </tr>
                        </table>

                       <hr class="divider">


                        <table class="table-div">
                            <tr>
                                <td  class="border-right">
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Star/Rasi </strong> </p>
                                                <p>Lagnam/Didi </p>
                                                <p>Nalikai </p>
                                            </td>
                                            <td>
                                                <p style="font-size:12px"><strong>{star_name}/{rasi_name}</strong></p>
                                                <p>{lagnam}/{didi}</p>
                                                <p>{nalikai}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>

                                <td>
                                    <table class="inner-table">
                                        <tr>
                                            <td>
                                                <p><strong>Surya Gothram : </strong></p>
                                                <p>Madhulam </p>
                                                <p>Birth Time </p>
                                            </td>
                                            <td>
                                                <p><strong>{suya_gothram}</strong></p>
                                                <p>{madulamn}</p>
                                                <p>{birth_time}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>
                            </tr>
                        </table>
                    
                    </div>
                    
                 {charts_html}

                        <tr>
                            <td>
                               {address_content}
                            </td>
                            <td>
                               {mobile_email_content}
                            </td>
                        </tr>
                    </table>
                    </td>
                    </tr>
                    <tr>
                        <td>
                            <p>Note: Please verify this profile yourself. No hidden charges or commissions if marriage is fixed through Vysyamala. For more details of this profile: <a href="{profile_url}" target="_blank" class="click-here">click here</a></p>
                        </td>
                    </tr>
                </table>
                </div>



                <table class="compatibility-page-wrapper" >
            <tr>
            <td style="text-align:center;margin:0 auto; padding:0px 20px;">
                        
            <h2 class="report-title">Marriage Compatibility Report</h2>
        
            <table class="report-table" border="0">
                <tr>
                <td class="header-cell">
                    <p class="profile-name">{login_my.Profile_name} - {login_my.ProfileId}</p>
                </td>
                <td class="header-cell">
                    <p class="profile-name"> {login_details.Profile_name} - {login_details.ProfileId}</p>   
                 </td>
                </tr>
                <tr>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_name_my} - {star_name_my}</p>
                </td>
                <td class="sub-header">
                    <p class="profile-rasi-star"> {rasi_name} - {star_name}</p>
                </td>
                </tr>
            </table>
            <br>
        
            <table class="profile-addtional-info" >
                <tr>
                <td class="data-row">
                     <p> Place of Birth : {horoscope_my.place_of_birth}</p>
                </td>
                <td class="data-row">
                    <p> Place of Birth : {horoscope.place_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Time of Birth : {horoscope_my.time_of_birth}</p>
                </td>
                <td class="data-row">
                    <p>  Time of Birth : {horoscope.time_of_birth}</p>
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> Date Of Birth : {login_my.Profile_dob}</p>
                </td>
                <td class="data-row">
                    <p> Date Of Birth : {login_details.Profile_dob}</p>
                </td>
                </tr>
            </table>
            <br>
        
              <table class="profile-addtional-info">
                <tr>
                <td class="data-row">
                    <p> Height : {cm_to_feet_inches(login_my.Profile_height)}</p>
                </td>
                <td class="data-row">
                        <p> Height : {cm_to_feet_inches(login_details.Profile_height)}</p>
        
                </td>
                </tr>
                <tr>
                <td class="data-row">
                    <p> {final_education_my}</p>
                </td>
                <td class="data-row">
                    <p> {final_education}</p>
                </td>
                </tr>
            </table>
                
            <h2 class="report-title" >Nakshatra Porutham & Rasi Porutham</h2>
           <table class="porutham-table">
                <tr>
                    <th>Porutham Name</th>
                    <th>Status</th>
                    <th>Matching Score</th>
                </tr>
                 {porutham_rows}
                 </table>        
              <table class="profile-addtional-info">
                <tr >
                <td class="data-row"  style="width:100%;">
                <p>
                Our best wishes for finding your soulmate in Vyasyamala soon. Please inform Vyasyamala if your marriage is fixed. Share your engagement photo and receive a surprise gift. No commissions / hidden charges. Jai Vasavi!
                </p>
                </td>
                </tr>
                </table>
                <br>
            </td>
            </tr>
            </table>

                <table class="porutham-page">
                <tr>
                <td>
                <br>
               

                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/horoHeader.png" >
                </div>

               <table class="upload-horo-image">
                <tr>
                <td>
                         {horoscope_content}
 
                </td>
                </tr>
                </table>
                <div class="upload-horo-bg" >
                    <img  src="https://vysyamat.blob.core.windows.net/vysyamala/pdfimages/uploadHoroFooter.png" >
                </div>


                   

                    </body>
                </html>
                """

                # Create a Django response object and specify content_type as pdf
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'

                # Create the PDF using xhtml2pdf
                pisa_status = pisa.CreatePDF(html_content, dest=response)

                # If there's an error, log it and return an HTML response with an error message
                if pisa_status.err:
                    logger.error(f"PDF generation error: {pisa_status.err}")
                    return HttpResponse('We had some errors <pre>' + html_content + '</pre>')

                return response