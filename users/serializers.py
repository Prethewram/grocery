from rest_framework import serializers
from django.contrib.auth import authenticate,get_user_model
from .models import *
import uuid
import random
from django.core.mail import send_mail
import pytz



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")
        email = data.get('email')
        mobile_number = data.get('mobile_number')

        try:
            user = User.objects.get(email=email, mobile_number=mobile_number)
            if user.is_verified:
                raise serializers.ValidationError({
                    'email': 'User with this email is already verified.',
                    'mobile_number': 'User with this mobile number is already verified.',
                })
            else:
                # If user exists but is not verified, allow OTP regeneration
                self.context['existing_user'] = user
        except User.DoesNotExist:
            pass

        return data

    def create(self, validated_data):
        if 'existing_user' in self.context:
            # User exists but not verified, regenerate OTP
            user = self.context['existing_user']
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Resend OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )
            return user
        else:
            # New user, create account and generate OTP
            validated_data.pop('confirm_password')
            username = str(uuid.uuid4())[:8]
            
            user = User.objects.create_user(
                username=username,
                name=validated_data['name'],
                email=validated_data['email'],
                mobile_number=validated_data['mobile_number'],
                password=validated_data['password'],
                is_active=False
            )

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )

            return user

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']
    
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified.")
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'is_verified', 'address', 'state', 'city','road_name','pincode', 'gender', 'DOB']

from django.utils.translation import gettext_lazy as _

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"), write_only=True)
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            coadmin_user = CoAdmin.objects.filter(email=email).first()
            if coadmin_user and coadmin_user.check_password(password):
                attrs['user'] = coadmin_user  # Store coadmin_user for response
                return attrs

            raise serializers.ValidationError(_("No user found with this email."), code='authorization')

        raise serializers.ValidationError(_("Must include 'email' and 'password'."), code='authorization')



#password_reset
User = get_user_model()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PassOTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=4)

class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("New password and confirm new password do not match.")
        
        return data

class CoAdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CoAdmin
        fields = ['name', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")
        email = data.get('email')

        try:
            co_admin = CoAdmin.objects.get(email=email)
            if co_admin.is_verified:
                raise serializers.ValidationError({'email': 'Co-admin with this email is already verified.'})
            else:
                # If co-admin exists but is not verified, allow OTP regeneration
                self.context['existing_co_admin'] = co_admin
        except CoAdmin.DoesNotExist:
            pass

        return data

    def create(self, validated_data):
        if 'existing_co_admin' in self.context:
            # Co-admin exists but not verified, regenerate OTP
            co_admin = self.context['existing_co_admin']
            otp = random.randint(100000, 999999)
            co_admin.otp = otp
            co_admin.save()

            # Resend OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [co_admin.email]
            )
            return co_admin
        else:
            # New co-admin, create account and generate OTP
            validated_data.pop('confirm_password')
            co_admin = CoAdmin.objects.create(
                name=validated_data['name'],
                email=validated_data['email'],
                password=validated_data['password'],  # Make sure to hash the password
                permissions={},  # Set default permissions as needed
            )

            otp = random.randint(100000, 999999)
            co_admin.otp = otp
            co_admin.save()

            # Send OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [co_admin.email]
            )

            return co_admin
        
class CoAdminDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoAdmin
        fields = ['id', 'name', 'email', 'permissions', 'is_verified']


class CoAdminOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            co_admin = CoAdmin.objects.get(email=email)
            if co_admin.otp != otp:
                raise serializers.ValidationError("Invalid OTP.")
        except CoAdmin.DoesNotExist:
            raise serializers.ValidationError("Co-admin not found.")

        return data
    


class CoAdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate the co-admin using the email and password
        co_admin = authenticate(email=email, password=password)

        if co_admin is None:
            raise serializers.ValidationError("Invalid email or password.")

        attrs['co_admin'] = co_admin
        return attrs



class CoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoAdmin
        fields = ['id', 'name', 'email', 'password', 'permissions', 'is_verified', 'is_active', 'is_staff', 'is_superuser']


class CoAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CoAdmin
        fields = ['id', 'name', 'email', 'password', 'permissions', 'is_verified', 'is_active', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password')
        is_superuser = validated_data.get('is_superuser', False)

        # If creating a super admin, set permissions accordingly
        if is_superuser:
            validated_data['permissions'] = ['*']  # Grant all permissions
        
        co_admin = CoAdmin(**validated_data)
        co_admin.set_password(password)
        co_admin.save()
        return co_admin

class SuperAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User  # or your custom user model
        fields = ['id', 'name', 'email', 'password', 'is_active', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password')
        super_admin = User(**validated_data)
        super_admin.set_password(password)
        super_admin.save()
        return super_admin



class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','address','state','pincode','city','road_name']


class AppNotificationSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = AppNotifications
        fields = ['id', 'user', 'message', 'created_at', 'is_read', 'time', 'image']  

    def get_time(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.created_at.astimezone(ist_timezone)      
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")


class SendsingleNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppNotifications
        fields = ['message']  

