from django.db import models
import json

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)  
    Enable_category = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class SubCategories(models.Model):
    Category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=100,default='sample')
    Sub_category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    Enable_subcategory = models.BooleanField(default=True)


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    sub_category = models.ForeignKey('SubCategories', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Discount percentage")
    description = models.TextField(default="product")
    # image = models.ImageField(upload_to='products/', null=True, blank=True)
    weight_measurement = models.CharField(max_length=100)
    Available = models.BooleanField(default=True)
    is_offer_product = models.BooleanField(default=False)
    is_popular_product = models.BooleanField(default=False)
    weights = models.JSONField(help_text="Store different weights with their respective prices, quantities, and stock status as a dictionary")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    whole_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=00.00)


    def calculate_offer_price(self):
        """
        Automatically calculate the offer price based on the discount percentage.
        """
        if self.discount and self.price:
            discount_amount = (self.discount / 100) * self.price
            self.offer_price = self.price - discount_amount
        else:
            self.offer_price = self.price


    def get_price_for_weight(self, weight):
        """
        Get the price for a specific weight from the stored weights data.
        This method handles both dictionaries and lists in the weights field.
        """
        if isinstance(self.weights, dict):
            # Handle weights as a dictionary
            weight_data = self.weights.get(weight, {})
            return weight_data.get('price', self.price)
        
        elif isinstance(self.weights, list):
            # Handle weights as a list of dictionaries
            for weight_data in self.weights:
                if weight_data.get('weight') == weight:
                    return weight_data.get('price', self.price)
        return self.price  # Default to the base price if weight not found

    def get_quantity_for_weight(self, weight):
        """
        Get the quantity for a specific weight from the stored weights data.
        Handles both dictionary and list formats.
        """
        if isinstance(self.weights, dict):
            # Handle weights as a dictionary
            weight_data = self.weights.get(weight, {})
            return weight_data.get('quantity', 0)
        
        elif isinstance(self.weights, list):
            # Handle weights as a list of dictionaries
            for weight_data in self.weights:
                if weight_data.get('weight') == weight:
                    return weight_data.get('quantity', 0)
        return 0  # Default to 0 if weight not found

    def get_stock_status_for_weight(self, weight):
        """
        Get the stock status for a specific weight from the stored weights data.
        Handles both dictionary and list formats.
        """
        if isinstance(self.weights, dict):
            # Handle weights as a dictionary
            weight_data = self.weights.get(weight, {})
            return weight_data.get('is_in_stock', False)
        
        elif isinstance(self.weights, list):
            # Handle weights as a list of dictionaries
            for weight_data in self.weights:
                if weight_data.get('weight') == weight:
                    return weight_data.get('is_in_stock', False)
        return False  # Default to False if weight not found

    def save(self, *args, **kwargs):
        self.calculate_offer_price()  # Make sure this is called before saving
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/', null=True, blank=True)
    def __str__(self):
        return f"Image for {self.product.name}"
    
    

class CarouselItem(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='carousel_images/')

    def __str__(self):
        return self.title


class PosterImage(models.Model):
    poster_heading = models.CharField(max_length=100)
    poster_title = models.CharField(max_length=100)
    poster_sub_title = models.CharField(max_length=100)
    poster_image = models.ImageField(upload_to='poster_images/')

    def __str__(self):
        return self.title
    

class HomePageImage(models.Model):
    Home_heading = models.CharField(max_length=100)
    Home_title = models.CharField(max_length=100)
    Home_sub_title = models.CharField(max_length=100)
    Home_image = models.ImageField(upload_to='poster_images/')
    products = models.ForeignKey(Product, on_delete=models.CASCADE,default=11)

    def __str__(self):
        return self.Home_title
    
class CarouselItem2(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='carousel_images/')

    def __str__(self):
        return self.title
