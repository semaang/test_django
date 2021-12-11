from django.db import models
# from django.db.models.fields import related
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# from django.db.models.deletion import CASCADE

# Create your models here.

class StreamPlatformList(models.Model):
    name = models.CharField(max_length=30)
    about = models.CharField(max_length=150)
    website = models.URLField(max_length=100)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    price = models.FloatField(default=0)
    # image = models.ImageField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(default=0)
    number_ratings = models.IntegerField(default=0)
    platform = models.ForeignKey(StreamPlatformList, on_delete=models.CASCADE, related_name="products")
    
    def __str__(self):
        return self.title

	# @property
	# def imageURL(self):
	# 	try:
	# 		url = self.image.url
	# 	except:
	# 		url = ''
	# 	return url
    
    
class Review(models.Model):
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=200, null=True)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    review_user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.rating) + "/5 for the product : " + self.product.title + " | written by : " + str(self.review_user)
    

class Customer(models.Model):
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class Order(models.Model):
	date_ordered = models.DateTimeField(auto_now_add=True)
	order_paid = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer")

	def __str__(self):
		return "order number : " + str(self.id) + " from customer : " + str(self.customer)
		
	# @property
	# def shipping(self):
	# 	shipping = False
	# 	orderitems = self.orderitem_set.all()
	# 	for i in orderitems:
	# 		if i.product.digital == False:
	# 			shipping = True
	# 	return shipping

	# @property
	# def get_cart_total(self):
	# 	orderitems = self.orderitem_set.all()
	# 	total = sum([item.get_total for item in orderitems])
	# 	return total 

	# @property
	# def get_cart_items(self):
	# 	orderitems = self.orderitem_set.all()
	# 	total = sum([item.quantity for item in orderitems])
	# 	return total 


class OrderLine(models.Model):
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="order_lines")
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    
	# @property
	# def get_total(self):
	# 	total = self.product.price * self.quantity
	# 	return total


class ShippingAddress(models.Model):
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_created = models.DateTimeField(auto_now_add=True)
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return self.address