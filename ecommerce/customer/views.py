from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.contrib import messages
from django.template.loader import render_to_string
from .forms import FeedbackForm, CheckoutForm
from main.models import Customer, Category, Brand, Product, Coupon, Feedback, CartItem, DeliveryAddress, Orders, \
    OrderDetails, Wishlist
from django.contrib.auth.models import User


# Send email newsletter
def send_email_newsletter(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            messages.warning(request, 'This email already exists')
            return redirect('/')
        else:
            send_email(request, email)
            messages.success(request, 'Thank you for subscribing to our newsletter. We will send you the latest news')
            return redirect('/')
    else:
        return redirect('/')


def send_email(request, email):
    current_site = get_current_site(request)
    mail_subject = 'Register newsletter.'
    message = render_to_string('registration/register/email_newsletter.html', {
        'domain': current_site.domain,
        'email': email,
        'protocol': 'http',
    })
    to_email = [email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


def send_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your feedback has been sent successfully. We will contact you soon')
            return redirect('contact')
    else:
        form = FeedbackForm()
    return render(request, 'customer_help/feedback.html', {'form': form})


def about(request):
    return render(request, 'customer_help/about.html')


# Code pagination
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


# Code for display product
def product_details(request, slug):
    product = Product.objects.get(slug=slug)
    context = {
        'product': product,
    }
    return render(request, 'customer_help/customer_product_details.html', context)


# Search product and filter product
def product_search(request):
    if request.method == 'GET':
        # get the search query from the request
        search_query = request.GET.get('search')
        sort_by = request.GET.get('sort_by')
        filter_by_brand = request.GET.get('filter_by_brand')
        filter_by_category = request.GET.get('filter_by_category')
        products = Product.objects.all()

        # apply brand filter if selected
        if filter_by_brand and filter_by_category:
            products = products.filter(brand__id=filter_by_brand, category__id=filter_by_category)
            brand_name = Brand.objects.get(id=filter_by_brand).name
            category_name = Category.objects.get(id=filter_by_category).name
            messages.success(request, 'Filtered by brand: "' + brand_name + '" and category: "' + category_name + '"')

        elif filter_by_brand:
            products = products.filter(brand__id=filter_by_brand)
            brand_name = Brand.objects.get(id=filter_by_brand).name
            messages.success(request, 'Filtered by brand: "' + brand_name + '"')
        # apply category filter if selected
        elif filter_by_category:
            products = products.filter(category__id=filter_by_category)
            category_name = Category.objects.get(id=filter_by_category).name
            messages.success(request, 'Filtered by category: "' + category_name + '"')

        # apply search filter if search query exists
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(
                    category__name__icontains=search_query) | Q(
                    brand__name__icontains=search_query) | Q(slug__icontains=search_query)
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
        # messages.success(request, 'Found ' + str(page_obj.paginator.count) + ' products')
        # Convert filter_by_brand and filter_by_category to int
        if filter_by_brand:
            filter_by_brand = int(filter_by_brand)
        if filter_by_category:
            filter_by_category = int(filter_by_category)
        context = {
            'products': page_obj,
            'search_query': search_query,
            'sort_by': sort_by,
            'filter_by_brand': filter_by_brand,
            'filter_by_category': filter_by_category,
        }
        return render(request, 'customer_help/customer_product_list.html', context)
    else:
        products = Product.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)


# Display product by category
def product_list_category(request, slug):
    if slug == 'all':
        products = Product.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)
    else:
        category = Category.objects.get(slug=slug)
        products = Product.objects.filter(category=category)
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)


# Display product by brand
def product_list_brand(request, slug):
    if slug == 'all':
        products = Product.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)
    else:
        brand = Brand.objects.get(slug=slug)
        products = Product.objects.filter(brand=brand)
        categories = Category.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)


@login_required(login_url='/auth/login')
# add to cart function for customer
def add_to_cart(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
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


def remove_from_cart(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
    customer = request.user.customer
    cart_item = CartItem.objects.get(customer=customer, product=product)
    cart_item.delete()
    messages.success(request, 'Product removed from cart successfully')
    return redirect('/customer/cart/')


def update_cart_quantity(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
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
    return render(request, 'customer_cart/view_cart.html')


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
def add_to_wishlist(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
    # check if the user is authenticated
    if request.user.is_authenticated:
        customer = request.user.customer
        # check if the product is already in the wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
        if created:
            messages.success(request, 'Product added to wishlist successfully. You can view it in your wishlist')
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
        customer = request.user.customer
        wishlists = Wishlist.objects.filter(customer=customer)
        context = {
            'wishlists': wishlists,
        }
        return render(request, 'customer_wishlist/view_wishlist.html', context)
    else:
        messages.success(request, 'Please login to view wishlist')
        return redirect('/auth/login/')


# remove from wishlist function for customer
def remove_from_wishlist(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
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
    wishlists = customer.wishlist_set.all()
    for item in wishlists:
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
            wishlists.delete()
        else:
            cart_item.quantity += quantity
            cart_item.price = price
            cart_item.amount += amount
            cart_item.save()
            wishlists.delete()
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
    render(request, 'customer_cart/view_cart.html')
