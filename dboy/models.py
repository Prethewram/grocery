from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from orders.models import Order
from django.utils import timezone


class DeliveryBoyManager(BaseUserManager):
    def create_user(self, email, mobile_number, name, vehicle_type, vehicle_number, gender, dob, identity_proof, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        delivery_boy = self.model(
            email=email,
            mobile_number=mobile_number,
            name=name,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            gender=gender,
            dob=dob,
            identity_proof=identity_proof,
            **extra_fields  # This allows fields like `is_active` to be passed
        )
        if password:
            delivery_boy.set_password(password)
        else:
            delivery_boy.set_unusable_password()
        delivery_boy.save(using=self._db)
        return delivery_boy

class DeliveryBoy(AbstractBaseUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    identity_proof = models.ImageField(upload_to='identity_proofs/')
    otp = models.CharField(max_length=6, blank=True, null=True) 
    is_working = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DeliveryBoyManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number', 'name', 'vehicle_type', 'vehicle_number', 'gender', 'dob', 'identity_proof']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return False

    def has_module_perms(self, app_label):
        return False

    @property
    def is_staff(self):
        return False


class OrderAssignment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="assignments")
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE, related_name="assignments")
    assigned_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, choices=Order.STATUS_CHOICES, default='OUT FOR DELIVERY')
    completed_at = models.DateTimeField(null=True, blank=True)


    def mark_as_completed(self):
        self.status = 'DELIVERED'
        self.completed_at = timezone.now()
        self.save()