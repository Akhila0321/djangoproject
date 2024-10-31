from django.db.models import Q
from django.shortcuts import render
from shop.models import Product


# Create your views here.
def search_page(request):
    query = ""
    p = None
    if request.method == "POST":
        query = request.POST['q']
        print(query)
        if query:
            p = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query))

    return render(request, 'search.html', {'product': p, 'q': query})
