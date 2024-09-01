from django.db import models
from restaurant.product.models import ProductVariant
from django.contrib.auth.models import User


''''
    Here we will have the server based shopping cart model.
    Cart, CartItem, and Order models.
    a cart belongs to a user, a cart can have many cartItems (food variants), a CartItem can have many ProductVariants.

    CartItem is simply a food variant that can be added to the cart.
    
    An order is a collection of data related to the other models
    it should have all of the products that were purchased inside of the cart.
    it should have the total_amount of the order.
    it should have the status of the order. default is 'pending'
    the date the order was created/payed.
    An order belongs to a user.

    # Once an order is "completed", it can NEVER go back to "pending" or "cancelled" <= enforce this logic.

    An OrderItem can contain many ProductVariants that were inside of the Order at the time of purchase.
    it's basically a wrap around the ProductVariant model.
    so an Order can have many OrderItems, and an OrderItem can have many ProductVariants.

'''

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts') # verify
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}\'s cart'
    
    class meta:
        ordering = ['-created_at'] 
        indexes = [
            models.Index(fields=['user']), 
            models.Index(fields=['created_at']),
            # where else does it make sns to add an index? 
        ]

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items') #example query from the other side: cart.items.all()
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items') #example query from the other side: product_variant.cart_items.all()
    quantity = models.PositiveIntegerField(default=1) # this might need some extra validations
       
    class Meta:
        unique_together = ['cart', 'product_variant'] # a cart can have many product variants, but the same product variant can't be in the cart twice. <- only change its quantity.



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, relatied_name='orders') # example query from the other side: user.orders.all()
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order') # this takes a "snapshot" of the cart at the time of purchase.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[ # this could also be its own model in the future.
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True) # this should be set when the order is created/payed.
    updated_at = models.DateTimeField(auto_now=True) # this should be updated when the status changes.
    
    def save(self, *args, **kwargs):  
        if self.status.lower() == 'completed' and self.pk and Order.objects.get(pk=self.pk).status != 'completed':
            raise ValueError('Once an order is completed, it can not be changed.')
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"Order {self.id} for {self.user.first_name} - Status: {self.status}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items') # example query from the other side: order.items.all()
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='order_items') #it's a wrap around the ProductVariant model.
    quantity = models.PositiveIntegerField(default=1) # this might need some extra validations

    class Meta:
        unique_together = ['order', 'product_variant'] # an order can have many product variants, but the same product variant can't be in the order twice. <- only change its quantity.
