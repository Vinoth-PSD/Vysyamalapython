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
from PIL import Image
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
import io
import os
from django.core.files.base import ContentFile
from django.db.models import Q
import requests
from collections import defaultdict
from datetime import datetime
from django.utils import timezone

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
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
# from xhtml2pdf import pisa
from django.db import connection
# from django.core.mail import send_mail

from django.core.mail import send_mail, EmailMultiAlternatives
import secrets

import logging
logger = logging.getLogger(__name__)




class LoginView(APIView):
    authentication_classes = []
    permission_classes = []



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
        print('Username, password',username,password)
        
        try:
            # auth_user = models.Registration1.objects.get(ProfileId=username,Password=password)
            auth_user = models.Registration1.objects.get(ProfileId=username, Password__iexact=password)
            user, created = User.objects.get_or_create(username=auth_user.ProfileId)
            if created:
                # Handle user creation logic if needed
                pass
                
            # Authentication successful, create token
            token, created = Token.objects.get_or_create(user=user)

            notify_count=models.Profile_notification.objects.filter(profile_id=username, is_read=0).count()

            logindetails=models.Registration1.objects.filter(ProfileId=username).first()
            
            #get first image for the profile icon
            profile_images=models.Image_Upload.objects.filter(profile_id=username).first()          
            plan_id = logindetails.Plan_id
            gender = logindetails.Gender
            height = logindetails.Profile_height
            marital_status=logindetails.Profile_marital_status
            profile_icon=''
            profile_completion=0


            if profile_images:
                profile_icon=profile_images.image.url
            #default image icon
            else:
                
                profile_icon = '/media/men.jpg' if gender == 'male' else 'media/women.jpg'
                
                
            profile_image = 'http://103.214.132.20:8000'+profile_icon


            logindetails_exists = models.Registration1.objects.filter(ProfileId=username).filter(Profile_address__isnull=False).exclude(Profile_address__exact='').first()

            family_details_exists=models.Familydetails.objects.filter(profile_id=username).first()
            horo_details_exists=models.Horoscope.objects.filter(profile_id=username).first()
            education_details_exists=models.Edudetails.objects.filter(profile_id=username).first()
            partner_details_exists=models.Partnerpref.objects.filter(profile_id=username).first()

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

                
            return JsonResponse({'status': 1,'token':token.key ,'profile_id':username ,'message': 'Login Successful',"notification_count":notify_count,"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,"gender":gender,"height":height,"marital_status":marital_status,"custom_message":1}, status=200)
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
            print('data123456')
            
            ProfileId= serializer.validated_data.get('ProfileId')

            print('data123456',ProfileId)
            
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
        
        if serializer.is_valid():
            serializer.save()
            mobile_no = serializer.validated_data.get('Mobile_no')
            Profile_for = serializer.validated_data.get('Profile_for')
            ProfileId= serializer.validated_data.get('ProfileId')
            Gender= serializer.validated_data.get('Gender')
            
            Profile_Owner = models.Profileholder.objects.get(Mode=Profile_for)

            otp = serializer.validated_data.get('Otp')
            #otp =123456
            numbers = serializer.validated_data.get('Mobile_no')

                # Create an instance of SendSMS and send OTP

            #comented on 30th jully to hardcode value to set

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
            # response_data = {
            #         "message": "OTP sent successfully.",
            #         "Send Message Response": '12345',
            #         "Delivery Report Status":  '12345',
            #         "Available Credit":  '12345'
            #     }
            return JsonResponse({"Status":1,"profile_owner":Profile_Owner.ModeName,"response_data":response_data,'Gender':Gender,"Mobile_no":mobile_no,"profile_id":ProfileId,"message": "Registration successful"}, status=status.HTTP_201_CREATED)
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
            
            try:
                #print('profil id',profile_id)
                # Check if the profile exists in Registration1 table
                
                registration = models.Basic_Registration.objects.get(ProfileId=profile_id,status=0)
                
                try:
                    last_record = models.Registration1.objects.latest('ContentId')
                    last_record_id = last_record.ContentId
                except models.Registration1.DoesNotExist:
                     last_record_id = 0 
                
                numeric_part = str(last_record_id + 1).zfill(3) 

                new_profile_id = f"VY240{numeric_part}" 
                
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
                    'status': 1,
                    'temp_profileid':profile_id,
                    'Reset_OTP_Time':None

                    
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
                registration2_instance = models.Registration1.objects.create(**registration_data)

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







# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import json

# class Registrationstep1(APIView):

#     def post(self, request, *args, **kwargs):
#         #try:
#         #     data = json.loads(request.body)
#         # except json.JSONDecodeError:
#         #     return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
#         data = json.loads(request.body)
#         required_fields = ['profile_for', 'gender', 'mobile_number', 'emailid']
#         is_valid, missing_fields = validate_required_fields(data, required_fields)
        
#         if not is_valid:
#             return JsonResponse({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
        
#         profile_for = data.get('profile_for')
#         gender = data.get('gender')
#         mobile_number = data.get('mobile_number')
#         emailid = data.get('emailid')
#         password = data.get('password')

#         auth_user = AuthUser.objects.get(username=username, password=password)


        
#         # Proceed with further processing (e.g., saving the data, authentication, etc.)
        
#         return JsonResponse({"message": "Registration step 1 successful"}, status=status.HTTP_200_OK)

# class Get_Profileholder(APIView):

#     def get(self, request, *args, **kwargs):
#         # Fetch all records from the Profileholder model
#         all_profiles = Profileholder.objects.all()
#         # Serialize all records
#         serializer = serializers.Get_Profileholder(all_profiles, many=True)
#         # Return the serialized data
#         return JsonResponse(serializer.data, status=status.HTTP_200_OK)

class Get_Profileholder(APIView):

    def post(self, request, *args, **kwargs):
        try:
            profileholders = models.Profileholder.objects.all()
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

            MaritalStatus =  models.ProfileMaritalstatus.objects.all().order_by('MaritalStatus')
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
            heights =  models.Profileheights.objects.all()
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
            complexions =  models.Profilecomplexion.objects.all()
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
            countrries =  models.Profilecountry.objects.filter(is_active=1).order_by('name')
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

            states =  models.Profilestate.objects.filter(is_active=1,country_id=country_id).order_by('name')
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
        state_id = data.get('state_id')
        try:

            if not state_id:
                #raise serializers.ValidationError("State ID is required")
                return JsonResponse({'error': 'state id is reuired'}, status=status.HTTP_404_NOT_FOUND)
            # state = models.Profilestate.objects.get(id=state_id)

            cities =  models.Profilecity.objects.filter(is_active=1,state_id=state_id).order_by('name')
            serializer =serializers.CustomCitySerializer(cities, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}

            return JsonResponse(data_dict, safe=False)
        except  models.Profilecity.DoesNotExist:
            return JsonResponse({'error': 'city lists not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            parent_occupation =  models.Parentoccupation.objects.all()
            serializer =serializers.CustomParentOccupSerializer(parent_occupation, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Parentoccupation.DoesNotExist:
            return JsonResponse({'error': 'Parent Occupation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ImageSetUpload(APIView):
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('image_files')
        profile_id = request.data.get('profile_id')
        photo_protection = request.data.get('photo_protection')
        image_objects = []

        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not files:
            return JsonResponse({"error": "image_files is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not photo_protection:
            return JsonResponse({"error": "photo_protection is required"}, status=status.HTTP_400_BAD_REQUEST)

        for file in files:
            # Open the image
            img = PILImage.open(file)

            # Resize the image
            img = img.resize((201, 200))  # Example size, adjust as needed

            # Add watermark
            watermark_text = "Vysyamala app"
            watermark_img = PILImage.new('RGBA', img.size, (255, 255, 255, 0))

            draw = ImageDraw.Draw(watermark_img)

            # font_path = "user_api/assets/PlaywriteAUVIC-VariableFont_wght.ttf"  # Update with your font path
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'PlaywriteAUVIC-VariableFont_wght.ttf')

            print('font_path',font_path)

            font_size = 36  # Adjust as needed

            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()
            
            textwidth, textheight = draw.textsize(watermark_text, font)

            # Position the text at the bottom right
            # x = img.width - textwidth - 10
            # y = img.height - textheight - 10
            # Calculate the position for the watermark to be centered
            x = (img.width - textwidth) / 2
            y = (img.height - textheight) / 2

            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
            
            img = img.convert('RGBA')

            # Combine original image with watermark
            watermarked = PILImage.alpha_composite(img, watermark_img)

            # Save to a BytesIO object
            output = io.BytesIO()
            watermarked = watermarked.convert("RGB")
            watermarked.save(output, format='JPEG')
            output.seek(0)

            # Create a new Image instance and save
            image_instance = models.Image_Upload(profile_id=profile_id)
            image_instance.image.save(file.name,ContentFile(output.read()), save=True)
            image_objects.append(image_instance)

        serializer = serializers.ImageSerializer(image_objects, many=True)
        
        photo_password = request.data.get('photo_password')
        video_url = request.data.get('video_url')
        photo_protection = int(request.data.get('photo_protection'))

        models.Registration1.objects.filter(ProfileId=profile_id).update(Photo_password=photo_password,Video_url=video_url,Photo_protection=photo_protection)
        #return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
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
            horoscope_instance = models.Horoscope.objects.get(profile_id=profile_id)
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

# class Get_Highest_Education(APIView):

#     def post(self, request, *args, **kwargs):
#         try:
#             highest_education =  models.Highesteducation.objects.all()
#             serializer =serializers.CustomHighestEduSerializer(highest_education, many=True)
            
#             data_dict = {i + 1: item for i, item in enumerate(serializer.data)}  
            
#             return JsonResponse(data_dict, safe=False)
#         except  models.Highesteducation.DoesNotExist:
#             return JsonResponse({'error': 'HighestEducation not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Due to not clarity i comented the previouse highest code and passed the education details in table data to the highest master that is used for the partner preferenses

class Get_Highest_Education(APIView):

    def post(self, request, *args, **kwargs):
        try:
            edupref =  models.Edupref.objects.all()
            serializer =serializers.CustomHighestEduSerializer(edupref, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Edupref.DoesNotExist:
            return JsonResponse({'error': 'Highest Education not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class Get_Ug_Degree(APIView):

    def post(self, request, *args, **kwargs):
        try:
            ug_degree =  models.Ugdegree.objects.all()
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
            annual_income =  models.Annualincome.objects.all()
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
            place_of_birth =  models.Placeofbirth.objects.all()
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
            lagnam_didi =  models.Lagnamdidi.objects.all()
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
            dasa_name =  models.Dasaname.objects.all()
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
            birth_star =  models.Birthstar.objects.order_by('star')
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
            familytype =  models.Familytype.objects.all()
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
            familystat =  models.Familystatus.objects.all()
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
            familyvalue =  models.Familyvalue.objects.all()
            serializer =serializers.CustomFamilyValSerializer(familyvalue, many=True)
            
            data_dict = {i + 1: item for i, item in enumerate(serializer.data)}
            
            return JsonResponse(data_dict, safe=False)
        except  models.Familyvalue.DoesNotExist:
            return JsonResponse({'error': 'Familystatus not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#class Get_Matchstr_Pref(APIView):
# class Get_Matchstr_Pref(APIView):

#     def post(self, request):
#         input_serializer = serializers.MatchingStarInputSerializer(data=request.data)
#         if input_serializer.is_valid():
#             birth_star_id = input_serializer.validated_data['birth_star_id']
#             gender = input_serializer.validated_data['gender']
#             data = models.MatchingStarPartner.get_matching_stars(birth_star_id, gender)
#             output_serializer = serializers.MatchingStarSerializer(data, many=True)

#             grouped_data = defaultdict(list)
#             for item in data:
#                 match_count = item['match_count']
#                 grouped_data[match_count].append(item)

#             # Construct the response structure
#             response = {f"No_of_porutham{count}": items for count, items in grouped_data.items()}

#             return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
#         return JsonResponse(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Get_Matchstr_Pref(APIView):

    def post(self, request):
        input_serializer = serializers.MatchingStarInputSerializer(data=request.data)
        if input_serializer.is_valid():
            birth_star_id = input_serializer.validated_data['birth_star_id']
            gender = input_serializer.validated_data['gender']
            data = models.MatchingStarPartner.get_matching_stars(birth_star_id, gender)
            output_serializer = serializers.MatchingStarSerializer(data, many=True)

            grouped_data = defaultdict(list)
            # for item in data:
            #     match_count = item['match_count']
            #     grouped_data[match_count].append(item)

            # # Construct the response structure
            # # response = {f"No_of_porutham{count}": items for count, items in grouped_data.items()}

            # response = {f"{count} Poruthas": items for count, items in grouped_data.items()}

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






class Get_State_Pref(APIView):

    def post(self, request, *args, **kwargs):
        try:
            statepref =  models.Statepref.objects.all()
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
            edupref =  models.Edupref.objects.all()
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
            profespref =  models.Profespref.objects.all()
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
        serializer = serializers.PartnerprefSerializer(data=request.data)

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
            if(page_id=='1'):
            
             fetch_data = models.Registration1.objects.get(ProfileId=profile_id)
             serializer_class = serializers.ContactSerializer

            if(page_id=='3'):
             
             print('inside the cond')
            
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
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 








class Login_with_mobileno(APIView):
    def generate_otp(self):
        # Implement your OTP generation logic here
        import random
        return str(random.randint(100000, 999999))

    def post(self, request, *args, **kwargs):
        print(request.data)  # Debugging statement to print incoming data
        serializer = serializers.LoginWithMobileSerializer(data=request.data)

        if serializer.is_valid():
            mobile_number = serializer.validated_data.get('Mobile_no')
            print("Validated mobile number:", mobile_number)  # Debugging statement

            # Check if the mobile number exists in Registration table
            try:
                profile = models.Registration1.objects.get(Mobile_no=mobile_number)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": 0, "message": "Invalid mobile number."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP
            otp = self.generate_otp()

            # Send OTP via SMS (implement SendSMS() appropriately)
            
            #Below code commented on 30th jully 2024 harcode value set as 1234

            # sms_sender = SendSMS()  # Ensure SendSMS class is implemented and imported correctly
            # message_id = sms_sender.send_sms(otp, mobile_number)
            # dlr_status = sms_sender.check_dlr(message_id)
            # available_credit = sms_sender.available_credit()

            # Save OTP to UserProfile
            #profile.Otp = otp
            profile.Otp = 123456 #otp
            profile.save()

            # Prepare response data
            response_data = {
                "message": "OTP sent successfully.",
                # "Send Message Response": message_id,
                # "Delivery Report Status": dlr_status,
                # "Available Credit": available_credit
            }

            return JsonResponse({"status": 1, "response_data": response_data, "message": "OTP sent successfully."}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Login_verifyotp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.VerifyOtpSerializer(data=request.data)
        
        if serializer.is_valid():
            mobile_number = serializer.validated_data.get('Mobile_no')
            otp = serializer.validated_data.get('Otp')
            
            # Check if the mobile number exists and OTP is correct
            try:
                profile = models.Registration1.objects.get(Mobile_no=mobile_number,Otp=otp)
                user, created = User.objects.get_or_create(username=profile.ProfileId)

                if created:
                    # Handle user creation logic if needed
                    pass

                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({'status': 1, 'token': token.key, 'message': 'Login Successful'}, status=status.HTTP_200_OK)
            except models.Registration1.DoesNotExist:
                return JsonResponse({"status": 0, "message": "Invalid OTP or mobile number."}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse({'status': 0, 'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class Send_profile_intrests(APIView):
    def post(self, request):
        serializer = serializers.ExpressintrSerializer(data=request.data)

        print('serializer',serializer)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')
            to_express_message = serializer.validated_data.get('to_express_message')

            print('profile_from',profile_from)
            print('profile_to',profile_to)
            
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

                models.Profile_notification.objects.create(
                    profile_id=profile_to,
                    from_profile_id=profile_from,
                    notification_type='express_interests',
                    #to_message='You received a express interests from profile ID '+profile_from,
                    to_message = to_express_message if to_express_message else 'You received an express interest from profile ID ' + profile_from,
                    is_read=0,
                    created_at=timezone.now()
                )




                return JsonResponse({"Status": 1, "message": "Express interests sent successfully"}, status=status.HTTP_200_OK)
        
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
                    
                    restricted_profile_details = [
                        {
                            "int_profileid": detail.get("ProfileId"),
                            "int_profile_name": detail.get("Profile_name"),
                            #"int_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            "int_Profile_img":Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
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

            

            #mutual_condition = {'status': 2,'profile_from':profile_id,'profile_to':profile_id}
            # matching_profile_counts = Q(status=2) & (Q(profile_from=profile_id) | Q(profile_to=profile_id))

            profile_details = models.Get_profiledata.get_profile_match_count(gender,profile_id)
            
            default_img=''

            user = models.Registration1.objects.get(ProfileId=profile_id)
            gender= user.Gender

            if gender.lower()=='male':
                
                default_img='/default_bride.png'


            if gender.lower()=='female':
                
                default_img='/default_groom.png'
                                


            #print('profile_details',profile_details)


            if profile_details is None:
                matching_profile_count = 0
                profile_ids=[]
            else:
                matching_profile_count = len(profile_details)
                profile_ids = [profile['ProfileId'] for profile in profile_details]

               
                #print('profile_ids',profile_ids)


            def get_filtered_images(profile_ids):
                base_url = "http://103.214.132.20:8000/media/"
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


            prof_details= {
                            "profile_id": profile_details[0]['ProfileId'],
                            "profile_name": profile_details[0]['Profile_name'],
                            "package_name": profile_details[0]['Package_name'] if profile_details[0]['Package_name'] else "No package",
                            "package_validity":profile_details[0]['PaymentExpire'] if profile_details[0]['PaymentExpire'] else " ",
                            "completion_per":"85%",
                            #"profile_image":"http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png"
                            "profile_image": Get_profile_image(profile_details[0]['ProfileId'],profile_details[0]['Gender'],1,0)
                           
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
                    "photo_int_count":photo_int_count
            }

            return JsonResponse({"Status": 1, "message": "Fetched Dashboard details successfully", "data": combined_data , "image_data":filtered_image_paths}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def matching_gallery(profile_id):
    

        user = models.Registration1.objects.get(ProfileId=profile_id)
        gender = user.Gender

        profile_details = models.Get_profiledata.get_profile_match_count(gender, profile_id)
            
        profile_ids = [profile['ProfileId'] for profile in profile_details]
        placeholders = ', '.join(['%s'] * len(profile_ids))

        base_url = 'http://103.214.132.20:8000/'

                        # Define the SQL query to fetch total images count
        sql_query_count = f"""SELECT COUNT(DISTINCT pi.profile_id)
                        FROM profile_images pi
                        JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                        WHERE ld.Photo_protection != 1
                        AND ld.ProfileId IN ({placeholders})"""
        
        with connection.cursor() as cursor:
                    cursor.execute(sql_query_count, profile_ids)
                    total_records = cursor.fetchone()[0]  # Get total count

        return total_records



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

            user = models.Registration1.objects.get(ProfileId=profile_id)
            gender = user.Gender

            profile_details = models.Get_profiledata.get_profile_match_count(gender, profile_id)

            if profile_details is None:
                return JsonResponse({"Status": 0, "message": "No matching Records for the profiles"}, status=status.HTTP_200_OK)
            else:
                profile_ids = [profile['ProfileId'] for profile in profile_details]
                placeholders = ', '.join(['%s'] * len(profile_ids))

                base_url = 'http://103.214.132.20:8000/media/'

                # Define the SQL query to fetch total images count
                sql_query_count = f"""
                SELECT COUNT(DISTINCT pi.profile_id)
                FROM profile_images pi
                JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                WHERE ld.Photo_protection != 1
                AND ld.ProfileId IN ({placeholders})
                """

                # Execute the count query
                with connection.cursor() as cursor:
                    cursor.execute(sql_query_count, profile_ids)
                    total_records = cursor.fetchone()[0]  # Get total count

                # Now define the SQL query to fetch paginated images
                sql_query_paginated = f"""
                SELECT pi.id, pi.profile_id, pi.image
                FROM profile_images pi
                JOIN logindetails ld ON pi.profile_id = ld.ProfileId
                WHERE ld.Photo_protection != 1
                AND ld.ProfileId IN ({placeholders})
                GROUP BY pi.profile_id
                LIMIT {per_page} OFFSET {(page - 1) * per_page};
                """

                # Execute the paginated query
                with connection.cursor() as cursor:
                    cursor.execute(sql_query_paginated, profile_ids)
                    paginated_images = cursor.fetchall()

                if not paginated_images:
                    return JsonResponse({"Status": 0, "message": "No matching image Fetched"}, status=status.HTTP_200_OK)
                else:
                    image_data = [
                        {
                            "profile_id": image[1],  # Assuming image[1] contains the profile ID
                            "img_url": f"{base_url}{image[2]}"  # Append base URL to image path
                        }
                        for image in paginated_images
                    ]

                    # Create dictionary for all profile IDs
                    all_profile_ids = {str(index + 1): image[1] for index, image in enumerate(paginated_images)}

                    combined_data = {
                        "image_data": image_data,
                        "page": page,
                        "per_page": per_page,
                        "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
                        "total_records": total_records,
                        "all_profile_ids": all_profile_ids
                    }

                    return JsonResponse({"Status": 1, "message": "Image Fetched successfully", "data": combined_data}, status=status.HTTP_200_OK)





# class Get_Gallery_lists(APIView):    
#     def post(self, request):
#         serializer = serializers.Profile_idValidationSerializer(data=request.data)

#         if serializer.is_valid():
#             profile_id = serializer.validated_data.get('profile_id')

#             page = int(request.data.get('page_number', 1))
#             per_page = int(request.data.get('per_page', 10))  

#             user = models.Registration1.objects.get(ProfileId=profile_id)
#             gender= user.Gender

#             profile_details = models.Get_profiledata.get_profile_match_count(gender,profile_id)

#             #print('profile_details',profile_details)


#             if profile_details is None:
#                 profile_ids=[]
                
#                 return JsonResponse({"Status": 0, "message": "No matching Records for the profiles"}, status=status.    HTTP_200_OK)

#             else:
#                 profile_ids = [profile['ProfileId'] for profile in profile_details]


#                 placeholders = ', '.join(['%s'] * len(profile_ids))

#                 base_url='http://103.214.132.20:8000/'

#                 # Define the SQL query to fetch images
#                 sql_query = f"""
#                 SELECT pi.id, pi.profile_id, pi.image
#                 FROM profile_images pi
#                 JOIN logindetails ld ON pi.profile_id = ld.ProfileId
#                 WHERE ld.Photo_protection != 1
#                 AND ld.ProfileId IN ({placeholders})
#                 GROUP BY profile_id 
#                 """

#                 # Execute the query
#                 with connection.cursor() as cursor:
#                     cursor.execute(sql_query, profile_ids)
#                     images = cursor.fetchall()

#                     total_records=len(images)

#                     offset = (page - 1) * per_page
                    
#                     # all_profile_ids=images[1]
#                     all_profile_ids = {str(index + 1): image[1] for index, image in enumerate(images)}

                                    

#                 sql_query_paginated = sql_query + f" LIMIT {per_page} OFFSET {offset};"

#                 # Execute the query with pagination
#                 with connection.cursor() as cursor:
#                     cursor.execute(sql_query_paginated, profile_ids)
#                     paginated_images = cursor.fetchall()

#                 if not paginated_images:
                    
#                     return JsonResponse({"Status": 0, "message": "No matching image Fetched"}, status=status.HTTP_200_OK)
                                   
#                 else:

#                     image_data = [
#                         {
#                             "profile_id": paginated_images[1],  # Assuming image[1] contains the profile ID
#                             "img_url": f"{base_url}{paginated_images[2]}"  # Append base URL to image path
#                         }
#                         for paginated_images in images
#                     ]
                       
#                     combined_data = {
#                         #"interests": serialized_fetch_data,
#                         "image_data": image_data,
#                         "page": page,
#                         "per_page": per_page,
#                         "total_pages": (total_records + per_page - 1) // per_page,  # Calculate total pages
#                         "total_records": total_records,
#                         "all_profile_ids":all_profile_ids
#                     }



#             return JsonResponse({"Status": 1, "message": "Image Fetched successfully","data":combined_data}, status=status.HTTP_200_OK)

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

                    # sent_intrest_count = {'status': 1,'profile_from':profile_id}
                    # sent_int_count = count_records(models.Express_interests, sent_intrest_count)
                    
                    
                    restricted_profile_details = [
                        {
                            "myint_profileid": detail.get("ProfileId"),
                            "myint_profile_name": detail.get("Profile_name"),
                            "myint_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "myint_profile_age": calculate_age(detail.get("Profile_dob")),
                            "myint_verified":detail.get("Profile_verified"),
                            "myint_height":detail.get("Profile_height"),
                            "myint_star":detail.get("star_name"),
                            "myint_profession":detail.get("profession"),
                            "myint_city":detail.get("Profile_city"),
                            "myint_degree":get_degree(detail.get("ug_degeree")),
                            "myint_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "myint_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "myint_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "myint_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "myint_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available"
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

                    
                    # mutual_condition = Q(status=2) & (Q(profile_from=profile_id) | Q(profile_to=profile_id))
                    # mutual_int_count = count_records_forQ(models.Express_interests, mutual_condition)
                    
                    restricted_profile_details = [
                        {
                            "mutint_profileid": detail.get("ProfileId"),
                            "mutint_profile_name": detail.get("Profile_name"),
                            "mutint_Profile_img":  Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),                           
                            "mutint_profile_age": calculate_age(detail.get("Profile_dob")),
                            "mutint_verified":detail.get("Profile_verified"),
                            "mutint_height":detail.get("Profile_height"),
                            "mutint_star":detail.get("star_name"),
                            "mutint_profession":detail.get("profession"),
                            "mutint_city":detail.get("Profile_city"),
                            "mutint_degree":get_degree(detail.get("ug_degeree")),
                            "mutint_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "mutint_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "mutint_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "mutint_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "mutint_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
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
                        "all_profile_ids":all_profile_ids_1
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

        print('serializer',serializer)
        
        if serializer.is_valid():
            profile_from = serializer.validated_data.get('profile_id')
            profile_to = serializer.validated_data.get('profile_to')
            int_status = serializer.validated_data.get('status')

            print('profile_from',profile_from)
            print('profile_to',profile_to)
            
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

                    # wishlist_condition = {'status': 1,'profile_from':profile_id}
                    
                    # wishlist_count = count_records(models.Profile_wishlists, wishlist_condition)

                    
                    restricted_profile_details = [
                        {
                            "wishlist_profileid": detail.get("ProfileId"),
                            "wishlist_profile_name": detail.get("Profile_name"),
                            # "wishlist_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            "wishlist_Profile_img":  Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),                                                        
                            "wishlist_profile_age": calculate_age(detail.get("Profile_dob")),
                            "wishlist_verified":detail.get("Profile_verified"),
                            "wishlist_height":detail.get("Profile_height"),
                            "wishlist_star":detail.get("star_name"),
                            "wishlist_profession":detail.get("profession"),
                            "wishlist_degree":get_degree(detail.get("ug_degeree")),
                            "wishlist_city":detail.get("Profile_city"),
                            "wishlist_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "wishlist_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "wishlist_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "wishlist_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "wishlist_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",

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
            
            print('datetime_value',datetime_value)
            
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
            try:
                fetch_data = models.Profile_visitors.objects.filter(viewed_profile=profile_id)
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_id', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender

                    my_vistor_count = {'status': 1,'viewed_profile':profile_id}

                    myvisitor_count = count_records(models.Profile_visitors, my_vistor_count)
                    
                    restricted_profile_details = [
                        {
                            "viwed_profileid": detail.get("ProfileId"),
                            "viwed_profile_name": detail.get("Profile_name"),
                            "viwed_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "viwed_profile_age": calculate_age(detail.get("Profile_dob")),
                            "viwed_verified":detail.get("Profile_verified"),
                            "viwed_height":detail.get("Profile_height"),
                            "viwed_star":detail.get("star_name"),
                            "viwed_profession":detail.get("profession"),
                            "viwed_city":detail.get("Profile_city"),
                            "viwed_degree":get_degree(detail.get("ug_degeree")),
                            "viwed_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "viwed_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "viwed_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "viwed_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "viwed_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                             
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched viewed profile  lists successfully", "data": combined_data,"viewd_count":myvisitor_count}, status=status.HTTP_200_OK)
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
            try:
                fetch_data = models.Profile_visitors.objects.filter(profile_id=profile_id)
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('viewed_profile', flat=True)
                    profile_details = get_profile_details(profile_ids)
                    
                    viewed_profile_count_cont = {'status': 1,'profile_id':profile_id}
                    viewed_profile_count = count_records(models.Profile_visitors, viewed_profile_count_cont)
                    
                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)
                    
                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender

                    restricted_profile_details = [
                        {
                            "visited_profileid": detail.get("ProfileId"),
                            "visited_profile_name": detail.get("Profile_name"),
                            # "visited_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            "visited_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "visited_profile_age": calculate_age(detail.get("Profile_dob")),
                            "visited_verified":detail.get("Profile_verified"),
                            "visited_height":detail.get("Profile_height"),
                            "visited_star":detail.get("star_name"),
                            "visited_profession":detail.get("profession"),
                            "visited_city":detail.get("Profile_city"),
                            "visited_degree":get_degree(detail.get("ug_degeree")),
                            "visited_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "visited_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "visited_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "visited_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "visited_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                            
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched viewed profile  lists successfully", "data": combined_data,"viewed_profile_count":viewed_profile_count}, status=status.HTTP_200_OK)
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
            
            print('datetime_value',datetime_value)
            
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
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Get_personal_notes(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            try:
                fetch_data = models.Profile_personal_notes.objects.filter(profile_id=profile_id)
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_id', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender



                    personal_notes = fetch_data.values_list('profile_id','notes','datetime')

                    notes_mapping = {profile_id: (notes, datetime) for profile_id, notes, datetime in personal_notes}
                   

                    personal_notes_condition={'status': 1,'profile_id':profile_id}

                    personal_notes_count = count_records(models.Profile_personal_notes, personal_notes_condition)
                    
                                      
                    restricted_profile_details = [
                        {
                            "notes_profileid": detail.get("ProfileId"),
                            "notes_profile_name": detail.get("Profile_name"),
                            # "notes_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            "notes_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "notes_profile_age": calculate_age(detail.get("Profile_dob")),
                            "notes_details": notes_mapping.get(detail.get("ProfileId"), ('notes', ''))[0],  # Get notes from the mapping
                            "notes_datetime": notes_mapping.get(detail.get("ProfileId"), ('datetime', ''))[1],
                            "notes_verified":detail.get("Profile_verified"),  # Get datetime from the mapping
                            "notes_height":detail.get("Profile_height"),
                            "notes_star":detail.get("star_name"),
                            "notes_profession":detail.get("profession"),
                            "notes_city":detail.get("Profile_city"),
                            "notes_degree":get_degree(detail.get("ug_degeree")),
                            "notes_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "notes_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "notes_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "notes_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "notes_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                        }
                        for detail in profile_details
                    ]
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched Notes  lists successfully", "data": combined_data,"personal_note_count":personal_notes_count}, status=status.HTTP_200_OK)
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
        print(f'profile_id: {profile_id}, user_profile_id: {user_profile_id}')

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

    print('degeree',degeree)

    try:
        
        Profile_ug_degree = models.Ugdegree.objects.get(id=degeree).degree
    
    except models.Ugdegree.DoesNotExist:
                Profile_ug_degree = None 
    
    return Profile_ug_degree




def Get_matching_score(source_star_id, source_rasi_id,dest_star_id,dest_rasi_id,gender):
    
    # print('source_star_id : ',source_star_id,'source_rasi_id: ',source_rasi_id,'dest_star_id: ', dest_star_id , 'dest_rasi_id: ',dest_rasi_id,'gender',gender)

    if source_star_id and source_rasi_id and dest_star_id and dest_rasi_id:
        
       

        # Get the first matching entry
        existing_entry = models.MatchingStarPartner.objects.filter(source_star_id=source_star_id, source_rasi_id=source_rasi_id, dest_star_id=dest_star_id,dest_rasi_id=dest_rasi_id,gender=gender)

        # print('sddgdsdhfvsfbsjhdbfgfg')

        #print('existing_entry:', existing_entry)

        if existing_entry:

            # print('sddgdfgfg')
            # Serialize the single instance
            serializer = serializers.MatchingscoreSerializer(existing_entry,many=True)

            match_count = serializer.data[0].get('match_count', 0)
            # Return only the status
            if(match_count==15):
                matching_score=100
            else:
                matching_score=match_count*10            

            return matching_score
        else:
            
            return 0

    return 0  # Return 0 if no entry exists or profile_id/user_profile_id are not provided






# def Get_profile_image(user_profile_id,gender,no_of_image,photo_protection):

#     base_url='http://103.214.132.20:8000/'
#     #base_url='http://127.0.0.1:8000/'
    
#     #default_img_grrom='media/default_groom.png'
#     default_img_bride='media/default_bride.png'
#     default_img_groom='media/default_groom.png'
#     default_lock='media/default_photo_protect.png'

#     if photo_protection !=1:        

#         if user_profile_id:
#             #print(f'profile_id: {profile_id}, user_profile_id: {user_profile_id}')

#             # Get the first matching entry
        

#             #print('existing_entry:', existing_entry)
        
#             if(no_of_image==1):

#                 get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id).first()           
            
#                 if get_entry:
#                         # Serialize the single instance
#                         serializer = serializers.ImageGetSerializer(get_entry)
#                         # Return only the status
#                         return base_url+serializer.data['image']
#                 else:
#                         #return 0
#                         if(gender=='male'):
                            
#                             return base_url+default_img_bride
                        
#                         if(gender=='female'):
                            
#                             return base_url+default_img_groom
                    
#             else:
#                 get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id)[:10]
#                 if get_entry.exists():
#                     # Serialize the single instance
#                     serializer = serializers.ImageGetSerializer(get_entry,many=True)
#                     # Return only the status
#                     images_dict = {
#                         str(index + 1): base_url + entry['image']
#                         for index, entry in enumerate(serializer.data)
#                     }
#                     #print(images_dict)
#                     return images_dict
                    
#                 else:                
#                     default_img = default_img_bride if gender == 'female' else default_img_groom
#                     return {"1":  base_url + default_img,"2":  base_url + default_img}
#     elif(no_of_image==1):
#         # if(gender=='male'):
                    
#         #     return base_url+default_img_bride
                
#         # if(gender=='female'):
                    
#         #     return base_url+default_img_groom
#         return base_url+default_lock
#     else:
        
#              return {"1":  base_url + default_lock,"2":  base_url + default_lock}
    #return 0  # Return 0 if no entry exists or profile_id/user_profile_id are not provided



def Get_profile_image(user_profile_id,gender,no_of_image,photo_protection):

    base_url='http://103.214.132.20:8000'
    #base_url='http://127.0.0.1:8000/'
    
    #default_img_grrom='media/default_groom.png'
    default_img_bride='/media/default_bride.png'
    default_img_groom='/media/default_groom.png'
    default_lock='/media/default_photo_protect.png'
    

    if photo_protection !=1:        

        if user_profile_id:
            #print(f'profile_id: {profile_id}, user_profile_id: {user_profile_id}')

            # Get the first matching entry
        

            #print('existing_entry:', existing_entry)
        
            if(no_of_image==1):

                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id).first()           
            
                if get_entry:
                        # Serialize the single instance
                        serializer = serializers.ImageGetSerializer(get_entry)
                        # Return only the status
                        return base_url+serializer.data['image']
                else:
                        
                        
                        #return 0
                        if(gender.lower()=='male'):
                           
                            return base_url+default_img_bride
                        
                        if(gender.lower()=='female'):
                            print(base_url+default_img_groom)
                            return base_url+default_img_groom
                        
                        print('gender',gender)
                    
            else:
                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id)[:10]
                if get_entry.exists():
                    # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry,many=True)
                    # Return only the status
                    images_dict = {
                        str(index + 1): base_url + entry['image']
                        for index, entry in enumerate(serializer.data)
                    }
                    #print(images_dict)
                    return images_dict
                    
                else:                
                    default_img = default_img_bride if gender == 'female' else default_img_groom
                    return {"1":  base_url + default_img,"2":  base_url + default_img}
                
    else:

        if(no_of_image==1):
            get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id).first()   

                #print('get_entry',get_entry)        
                    
            if get_entry:
                        # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry)
                                # Return only the status

                    print('serializer',serializer)
                        
                    # return img_base64
                    response = requests.get(base_url+serializer.data['image'])
                    if response.status_code == 200:
                        # Open the image from the downloaded bytes
                        img = Image.open(BytesIO(response.content))

                        # Apply a blur filter to the image
                        blurred_image = img.filter(ImageFilter.GaussianBlur(radius=9))

                        # Convert the image to a bytes buffer
                        buffer = BytesIO()
                        blurred_image.save(buffer, format="JPEG")
                        buffer.seek(0)

                        # Encode the bytes buffer to base64
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                        return 'data:image/jpeg;base64,'+ img_base64


        else:

                get_entry = models.Image_Upload.objects.filter(profile_id=user_profile_id).first()   

                #print('get_entry',get_entry)        
                    
                if get_entry:
                        # Serialize the single instance
                    serializer = serializers.ImageGetSerializer(get_entry)
                                # Return only the status

                    print('serializer',serializer)
                        
                    # return img_base64
                    response = requests.get(base_url+serializer.data['image'])
                    if response.status_code == 200:
                        # Open the image from the downloaded bytes
                        img = Image.open(BytesIO(response.content))

                        # Apply a blur filter to the image
                        blurred_image = img.filter(ImageFilter.GaussianBlur(radius=9))

                        # Convert the image to a bytes buffer
                        buffer = BytesIO()
                        blurred_image.save(buffer, format="JPEG")
                        buffer.seek(0)

                        # Encode the bytes buffer to base64
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                        return {"1":  'data:image/jpeg;base64,'+ img_base64,"2":  'data:image/jpeg;base64,'+img_base64}

                        # return 'data:image/jpeg;base64,' + img_base64
                        
                    else:
                        raise Exception(f"Failed to download image. Status code: {response.status_code}")
             
                else:
                    if(gender=='male'):
                        
                        return base_url+default_img_bride
                                
                    if(gender=='female'):
                                    
                        return base_url+default_img_groom
                    


# class Get_prof_list_match(APIView):

#     def post(self, request):
#         #profile_id = 'VY240013'
#         profile_id = request.data.get('profile_id')


#         profile_hr_data = {
#             "1": {
#                 "profile_id": "VY24001",
#                 "profile_name": "vinoth",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "bsc",
#                 "profession": "Un employeed",
#                 "location": "Chennai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png",
#                 "wish_list":"0"
#             },
#             "2": {
#                 "profile_id": "VY24001",
#                 "profile_name": "test123",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png",
#                 "wish_list":"0"
#             },
#             "3": {
#                 "profile_id": "VY24001",
#                 "profile_name": "test125",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "wish_list":"1"
#             },
#             "4": {
#                 "profile_id": "VY24001",
#                 "profile_name": "Test125",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "trichy",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png",
#                 "wish_list":"1"
#             },
#             "4": {
#                 "profile_id": "VY24001",
#                 "profile_name": "Test125",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"1"
#             },
#             "5": {
#                 "profile_id": "VY24001",
#                 "profile_name": "Test125",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"1"
#             },
#             "6": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "7": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "wish_list":"0"
#             },
#             "8": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "9": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "10": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "11": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "12": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "13": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "14": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "wish_list":"0"
#             },
#             "15": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "16": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                  "wish_list":"0"
#             },
#             "17": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "wish_list":"0"
#             },
#             "18": {
#                 "profile_id": "VY24001",
#                 "profile_name": "TestUser",
#                 "age": "26",
#                 "height": "5.5",
#                 "weight": "56",
#                 "degree": "Mca",
#                 "profession": "Employee",
#                 "location": "Madurai",
#                 "profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "wish_list":"0"
#             }

#         }


#         try:
#             #data = models.Get_profiledata.get_edit_profile(profile_id)
#             # Uncomment and modify the following line if you have a serializer
#             # output_serializer = serializers.MatchingStarSerializer(data, many=True)

#             # Construct the response structure
#             #response = data

#             return JsonResponse(profile_hr_data, safe=False, status=status.HTTP_200_OK)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class Get_prof_list_match(APIView):

    def post(self, request):
        serializer = serializers.GetproflistSerializer(data=request.data)

        #print('Testing','123456')

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

            # response_data = {
            #     "message": "Profile ID is valid.",
            #     "profile_id": profile_id,
            #     "gender": profile_data.Gender,
            # }

            profile_details , total_count ,profile_with_indices = models.Get_profiledata.get_profile_list(gender,profile_id,start,per_page,search_profile_id,order_by,search_profession,search_age,search_location)

            my_profile_id = [profile_id]   

            # print('my_profile_id',my_profile_id) 

            # print('profile_details',profile_details)        

           
            my_profile_details = get_profile_details(my_profile_id)

            # print('my_profile_details',my_profile_details)
            
            my_gender=my_profile_details[0]['Gender']
            my_star_id=my_profile_details[0]['birthstar_name']
            my_rasi_id=my_profile_details[0]['birth_rasi_name']

            # print('Testing','8752145')

            #print('matching profile limit 1',profile_details[0])

            #return JsonResponse(response_data, status=status.HTTP_200_OK)

            if profile_details:


                restricted_profile_details = [
                            {
                                "profile_id": detail.get("ProfileId"),
                                "profile_name": detail.get("Profile_name"),
                                "profile_img": Get_profile_image(detail.get("ProfileId"),my_gender,1,detail.get("Photo_protection")),
                                "profile_age": calculate_age(detail.get("Profile_dob")),
                                "profile_gender":detail.get("Gender"),
                                "height": detail.get("Profile_height"),
                                "weight": "56",
                                "degree": "Mca",
                                "star":detail.get("star_name"),
                                "profession": "Employee",
                                "location":detail.get("Profile_city"),
                                "photo_protection":detail.get("Photo_protection"),
                                "matching_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                                #"profile_image":"http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                                "wish_list":Get_wishlist(profile_id,detail.get("ProfileId")),
                                "verified":detail.get('Profile_verified'),
                                #"wishlist_profile_notes": 'Iam intrested in your profile if you are intrested in my profile , please contact me',
                            }
                            for detail in profile_details
                        ]
            
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





# class Get_profile_det_match(APIView):

#  def post(self, request):
#         #profile_id = 'VY240013'
#         profile_id = request.data.get('profile_id')

#         profile_details={
#             "basic_details": {
#                 "profile_id": "VY24001",
#                 "profile_name": "Test User",
#                 "age": "24 years",
#                 "weight": "70",
#                 "height": "15ft",
#                 "star": "Rohini",
#                 "profession": "Mca",
#                 "education": "Mca",
#                 "about": "About user profile",
#                 "gothram": "test",
#                 "horoscope_available": "0",
#                 "user_status": "0",
#                 "last_visit": "0",
#                 "user_profile_views": "121",
#                 "express_int": "1",
#                 "matching_score": "75%"
#             },
#             "user_images": {
#                 "1": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "2": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "3": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "4": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "5": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "6": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "7": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "8": "https://swiperjs.com/demos/images/nature-1.jpg",
#                 "9": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
#                 "10": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png"
#             },
#             "personal_details": {
#                 "profile_name": "Vinoth",
#                 "gender": "Male",
#                 "age": "25",
#                 "dob": "23-03-1999",
#                 "place_of_birth": "trichy",
#                 "time_of_birth": "trichy",
#                 "weight": "70 kg",
#                 "height": "15ft",
#                 "marital_status": "Not married",
#                 "blood_group": "A1 +ve",
#                 "body_type": "Slim",
#                 "about_self": "Test",
#                 "complexion": "Dusky",
#                 "hobbies": "test, test, test",
#                 "physical_status": "Normal",
#                 "eye_wear": "Unknown",
#                 "profile_created_by": "Admin"
#             },
#             "education_details": {
#                 "education_level": "Diploma/Pg Diploma",
#                 "education_detail": "DCE",
#                 "about_education": "",
#                 "profession": "Trainer",
#                 "company_name": "Ganapathi Medicals",
#                 "business_name": "Ganapathi Medicals",
#                 "business_address": "24, Alanangathapuram 2nd street tharanalllur trichy 620008",
#                 "annual_income": "Rs 50,000 - Rs 7,50,000",
#                 "gross_annual_income": "Rs 50,000 - Rs 7,50,000",
#                 "place_of_stay": ""
#             },
#             "family_details": {
#                 "about_family": "Test details",
#                 "father_name": "Test",
#                 "father_occupation": "test occupation",
#                 "mother_name": "test name",
#                 "mother_occupation": "Home maker",
#                 "family_status": "Test status",
#                 "no_of_sisters": "0",
#                 "no_of_brothers": "2",
#                 "no_of_sis_married": "0",
#                 "no_of_bro_married": "2",
#                 "property_details": "Test details"
#             },
#             "horoscope_details": {
#                 "rasi": "taurus",
#                 "star_name": "Rohini",
#                 "lagnam": "test",
#                 "nallikai": "test",
#                 "didi": "test",
#                 "surya_gothram": "test",
#                 "dasa_name": "test",
#                 "dasa_balance": "test",
#                 "chevvai_dosham": "Yes",
#                 "sarpadosham": "No"
#             },
#             "contact_details": {
#                 "address": "trichy 620008",
#                 "city": "trichy",
#                 "state": "tamilnadu",
#                 "country": "india",
#                 "phone": "9087408476",
#                 "mobile": "6369039520",
#                 "whatsapp": "6369039520",
#                 "email": "vunoth@psdigitise.com"
#             }
#         }

#         try:
#             return JsonResponse(profile_details, safe=False, status=status.HTTP_200_OK)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Get_profile_det_match(APIView):

 def post(self, request):
        #profile_id = 'VY240013'
      profile_id = request.data.get('profile_id')
      user_profile_id = request.data.get('user_profile_id')
      
      print('match_profile_id',user_profile_id)
      
      serializer = serializers.GetproflistSerializer_details(data=request.data)
      if serializer.is_valid():   
          
          #profile_ids = profile_id
          print('match_profile_id',user_profile_id)

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

                # Plan_subscribed = None

        

          print('Profile_id',profile_details[0]['ProfileId'])
        
          user_images = Get_profile_image(profile_details[0]['ProfileId'], profile_details[0]['Gender'], 'all',profile_details[0]['Photo_protection'])  
          
          try:
                Profile_complexion = models.Profilecomplexion.objects.get(complexion_id=profile_details[0]['Profile_complexion']).complexion_desc
          except models.Profilecomplexion.DoesNotExist:
                Profile_complexion = None
          
          #Profile_high_edu = models.Edupref.objects.get(RowId=profile_details[0]['highest_education']).EducationLevel  
        
          try:
                Profile_high_edu = models.Edupref.objects.get(RowId=profile_details[0]['highest_education']).EducationLevel
          except models.Edupref.DoesNotExist:
                Profile_high_edu = None

          #Profile_high_edu=''
          
          #Profile_ug_degree = models.Ugdegree.objects.get(id=profile_details[0]['ug_degeree']).degree    


          try:
                Profile_ug_degree = models.Ugdegree.objects.get(id=profile_details[0]['ug_degeree']).degree
          except models.Ugdegree.DoesNotExist:
                Profile_ug_degree = None 

        #   Profile_owner = models.Profileholder.objects.get(Mode=profile_details[0]['Profile_for']).ModeName

        #   Profile_marital_status = models.ProfileMaritalstatus.objects.get(StatusId=profile_details[0]['Profile_marital_status']).MaritalStatus

          try:
                Profile_owner = models.Profileholder.objects.get(Mode=profile_details[0]['Profile_for']).ModeName
          except models.Profileholder.DoesNotExist:
                Profile_owner = None

          try:
                Profile_marital_status = models.ProfileMaritalstatus.objects.get(StatusId=profile_details[0]['Profile_marital_status']).MaritalStatus
          except models.ProfileMaritalstatus.DoesNotExist:
                Profile_marital_status = None


          #Profile_status_active = profile_details[0]['Profile_verified']

        #   now = timezone.now()
        #   one_month_ago = now - timedelta(days=30)

          now = timezone.now()

            # Convert now to a naive datetime
          now_naive = now.replace(tzinfo=None)
          one_month_ago = now_naive - timedelta(days=30)

        #   Profile_status_active = ''

            # Ensure Last_login_date is not None and convert it to a datetime object
        #   if profile_details[0]['Last_login_date']:
        #         try:
        #             # Assuming the date format is "%Y-%m-%d %H:%M:%S"
        #             last_login_date = datetime.strptime(profile_details[0]['Last_login_date'], "%Y-%m-%d %H:%M:%S")

        #             # Compare the last_login_date with one_month_ago
        #             if last_login_date < one_month_ago:
        #                 Profile_status_active = "In Active User"  # Mark as inactive if last login is older than one month
        #             else:
        #                 Profile_status_active = "Active User"
        #         except ValueError:
        #             Profile_status_active = "Invalid Date Format"  # Handle invalid date format
        #   else:
        #         Profile_status_active = "No Last Login Date"  # Handle case where Last_login_date is None or empty


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
                    print('Hai')
                    # if isinstance(last_login_date, str):
                    #     print(last_login_date,'last_login_date123')
                    try:
                            # Convert string to datetime
                            # print(last_login_date,'last_login_date12345')                          

                            last_visit =profile_details[0]['Last_login_date'].strftime("(%B %d, %Y)") 
                                

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
               
                   

        #   profile_star_name = models.Birthstar.objects.get(id=profile_details[0]['birthstar_name']).star

        #   profile_rasi_name = models.Rasi.objects.get(id=profile_details[0]['birth_rasi_name']).name

          try:
                profile_star_name = models.Birthstar.objects.get(id=profile_details[0]['birthstar_name']).star
          except models.Birthstar.DoesNotExist:
                profile_star_name = None

          try:
                profile_rasi_name = models.Rasi.objects.get(id=profile_details[0]['birth_rasi_name']).name
          except models.Rasi.DoesNotExist:
                profile_rasi_name = None

          try:
                profile_state_name = models.Profilestate.objects.get(id=profile_details[0]['Profile_state']).name
          except models.Profilestate.DoesNotExist:
                profile_state_name = None
          
          try:
                profile_country_name = models.Profilecountry.objects.get(id=profile_details[0]['Profile_country']).name
          except models.Profilecountry.DoesNotExist:
                profile_country_name = None


        #   profile_details[0]['birth_rasi_name']  

          Profile_horoscope=0
          Profile_horoscope_txt='Not available'
          Profile_horoscope_file = profile_details[0]['horoscope_file']
          Profile_horoscope_file_link=''
          if(Profile_horoscope_file):
                              
                Profile_horoscope=1
                Profile_horoscope_txt="Horoscope Available"
                
                Profile_horoscope_file_link='http://103.214.132.20:8000/media/'+Profile_horoscope_file 




          profile_details={
                "basic_details": {
                    "profile_id": profile_details[0]['ProfileId'],
                    "profile_name": profile_details[0]['Profile_name'],
                    "age": calculate_age(profile_details[0]['Profile_dob']),
                    "weight": profile_details[0]['weight'],
                    "height": profile_details[0]['Profile_height'],
                    "star":  profile_details[0]['star_name'],
                    "profession": profile_details[0]['profession'],
                    "education": Profile_high_edu,
                    "about": profile_details[0]['about_self'],
                    "gothram": profile_details[0]['suya_gothram'],
                    "horoscope_available": Profile_horoscope,
                    "horoscope_available_text": Profile_horoscope_txt,
                    "horoscope_link":Profile_horoscope_file_link,
                    "user_status": Profile_status_active,
                    "verified":profile_details[0]['Profile_verified'],
                #     "last_visit": (profile_details[0]['Last_login_date'].strftime("(%B %d, %Y)") 
                #   if profile_details[0]['Last_login_date'] else "Date not available"),
                    # "last_visit":(profile_details[0]['Last_login_date'].strftime("(%B %d, %Y)") 
                    #     if profile_details[0]['Last_login_date'] and isinstance(profile_details[0]['Last_login_date'], datetime) 
                    #     else "Date not available"),
                    "last_visit":last_visit,
                    "user_profile_views": count_records(models.Profile_visitors, {'status': 1,'viewed_profile':user_profile_id}),
                    "wish_list": Get_wishlist(profile_id,user_profile_id),
                    "express_int": Get_expressstatus(profile_id,user_profile_id),
                    "personal_notes": Get_personalnotes_value(profile_id,user_profile_id),
                    #"matching_score": "75%"

                    "matching_score":Get_matching_score(my_star_id,my_rasi_id,profile_details[0]['birthstar_name'],profile_details[0]['birth_rasi_name'],my_gender),
                    "plan_subscribed":Plan_subscribed
                },
                # "user_images": {
                #     "1": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "2": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "3": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "4": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "5": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "6": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "7": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "8": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "9": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png",
                #     "10": "http://matrimonyapp.rainyseasun.com/assets/Bride-BEuOb3-D.png"
                # },
                "photo_protection":profile_details[0]['Photo_protection'],
                "user_images":user_images,
                "personal_details": {
                    "profile_name": profile_details[0]['Profile_name'],
                    "gender": profile_details[0]['Gender'],
                    "age": calculate_age(profile_details[0]['Profile_dob']),
                    "dob": profile_details[0]['Profile_dob'],
                    "place_of_birth": profile_details[0]['place_of_birth'],
                    "time_of_birth": profile_details[0]['time_of_birth'],                   
                    "height": profile_details[0]['Profile_height'],
                    "marital_status": Profile_marital_status,
                    "blood_group": profile_details[0]['blood_group'],
                    "about_self": profile_details[0]['about_self'],
                    "complexion": Profile_complexion,
                    "hobbies": profile_details[0]['hobbies'],
                    "physical_status": profile_details[0]['Pysically_changed'],
                    "eye_wear": profile_details[0]['eye_wear'] ,
                    "weight": profile_details[0]['weight'] ,
                    "body_type": profile_details[0]['body_type'] ,
                    "profile_created_by": Profile_owner,
                },
                "education_details": {
                    "education_level": profile_details[0]['ug_degeree'],
                    "education_detail": " ",
                    "ug_degeree": Profile_ug_degree,
                    "about_education": profile_details[0]['highest_education'],
                    "profession": profile_details[0]['profession'],
                    "company_name": profile_details[0]['company_name'],
                    "business_name": profile_details[0]['business_name'],
                    "business_address": profile_details[0]['business_address'],
                    "annual_income": profile_details[0]['anual_income'],
                    "gross_annual_income": profile_details[0]['actual_income'],
                    "place_of_stay": profile_details[0]['Profile_city'],
                },
                "family_details": {
                    "about_family": profile_details[0]['about_self'],
                    "father_name": profile_details[0]['father_name'],
                    "father_occupation": profile_details[0]['father_occupation'],
                    "mother_name": profile_details[0]['mother_name'],
                    "mother_occupation": profile_details[0]['mother_occupation'],
                    "family_status": profile_details[0]['family_status'],
                    "no_of_sisters": profile_details[0]['no_of_sister'],
                    "no_of_brothers": profile_details[0]['no_of_brother'],
                    "no_of_sis_married": profile_details[0]['no_of_sis_married'],
                    "no_of_bro_married": profile_details[0]['no_of_bro_married'],
                    "property_details": profile_details[0]['property_details'],
                },
                "horoscope_details": {
                    "rasi": profile_rasi_name,
                    "star_name": profile_star_name,
                    "lagnam": profile_details[0]['lagnam_didi'],
                    "nallikai": profile_details[0]['nalikai'],
                    "didi": profile_details[0]['lagnam_didi'],
                    "surya_gothram": profile_details[0]['suya_gothram'],
                    "dasa_name": profile_details[0]['dasa_name'],
                    "dasa_balance": profile_details[0]['dasa_balance'],
                    "chevvai_dosham": profile_details[0]['calc_chevvai_dhosham'],
                    "sarpadosham": profile_details[0]['calc_raguketu_dhosham'],
                    "rasi_kattam":profile_details[0]['rasi_kattam'],
                    "amsa_kattam":profile_details[0]['amsa_kattam'],
                },
                "contact_details": {
                    "address": profile_details[0]['Profile_address'],
                    "city": profile_details[0]['Profile_city'],
                    "state": profile_state_name,
                    "country": profile_country_name,
                    "phone": profile_details[0]['Mobile_no'],
                    "mobile": profile_details[0]['Mobile_no'],
                    "whatsapp": profile_details[0]['Profile_whatsapp'],
                    "email": profile_details[0]['EmailId'],
                }
            }

      
          return JsonResponse(profile_details, safe=False, status=status.HTTP_200_OK)
    
      return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
                file_path = self.resize_and_save_image(img, profile_dir, image_file.name, watermark_text="vysyamala.com")
                JsonResponse.objects.create(profile=profile, image=file_path)

                print('file_path',file_path)


        return JsonResponse({'status': 'success', 'message': 'Images uploaded and resized successfully.'}, status=status.HTTP_201_CREATED)

    def resize_and_save_image(self, img, profile_dir, file_name, watermark_text):
        # Get the actual file size in bytes
        img_byte_array = BytesIO()
        img.save(img_byte_array, format=img.format)
        img_size = img_byte_array.tell()

        # Check if image size exceeds 10MB
        if img_size > (10 * 1024 * 1024):
            # Resize the image
            img.thumbnail((img.width // 2, img.height // 2), Image.ANTIALIAS)
        font_path = os.path.join(settings.BASE_DIR, 'fonts', 'timesnewarial.ttf')
        font_size = 175
        watermark_font = ImageFont.truetype(font_path, font_size)
        # Add watermark to the image diagonally
        #watermark_font = ImageFont.load_default()  # Default font for watermark
        draw = ImageDraw.Draw(img)
        watermark_position = (50, img.height - 530)  # Adjust position as needed
        draw.text(watermark_position, watermark_text, fill='black', font=watermark_font)

        img_path = os.path.join(profile_dir, file_name)
        img.save(img_path)
        return img_path

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
        profile_images =  models.Image_Upload.objects.filter(profile_id=profile_id)
        media_root_len = len(settings.MEDIA_ROOT)
        
        # Define the URL prefix
        url_prefix = "https://103.214.132.20:8000/images/"
        
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

            print('profile_from',profile_from)
            print('profile_to',profile_to)
            
            # Check if an entry with the same profile_from and profile_to already exists
            existing_entry = models.Photo_request.objects.filter(profile_from=profile_from, profile_to=profile_to).first()
            
            if existing_entry:
                # Update the status to 0 if the entry already exists
                #existing_entry.status = 0
                existing_entry.status = int_status
                existing_entry.req_datetime = timezone.now()
                existing_entry.save()
                
                 # Insert notification for the update
                # models.Profile_notification.objects.create(
                #     profile_id=profile_to,
                #     from_profile_id=profile_from,
                #     notification_type='photo_request',
                #     message='You received a photo request update from profile ID '+profile_from,
                #     is_read=0,
                #     created_at=timezone.now()
                # )
                                
                
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
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class Get_photo_request_list(APIView):

    def post(self, request):
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():
            profile_id = serializer.validated_data.get('profile_id')
            try:
                fetch_data = models.Photo_request.objects.filter(profile_to=profile_id,status__in=[1, 2, 3])
                if fetch_data.exists():
                    profile_ids = fetch_data.values_list('profile_from', flat=True)
                    profile_details = get_profile_details(profile_ids)

                    profile_data =  models.Registration1.objects.get(ProfileId=profile_id)

                    horo_data=models.Horoscope.objects.get(profile_id=profile_id)


                    my_star_id=horo_data.birthstar_name
                    my_rasi_id=horo_data.birth_rasi_name
            
                    my_gender=profile_data.Gender

                    # print('fetch_data',fetch_data)
                    # print('profile_ids',profile_ids)

                    # print('profile_details length',len(profile_details))
                    # print('profile_details',(profile_details))

                    
                    
                    restricted_profile_details = [
                        {
                            "req_profileid": detail.get("ProfileId"),
                            "req_profile_name": detail.get("Profile_name"),
                            #"req_Profile_img": 'http://matrimonyapp.rainyseasun.com/assets/Groom-Cdjk7JZo.png',
                            "req_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "req_profile_age": calculate_age(detail.get("Profile_dob")),
                            "response_message": fetch_data[index].response_message,
                            "req_status": fetch_data[index].status,
                            "req_verified":detail.get('Profile_verified'),
                            "req_height":detail.get("Profile_height"),
                            "req_star":detail.get("star_name"),
                            "req_profession":detail.get("profession"),
                            "req_city":detail.get("Profile_city"),
                            "req_degree":get_degree(detail.get("ug_degeree")),
                            "req_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "req_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "req_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "req_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "req_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
                        }
                        # for detail in profile_details
                        for index, detail in enumerate(profile_details)
                    ]

                    #print('fetch_data',fetch_data)
                    
                    #serialized_fetch_data = serializers.ExpressintrSerializer(fetch_data, many=True).data
                    #serialized_profile_details = serializers.ProfileDetailsSerializer(profile_details, many=True).data

                    combined_data = {
                        #"interests": serialized_fetch_data,
                        "profiles": restricted_profile_details
                    }

                    return JsonResponse({"Status": 1, "message": "Fetched Photo request and profile details successfully", "data": combined_data, "photoreq_count":10}, status=status.HTTP_200_OK)
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
            try:
                
                now = timezone.now()

                # Calculate the date 30 days ago
                last_60_days = now - timedelta(days=60)

                notify_count=models.Profile_notification.objects.filter(profile_id=profile_id, is_read=0).count()

                notification_list=models.Profile_notification.objects.filter(profile_id=profile_id, created_at__gte=last_60_days)

                notifications_data = [
                    {
                        "id": notification.id,
                        "notify_img": 'https://vysyamala.com/images/heading_icon.png',
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
                        "data": notifications_data
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

            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)
                if user.Password != old_password:
                    return JsonResponse({"status": "error", "message": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)

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

        def process_and_save_image(file, image_instance=None):
            valid_extensions = ['png', 'jpeg', 'jpg']
            file_extension = os.path.splitext(file.name)[1][1:].lower()
            if file_extension not in valid_extensions:
                return JsonResponse({"error": "Invalid file type. Accepted formats are: png, jpeg, jpg"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Image processing (resize, watermark, etc.)
            img = PILImage.open(file)
            img = img.resize((201, 200))
            watermark_text = "Vysyamala app"
            watermark_img = PILImage.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_img)
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'PlaywriteAUVIC-VariableFont_wght.ttf')
            font_size = 36

            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()
            
            textwidth, textheight = draw.textsize(watermark_text, font)
            x = (img.width - textwidth) / 2
            y = (img.height - textheight) / 2
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
            img = img.convert('RGBA')
            watermarked = PILImage.alpha_composite(img, watermark_img)
            output = io.BytesIO()
            watermarked = watermarked.convert("RGB")
            watermarked.save(output, format='JPEG')
            output.seek(0)

            # Unlink (delete) the existing image if replacing
            if image_instance:
                if os.path.isfile(image_instance.image.path):
                    os.remove(image_instance.image.path)
                image_instance.image.save(os.path.join(file.name), ContentFile(output.read()), save=True)
            else:
                image_instance = models.Image_Upload(profile_id=profile_id)
                image_instance.image.save(os.path.join(file.name), ContentFile(output.read()), save=True)
            
            image_objects.append(image_instance)

        # Process replacement images
        for idx, image_id in enumerate(replace_image_ids):
            image_instance = models.Image_Upload.objects.get(id=image_id, profile_id=profile_id)
            process_and_save_image(replace_files[idx], image_instance)

        # Process new images
        for file in new_files:
            process_and_save_image(file)

        serializer = serializers.ImageSerializer(image_objects, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    


class Remove_profile_img(APIView):
    def delete_image(self, instance):
        if instance.image:
            image_path = instance.image.path
            if os.path.exists(image_path):
                os.remove(image_path)
            instance.image = None
            instance.save()

    def post(self, request, *args, **kwargs):
        try:
            # Get the profile_id from the POST data
            profile_id = request.POST.get('profile_id')
            image_id = request.POST.get('image_id')

            # Ensure profile_id is provided
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

            # Get the object by profile_id
            instance = get_object_or_404(models.Image_Upload, profile_id=profile_id,id=image_id)

            # Delete the image file and clear the database field
            self.delete_image(instance)
            instance.delete()
            
            return JsonResponse({
                'success': 1,
                'message': 'Image deleted successfully.'                
            },status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                'success': 0,
                'message': str(e)
            }, status=status.HTTP_200_OK)


class Get_profile_images(APIView):
    def post(self, request, *args, **kwargs):
        
        profile_id = request.data.get('profile_id')
        serializer = serializers.Profile_idValidationSerializer(data=request.data)

        if serializer.is_valid():

            # Get images for the specified profile
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
        base_url='http://103.214.132.20:8000'
        
        
        if serializer.is_valid():
            profile_to = serializer.validated_data['profile_to']

            get_entry = models.Image_Upload.objects.filter(profile_id=profile_to)[:10]
            if get_entry.exists():
                # Serialize the single instance
                serializer = serializers.ImageGetSerializer(get_entry,many=True)
                # Return only the status
                images_dict = {
                    str(index + 1): base_url + entry['image']
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
                
                #get first image for the profile icon
                profile_images=models.Image_Upload.objects.filter(profile_id=profile_id).first()
                
                plan_id = logindetails.Plan_id
                gender = logindetails.Gender
                profile_icon=''
                profile_completion=0
                height = logindetails.Profile_height
                marital_status=logindetails.Profile_marital_status


                if profile_images:
                    profile_icon=profile_images.image.url
                #default image icon
                else:
                    
                    profile_icon = '/media/men.jpg' if gender == 'male' else 'media/women.jpg'
                    
                    
                profile_image = 'http://103.214.132.20:8000'+profile_icon


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

                return JsonResponse({'status': 1,'message': 'Details fetched sucessfully',"cur_plan_id":plan_id,"profile_image":profile_image,"profile_completion":profile_completion,'gender':gender,'height':height,'marital_status':marital_status}, status=200)
                                       
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
                    star_name = "Unknown"

                # Fetch rasi name from Rasi model
                try:
                    rasi = models.Rasi.objects.get(pk=horoscope.birth_rasi_name)
                    rasi_name = rasi.name  # Or use rasi.tamil_series, telugu_series, etc. as per your requirement
                except models.Rasi.DoesNotExist:
                    rasi_name = "Unknown"

                time_of_birth = horoscope.time_of_birth
                place_of_birth = horoscope.place_of_birth
                lagnam_didi = horoscope.lagnam_didi
                nalikai =  horoscope.nalikai

                # Planet mapping dictionary
                planet_mapping = {
                    "1": "Sun",
                    "2": "Moo",
                    "3": "Mar",
                    "4": "Mer",
                    "5": "Jup",
                    "6": "Ven",
                    "7": "Sat",
                    "8": "Rahu",
                    "9": "Kethu",
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
                                            <img src="https://vysyamala.com/img/newlogo.png" alt="Vysyamala Logo">
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
                                    <p><strong>Madhulam : </strong> Not Specified</p>
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
            
            # Get the Profile_for value and lookup the corresponding ModeName
            profile_for_mode = models.Profileholder.objects.get(Mode=registration.Profile_for)
            profile_for_name = profile_for_mode.ModeName

            try:
                marital_status = models.ProfileMaritalstatus.objects.get(StatusId=registration.Profile_marital_status)
                marital_status_name = marital_status.MaritalStatus
            except models.ProfileMaritalstatus.DoesNotExist:
                marital_status_name = None

            try:
                complexion = models.Profilecomplexion.objects.get(complexion_id=registration.Profile_complexion)
                complexion_name = complexion.complexion_desc
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

            data = {
                "personal_profile_name": registration_serializer.data.get("Profile_name"),
                "personal_gender": registration_serializer.data.get("Gender"),
                "personal_age": registration_serializer.data.get("age"),
                "personal_profile_dob": registration_serializer.data.get("Profile_dob"),
                "personal_place_of_birth": horoscope_serializer.data.get("place_of_birth"),
                "personal_time_of_birth": horoscope_serializer.data.get("time_of_birth"),
                "personal_profile_height": registration_serializer.data.get("Profile_height"),
                "personal_profile_marital_status_id": registration_serializer.data.get("Profile_marital_status"),
                "personal_profile_marital_status_name": marital_status_name,
                "personal_blood_group": familydetails_serializer.data.get("blood_group"),
                "personal_about_self": familydetails_serializer.data.get("about_self"),
                "personal_profile_complexion_id": registration_serializer.data.get("Profile_complexion"),
                "personal_profile_complexion_name": complexion_name,
                "personal_hobbies": familydetails_serializer.data.get("hobbies"),
                "personal_pysically_changed": familydetails_serializer.data.get("Pysically_changed"),
                "personal_profile_for_id":  registration_serializer.data.get("Profile_for"),
                "personal_profile_for_name": profile_for_name,
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

        print('1234mars')
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
        planet_mapping = {
            1: "Sun",
            2: "Moon",
            3: "Mars",
            4: "Mercury",
            5: "Jupiter",
            6: "Venus",
            7: "Saturn",
            8: "Rahu",
            9: "Kethu",
            10: "Lagnam",
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
            if 3 in planets:  # Mars
                mars_position = int(grid_num.split()[1])
            if 8 in planets:  # Rahu
                rahu_positions.append(int(grid_num.split()[1]))
            if 9 in planets:  # Kethu
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

        # Calculate mars position from lagnam
        mars_position_from_lagnam = calculate_position(lagnam_position, mars_position)

        # Determine if there is Mars dosham
        mars_dosham = False
        if mars_position_from_lagnam in {1, 2, 4, 7, 8, 12}:
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
        
        try:
            # Check if request data is empty
            if not profile_id or not plan_id:
                return JsonResponse({"status": "error", "message": "profile_id and plan_id are required"}, status=status.HTTP_400_BAD_REQUEST)


            if not request.data:
                return JsonResponse({"status": "error", "message": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the instances by profile_id
            registration = models.Registration1.objects.get(ProfileId=profile_id)
             # Update the fields
            registration.Plan_id = plan_id
            registration.Addon_package = addon_package_id
            registration.Payment= total_amount
            
            # Save the changes
            registration.save()            

                                   
            # Success response
            return JsonResponse({
                    "status": "success",
                    "message": "Plans and packages updated successfully",
                    "data_message": f"Thank you for registering in Vysyamala. Your Profile Id is  {profile_id} . Thanks a bunch for filling that out. It means a lot to us, just like you do! We really appreciate you giving us a moment of your time today. Thanks for being you!"
                }, status=status.HTTP_200_OK)
        
        except models.Registration1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        

def GetMarsRahuKethuDoshamDetails(raw_input):
    # def post(self, request):
        # Get the input data from the single text field
        # raw_input = request.data.get('input_data', '')
        # if not raw_input:
        #     raw_input = request.POST.get('input_data', '')
        # if not raw_input:
        #     raw_input = request.query_params.get('input_data', '')

        # Parse the input string to create the rasi_grid_data dictionary
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
        planet_mapping = {
            1: "Sun",
            2: "Moon",
            3: "Mars",
            4: "Mercury",
            5: "Jupiter",
            6: "Venus",
            7: "Saturn",
            8: "Rahu",
            9: "Kethu",
            10: "Lagnam",
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
            if 3 in planets:  # Mars
                mars_position = int(grid_num.split()[1])
            if 8 in planets:  # Rahu
                rahu_positions.append(int(grid_num.split()[1]))
            if 9 in planets:  # Kethu
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

        # Calculate mars position from lagnam
        mars_position_from_lagnam = calculate_position(lagnam_position, mars_position)

        # Determine if there is Mars dosham
        mars_dosham = False
        if mars_position_from_lagnam in {1, 2, 4, 7, 8, 12}:
            mars_dosham = True

        # Determine if there is Rahu-Kethu dosham
        critical_positions = {1, 2, 7, 8}
        rahu_kethu_dosham = False

        # Check if any Rahu or Kethu position falls within the critical positions
        if any(pos in critical_positions for pos in rahu_positions_from_lagnam) or \
           any(pos in critical_positions for pos in kethu_positions_from_lagnam):
            rahu_kethu_dosham = True

        # Debugging: Print positions and dosham status
        print(f"Lagnam position: {lagnam_position}")
        print(f"Rahu positions from Lagnam: {rahu_positions_from_lagnam}")
        print(f"Kethu positions from Lagnam: {kethu_positions_from_lagnam}")
        print(f"Rahu-Kethu Dosham: {rahu_kethu_dosham}")
        print(f"mars_position_from_lagnam: {mars_position_from_lagnam}")
        print(f"mars_dosham: {mars_dosham}")

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

            # family_status_id = serializer.data.get("family_status")
            # family_status = models.Familystatus.objects.get(id=family_status_id)
            # family_status_serializer = serializers.FamilyStatusSerializer(family_status)

            # father_occupation_id = serializer.data.get("father_occupation")
            # mother_occupation_id = serializer.data.get("mother_occupation")

            # father_occupation = models.Parentoccupation.objects.get(id=father_occupation_id)
            # mother_occupation = models.Parentoccupation.objects.get(id=mother_occupation_id)


            try:
                family_status_id = serializer.data.get("family_status")
                
                # Check if the family_status_id is purely numeric
                if family_status_id.isdigit():
                    family_status = models.Familystatus.objects.get(id=family_status_id)
                    family_status_serializer = serializers.FamilyStatusSerializer(family_status)
                else:
                    # If family_status_id is alphanumeric or not valid, set family_status to None
                    family_status = None

            except models.Familystatus.DoesNotExist:
                family_status = None



            try:
                father_occupation_id = serializer.data.get("father_occupation")
                
                if father_occupation_id.isdigit():  # Check if the value is numeric
                    father_occupation = models.Parentoccupation.objects.get(id=father_occupation_id)
                else:
                    father_occupation = None  # Set to None if the ID is alphanumeric or invalid
                    father_occupation_id=None

                    
            except models.Parentoccupation.DoesNotExist:
                father_occupation = None
                father_occupation_id = None
            except ValueError:
                father_occupation = None  # Handle invalid type for ID (e.g., non-numeric string)
                father_occupation_id=None


            try:
                mother_occupation_id = serializer.data.get("mother_occupation")
                
                # Check if the mother_occupation_id is a valid number
                if mother_occupation_id.isdigit():
                    mother_occupation = models.Parentoccupation.objects.get(id=mother_occupation_id)
                else:
                    # If mother_occupation_id is alphanumeric, set mother_occupation to None
                    mother_occupation = None
                    mother_occupation_id=None

            except models.Parentoccupation.DoesNotExist:
                mother_occupation = None
                mother_occupation_id=None
            except ValueError:
                mother_occupation = None  # Handle cases where the ID is not a number or valid format
                mother_occupation_id=None
             
             
            data = {
                "personal_about_fam": serializer.data.get("about_family"),
                "personal_father_name": serializer.data.get("father_name"),
                "personal_father_occu_id": father_occupation_id,
                "personal_father_occu_name": father_occupation,  
                "personal_mother_name": serializer.data.get("mother_name"),
                "personal_mother_occu_id": mother_occupation_id,
                "personal_mother_occu_name": mother_occupation,  
                "personal_fam_sta_id": family_status_id,
                #"personal_fam_sta_name": family_status_serializer.data.get("status"),
                "personal_fam_sta_name": family_status,
                "personal_sis": serializer.data.get("no_of_sister"),
                "personal_sis_married": serializer.data.get("no_of_sis_married"),
                "personal_bro": serializer.data.get("no_of_brother"),
                "personal_bro_married": serializer.data.get("no_of_bro_married"),
                "personal_prope_det": serializer.data.get("property_details"),
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

            if serializer.is_valid():
                serializer.save()

                family_status_id = request.data.get("family_status")
                if family_status_id:
                    family_status = models.Familystatus.objects.get(id=family_status_id)
                    family_details.family_status = family_status_id
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

            birthstar_id = horoscope.birthstar_name  
            birthstar = models.Birthstar.objects.get(id=birthstar_id)
            birthstar_name = birthstar.star

            rasi_id = horoscope.birth_rasi_name  
            rasi = models.Rasi.objects.get(id=rasi_id)
            rasi_name = rasi.name

            lagnam_didi_id = horoscope_serializer.data.get("lagnam_didi")
            lagnam_didi = models.Lagnamdidi.objects.get(id=lagnam_didi_id)
            lagnam_didi_name = lagnam_didi.name

            data = {
                "personal_bthstar_id": birthstar_id,
                "personal_bthstar_name": birthstar_name,
                "personal_bth_rasi_id": rasi_id,
                "personal_bth_rasi_name": rasi_name,
                "personal_lagnam_didi_id": lagnam_didi_id,
                "personal_lagnam_didi_name": lagnam_didi_name,
                "personal_chevvai_dos": horoscope_serializer.data.get("chevvai_dosaham"),
                "personal_ragu_dos": horoscope_serializer.data.get("ragu_dosham"),
                "personal_nalikai": horoscope_serializer.data.get("nalikai"),
                "personal_surya_goth": family_serializer.data.get("suya_gothram"),
                "personal_dasa": horoscope_serializer.data.get("dasa_name"),
                "personal_dasa_bal": horoscope_serializer.data.get("dasa_balance"),
                "personal_rasi_katt": horoscope_serializer.data.get("rasi_kattam"),
                "personal_amsa_katt": horoscope_serializer.data.get("amsa_kattam")
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
        if not profile_id:
            return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            horoscope = models.Horoscope.objects.get(profile_id=profile_id)
            family_details = models.Familydetails.objects.get(profile_id=profile_id)

            horoscope_serializer = serializers.HoroscopeSerializer(horoscope, data=request.data, partial=True)
            if horoscope_serializer.is_valid():
                horoscope_serializer.save()
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
                education_level = models.Edupref.objects.get(RowId=highest_education_id)
                education_level_name = education_level.EducationLevel
            except models.Edupref.DoesNotExist:
                education_level_name = None

            annual_income_id = education_serializer.data.get("anual_income")
            try:
                annual_income = models.Annualincome.objects.get(id=annual_income_id)
                annual_income_name = annual_income.income
            except models.Annualincome.DoesNotExist:
                annual_income_name = None

            work_country_id = education_serializer.data.get("work_country")
            try:
                work_country = models.Profilecountry.objects.get(id=work_country_id) if work_country_id else None
                work_country_name = work_country.name if work_country else None
            except models.Profilecountry.DoesNotExist:
                work_country_name = None

            work_state_id = education_serializer.data.get("work_state")
            try:
                work_state = models.Profilestate.objects.get(id=work_state_id) if work_state_id else None
                work_state_name = work_state.name if work_state else None
            except models.Profilestate.DoesNotExist:
                work_state_name = None

            data = {
                "personal_edu_id": highest_education_id,
                "personal_edu_name": education_level_name,
                "persoanl_edu_details": education_serializer.data.get("education_details"),
                "personal_about_edu": education_serializer.data.get("about_edu"),
                "personal_profession": education_serializer.data.get("profession"),
                "personal_ann_inc_id": annual_income_id, 
                "personal_ann_inc_name": annual_income_name, 
                "personal_gross_ann_inc": education_serializer.data.get("actual_income"),
                "personal_work_coun_id": work_country_id,
                "personal_work_coun_name": work_country_name,
                "personal_work_sta_id": work_state_id,
                "personal_work_sta_name": work_state_name,
                "personal_work_pin": education_serializer.data.get("work_pincode"),
                "personal_career_plans": education_serializer.data.get("career_plans"),
            }

            response = {
                "status": "success",
                "message": "Personal details fetched successfully",
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

class UpdateMyProfileEducation(APIView):
    def post(self, request):
        try:
            profile_id = request.data.get('profile_id')

            if not profile_id:
                return JsonResponse({"status": "error", "message": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            education = models.Edudetails.objects.get(profile_id=profile_id)

            education_serializer = serializers.PersonalEdudetailsSerializer(education, data=request.data, partial=True)

            if education_serializer.is_valid():
                validated_data = education_serializer.validated_data

                highest_education_id = request.data.get('education_level')
                if highest_education_id is not None:
                    try:
                        highest_education_id = int(highest_education_id)
                        if models.Edupref.objects.filter(RowId=highest_education_id).exists():
                            education.highest_education = highest_education_id
                        else:
                            return JsonResponse({"status": "error", "message": "Invalid education level ID"}, status=status.HTTP_400_BAD_REQUEST)
                    except ValueError:
                        return JsonResponse({"status": "error", "message": "Education level ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

                anual_income_id = request.data.get('annual_income')
                if anual_income_id is not None:
                    try:
                        anual_income_id = int(anual_income_id)
                        if models.Annualincome.objects.filter(id=anual_income_id).exists():
                            education.anual_income = anual_income_id
                        else:
                            return JsonResponse({"status": "error", "message": "Invalid annual income ID"}, status=status.HTTP_400_BAD_REQUEST)
                    except ValueError:
                        return JsonResponse({"status": "error", "message": "Annual income ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

                education_serializer.save()

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
            print("Exception:", e)
            return JsonResponse({
                "status": "error",
                "message": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


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

        country_name = models.Profilecountry.objects.filter(id=country_id).first().name if country_id else "Country not found"
        state_name = models.Profilestate.objects.filter(id=state_id).first().name if state_id else "State not found"
        
        data = {
            "personal_prof_addr": contact_serializer.data.get("Profile_address"),
            "personal_prof_city": contact_serializer.data.get("Profile_city"),
            "personal_prof_stat_id": contact_serializer.data.get("Profile_state"),
            "personal_prof_stat_name": state_name,
            "personal_prof_count_id": contact_serializer.data.get("Profile_country"),
            "personal_prof_count_name": country_name,
            "personal_prof_pin": contact_serializer.data.get("Profile_pincode"),
            "personal_prof_phone": contact_serializer.data.get("Profile_alternate_mobile"),
            "personal_prof_mob_no": contact_serializer.data.get("Profile_mobile_no"),
            "personal_prof_whats": contact_serializer.data.get("Profile_whatsapp"),
            "personal_email": contact_serializer.data.get("EmailId"),
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

            if state_id is not None:
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
            "partner_fgn_Int": partner_serializer.data.get("pref_foreign_intrest"),
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

        serializer = serializers.ParPrefSerializer(partner_preferences, data=request.data, partial=True)

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
        SELECT a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income , e.birthstar_name , e.birth_rasi_name
                       ,a.Photo_protection,a.Gender        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        WHERE a.gender != %s AND a.ProfileId != %s
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
                base_query += " AND a.Profile_marital_status = %s"
                query_params.append(marital_status)

            # Add profession filter
            if profession:
                base_query += " AND f.profession = %s"
                query_params.append(profession)

            # Add education filter
            if education:
                base_query += " AND f.highest_education = %s"
                query_params.append(education)

            # Add income filter
            if income:
                base_query += " AND h.income >= %s"
                query_params.append(income)

            # Add star filter
            if star:
                base_query += " AND d.star = %s"
                query_params.append(star)

            if chevvai_dhosam:
                base_query += " AND e.calc_chevvai_dhosham = %s"
                query_params.append(chevvai_dhosam)
            
            if ragukethu_dhosam:
                base_query += " AND e.calc_raguketu_dhosham = %s"
                query_params.append(ragukethu_dhosam)

            if native_state:
                base_query += " AND a.Profile_state = %s"
                query_params.append(native_state)

            if search_worklocation:
                base_query += " AND f.work_state = %s"
                query_params.append(search_worklocation)


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


            # Add pagination to the query
            # Modify the query to use LIMIT with start and count
            base_query += f" LIMIT %s, %s"
            query_params.extend([start, per_page])

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
                        # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': full_query}, status=status.HTTP_404_NOT_FOUND)
                        return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetFeaturedList(APIView):

    def post(self, request):
        # Extract the input data from the JSON body (POST request)
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'profile_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get gender from logindetails table
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

        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')

        # Set default values if not provided
        per_page = int(received_per_page) if received_per_page else 10
        page_number = int(received_page_number) if received_page_number else 1

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        # Initialize the query with the base structure
        base_query = """
        SELECT a.*, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income
        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        WHERE a.gender != %s AND a.ProfileId != %s AND a.Featured_profile = 1
        """

        # Prepare the query parameters
        query_params = [gender, profile_id]

        # Check if additional filters are provided, and add them to the query
        if from_age or to_age or from_height or to_height:
            # Add age filter
            age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=" if from_age else "<=" if to_age else None
            if age_condition_operator:
                base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
                if from_age and to_age:
                    query_params.extend([from_age, to_age])
                else:
                    query_params.append(from_age or to_age)
            
            if from_height and to_height:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([from_height, to_height])
            elif from_height:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(from_height)
            elif to_height:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(to_height)

        count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_query"

                    # Execute the count query to get the total number of records
        with connection.cursor() as cursor:
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()[0]  # Fetch the count




        base_query += " LIMIT %s, %s"
        query_params.extend([start, per_page])

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



                    print(full_query)  
                    return JsonResponse({
                        'status': 'success',
                        'total_count':total_count,
                        # 'data': results,
                        'data':transformed_results,
                        # 'query': full_query,  
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
        



class SuggestedProfiles1(APIView):

    def post(self, request):
        # Extract the input data from the JSON body (POST request)
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return JsonResponse({'status': 'failure', 'message': 'Profile ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get gender from logindetails table
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

        received_per_page = request.data.get('per_page')
        received_page_number = request.data.get('page_number')

        # Set default values if not provided
        per_page = int(received_per_page) if received_per_page else 10
        page_number = int(received_page_number) if received_page_number else 1

        # Ensure valid values for pagination
        per_page = max(1, per_page)
        page_number = max(1, page_number)

        # Calculate the starting record for the SQL LIMIT clause
        start = (page_number - 1) * per_page

        # Initialize the query with the base structure
        base_query = """
        SELECT a.*, 
               f.profession, f.highest_education, g.EducationLevel, d.star, h.income
        FROM logindetails a 
        JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
        JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
        JOIN masterbirthstar d ON d.id = e.birthstar_name 
        JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
        JOIN mastereducation g ON f.highest_education = g.RowId 
        JOIN masterannualincome h ON h.id = f.anual_income
        WHERE a.gender != %s AND a.ProfileId != %s AND a.Featured_profile = 1
        """

        # Prepare the query parameters
        query_params = [gender, profile_id]

        # Check if additional filters are provided, and add them to the query
        if from_age or to_age or from_height or to_height:
            # Add age filter
            age_condition_operator = "BETWEEN %s AND %s" if from_age and to_age else ">=" if from_age else "<=" if to_age else None
            if age_condition_operator:
                base_query += f" AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {age_condition_operator}"
                if from_age and to_age:
                    query_params.extend([from_age, to_age])
                else:
                    query_params.append(from_age or to_age)
            
            if from_height and to_height:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([from_height, to_height])
            elif from_height:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(from_height)
            elif to_height:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(to_height)

        count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_query"

                    # Execute the count query to get the total number of records
        with connection.cursor() as cursor:
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()[0]  # Fetch the count




        base_query += " LIMIT %s, %s"
        query_params.extend([start, per_page])

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



                    print(full_query)  
                    return JsonResponse({
                        'status': 'success',
                        'total_count':total_count,
                        # 'data': results,
                        'data':transformed_results,
                        # 'query': full_query,  
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
        "profession": original_data.get("profession"),
        "location": original_data.get("Profile_city"),      # Default value

    }
    return transformed_data







def transform_data(original_data,my_profile_id,my_gender,source_rasi_id,source_star_id):

    # print('original_data',original_data)

    transformed_data = {
        "profile_id": original_data.get("ProfileId"),
        "profile_name": original_data.get("Profile_name"),
        "profile_age": calculate_age(original_data.get("Profile_dob")),
        "profile_gender": original_data.get("Gender"),
        "profile_img": Get_profile_image(original_data.get("ProfileId"),my_gender,1,original_data.get("Photo_protection")),
        "profile_height": original_data.get("Profile_height"),
        "weight": None,  # You need to add this if you have this information
        "degree": original_data.get("EducationLevel"),
        "star": original_data.get("star"),
        "profession": original_data.get("profession"),
        "location": original_data.get("Profile_city"),
        "photo_protection": original_data.get("Photo_protection"),  # Default value
        "matching_score":Get_matching_score(source_star_id,source_rasi_id,original_data.get("birthstar_name"),original_data.get("birth_rasi_name"),my_gender),    # Default value
        "wish_list": Get_wishlist(my_profile_id,original_data.get("ProfileId")),          # Default value

    }
    return transformed_data


class Get_Profession(APIView):

    def post(self, request):
        try:
            professions = models.MasterProfession.objects.all()
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
                    user = models.Registration1.objects.get(ProfileId=profile_id)
                    email = user.EmailId  # Override email with the one from the user record
                else:
                    # Fetch user by email
                    user = models.Registration1.objects.get(EmailId=email)

                otp = str(secrets.randbelow(1000000)).zfill(6)
                logging.debug(f"Generated OTP: {otp}")

                user.Reset_OTP = otp
                user.Reset_OTP_Time = timezone.now() 
                logging.debug(f"Setting OTP: {otp} for user with ProfileId: {user.ProfileId}")
                user.save()
                logging.debug(f"Saved OTP: {user.Reset_OTP} for user with ProfileId: {user.ProfileId}")

                context = {
                    'profile_id': user.ProfileId,
                    'otp': otp,
                    'logo_url': 'https://vysyamala.com/img/newlogo.png',
                }

                subject = "Your Password Reset OTP"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [email]
                html_content = render_to_string('user_api/authentication/forget_password.html', context)

                email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()
                
                return JsonResponse({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
            
            except models.Registration1.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            except Exception as e:
                logging.error(f"Error sending OTP: {e}")
                return JsonResponse({"error": "An error occurred while sending the OTP. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def is_otp_valid(user):
    otp_expiry_time = user.Reset_OTP_Time + timedelta(minutes=5)
    current_time = timezone.now()
    
    if current_time > otp_expiry_time:
        return False  
    return True  

class ResetPassword(APIView):
    def post(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            try:
                user = models.Registration1.objects.get(ProfileId=profile_id)

                if user.Reset_OTP != otp:
                    return JsonResponse({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

                if not is_otp_valid(user):
                    return JsonResponse({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

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
    






class FeaturedProfile(APIView):
    def post(self, request):
        gender = request.query_params.get('gender') or request.data.get('gender')
        

        if not gender:
            return JsonResponse({"Status": 0, "message": "Gender is required"}, status=status.HTTP_400_BAD_REQUEST)

        normalized_gender = gender.strip().lower()

        try:
            print(f"Normalized Gender: {normalized_gender}")

            profile_details = models.Registration1.objects.filter(
                Gender__iexact=normalized_gender, Featured_profile=1
            )

            print(f"Number of profiles found: {profile_details.count()}")

            if not profile_details.exists():
                return JsonResponse({"Status": 0, "message": "No featured profiles found"}, status=status.HTTP_200_OK)

            profile_ids = profile_details.values_list('ProfileId', flat=True)

            edu_details = models.Edudetails.objects.filter(profile_id__in=profile_ids)

            profession_id_mapping = {edu.profile_id: edu.profession for edu in edu_details}
            highest_education_mapping = {edu.profile_id: edu.highest_education for edu in edu_details}

            professions = models.Profespref.objects.all()

            degrees = models.Highesteducation.objects.all()

            profession_mapping = {str(prof.RowId): prof.profession for prof in professions}
            degree_mapping = {str(degree.id): degree.degree for degree in degrees}

            restricted_profile_details = [
                {
                    "profile_id": detail.ProfileId,
                    "profile_name": detail.Profile_name,
                    "profile_img": Get_profile_image(detail.ProfileId, normalized_gender, 1, detail.Photo_protection),
                    "profile_age": calculate_age(detail.Profile_dob),
                    "profile_gender": detail.Gender,
                    "height": detail.Profile_height,
                    "degree": degree_mapping.get(str(highest_education_mapping.get(detail.ProfileId, "")), ""),  
                    "profession": profession_mapping.get(str(profession_id_mapping.get(detail.ProfileId, "")), ""), 
                    "location": detail.Profile_city
                }
                for detail in profile_details
            ]

            return JsonResponse({
                "Status": 1,
                "message": "Featured profiles fetched successfully",
                "profiles": restricted_profile_details
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"Status": 0, "message": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        








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
        WHERE a.gender != %s AND a.ProfileId != %s AND a.ProfileId = %s
        """

        # Prepare the query parameters
        query_params = [gender, profile_id , search_profile_id]

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
                    return JsonResponse({'status': 'failure', 'message': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

                    # vysassist_cond = {'status': 1,'profile_from':profile_id}
                    # vysassist_count = count_records(models.Profile_vysassist, vysassist_cond)
                    
                    restricted_profile_details = [
                        {
                            "vys_profileid": detail.get("ProfileId"),
                            "vys_profile_name": detail.get("Profile_name"),
                            "vys_Profile_img": Get_profile_image(detail.get("ProfileId"),detail.get("Gender"),1,detail.get("Photo_protection")),
                            "vys_profile_age": calculate_age(detail.get("Profile_dob")),
                            "vys_verified":detail.get("Profile_verified"),
                            "vys_height":detail.get("Profile_height"),
                            "vys_star":detail.get("star_name"),
                            "vys_profession":detail.get("profession"),
                            "vys_city":detail.get("Profile_city"),
                            "vys_degree":get_degree(detail.get("ug_degeree")),
                            "vys_match_score":Get_matching_score(my_star_id,my_rasi_id,detail.get("birthstar_name"),detail.get("birth_rasi_name"),my_gender),
                            "vys_views":count_records(models.Profile_visitors, {'status': 1,'viewed_profile':detail.get("ProfileId")}),
                            "vys_lastvisit": get_user_statusandlastvisit(detail.get("Last_login_date"))[0],
                            "vys_userstatus": get_user_statusandlastvisit(detail.get("Last_login_date"))[1],
                            "vys_horoscope": "Horoscope Available" if detail.get("horoscope_file") else "Horoscope Not Available",
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
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



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
                print('Hai')
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

        base_url = 'http://103.214.132.20:8000'

        # Modify the serialized data to include the full image URL
        serialized_data = serializer.data
        for item in serialized_data:
            item['photo'] = f"{base_url}{item['photo']}"
        
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

        base_url = 'http://103.214.132.20:8000'

        serialized_data = serializer.data
        for item in serialized_data:
            item['image'] = f"{base_url}{item['image']}"
        
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

        base_url = 'http://103.214.132.20:8000'

        serialized_data = serializer.data
        for item in serialized_data:
            item['user_image'] = f"{base_url}{item['user_image']}"
        
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
        
        if not any([gender,from_age, to_age, native_state,profession]):
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

                        transformed_results = [transform_data2(result, gender) for result in results]

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
                return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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