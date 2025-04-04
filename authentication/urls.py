# urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 
# from .views import WithoutAddressSendEmailAPI,HoroscopeKattamAPI


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('Registrationstep1/', views.Registrationstep1.as_view(), name='Registrationstep1'),
    path('Registrationstep2/', views.Registrationstep2.as_view(), name='Registrationstep1'),
    path('Otp_verify/', views.Otp_verify.as_view(), name='Otp_verify'),
    path('Get_Profileholder/', views.Get_Profileholder.as_view(), name='Get_Profileholder'),
    path('Get_Height/', views.Get_Height.as_view(), name='Get_Height'),
    path('Get_Complexion/', views.Get_Complexion.as_view(), name='Get_Complextion'),
    path('Get_Country/', views.Get_Country.as_view(), name='Get_Country'),
    path('Get_State/', views.Get_State.as_view(), name='Get_State'),
    path('Get_City/', views.Get_City.as_view(), name='Get_City'),
    path('Get_Marital_Status/', views.Get_Marital_Status.as_view(), name='Get_Marital_Status'),
    path('Get_Parent_Occupation/', views.Get_Parent_Occupation.as_view(), name='Get_Parent_Occupation'),
    path('ImageSetUpload/', views.ImageSetUpload.as_view(), name='ImageSetUpload'),
    path('Get_profile_images/', views.Get_profile_images.as_view(), name='Get_profile_images'),
    
    path('Horoscope_upload/', views.Horoscope_upload.as_view(), name='Horoscope_upload'),
    path('Idproof_upload/', views.Idproof_upload.as_view(), name='Idproof_upload'),
    path('Divorceproof_upload/', views.Divorceproof_upload.as_view(), name='Divorceproof_upload'),
    path('Photo_Id_Settings/', views.Photo_Id_Settings.as_view(), name='Photo_Id_Settings'),


    path('ListProfileImagesView/', views.ListProfileImagesView.as_view(), name='ListProfileImagesView'),

    path('Get_Property_Worth/', views.Get_Property_Worth.as_view(), name='Get_Property_Worth'),
    path('Get_Highest_Education/', views.Get_Highest_Education.as_view(), name='Get_Highest_Education'),
    path('Get_Ug_Degree/', views.Get_Ug_Degree.as_view(), name='Get_Ug_Degree'),
    path('Get_Field_ofstudy/', views.Get_Field_ofstudy.as_view(), name='Get_Field_ofstudy'),
    path('Get_Degree_list/', views.Get_Degree_list.as_view(), name='Get_Degree_list'),
    path('Get_Annual_Income/', views.Get_Annual_Income.as_view(), name='Get_Annual_Income'),
    path('Get_Place_Of_Birth/', views.Get_Place_Of_Birth.as_view(), name='Get_Place_Of_Birth'),
    path('Get_Lagnam_Didi/', views.Get_Lagnam_Didi.as_view(), name='Get_Lagnam_Didi'),
    path('Get_Dasa_Name/', views.Get_Dasa_Name.as_view(), name='Get_Dasa_Name'),
    path('Get_Birth_Star/', views.Get_Birth_Star.as_view(), name='Get_Birth_Star'),
    path('Get_Rasi/', views.Get_Rasi.as_view(), name='Get_Rasi'),

    path('Get_District/', views.Get_District.as_view(), name='Get_District'),
    path('Get_City/', views.Get_City.as_view(), name='Get_City'),

    path('Contact_registration/', views.Contact_registration.as_view(), name='Contact_registration'),
   
    
    # path('api/send-sms/', views.SendSMS.as_view(), name='send_sms'),
    path('Get_FamilyType/', views.Get_FamilyType.as_view(), name='Get_FamilyType'),
    path('Get_FamilyValue/', views.Get_FamilyValue.as_view(), name='Get_FamilyValue'),
    path('Get_FamilyStatus/', views.Get_FamilyStatus.as_view(), name='Get_FamilyStatus'),
    path('Get_Matchstr_Pref/', views.Get_Matchstr_Pref.as_view(), name='Get_Matchstr_Pref'),
    path('Get_State_Pref/', views.Get_State_Pref.as_view(), name='Get_State_Pref'),
    path('Get_Edu_Pref/', views.Get_Edu_Pref.as_view(), name='Get_Edu_Pref'),
    path('Get_Profes_Pref/', views.Get_Profes_Pref.as_view(), name='Get_Profes_Pref'),
    path('Horoscope_registration/', views.Horoscope_registration.as_view(), name='Horoscope_registration'),
    path('Family_registration/', views.Family_registration.as_view(), name='Family_registration'),
    path('Education_registration/', views.Education_registration.as_view(), name='Education_registration'),
    path('Partner_pref_registration/', views.Partner_pref_registration.as_view(), name='Partner_pref_registration'),
    path('Get_save_details/', views.Get_save_details.as_view(), name='Get_save_details'),
    path('Get_resend_otp/', views.Get_resend_otp.as_view(), name='Get_resend_otp'),
    path('Get_palns/', views.Get_palns.as_view(), name='Get_palns'),
    
    path('Login_with_mobileno/', views.Login_with_mobileno.as_view(), name='Login_with_mobileno'),
    path('Login_verifyotp/', views.Login_verifyotp.as_view(), name='Login_verifyotp'),
    path('Get_prof_list_match/', views.Get_prof_list_match.as_view(), name='Get_prof_list_match'),
    path('Get_profile_det_match/', views.Get_profile_det_match.as_view(), name='Get_profile_det_match'),
    path('Send_profile_intrests/', views.Send_profile_intrests.as_view(), name='Send_profile_intrests'),
    path('Get_profile_intrests_list/', views.Get_profile_intrests_list.as_view(), name='Get_profile_intrests_list'),
    path('Update_profile_intrests/', views.Update_profile_intrests.as_view(), name='Update_profile_intrests'),
    path('My_intrests_list/', views.My_intrests_list.as_view(), name='My_intrests_list'),
    
    path('Get_mutual_intrests/', views.Get_mutual_intrests.as_view(), name='Get_mutual_intrests'),

    path('Mark_profile_wishlist/', views.Mark_profile_wishlist.as_view(), name='Mark_profile_wishlist'),
    path('Get_profile_wishlist/', views.Get_profile_wishlist.as_view(), name='Get_profile_wishlist'),


    path('Create_profile_visit/', views.Create_profile_visit.as_view(), name='Create_profile_visit'),
    path('My_viewed_profiles/', views.My_viewed_profiles.as_view(), name='My_viewed_profiles'),
    path('My_profile_visit/', views.My_profile_visit.as_view(), name='My_profile_visit'),

    path('Get_personal_notes/', views.Get_personal_notes.as_view(), name='Get_personal_notes'),
    path('Save_personal_notes/', views.Save_personal_notes.as_view(), name='Save_personal_notes'),


    path('Get_dashboard_details/', views.Get_dashboard_details.as_view(), name='Get_dashboard_details'),
    path('Send_photo_request/', views.Send_photo_request.as_view(), name='Send_photo_request'),
    path('Get_photo_request_list/', views.Get_photo_request_list.as_view(), name='Get_photo_request_list'),
    path('Update_photo_request/', views.Update_photo_request.as_view(), name='Update_photo_request'),

    path('Get_notification_list/', views.Get_notification_list.as_view(), name='Get_notification_list'),
    path('Read_notifications/', views.Read_notifications.as_view(), name='Read_notifications'),

    path('User_change_password/', views.User_change_password.as_view(), name='User_change_password'),
    path('ImageSetEdit/', views.ImageSetEdit.as_view(), name='ImageSetEdit'),
    
    path('Set_photo_password/', views.Set_photo_password.as_view(), name='Set_photo_password'),

    path('Get_photo_bypassword/', views.Get_photo_bypassword.as_view(), name='Get_photo_bypassword'),


    path('Get_common_details/', views.Get_common_details.as_view(), name='Get_common_details'),

    path('Get_addon_packages/', views.Get_addon_packages.as_view(), name='Get_addon_packages'),
      
    path('generate-pdf/<str:user_profile_id>/',  views.render_pdf_view, name='generate_pdf'),

      
    path('get_myprofile_personal/', views.GetMyProfilePersonal.as_view(), name='get_myprofile_personal'),
   
    path('update_myprofile_personal/', views.UpdateMyProfilePersonal.as_view(), name='update_myprofile_personal'),

    path('Remove_profile_img/', views.Remove_profile_img.as_view(), name='Remove_profile_img'),

    path('Save_plan_package/', views.Save_plan_package.as_view(), name='Save_plan_package'),    

    #path('profile/update/page1/', views.ProfileUpdateForPage1APIView.as_view(), name='profile-update-page1'),    
           

    path('get_myprofile_family/', views.GetMyProfileFamily.as_view(), name='get_my_profile_family'),

    path('update_myprofile_family/', views.UpdateMyProfileFamily.as_view(), name='update_myprofile_family'),

    path('get_myprofile_horoscope/', views.GetMyProfileHoroscope.as_view(), name='get_myprofile_horoscope'),

    path('update_myprofile_horoscope/',views.UpdateMyProfileHoroscope.as_view(), name='update_myprofile_horoscope'),


    path('get_myprofile_education/', views.GetMyProfileEducation.as_view(), name='get_myprofile_education'),

    path('update_myprofile_education/', views.UpdateMyProfileEducation.as_view(), name='update_education_details'),


    path('get_myprofile_contact/', views.GetMyProfileContact.as_view(), name='get_myprofile_contact'),

    path('update_myprofile_contact/', views.UpdateMyProfileContact.as_view(), name='get_myprofile_contact'),
    

    path('Get_enabled_notifications/', views.GetAlertSettingsByProfile.as_view(), name='Get_enabled_notifications'),

    path('Update_notification_settings/', views.UpdateNotificationSettings.as_view(), name='Update_notification_settings'),
    
    path('Get_alert_settings/', views.GetAlertSettings.as_view(), name='Get_alert_settings'),

    path('Get_myprofile_partner/', views.GetMyProfilePartner.as_view(), name='get_myprofile_partner'),

    path('Update_myprofile_partner/', views.UpdateMyProfilePartner.as_view(), name='update_myprofile_partner'),

    path('Get_advance_search/',views.GetSearchResults.as_view(), name='GetSearchResults'),

    path('Get_Featured_List/',views.GetFeaturedList.as_view(), name='Get_Featured_List'),

    path('Get_photo_protection/', views.PhotoProtectionView.as_view(), name='Get_photo_protection'),

    path('Update_photo_password/', views.UpdatePhotoPasswordView.as_view(), name='update_photo_password'),
    
    path('Get_profession/', views.Get_Profession.as_view(), name='Get_profession'),

    path('Forget_password/', views.ForgetPassword.as_view(), name='forget_password'),

    path('Forget_password_otp_verify/', views.ForgetPassword_otpverify.as_view(), name='Forget_password_otp_verify'),

    path('Reset_password/', views.ResetPassword.as_view(), name='reset_password_confirm'),

    path('Get_featured_profiles/', views.FeaturedProfile.as_view(), name='Get_featured_profiles'),
    
    path('Get_Suggested_List/', views.SuggestedProfiles1.as_view(), name='Suggested_profiles'),

    path('Search_byprofile_id/', views.Search_byprofile_id.as_view(), name='Search_byprofile_id'),


    path('My_vysassist_list/', views.My_vysassist_list.as_view(), name='My_vysassist_list'),
    path('Send_vysassist_request/', views.Send_vysassist_request.as_view(), name='Send_vysassist_request'),

    path('Click_call_request/', views.Click_call_request.as_view(), name='Click_call_request'),

    path('Get_Gallery_lists/', views.Get_Gallery_lists.as_view(), name='Get_Gallery_lists'),

    path('Success_stories/', views.SuccessStoryListView.as_view(), name='Success_stories'),

    path('Awards_gallery/', views.AwardListView.as_view(), name='Awards_gallery'),
    
    path('Testimonials/', views.TestimonialListView.as_view(), name='Testimonials'),

    path('Searchbeforelogin/', views.Searchbeforelogin.as_view(), name='Searchbeforelogin'),

    path('Get_page_details/', views.GetPageDetails.as_view(), name='get_page_details'),


    path('Get_expresint_status/', views.Get_expresint_status.as_view(), name='Get_expresint_status'),

    path('Just_registered/', views.JustRegisteredAPIView.as_view(), name='just_registered'),
    
    
     path('Active_happy_customers/', views.ActiveProfilesAndHappyCustomersAPIView.as_view(), name='active_happy_customers'),
     
     path('Get_footer/', views.GetFooterView.as_view(), name='get_footer'),
     path('Create_or_retrievechat/', views.CreateOrRetrieveChat.as_view(), name='Create_or_retrievechat'),
     path('Get_user_chatlist/', views.GetUserChat.as_view(), name='Get_user_chatlist'),
     path('Get_user_chatlist_search/', views.GetUserChat_search.as_view(), name='Get_user_chatlist_search'),
     path('GetMessages/', views.getMessages.as_view(), name='getMessages'),
     path('Homepage_cms/', views.HomepageListView.as_view(), name='homepage-list'),
     path('notify_to_profiles/', views.notify_to_profiles.as_view(), name='notify_to_profiles'),
     path('Get_district_pref/', views.Get_DistrictPref.as_view(), name='get_district_pref'),
     path('Update_profile_visibility/', views.Update_profile_visibility.as_view(), name='Update_profile_visibility'),
     path('Get_profile_visibility/', views.Get_profile_visibility.as_view(), name='Get_profile_visibility'),
     path('mark-as-read/<str:room_name>/', views.mark_messages_as_read, name='mark_as_read'),
     path('unread_message_count/', views.UnreadMessagesCountView.as_view(), name='unread_message_count'),
     path('Profile_other_fields/', views.Profile_other_fields.as_view(), name='Profile_other_fields'),
     path("create-orderid/", views.CreateOrderView.as_view(), name="create_orderid"),
     path("razorpay-webhook/", views.RazorpayWebhookView.as_view(), name="razorpay_webhook"),
     path("update-payment-status/", views.UpdatePaymentStatusView.as_view(), name="update-payment-status"),
     path("profile/<str:profile_id>/", views.profile_preview, name="profile_preview"),
     path("profile_view/<str:profile_id>/", views.profile_preview_withouphoto, name="profile_preview"),


     path('generate-porutham-pdf/', views.generate_porutham_pdf, name='generate_porutham_pdf'),
      
     path('My_horoscope_pdf_color/<str:user_profile_id>/',  views.My_horoscope_generate, name='horoscope_pdf'),

    path('My_horoscope_black/<str:user_profile_id>/',  views.My_horoscope, name='horoscope_pdf'),
    
    path('without-address-send-email/', WithoutAddressSendEmailAPI.as_view(), name='without_address_send_email'),
    # path('horoscope/kattam/', HoroscopeKattamAPI.as_view(), name='horoscope_kattam'),
    





      #  path('get_blurred_image/', views.get_blurred_image.as_view(), name='get_blurred_image'),
     path('', views.home, name='home'),
     path('<str:room>/', views.room, name='room'),
     path('checkview', views.checkview, name='checkview'),
     path('send', views.send, name='send'),
     
    #  path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
    


]