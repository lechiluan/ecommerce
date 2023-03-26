from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.contrib import messages
from .forms import ContactForm, CheckoutForm
from main.models import Customer, Category, Brand, Product, Coupon, Contact, CartItem, DeliveryAddress, Orders, \
    OrderDetails, Wishlist
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def paginator(request, objects):
    # Set the number of items per page
    per_page = 8

    # Create a Paginator object with the customers queryset and the per_page value
    page = Paginator(objects, per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the current page object from the Paginator object
    page_obj = page.get_page(page_number)
    return page_obj


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'customer_help/contact.html', {'form': form})


def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'customer_help/customer_product_details.html', context)


def search(request):
    products = Product.objects.all().order_by('id')
    categories = Category.objects.all().order_by('id')
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, products)
    context = {'products': page_object,
               'categories': categories,
               'brands': brands}
    return render(request, 'customer_help/customer_product_list.html', context)


def product_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search')
        sort_by = request.GET.get('sort_by')
        brand_id = request.GET.get('filter_by_brand')  # updated variable name
        category_id = request.GET.get('filter_by_category')  # updated variable name

        products = Product.objects.all()

        # apply brand filter if selected

        if brand_id and category_id:
            products = products.filter(brand__id=brand_id, category__id=category_id)
            brand_name = Brand.objects.get(id=brand_id).name
            category_name = Category.objects.get(id=category_id).name
            messages.success(request, 'Filtered by brand: "' + brand_name + '" and category: "' + category_name + '"')
        elif brand_id:
            products = products.filter(brand__id=brand_id)
            brand_name = Brand.objects.get(id=brand_id).name
            messages.success(request, 'Filtered by brand: "' + brand_name + '"')

        # apply category filter if selected
        elif category_id:
            products = products.filter(category__id=category_id)
            category_name = Category.objects.get(id=category_id).name
            messages.success(request, 'Filtered by category: "' + category_name + '"')

        # apply search filter if search query exists
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(
                    category__name__icontains=search_query) | Q(
                    brand__name__icontains=search_query)
            )
            messages.success(request, 'Search results for: ' + search_query)

        # apply sorting based on selected option
        if sort_by == 'newest':
            products = products.order_by('-created_date')
            messages.success(request, 'Sorted by newest')
        elif sort_by == 'best_seller':
            products = products.order_by('-updated_date')
            messages.success(request, 'Sorted by best seller')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
            messages.success(request, 'Sorted by name ascending')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
            messages.success(request, 'Sorted by name descending')
        elif sort_by == 'price_asc':
            products = products.order_by('price')
            messages.success(request, 'Sorted by price ascending')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
            messages.success(request, 'Sorted by price descending')

        page_obj = paginator(request, products)

        brands = Brand.objects.all()
        categories = Category.objects.all()

        context = {
            'products': page_obj,
            'brands': brands,  # add brands to the context
            'categories': categories,
            'search_query': search_query,
            'brand_id': brand_id,  # updated variable name
            'category_id': category_id,  # updated variable name
        }
        return render(request, 'customer_help/customer_product_list.html', context)
    else:
        products = Product.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)


def product_list_category(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    page_object = paginator(request, products)
    context = {
        'products': page_object,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'customer_help/customer_product_list.html', context)


def product_list_brand(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    products = Product.objects.filter(brand=brand)
    page_object = paginator(request, products)
    context = {
        'products': page_object,
    }
    return render(request, 'customer_help/customer_product_list.html', context)


@login_required(login_url='/auth/login')
# add to cart function for customer
def add_to_cart(request, product_id):
    # get the product from the database
    product = Product.objects.get(id=product_id)
    price = product.price
    quantity = 1
    amount = price * quantity
    # check if the user is authenticated
    if request.user.is_authenticated:
        customer = request.user.customer
        # check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
        if created:
            cart_item.quantity = quantity
            cart_item.price = price
            cart_item.amount = amount
            cart_item.save()
            messages.success(request, 'Product added to cart successfully')
            return redirect('/customer/cart/')
        else:
            cart_item.quantity += quantity
            cart_item.price = price
            cart_item.amount += amount
            cart_item.save()
            messages.success(request, 'Product quantity updated successfully')
            return redirect('/customer/cart/')
    else:
        messages.success(request, 'Please login to add to cart')
        return redirect('/auth/login/')


# view cart function for customer
def view_cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart_items = CartItem.objects.filter(customer=customer)
        total = sum([cart_item.amount for cart_item in cart_items])
        context = {
            'cart_items': cart_items,
            'total': total,
        }
        return render(request, 'customer_cart/view_cart.html', context)
    else:
        messages.success(request, 'Please login to view cart')
        return redirect('/auth/login/')


def remove_from_cart(request, product_id):
    # get the product from the database
    product = Product.objects.get(id=product_id)
    customer = request.user.customer
    cart_item = CartItem.objects.get(customer=customer, product=product)
    cart_item.delete()
    messages.success(request, 'Product removed from cart successfully')
    return redirect('/customer/cart/')


def update_cart_quantity(request, product_id):
    # get the product from the database
    product = Product.objects.get(id=product_id)
    price = product.price
    customer = request.user.customer
    cart_item = CartItem.objects.get(customer=customer, product=product)
    quantity = request.POST.get('quantity')
    amount = price * int(quantity)
    cart_item.quantity = quantity
    cart_item.price = price
    cart_item.amount = amount
    cart_item.save()
    messages.success(request, 'Product quantity updated successfully')
    return redirect('/cart/')


@login_required(login_url='/auth/login/')
def checkout(request):
    customer = request.user.customer
    cart_items = CartItem.objects.filter(customer=customer)
    total = sum([cart_item.amount for cart_item in cart_items])
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.customer = customer
            delivery_address.save()
            messages.success(request, 'Delivery address saved successfully')
            return redirect('/customer/payment/')
    else:
        form = CheckoutForm()
    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    return render(request, 'customer_cart/checkout.html', context)


# add to wishlist function for customer
def add_to_wishlist(request, product_id):
    # get the product from the database
    product = Product.objects.get(id=product_id)
    # check if the user is authenticated
    if request.user.is_authenticated:
        customer = request.user.customer
        # check if the product is already in the wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
        if created:
            messages.success(request, 'Product added to wishlist successfully')
            return redirect('/')
        else:
            messages.success(request, 'Product already in wishlist')
            return redirect('/')
    else:
        messages.success(request, 'Please login to add product to wishlist')
        return redirect('/auth/login/')


# view wishlist function for customer
def view_wishlist(request):
    if request.user.is_authenticated:
        wishlist = request.user.customer.wishlist_set.all()
        context = {
            'wishlist': wishlist,
        }
        return render(request, 'customer_wishlist/view_wishlist.html', context)
    else:
        messages.success(request, 'Please login to view wishlist')
        return redirect('/auth/login/')


# remove from wishlist function for customer
def remove_from_wishlist(request, product_id):
    # get the product from the database
    product = Product.objects.get(id=product_id)
    customer = request.user.customer
    try:
        wishlist_item = Wishlist.objects.get(customer=customer, product=product)
        wishlist_item.delete()
        messages.success(request, 'Product removed from wishlist successfully')
    except Wishlist.DoesNotExist:
        messages.warning(request, 'Product not found in wishlist')
    return redirect('/customer/wishlist/')


# add all products to cart form wishlist function for customer
def add_all_to_cart_form_wishlist(request):
    customer = request.user.customer
    wishlist = customer.wishlist_set.all()
    for item in wishlist:
        product = item.product
        price = product.price
        quantity = 1
        amount = price * quantity
        # check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
        if created:
            cart_item.quantity = quantity
            cart_item.price = price
            cart_item.amount = amount
            cart_item.save()
            wishlist.delete()
        else:
            cart_item.quantity += quantity
            cart_item.price = price
            cart_item.amount += amount
            cart_item.save()
            wishlist.delete()
    messages.success(request, 'All products added to cart successfully')
    return redirect('/customer/cart/')


# add list selected products to cart from wishlist function for customer
def add_selected_products_from_wishlist(request):
    customer = request.user.customer
    wishlist = customer.wishlist_set.all()
    for item in wishlist:
        product = item.product
        price = product.price
        quantity = 1
        amount = price * quantity
        # check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
        if created:
            cart_item.quantity = quantity
            cart_item.price = price
            cart_item.amount = amount
            cart_item.save()
        else:
            cart_item.quantity += quantity
            cart_item.price = price
            cart_item.amount += amount
            cart_item.save()
    messages.success(request, 'All products added to cart successfully')
    return redirect('/customer/cart/')
