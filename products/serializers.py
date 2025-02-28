from rest_framework import serializers
from .models import *
from rest_framework import serializers
from django.conf import settings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    Category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = SubCategories
        fields = ['id', 'name', 'Sub_category_image', 'category_name', 'Category','Enable_subcategory']

    def get_category_name(self, obj):
        return obj.Category.name

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image'] 
 
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategories.objects.all())
    category_name = serializers.SerializerMethodField()
    sub_category_name = serializers.SerializerMethodField()
    price_for_selected_weight = serializers.SerializerMethodField()
    offer_price = serializers.ReadOnlyField()
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    weights = serializers.JSONField(required=False)
    images = ProductImageSerializer(many=True, read_only=True)  
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'sub_category', 'sub_category_name', 'name', 'price',
            'offer_price', 'discount', 'description', 'images','uploaded_images', 'weight_measurement',
            'price_for_selected_weight', 'is_offer_product', 'is_popular_product', 'weights','Available','created_at','whole_sale_price'
        ]

    # Method to get category name
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    # Method to get sub-category name
    def get_sub_category_name(self, obj):
        return obj.sub_category.name if obj.sub_category else None

    # Method to get price for selected weight
    def get_price_for_selected_weight(self, obj):
        selected_weight = self.context.get('selected_weight')
        if selected_weight:
            return obj.get_price_for_weight(selected_weight)
        return obj.price

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)
        
        if uploaded_images:
            # Clear existing images if needed or add new ones
            ProductImage.objects.filter(product=instance).delete()
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)
        
        return instance
    
    

class singleProductSerializer(serializers.ModelSerializer):
    price_for_selected_weight = serializers.SerializerMethodField()
    offer_price = serializers.ReadOnlyField()
    weights = serializers.JSONField()
    images = ProductImageSerializer(many=True, read_only=True)  


    class Meta:
        model = Product
        fields = [
            'id', 'name', 'offer_price','images'
            'description',
            'price_for_selected_weight', 'weights','Available',
        ]

    def get_category_name(self, obj):
        return obj.category.name

    def get_price_for_selected_weight(self, obj):
        weight = self.context.get('weight')  
        if weight:
            return obj.get_price_for_weight(weight)
        return obj.price


class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = ['id', 'title', 'image',]

class CarouselItemSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = ['id', 'title', 'image',]


class PosterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosterImage
        fields = ['id', 'poster_heading', 'poster_title','poster_sub_title','poster_image']

class HomePageImageSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = HomePageImage
        fields = ['id', 'Home_heading', 'Home_title', 'Home_sub_title', 'Home_image', 'products','product_name']
    def get_product_name(self, obj):
            return obj.products.name if obj.products else "No product associated"       


class ProductWeightsSerializer(serializers.ModelSerializer):
    weights = serializers.JSONField()

    class Meta:
        model = Product
        fields = ['id','weights']

# class ProductSearchSerializer(serializers.ModelSerializer):
#     category = CategorySerializer()
#     sub_category = SubCategorySerializer()

#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'price', 'offer_price', 'discount', 'quantity', 'description', 'image', 
#                   'weight_measurement', 'is_offer_product', 'is_popular_product', 'weights', 
#                   'category', 'sub_category']
        
class ProductSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField(max_length=100, required=True) 

class ProductStockSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    product_name = serializers.CharField(source='name', read_only=True)
    stock_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category_name', 'sub_category_name', 'product_name', 'weight_measurement', 'stock_info']

    def get_stock_info(self, obj):
        """
        Return a dictionary containing the stock details for each weight measurement.
        """
        stock_info = {}

        # Ensure weights is a dictionary
        if isinstance(obj.weights, dict):
            for weight, details in obj.weights.items():
                if isinstance(details, dict):  # Ensure details is a dictionary
                    stock_info[weight] = {
                        "price": details.get("price", 0),
                        "quantity": details.get("quantity", 0),  # Get quantity from weights
                        "is_in_stock": details.get("is_in_stock", False)
                    }
                else:
                    stock_info[weight] = {
                        "price": 0,
                        "quantity": 0,
                        "is_in_stock": False
                    }
        else:
            # If weights is not a valid dictionary, log the issue
            print(f"Product ID {obj.id} has weights that is not a dictionary: {obj.weights}")

        return stock_info