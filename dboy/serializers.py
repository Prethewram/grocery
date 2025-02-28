from rest_framework import serializers
from .models import *
from products.models import Product
import pytz
from django.shortcuts import get_object_or_404

class DeliveryBoySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoy
        fields = ['email', 'mobile_number', 'name', 'vehicle_type', 'vehicle_number', 'gender', 'dob', 'identity_proof', 'is_active']
        extra_kwargs = {
            'email': {'required': True},
            'mobile_number': {'required': True},
            'name': {'required': True},
            'vehicle_type': {'required': True},
            'vehicle_number': {'required': True},
            'gender': {'required': True},
            'dob': {'required': True},
            'identity_proof': {'required': True},
        }

    def create(self, validated_data):
        delivery_boy = DeliveryBoy.objects.create_user(**validated_data)
        return delivery_boy
    
class DeliveryBoySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoy
        fields = ['id', 'email', 'mobile_number', 'name', 'vehicle_type', 'vehicle_number', 'gender', 'dob', 'identity_proof','is_working','created_at']

class DeliveryBoyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

class DeliveryBoyOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class DeliveryBoyStatusUpdateSerializer(serializers.Serializer):
    is_working = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.is_working = validated_data.get('is_working', instance.is_working)
        instance.save()
        return instance
    
class OrderAssignmentSerializer(serializers.ModelSerializer):
    order_ids = serializers.CharField(source='order.order_ids', read_only=True)
    Assigned_to = serializers.CharField(source='delivery_boy.name',read_only=True)
    Assigned_at = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='order.user.name', read_only=True)
    location = serializers.CharField(source='order.user.road_name', read_only=True)
    Total_amount = serializers.CharField(source='order.total_price', read_only=True)
    Mobile = serializers.CharField(source='order.user.mobile_number', read_only=True)
    Order_date = serializers.SerializerMethodField()  
    Payment = serializers.CharField(source='order.payment_method', read_only=True)
    
    class Meta:
        model = OrderAssignment
        fields = ['id', 'order_ids','Assigned_to' ,'status','Assigned_at','user_name','Mobile','location','Order_date','Payment','Total_amount']

    def get_Assigned_at(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.assigned_at.astimezone(ist_timezone)
        
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")
    
    def get_Order_date(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        order_date = obj.order.created_at.astimezone(ist_timezone)  
        return order_date.strftime("%d/%m/%Y at %I:%M%p")
    
class OrderDboySerializer(serializers.ModelSerializer):
    order_ids = serializers.CharField(source='order.order_ids', read_only=True)
    user_name = serializers.CharField(source='order.user.name', read_only=True)
    Mobile = serializers.CharField(source='order.user.mobile_number', read_only=True)
    location = serializers.CharField(source='order.user.road_name', read_only=True)
    Address = serializers.CharField(source='order.user.address', read_only=True)
    Order_date = serializers.SerializerMethodField()  
    
    class Meta:
        model = OrderAssignment
        fields = ['id', 'order_ids','user_name','Mobile','Order_date','location','Address']
 
    def get_Order_date(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        order_date = obj.order.created_at.astimezone(ist_timezone)  
        return order_date.strftime("%d/%m/%Y at %I:%M%p")
    
class SingleorderSerializer(serializers.ModelSerializer):
    order_ids = serializers.CharField(source='order.order_ids', read_only=True)
    user_name = serializers.CharField(source='order.user.name', read_only=True)
    location = serializers.CharField(source='order.user.road_name', read_only=True)
    Address = serializers.CharField(source='order.user.address', read_only=True)
    Total_amount = serializers.DecimalField(source='order.total_price', max_digits=10, decimal_places=2, read_only=True)
    Payment = serializers.CharField(source='order.payment_method', read_only=True)
    status = serializers.CharField(source='order.status', read_only=True)
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = OrderAssignment
        fields = [
            'id', 'order_ids', 'user_name', 'location', 'Address', 'Payment', 
            'Total_amount', 'product_details', 'status'
        ]

    def get_product_details(self, obj):
        product_ids = obj.order.product_ids.split(',') if obj.order.product_ids else []
        product_names = obj.order.product_names.split(',') if obj.order.product_names else []
        weights = obj.order.selected_weights.split(',') if obj.order.selected_weights else []
        quantities = obj.order.quantities.split(',') if obj.order.quantities else []

        product_details = []
        base_url = "https://groceryct.pythonanywhere.com"

        for idx, product_id in enumerate(product_ids):
            product = get_object_or_404(Product, id=product_id)

            # Fetch the first image for the product from ProductImage model
            product_image = product.images.first()  # Fetch first image related to the product

            # Get the image URL if it exists, otherwise None
            image_url = f"{base_url}{product_image.image.url}" if product_image and product_image.image else None

            product_info = {
                "name": product_names[idx] if idx < len(product_names) else "",
                "weight": weights[idx] if idx < len(weights) else "",
                "quantity": quantities[idx] if idx < len(quantities) else "",
                "image": image_url,
            }
            product_details.append(product_info)

        return product_details

    def get_Assigned_at(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.assigned_at.astimezone(ist_timezone)
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")

    def get_Order_date(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        order_date = obj.order.created_at.astimezone(ist_timezone)
        return order_date.strftime("%d/%m/%Y at %I:%M%p")


class CompletedOrderSerializer(serializers.ModelSerializer):
    order_ids = serializers.CharField(source='order.order_ids', read_only=True)
    user_name = serializers.CharField(source='order.user.name', read_only=True)
    total_amount = serializers.CharField(source='order.total_price', read_only=True)
    location = serializers.CharField(source='order.user.road_name', read_only=True)
    Order_date = serializers.SerializerMethodField() 

    class Meta:
        model = OrderAssignment
        fields = ['id','order_ids', 'user_name', 'total_amount', 'Order_date','location']

    def get_Order_date(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        order_date = obj.order.created_at.astimezone(ist_timezone)  
        return order_date.strftime("%d/%m/%Y at %I:%M%p")

class deliveryboyserializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryBoy
        fields = ['id','name','mobile_number','email','is_working']


class Assignedorderserializer(serializers.ModelSerializer):
    assigned_at = serializers.SerializerMethodField()    
    delivery_boy_name = serializers.CharField(source='delivery_boy.name', read_only=True)
    order_id = serializers.CharField(source='order.order_ids', read_only=True)
    class Meta:
        model = OrderAssignment
        fields = ['id','assigned_at','status','delivery_boy_name','order_id']


    def get_assigned_at(self, obj):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        order_date = obj.order.created_at.astimezone(ist_timezone)  
        return order_date.strftime("%d/%m/%Y at %I:%M%p")


class DeliveryBoyByOrderIDSerializer(serializers.ModelSerializer):
    delivery_boy_name = serializers.CharField(source='delivery_boy.name', read_only=True)
    
    class Meta:
        model = OrderAssignment
        fields = ['id','delivery_boy_name']