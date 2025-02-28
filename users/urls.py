from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),

    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-otp/', PassOTPVerificationView.as_view(), name='otp-verification'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('allusers/', UserListView.as_view(), name='user-details-view'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('User/address/<int:pk>/', UserAddressListView.as_view(), name='user-Address'),
    path('user-registration-analytics/', UserRegistrationAnalyticsView.as_view(), name='user-registration-analytics'),
 

    #admin login
    
    path('adminlogin/', AdminLoginView.as_view(), name='admin-login'),

#co admin

    # path('register-coadmin/', CoAdminRegisterView.as_view(), name='register-coadmin'),
    # path('verify-otp-co-admin/', CoAdminOTPVerifyView.as_view(), name='verify-otp-co-admin'),
    # path('coadmin-login/', CoAdminLoginView.as_view(), name='coadmin-login'),  # Add this line
    # path('co-admins/<int:pk>/', CoAdminDetailView.as_view(), name='co-admin-detail'),


    # path('coadmin-create/', CoAdminCreateView.as_view(), name='coadmin-create'),
    # path('coadmin/list/', CoAdminListView.as_view(), name='coadmin-list'),

    path('send-notification/', SendNotificationView.as_view(), name='send-notification'),
    path('notifications/user/<int:user_id>/', UserNotificationsListView.as_view(), name='user-notifications-apk'),
    path('notifications/<int:pk>/', UserNotificationDetailView.as_view(), name='notification-detail-apk'),
    path('total-notifications/', TotalUserNotificationsListView.as_view(), name='total-user-notifications-apk'),  # List notifications

    path('send-notification/<int:user_id>/', SendNotificationViewSingleuser.as_view(), name='send-notification-apk'),

    path('notifications-single-user/<int:user_id>/', RetrieveUserNotificationsView.as_view(), name='retrieve-user-notifications-apk'),
    path('notifications/update/<int:id>/', UpdateNotificationView.as_view(), name='update-notification-apk'),
    path('read-notifications/<int:user_id>/', MarkNotificationsAsReadView.as_view(), name='mark-notifications-as-read'),


    path('super-admins/', SuperAdminCreateView.as_view(), name='super-admin-create'),

    path('coadmin-login/', CoAdminLoginView.as_view(), name='coadmin-login'),
    path('coadmins-reg/', CoAdminListCreateView.as_view(), name='coadmin-list-create'),
    path('coadmins/<int:pk>/', CoAdminDetailView.as_view(), name='coadmin-detail'),
    path('coadmins/', CoAdminlistView.as_view(), name='coadmin-list'), 


]
