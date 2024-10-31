from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Cart, Payment, Order_details
from shop.models import Product, Category
import razorpay
from django.contrib.auth.models import User
from django.contrib.auth import login


# Create your views here.
@login_required()
def add_cart(request, i):
    p = Product.objects.get(id=i)
    u = request.user  # Current logged-in user
    try:
        if p.stock > 0:  # If the product is already in the cart, increase its quantity
            c = Cart.objects.get(product=p, user=u)
            c.quantity += 1
            c.save()
            p.stock -= 1  # Decrease product stock
            p.save()
    except:
        if p.stock > 0:  # If the product is not already in the cart, create a new cart entry
            c = Cart.objects.create(product=p, user=u, quantity=1)
            c.save()
            p.stock -= 1
            p.save()

    return redirect('cart:cartview')  # Redirect to cart view after updating the cart


def cart_view(request):
    u = request.user
    total = 0
    c = Cart.objects.filter(user=u)  # Retrieve items in the cart for the user
    for i in c:
        total += i.quantity * i.product.price  # Calculate the total price
    context = {'cart': c, 'total': total}
    return render(request, 'cart.html', context)


@login_required()
def cart_remove(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:
        c = Cart.objects.get(user=u, product=p)
        if c.quantity > 1:
            c.quantity -= 1
            c.save()
            p.stock += 1
            p.save()
        else:
            c.delete()  # Remove item from cart if quantity is 1
            p.stock += 1
            p.save()
    except:
        pass

    return redirect('cart:cartview')


@login_required()
def cart_delete(request, i):
    u = request.user
    p = Product.objects.get(id=i)

    try:
        c = Cart.objects.get(user=u, product=p)
        c.delete()  # Restore the stock for the deleted quantity
        p.stock += c.quantity
        p.save()

    except:
        pass
    return redirect('cart:cartview')


@login_required()
def checkout(request):
    if request.method == "POST":  # Get details from the checkout form
        address = request.POST['a']
        phone_no = request.POST['p']
        pin = request.POST['n']

        u = request.user
        c = Cart.objects.filter(user=u)
        total = 0
        for i in c:
            total += i.quantity * i.product.price

        total = int(total * 100)  # Convert total to paise for Razorpay

        # Razorpay order creation happens here after calculating the total
        client = razorpay.Client(auth=('rzp_test_zl6krAbsL0hjn4', 's02HnvSpQ6iGdPNpTK0bGGPR'))
        response_payment = client.order.create(dict(amount=total, currency="INR"))
        order_id = response_payment['id']
        order_status = response_payment['status']
        if order_status == "created":  # Save payment and order details
            p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
            p.save()
            for i in c:
                o = Order_details.objects.create(product=i.product, user=u, no_of_items=i.quantity, address=address,
                                                 phone_no=phone_no, pin=pin, order_id=order_id)
                o.save()  # Return payment details to payment page
        else:
            pass
        response_payment['name'] = u.username
        context = {'payment': response_payment}
        return render(request, 'payment.html', context)
    return render(request, 'checkout.html')


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def payment_status(request, u):
    # Defines the payment_status function, which takes request and a username (u) as arguments.
    user = User.objects.get(username=u)
    if not request.user.is_authenticated:  # if user is not authenticated
        login(request, user)  # allowing request user to login
    if request.method == "POST":
        response = request.POST
        print(response)

        # Creates a dictionary that holds the razorpay_order_id,
        # razorpay_payment_id, and razorpay_signature received from Razorpay in the POST data.
        # These values are needed to verify the authenticity of the payment.
        param_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature'],
        }
        client = razorpay.Client(auth=('rzp_test_zl6krAbsL0hjn4', 's02HnvSpQ6iGdPNpTK0bGGPR'))
        print(client)
        try:
            status = client.utility.verify_payment_signature(param_dict)  # to check authenticity of razorpay_signature
            print(status)
            # To retrieve a particular record in payment table whose order id matches the response order id
            p = Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id = response['razorpay_payment_id']  # adds the payment id after successful payment
            p.paid = True  # changes the paid status to true
            p.save()
            o = Order_details.objects.filter(user=user,
                                             order_id=response[
                                                 'razorpay_order_id'])  # retrieve the records in order_details
            # matching with current user and response order_id
            for i in o:
                i.payment_status = "paid"
                i.save()
            # After successful payment delete the items in cart for particular user
            c = Cart.objects.filter(user=user)
            c.delete()
        except:
            pass

    return render(request, 'payment_status.html', {'status': status})


# Checks the payment status returned by Razorpay. If successful, it updates the payment and order records as "paid,"
# then clears the cart for the user.

def orders(request):
    u = request.user
    o = Order_details.objects.filter(user=u, payment_status="paid")
    return render(request, 'order.html', {'order_details': o})


@login_required
def add_category(request):
    if request.method == "POST":
        c = request.POST['c']
        d = request.POST['d']
        i = request.FILES['i']

        c = Category.objects.create(name=c, desc=d, image=i)
        c.save()
        return redirect('shop:categories')
    return render(request, 'add_category.html')


def add_product(request):
    if request.method == 'POST':
        t = request.POST['t']
        r = request.POST['r']
        m = request.FILES['m']
        p = request.POST['p']
        s = request.POST['s']
        c = request.POST['c']
        cat = Category.objects.get(name=c)

        p = Product.objects.create(name=t, desc=r, image=m, price=p, stock=s, category=cat)
        p.save()

        return redirect('shop:categories')

    return render(request, 'add_product.html')
