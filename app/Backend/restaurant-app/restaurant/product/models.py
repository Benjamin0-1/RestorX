from django.db import models

'''
    This is the product/food model, this is a base model for each plate,
    we then have the ProductVariant/PlateVariant model which is the model the user will interact with.
    A product can have many variants, each variant belongs to one product.
    example: lasagna is a product, lasagna with extra cheese is a variant of lasagna.
    We can also "mimic" categories by doing it this way.
'''


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100) # variant name, example: lasagna with extra cheese or large pepperoni pizza
    price = models.DecimalField(max_digits=10, decimal_places=2) # 10.99
    description = models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True) # if the variant is active or not, example if out of stock: False

    class Meta:
        unique_together = ['product', 'name'] # A product can have many variants but the name of the variant should be unique for that product

class Image(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images') # One to many relationship
    url = models.URLField() # https://example.com/image.jpg
    alt_text = models.CharField(max_length=255, blank=True, null=True) # alt text for the image
