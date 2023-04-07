from .models import Category, Brand, Product


def categories(request):
    categories = Category.objects.all().order_by('id')
    get_products = Product.objects.all().count()
    return {'categories': categories,
            'get_products': get_products}


def brands(request):
    brands = Brand.objects.all().order_by('id')
    get_products = Product.objects.all().count()
    return {'brands': brands,
            'get_products': get_products}
