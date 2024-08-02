from django.db import models
from django.utils import timezone
# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	address=models.TextField()
	password=models.CharField(max_length=100)
	profile_picture=models.ImageField(upload_to="profile_picture/",default="")
	usertype=models.CharField(max_length=100,default="buyer")

	def __str__(self):
		return self.fname+" "+self.lname

class Product(models.Model):
	choice1=(
			("Men","Men"),
			("Women","Women"),
			("kids","kids"),
		)
	seller=models.ForeignKey(User,on_delete=models.CASCADE)		
	product_category=models.CharField(max_length=100,choices=choice1)
	product_name=models.CharField(max_length=100)
	product_price=models.PositiveIntegerField()
	product_desc=models.TextField()
	product_image=models.ImageField(upload_to="product_image/")

	def __str__(self):
		return self.seller.fname+" - "+self.product_name

class Wishlist(models.Model):
	usr=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.usr.fname+" - "+self.product.product_name

class Cart(models.Model):
	usr=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	product_price=models.PositiveIntegerField()
	product_qty=models.PositiveIntegerField(default=1)
	total_price=models.PositiveIntegerField()
	payment_status=models.BooleanField(default=False)

	def __str__(self):
		return self.usr.fname+" - "+self.product.product_name
