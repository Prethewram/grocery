from django.db import models
from users.models import User
from products.models import Product
from django.conf import settings
from django.utils import timezone
import uuid

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_weight = models.CharField(max_length=50,default="100l")  
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart item for {self.user} - {self.product.name} ({self.selected_weight})"

     
class Order(models.Model):
    STATUS_CHOICES = [
        ('WAITING FOR CONFIRMATION','Waiting for confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('OUT FOR DELIVERY', 'out for delivery'),
        ('DELIVERED', 'delivered'),
        ('REJECTED', 'rejected')
    ]   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')])
    product_ids = models.CharField(max_length=255, null=True)
    product_names = models.CharField(max_length=255, null=True)
    total_price = models.FloatField(default=0.00)  
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='WAITING FOR CONFIRMATION')  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    razorpay_order_id = models.CharField(max_length=100,null=True,blank=True)
    order_ids= models.CharField(max_length=100,null=True,blank=True)
    total_cart_items = models.PositiveIntegerField(default=0)  
    selected_weights = models.TextField(null=True, blank=True)
    quantities = models.TextField(null=True, blank=True)  
    delivery_pin = models.CharField(max_length=6, null=True, blank=True)  

    def __str__(self):
        return f"Order {self.unique_order_serial} by {self.user.email} - Payment: {self.payment_method}"

    def get_order_time(self):
        return self.created_at.strftime("Ordered on %Y-%m-%d at %I:%M%p")

