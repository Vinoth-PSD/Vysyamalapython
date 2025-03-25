from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
     ModeViewSet, ProfileHoroscopeViewSet,PropertyViewSet,GothramViewSet,EducationLevelViewSet,ProfessionViewSet,MasterStatePrefViewSet,Get_all_profiles, ProfilePartnerPrefViewSet, SignInView, ChangePasswordView, CountryViewSet, StateViewSet, DistrictViewSet,
     ProfileHolderViewSet, MaritalStatusViewSet, HeightViewSet,
    ComplexionViewSet, ParentsOccupationViewSet, HighestEducationViewSet, SubmitProfileAPIView, UgDegreeViewSet,
    AnnualIncomeViewSet,  BirthStarViewSet, RasiViewSet, LagnamViewSet,
    DasaBalanceViewSet, FamilyTypeViewSet, FamilyStatusViewSet, FamilyValueViewSet, LoginDetailsTempViewSet , Newprofile_get ,GetProfileDataView,LoginDetailsListCreateView, LoginDetailsDetailView , MatchViewSet , SuccessStoryViewSet, SuccessStoryListViewSet , AwardViewSet , AwardListViewSet , TestimonialViewSet , TestimonialListViewSet , CityViewSet , EditProfileAPIView , GetProfEditDetailsAPIView, fetch_login_details  , fetch_login_details_profile ,VysycommentsListViewSet
)
from .views import LoginDetailsViewSet, ProfileFamilyDetailsViewSet, ProfileEduDetailsViewSet, Newprofile_get, PageViewSet, PageListViewSet, PageEditView, PageDeleteView,  AdminSettingsView, AdminSettingsUpdateView, ImageUploadView,  AdminUserDetailView , list_admin_users , list_admin_users,list_roles, add_admin_user, edit_admin_user, delete_admin_user , SuccessStoryEditView, SuccessStoryDeleteView , AwardEditView , AwardDeleteView , TestimonialEditView,TestimonialDeleteView,export_excel , QuickUploadAPIView , ExpressInterestView , ViewedProfileByDateRangeView,PhotoRequestView , BookmarksView , ProfileImages , ProfileImagesView , GetMasterStatus , Get_prof_list_match , ProfileVysAssistView , HomepageListView, delete_profile, My_viewed_profiles, Get_photo_request_list, My_vysassist_list, Get_personal_notes, Exp_intrests_list , send_bulk_email, ProfileSendTo , Update_AdminComments ,GetSubMasterStatus , GetPlanbyStatus , ProfileVysAssistFollowupListCreateView , ProfileVysAssistFollowupRetrieveUpdateDeleteView , My_profiles_vistors , CallactionReceived , CallactionSent , Get_suggest_list_match , Exp_intrests_received , Exp_intrests_mutual , Matchingprintprofile , Matchingwhatsapp , Matchingsendemail ,Partnersettings , Suggestsettings ,GetallPlans


router = DefaultRouter()

router.register(r'profile_owner', ModeViewSet)
router.register(r'education-levels', EducationLevelViewSet) 
router.register(r'properties', PropertyViewSet)
router.register(r'gothrams', GothramViewSet) 
router.register(r'countries', CountryViewSet)
router.register(r'professions', ProfessionViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'stateprefs', MasterStatePrefViewSet)
router.register(r'states', StateViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'cities', CityViewSet)
router.register(r'profile-holders', ProfileHolderViewSet)
router.register(r'marital-statuses', MaritalStatusViewSet)
router.register(r'heights', HeightViewSet)
router.register(r'complexions', ComplexionViewSet)
router.register(r'parents-occupations', ParentsOccupationViewSet)
# router.register(r'highest-educations', HighestEducationViewSet)
router.register(r'ug-degrees', UgDegreeViewSet)
router.register(r'annual-incomes', AnnualIncomeViewSet)
router.register(r'birth-stars', BirthStarViewSet)
router.register(r'rasis', RasiViewSet)
router.register(r'lagnams', LagnamViewSet)
router.register(r'dasa-balances', DasaBalanceViewSet)
router.register(r'family-types', FamilyTypeViewSet)
router.register(r'family-statuses', FamilyStatusViewSet)
router.register(r'family-values', FamilyValueViewSet)
router.register(r'logindetails_temp', LoginDetailsTempViewSet, basename='logindetails_temp')
router.register(r'logzin-details-temp', LoginDetailsTempViewSet)
router.register(r'logindetails', LoginDetailsViewSet)
router.register(r'profile-familydetails', ProfileFamilyDetailsViewSet)
router.register(r'profile-edudetails', ProfileEduDetailsViewSet)
router.register(r'profile-partner-pref', ProfilePartnerPrefViewSet)
router.register(r'profile-horoscope', ProfileHoroscopeViewSet)
router.register(r'page', PageViewSet)
router.register(r'page-list', PageListViewSet, basename='page-list')
router.register(r'awards', AwardViewSet)
router.register(r'awards_list', AwardListViewSet, basename='award_list')
router.register(r'success_stories', SuccessStoryViewSet)
router.register(r'success_stories_list', SuccessStoryListViewSet, basename='success_stories_list')
router.register(r'testimonials', TestimonialViewSet)
router.register(r'testimonials_list', TestimonialListViewSet, basename='testimonial-list-view')
router.register(r'vysyassist_comments', VysycommentsListViewSet, basename='vysyassist_comments')
# router.register(r'homepage', HomepageViewSet)
# router.register(r'homepage-list', HomepageListViewSet, basename='homepage-list')

# router.register(r'admin-users', AdminUserViewSet)
# router.register(r'admin-users-list', AdminUserListViewSet, basename='admin-users-list')

# router.register(r'Newprofile_get', Newprofile_get)

urlpatterns = [
    path('signin/', SignInView.as_view(), name='signin'),
    
    #path('update_adminComments/', Update_AdminComments.as_view(), name='Update_AdminComments'),
    path('update-admincomments/<str:profile_id>/', Update_AdminComments, name='update_comments_by_profile'),
    path('add-profile/', SubmitProfileAPIView.as_view(), name='submit-profile'),
    path('edit-profile/<str:profile_id>/', EditProfileAPIView.as_view(), name='edit-profile'),
    path('profile_details/<str:profile_id>/', GetProfEditDetailsAPIView.as_view(),name='profile_details'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
    path('api/', include(router.urls)),   
    path('api/logindetails_temp/<int:pk>/approve/', LoginDetailsTempViewSet.as_view({'patch': 'approve'}), name='logindetails_temp-approve'),
    path('api/logindetails_temp/<int:pk>/disapprove/', LoginDetailsTempViewSet.as_view({'patch': 'disapprove'}), name='logindetails_temp-disapprove'),
    path('api/logindetails_temp/<int:pk>/approve/', LoginDetailsTempViewSet.as_view({'patch': 'approve'}), name='logindetails_temp-approve'),
    path('newprofile_get/', Newprofile_get.as_view(), name='newprofile_get'),
    path('Get_Profile_data/', GetProfileDataView.as_view(), name='Get_Profile_data'),
    path('logindetails/', LoginDetailsListCreateView.as_view(), name='login-details-list-create'),
    path('logindetails/<int:pk>/', LoginDetailsDetailView.as_view(), name='login-details-detail'),
    path('Get_all_profiles/deleted/', Get_all_profiles.as_view(), name='Get_all_profiles_deleted', kwargs={'profile_status': 0}),
    path('Get_all_profiles/paid/', Get_all_profiles.as_view(), name='Get_all_profiles_paid', kwargs={'profile_status': 2}),
    path('Get_all_profiles/approved/', Get_all_profiles.as_view(), name='Get_all_profiles_approved', kwargs={'profile_status': 3}),
    path('Get_all_profiles/featured/', Get_all_profiles.as_view(), name='Get_all_profiles_featured', kwargs={'profile_status': 4}),
    path('', include(router.urls)),
    path('page/edit/<int:pk>/', PageEditView.as_view(), name='page-edit'),
    path('page/delete/<int:pk>/', PageDeleteView.as_view(), name='page-delete'),
    path('admin-settings/', AdminSettingsView.as_view(), name='admin-settings'),
    path('admin-settings/update/', AdminSettingsUpdateView.as_view(), name='admin-settings-update'),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),

    path('call_action_received/', CallactionReceived.as_view(), name='express-interest'),
    path('call_action_sent/', CallactionSent.as_view(), name='express-interest'),

    path('call_action_received/', CallactionReceived.as_view(), name='express-interest'),
    path('call_action_sent/', CallactionSent.as_view(), name='express-interest'),
    # path('admin-users/<int:pk>/edit/', AdminEditView.as_view(), name='admin-user-edit'),
    # path('admin-users/<int:pk>/delete/', AdminDeleteView.as_view(), name='admin-user-delete'),
    
    path('admin-user/login/', AdminUserDetailView.as_view(), name='admin-user-login'),
    path('admin-users/', list_admin_users, name='list-admin-users'),
    path('admin-users/<int:pk>/', list_admin_users, name='list-admin-user'),  # For retrieving a specific user by ID
    path('admin-users/roles/', list_roles, name='list_roles'),
    path('admin-user/add/', add_admin_user, name='admin-user-add'),
    path('admin-user/edit/<int:pk>/', edit_admin_user, name='admin-user-edit'),
    path('admin-user/delete/<int:pk>/', delete_admin_user, name='admin-user-delete'),
    path('awards/edit/<int:pk>/', AwardEditView.as_view(), name='award_edit'),
    path('awards/delete/<int:pk>/', AwardDeleteView.as_view(), name='award_delete'),
    path('success_stories/edit/<int:pk>/', SuccessStoryEditView.as_view(), name='success_story_edit'),
    path('success_stories/delete/<int:pk>/', SuccessStoryDeleteView.as_view(), name='success_story_delete'),

    path('testimonials/edit/<int:pk>/', TestimonialEditView.as_view(), name='testimonial-edit'),
    path('testimonials/delete/<int:pk>/', TestimonialDeleteView.as_view(), name='testimonial-delete'),
    
    # path('homepage/edit/<int:pk>/', HomepageEditView.as_view(), name='homepage-edit'),
    # path('homepage/delete/<int:pk>/', HomepageDeleteView.as_view(), name='homepage-delete'),
    path('export/excel/', export_excel, name='export_excel'),   
    path('quick-upload/', QuickUploadAPIView.as_view(), name='quick-upload'),
    path('express-interest/', ExpressInterestView.as_view(), name='express-interest'),
    path('viewed-profiles/', ViewedProfileByDateRangeView.as_view(), name='express-interest'),
    path('bookmarks/', BookmarksView.as_view(), name='bookmarks'),  
    path('photo-requests/', PhotoRequestView.as_view(), name='photo-requests'),

    path('get_profile-images_approval/', ProfileImages.as_view(), name='profile_images'),
    path('get_profile_imagebyId/', ProfileImagesView.as_view(), name='all_profile_images') , 
    path('get_status_master/', GetMasterStatus.as_view(), name='get_status_master'),
    path('get_sub_status_master/', GetSubMasterStatus.as_view(), name='get_sub_status_master'),
    path('get_plan_bystatus/', GetPlanbyStatus.as_view(), name='get_plan_bystatus'),
    path('get_allplans/', GetallPlans.as_view(), name='get_allplans'),
    path('Get_prof_list_match/', Get_prof_list_match.as_view(), name='Get_prof_list_match'),
    path('Get_suggest_list_match/', Get_suggest_list_match.as_view(), name='Get_suggest_list_match'),
    path('profile-vys-assist/', ProfileVysAssistView.as_view(), name='profile_vys_assist'),
    path('home_page_list/', HomepageListView.as_view(), name='home_page_list'),
    path('delete-profile/<str:profile_id>/', delete_profile, name='delete_profile'),
    path('Viewed_profiles/', My_viewed_profiles.as_view(), name='viewed_profiles'),
    path('Visitor_profiles/', My_profiles_vistors.as_view(), name='Visitor_profiles'),
    path('Get_photo_request/', Get_photo_request_list.as_view(), name='Get_photo_request_list'),
    path('vysassist/', My_vysassist_list.as_view(), name='My_vysassist_list'),
    path('Personal_notes/', Get_personal_notes.as_view(), name='Get_personal_notes'),
    path('Express_interest/', Exp_intrests_list.as_view(), name='Exp_intrests_list'), #express intrests sent
    path('Express_interest_received/', Exp_intrests_received.as_view(), name='Exp_intrests_list'),
    path('Express_interest_mutual/', Exp_intrests_mutual.as_view(), name='Exp_intrests_list'), 
    path('send_bulk_email/', send_bulk_email, name='send_bulk_email'),
    path('login-details/', fetch_login_details, name='fetch_login_details'),
    path('login-details/<str:profile_from_id>/', fetch_login_details_profile, name='fetch_login_details'),
    path('profile-send-to/<str:profile_id>/', ProfileSendTo.as_view(), name='profile_send_to'),

    path('Vysfollowups/', ProfileVysAssistFollowupListCreateView.as_view(), name='Vysfollowups_create'),
    path('Vysfollowups/<int:pk>/', ProfileVysAssistFollowupRetrieveUpdateDeleteView.as_view(), name='vysfollowups'),
    #matching profilesaction
    path('partnersettings/', Partnersettings.as_view(), name='vysfollowups'),
    path('suggestsettings/', Suggestsettings.as_view(), name='suggestsettings'),


    
    path('Matching_print_profiles/', Matchingprintprofile.as_view(), name='Matching_print_profiles'),
    path('Matching_whatsapp/', Matchingwhatsapp.as_view(), name='Matching_whatsapp'),
    path('Matching_sendemail/', Matchingsendemail.as_view(), name='Matching_sendemail'),




]
