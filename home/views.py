from django.shortcuts import render
from home.models import Product
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60*1)  
def index(request):
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    brand = request.GET.get('brand')
    category = request.GET.get('category')

  
    results = Product.objects.all()

    
    if search:
        query = SearchQuery(search)
        vector = SearchVector("title", "description", "category", "brand")
        rank = SearchRank(vector, query)
        results = results.annotate(
            rank=rank,
            similarity=TrigramSimilarity('title', search) + 
                       TrigramSimilarity('description', search) + 
                       TrigramSimilarity('category', search) + 
                       TrigramSimilarity('brand', search)
        ).filter(Q(rank__gte=0.3) | Q(similarity__gte=0.3)).distinct().order_by('-rank', '-similarity')

    
    if min_price and max_price:
        results = results.filter(
            price__gte=float(min_price), price__lte=float(max_price)
        ).order_by('price')

    
    if brand:
        results = results.filter(brand__icontains=brand)

   
    if category:
        results = results.filter(category__icontains=category)

    
    brands = cache.get("brands")
    if brands is None:
        brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')
        cache.set("brands", brands, 60 * 10)  

 
    categories = cache.get("categories")
    if categories is None:
        categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        cache.set("categories", categories, 60 * 10)  
    
    context = {
        'results': results,
        'categories': categories,
        'brands': brands,
        'search': search,
        'min_price': min_price,
        'max_price': max_price,
        'selected_brand': brand,
        'selected_category': category,
    }

    return render(request, 'index.html', context)
