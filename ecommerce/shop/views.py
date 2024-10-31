from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from shop.models import Category, Product


# Create your views here.
def allcategories(request):
    c = Category.objects.all()
    context = {'cat': c}
    return render(request, 'category.html', context)


def allproducts(request, p):
    c = Category.objects.get(id=p)
    p = Product.objects.filter(category=c)
    context = {'cat': c, 'product': p}
    return render(request, 'product.html', context)


def alldetails(request, p):
    p = Product.objects.get(id=p)
    context = {'product': p}
    return render(request, 'details.html', context)


def register(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        c = request.POST['c']
        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']
        if p == c:
            u = User.objects.create_user(username=u, password=p, first_name=f, last_name=l, email=e)
            u.save()
        else:
            return HttpResponse("Passwords are not same")
        return redirect('shop:user_login')
    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('shop:categories')
        else:
            return HttpResponse("Invalid Credentials")
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('shop:user_login')


@login_required()
def add_stock(request, p):
    product = Product.objects.get(id=p)
    if request.method == "POST":
        product.stock = request.POST['s']
        product.save()

        return redirect('shop:categories')
    context = {'pro': product}

    return render(request, 'add_stock.html', context)
