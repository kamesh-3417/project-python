from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart
import requests
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).	exists()
	}
	return JsonResponse(data)

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100

	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'INR',
				'product_data': {
					'name': 'Checkout Session Data',
				},
				'unit_amount': final_amount,
			},
			'quantity': 1,
		}],	
		mode='payment',
		success_url=YOUR_DOMAIN + '/success',
		cancel_url=YOUR_DOMAIN + '/cancel',)
	return JsonResponse({'id': session.id})

def success(request):
	print("Success")
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')
def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller-index.html')	

def contact(request):
	return render(request,'contact.html')

def about(request):
	return render(request,'about.html')

def shop(request):
	product=Product.objects.all()
	return render(request,'shop.html',{'product':product})

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						
						profile_picture=request.FILES['profile_picture'],
						usertype=request.POST['usertype']
					)
				msg="User Sign Up Succesfully"
				return render(request,'signup.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})

	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			u=User.objects.get(email=request.POST['email'])
			if u.password==request.POST['password']:
				if u.usertype=="buyer":
					request.session['email']=u.email
					request.session['fname']=u.fname
					wishlists=Wishlist.objects.filter(usr=u)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(usr=u,payment_status=False)
					request.session['cart_count']=len(carts)
					request.session['profile_picture']=u.profile_picture.url
					return render(request,'index.html')
				else:
					print("else 1")
					request.session['email']=u.email
					request.session['fname']=u.fname
					request.session['profile_picture']=u.profile_picture.url
					return render(request,'seller-index.html')
			else:
				print("else 2")
				msg="Incorrect password"
				return render(request,'login.html',{'msg':msg})

		except Exception as e:
			print("Except : ",e)
			msg="Email not Registered"
			return render(request,'login.html',{'msg':msg})

	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		request.session['profile_picture']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	u=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if u.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				u.password=request.POST['new_password']
				u.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				if u.usertype=="buyer":
					return render(request,'change-password.html',{'msg':msg})
				else:
					return render(request,'seller-change-password.html',{'msg':msg})
						
		else:
			msg="Old Password Does Not Matched"
			if u.usertype=="buyer":
				return render(request,'change-password.html',{'msg':msg})
			else:
				return render(request,'seller-change-password.html',{'msg':msg})
			
	else:
		if u.usertype=="buyer":
			return render(request,'change-password.html')
		else:
			return render(request,'seller-change-password.html')		

def profile(request):
	u=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		u.fname=request.POST['fname']
		u.lname=request.POST['lname']
		u.mobile=request.POST['mobile']
		u.address=request.POST['address']
		try:
			u.profile_picture=request.FILES['profile_picture']
		except:
			pass
		u.save()
		request.session['profile_picture']=u.profile_picture.url
		msg="Profile Updated Succesfully"
		if u.usertype=="buyer":
			return render(request,'profile.html',{'u':u,'msg':msg})
		else:
			return render(request,'seller-profile.html',{'u':u,'msg':msg})
				
	else:
		if u.usertype=="buyer":
			return render(request,'profile.html',{'u':u})
		else:
			return render(request,'seller-profile.html',{'u':u})

def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
				seller=seller,
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_image=request.FILES['product_image']
			)
		msg="Product Added Succesfully"
		return render(request,'seller-add-product.html',{'msg':msg})

	else:
		return render(request,'seller-add-product.html')

def seller_view_product(request):
	products=Product.objects.all()
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-single.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Updated Succesfully"
		return render(request,'seller-edit-product.html',{'product':product,'msg':msg})

	else:
		 return render(request,'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
		product=Product.objects.get(pk=pk)
		product.delete()
		return redirect('seller-view-product')

def product_category(request,cat):
	products=Product()
	if cat=="All":
		product=Product.objects.all()
	else:
		product=Product.objects.filter(product_category=cat)
	return render(request,'shop.html',{'product':product})
 
def single_product(request,pk):
	wishlist_flag=False
	cart_flag=False
	product=Product.objects.get(pk=pk)
	usr=User.objects.get(email=request.session['email'])
	try:
		Wishlist.objects.get(usr=usr,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		Cart.objects.get(usr=usr,product=product,payment_status=False)
		cart_flag=True
	except:
		pass	
	return render(request,'single-product.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	usr=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(usr=usr,product=product)
	return redirect('wishlist')

def wishlist(request):
	usr=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(usr=usr)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	usr=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(usr=usr,product=product)
	wishlist.delete()
	return redirect('wishlist')

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	usr=User.objects.get(email=request.session['email'])
	Cart.objects.create(
		usr=usr,
		product=product,
		product_price=product.product_price,
		product_qty=1,
		total_price=product.product_price,
		payment_status=False
	)
	return redirect('cart')

def cart(request):
	net_price=0
	usr=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(usr=usr,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	usr=User.objects.get(email=request.session['email'])
	crt=Cart.objects.get(usr=usr,product=product)
	crt.delete()
	return redirect('cart')

def change_qty(request):
	cid=int(request.POST['cid'])
	product_qty=int(request.POST['product_qty'])
	crt=Cart.objects.get(pk=cid)
	crt.product_qty=product_qty
	crt.total_price=crt.product_price*product_qty
	crt.save()
	return redirect('cart')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(usr=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})	