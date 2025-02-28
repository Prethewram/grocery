from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
import random
from .models import *
from .serializers import *
from rest_framework import generics
from .models import User
from .serializers import UserDetailSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.db.models import Count


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')

        try:
            user = User.objects.get(email=email, mobile_number=mobile_number)

            if user.is_verified:
                return Response({'error': 'User with this email and mobile number is already verified.'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'day7grocery@gmail.com',
                [user.email]
            )

            self.create_notification(user.name)

            return Response({
                'message': 'A new OTP has been sent to your email. Please verify your OTP.',
                'id': user.id
            }, status=status.HTTP_200_OK)


        except User.DoesNotExist:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                otp = random.randint(100000, 999999)
                user.otp = otp
                user.save()


                send_mail(
                    'OTP Verification',
                    f'Your OTP is {otp}',
                    'praveencodeedex@gmail.com',
                    [user.email]
                )

                
                self.create_notification(user.name)

                return Response({'message': 'OTP Sent successfully! Please verify your OTP.'}, 
                                status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_notification(self, username):
        message = f'A new user "{username}" is registered.'
        Notification.objects.create(message=message, created_at=timezone.now())


class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class OTPVerifyView(APIView):
    permission_classes=[]
    authentication_classes=[]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp:
                    user.is_active = True  
                    user.is_verified = True
                    user.otp = None  
                    user.save()
                    return Response({'message': 'Email verified successfully! You can now log in.'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes=[]
    authentication_classes=[]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            return Response({'message': 'Logged in successfully!','user_id': user.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserProfileView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         profile, created = UserProfile.objects.get_or_create(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data)

#     def put(self, request):
#         profile, created = UserProfile.objects.get_or_create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request):
#         request.user.delete()
#         return Response({'message': 'User deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

class CustomProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


from django.contrib.auth import get_user_model

User = get_user_model()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    pagination_class=None


class UserListView(generics.ListCreateAPIView):
    serializer_class = UserDetailSerializer
    pagination_class = CustomProductPagination

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)


from django.utils.translation import gettext_lazy as _

class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  # Get the user instance (could be User or CoAdmin)

        if isinstance(user, CoAdmin):
            # CoAdmin permissions
            user_type = 'co-admin'
            permissions_map = user.permissions  # Using the JSONField for CoAdmin permissions

        elif isinstance(user, User) and user.is_superuser:
            # Super admin has all permissions
            user_type = 'super admin'
            permissions_map = {
                'products': True,
                'orders': True,
                'users': True
            }
        else:
            # Regular admin (if needed)
            user_type = 'admin'
            permissions_map = {
                'products': user.has_perm('products.add_product') or user.has_perm('products.change_product') or user.has_perm('products.delete_product'),
                'orders': user.has_perm('orders.add_order') or user.has_perm('orders.change_order') or user.has_perm('orders.delete_order'),
                'users': user.has_perm('users.add_user') or user.has_perm('users.change_user') or user.has_perm('users.delete_user'),
            }

        # Format and return the response
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'permissions': permissions_map,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'user_type': user_type
        }, status=status.HTTP_200_OK)

    

# Email: admingrocery@gmail.com
# Mobile number: 8075189808
# Name: admin
# Password:admingrocery


#password_reset
User = get_user_model()

class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes=[]
    authentication_classes=[]

    def post(self, request):
        email = request.data.get('email', None)
        user = User.objects.filter(email=email).first()

        if user:
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            user.otp_secret_key = otp
            user.save()

            email_subject = 'Password Reset OTP'
            email_body = f'Your OTP for password reset is: {otp}'
            to_email = [user.email] 
            send_mail(email_subject, email_body, from_email=None, recipient_list=to_email)


            return Response({'detail': 'OTP sent successfully.','status':True}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User not found.','status':False}, status=status.HTTP_404_NOT_FOUND)
        
User = get_user_model()

class PassOTPVerificationView(generics.GenericAPIView):
    serializer_class = PassOTPVerificationSerializer
    permission_classes=[]
    authentication_classes=[]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email', None)
        otp = serializer.validated_data.get('otp', None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': f'User with email {email} not found.', 'status': False}, status=status.HTTP_404_NOT_FOUND)

        if not self.verify_otp(user.otp_secret_key, otp):
            return Response({'detail': 'Invalid OTP.', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        user.otp_secret_key = None
        user.save()

        return Response({'detail': 'OTP verification successful. Proceed to reset password.', 'status': True}, status=status.HTTP_200_OK)

    def verify_otp(self, secret_key, otp):

        return secret_key == otp



class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes=[]
    authentication_classes=[]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        new_password = serializer.validated_data.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': f'User with email {email} not found.', 'status': False}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Password changed successfully.', 'status': True}, status=status.HTTP_200_OK)
    

from rest_framework.permissions import IsAdminUser

# class CoAdminRegisterView(generics.CreateAPIView):
#     queryset = CoAdmin.objects.all()
#     serializer_class = CoAdminRegisterSerializer
#     permission_classes = []  # Allow registration without admin permissions

#     def create(self, request, *args, **kwargs):
#         email = request.data.get('email')

#         try:
#             co_admin = CoAdmin.objects.get(email=email)

#             if co_admin.is_verified:
#                 return Response({'error': 'Co-admin with this email is already verified.'}, 
#                                 status=status.HTTP_400_BAD_REQUEST)

#             otp = random.randint(100000, 999999)
#             co_admin.otp = otp
#             co_admin.save()

#             send_mail(
#                 'OTP Verification',
#                 f'Your new OTP is {otp}',
#                 'praveencodeedex@gmail.com',
#                 [co_admin.email]
#             )

#             return Response({'message': 'A new OTP has been sent to your email. Please verify your OTP.'}, 
#                             status=status.HTTP_200_OK)

#         except CoAdmin.DoesNotExist:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             co_admin = serializer.save()
#             otp = random.randint(100000, 999999)
#             co_admin.otp = otp
#             co_admin.save()

#             send_mail(
#                 'OTP Verification',
#                 f'Your OTP is {otp}',
#                 'praveencodeedex@gmail.com',
#                 [co_admin.email]
#             )

#             return Response({'message': 'OTP Sent successfully! Please verify your OTP.'}, 
#                             status=status.HTTP_201_CREATED)

    

class CoAdminListCreateView(generics.ListCreateAPIView):
    queryset = CoAdmin.objects.all()
    serializer_class = CoAdminDetailSerializer
    permission_classes = [IsAdminUser]

# class CoAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = CoAdmin.objects.all()
#     serializer_class = CoAdminDetailSerializer
#     permission_classes = [IsAdminUser]



from django.utils import timezone

# class CoAdminLoginView(generics.GenericAPIView):
#     serializer_class = CoAdminLoginSerializer
#     permission_classes = []

  
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         co_admin = serializer.validated_data['co_admin']
        
#         # Log the user in
#         login(request, co_admin)

#         # Update last_login
#         co_admin.last_login = timezone.now()
#         co_admin.save(update_fields=['last_login'])

#         return Response({
#             'message': 'Logged in successfully!',
#             'user_id': co_admin.id,
#             'name': co_admin.name,
#             'email': co_admin.email,
#         }, status=status.HTTP_200_OK)


# class CoAdminOTPVerifyView(generics.GenericAPIView):
#     serializer_class = CoAdminOTPVerifySerializer

#     def post(self, request):
#         email = request.data.get('email')
#         otp = request.data.get('otp')

#         try:
#             co_admin = CoAdmin.objects.get(email=email)

#             if co_admin.otp == otp:
#                 co_admin.is_verified = True
#                 co_admin.otp = None  # Clear OTP after verification
#                 co_admin.save()

#                 return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

#         except CoAdmin.DoesNotExist:
#             return Response({'error': 'Co-admin not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
from rest_framework import generics, permissions


    
# class CoAdminCreateView(generics.CreateAPIView):
#     queryset = CoAdmin.objects.all()
#     serializer_class = CoAdminSerializer

#     def perform_create(self, serializer):
#         serializer.save()

# class CoAdminListView(generics.ListAPIView):
#     queryset = CoAdmin.objects.all()
#     serializer_class = CoAdminSerializer
#     permission_classes = []
#     pagination_class=None


User = get_user_model()
class UserAddressListView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class =UserAddressSerializer
    pagination_class=None
    

User = get_user_model()

class SendNotificationView(generics.CreateAPIView):
    permission_classes = []  
    queryset = AppNotifications.objects.all().order_by('-created_at') 
    serializer_class = AppNotificationSerializer  

    def post(self, request, *args, **kwargs):
        message = request.data.get('message', None)
        image = request.FILES.get('image', None)

        if not message:
            return Response({"detail": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(is_active=True)

        notifications = [
            AppNotifications(user=user, message=message, image=image)
            for user in users
        ]

        AppNotifications.objects.bulk_create(notifications)

        return Response({"detail": "Notification sent successfully to all users"}, status=status.HTTP_200_OK)

    

User = get_user_model()

class UserNotificationsListView(generics.ListAPIView):
    permission_classes = []  
    serializer_class = AppNotificationSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  
        return AppNotifications.objects.filter(user__id=user_id).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserNotificationDetailView(generics.RetrieveAPIView):
    permission_classes = []
    queryset = AppNotifications.objects.all()
    serializer_class = AppNotificationSerializer

    def get(self, request, *args, **kwargs):
        notification = self.get_object()  # Get the notification object
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
User = get_user_model()

class TotalUserNotificationsListView(generics.ListAPIView):
    permission_classes = []  
    serializer_class = AppNotificationSerializer

    def get_queryset(self):
        cutoff_date = timezone.now() - timedelta(days=2)

        recent_notifications = AppNotifications.objects.filter(created_at__gte=cutoff_date).order_by('-created_at')

        AppNotifications.objects.filter(created_at__lt=cutoff_date).delete()

        return recent_notifications

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from django.shortcuts import get_object_or_404
class SendNotificationViewSingleuser(generics.CreateAPIView):
    permission_classes = []  # Ensure the user is authenticated
    serializer_class = SendsingleNotificationSerializer

    def post(self, request, user_id, *args, **kwargs):
        # Get the user to whom the notification will be sent
        user = get_object_or_404(User, id=user_id)

        # Validate and save the notification
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the notification for the user
        AppNotifications.objects.create(user=user, **serializer.validated_data)
        
        return Response({'message': 'Notification sent successfully!'}, status=status.HTTP_201_CREATED)
    

class RetrieveUserNotificationsView(generics.ListAPIView):
    permission_classes = []  # Ensure the user is authenticated
    serializer_class = AppNotificationSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Get user_id from URL parameters
        user = get_object_or_404(User, id=user_id)  # Ensure the user exists
        return AppNotifications.objects.filter(user=user)  # Retrieve notifications for the user

    def get(self, request, user_id, *args, **kwargs):
        self.object_list = self.get_queryset()
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CoAdminListCreateView(generics.ListCreateAPIView):
    queryset = CoAdmin.objects.all()
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CoAdminCreateSerializer
        return CoAdminSerializer

    def perform_create(self, serializer):
        serializer.save()

class SuperAdminCreateView(generics.CreateAPIView):
    queryset = CoAdmin.objects.all()
    serializer_class = CoAdminCreateSerializer
    permission_classes = []

    def perform_create(self, serializer):
        # Optionally, you can check here for additional logic
        serializer.save()# Only allow admin users to create super admins


# Get, update or delete a co-admin by ID

class   CoAdminlistView(generics.ListAPIView):
    queryset = CoAdmin.objects.filter(is_superuser=False)  
    serializer_class = CoAdminSerializer
    permission_classes = []


class   CoAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoAdmin.objects.all()
    serializer_class = CoAdminSerializer
    permission_classes = []

    def delete(self, request, *args, **kwargs):
        co_admin = self.get_object()
        co_admin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        co_admin = self.get_object()
        serializer = CoAdminCreateSerializer(co_admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework_simplejwt.tokens import RefreshToken


class CoAdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Authenticate the co-admin
        coadmin = authenticate(request, email=email, password=password)

        if coadmin is not None:
            if coadmin.is_active and coadmin.is_verified:
                # Generate tokens using SimpleJWT
                refresh = RefreshToken.for_user(coadmin)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'coadmin_id': coadmin.id,
                    'name': coadmin.name,
                    'email': coadmin.email,
                }, status=status.HTTP_200_OK)
            return Response({"error": "Account is inactive or not verified"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

User = get_user_model()   
class UpdateNotificationView(generics.RetrieveUpdateAPIView):
    queryset = AppNotifications.objects.all()
    serializer_class = AppNotificationSerializer
    lookup_field = 'id'  # Assuming 'id' is used to identify the notification

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    

class MarkNotificationsAsReadView(generics.UpdateAPIView):
    permission_classes = [] 

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']  
        notifications = AppNotifications.objects.filter(user__id=user_id, is_read=False)

        updated_count = notifications.count()

        notifications.update(is_read=True)

        return Response({"detail": f"All {updated_count} notifications marked as read."}, status=status.HTTP_200_OK)
    
class UserRegistrationAnalyticsView(APIView):
    def get(self, request):
        # Daily registrations
        daily_registrations = (
            User.objects.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # Weekly registrations
        weekly_registrations = (
            User.objects.annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )

        # Monthly registrations
        monthly_registrations = (
            User.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Prepare the response data
        data = {
            "daily_registrations": list(daily_registrations),
            "weekly_registrations": list(weekly_registrations),
            "monthly_registrations": list(monthly_registrations),
        }

        return Response(data, status=status.HTTP_200_OK)


