from rest_framework import serializers
from .models import *
from products.serializers import *
import pytz

# class CartSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'product', 'quantity', 'created_at', 'updated_at']

#     def get_product(self, obj):
#         return ProductSerializer(obj.product, context=self.context).data

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductSerializer(read_only=True, context={'selected_weight': 'selected_weight'})
    quantity = serializers.IntegerField()
    selected_weight = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'selected_weight', 'price', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_serializer = ProductSerializer(instance.product, context={'selected_weight': instance.selected_weight})
        representation['product'] = product_serializer.data
        return representation

class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name')
    order_time = serializers.SerializerMethodField()
    cart_products = CartSerializer(source='cart.products', many=True, read_only=True)


    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'status', 'created_at','product_names','payment_method','product_ids', 'total_price','order_ids', 'cart_products','total_cart_items','order_time']

    def get_order_time(self, obj):
        # Convert to IST (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.created_at.astimezone(ist_timezone)
        
        # Format the datetime in the desired format
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")

class OrderDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    Address = serializers.CharField(source='user.address', read_only=True)
    total_price = serializers.ReadOnlyField()
    cart_products = serializers.SerializerMethodField()  # Custom method to get product details
    order_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'status', 'created_at', 
            'product_names', 'payment_method', 'product_ids', 
            'total_price', 'order_ids', 'cart_products','Address',
            'total_cart_items', 'order_time','delivery_pin'
        ]

    def get_order_time(self, obj):
        return obj.created_at.strftime("%d/%m/%Y at %I:%M%p")

    def get_cart_products(self, obj):
        product_ids = obj.product_ids.split(",") if obj.product_ids else []
        product_names = obj.product_names.split(",") if obj.product_names else []
        selected_weights = obj.selected_weights.split(",") if obj.selected_weights else []
        quantities = obj.quantities.split(",") if obj.quantities else []

        products = Product.objects.filter(id__in=product_ids)

        cart_products = []
        for product in products:
            index = product_ids.index(str(product.id))  
            selected_weight = selected_weights[index] if len(selected_weights) > index else "N/A"  
            quantity = int(quantities[index]) if len(quantities) > index else 1  
            
            # Get the price based on the selected weight
            selected_weight_price = product.get_price_for_weight(selected_weight)

            cart_products.append({
                "name": product_names[index],
                "quantity": quantity,
                "selected_weight": selected_weight,  
                "price": str(selected_weight_price)
            })

        return cart_products






class AllOrdersSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    cart_products = CartSerializer(source='cart.products', many=True, read_only=True)
    order_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'status','payment_method','order_ids','delivery_pin', 'cart_products','order_time']

    def get_order_time(self, obj):
        # Convert to IST (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.created_at.astimezone(ist_timezone)
        
        # Format the datetime in the desired format
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")
    
class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('WAITING FOR CONFIRMATION', 'Waiting for confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('OUT FOR DELIVERY', 'Out for delivery'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED','rejected')
    ])