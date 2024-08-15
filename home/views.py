from django.shortcuts import render
from home.models import Product

def index(request):
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000)

    # Filter products based on search query
    products = Product.objects.filter(title__icontains=search_query)

    # Further filter based on price range
    products = products.filter(price__gte=min_price, price__lte=max_price)

    return render(request, 'index.html', {'results': products})

