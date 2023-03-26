from .models import Category, Brand


def categories(request):
    categories = Category.objects.all().order_by('id')
    return {'categories': categories}


def brands(request):
    brands = Brand.objects.all().order_by('id')
    return {'brands': brands}
