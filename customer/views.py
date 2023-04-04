from datetime import datetime

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import FeedbackForm
from main.models import Customer, Category, Brand, Product, Coupon, Feedback, CartItem, DeliveryAddress, Orders, \
    OrderDetails, Wishlist, Payment
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
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
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
            page_obj = paginator(request, products)
        elif filter_by_brand:
            products = products.filter(brand__id=filter_by_brand)
            page_obj = paginator(request, products)
        # apply category filter if selected
        elif filter_by_category:
            products = products.filter(category__id=filter_by_category)
            page_obj = paginator(request, products)
        # apply search filter if search query exists
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(
                    category__name__icontains=search_query) | Q(
                    brand__name__icontains=search_query) | Q(slug__icontains=search_query)
            )
            page_obj = paginator(request, products)
        # apply sorting based on selected option
        if sort_by == 'newest':
            products = products.order_by('-created_date')
        elif sort_by == 'best_seller':
            products = products.order_by('-sold')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        if filter_by_brand:
            filter_by_brand = int(filter_by_brand)
        if filter_by_category:
            filter_by_category = int(filter_by_category)
        page_obj = paginator(request, products)
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
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'customer_help/customer_product_list.html', context)


@login_required(login_url='/auth/login')
def add_to_cart(request, slug):
    if request.method == 'POST':
        product = Product.objects.get(slug=slug)
        quantity = int(request.POST.get('quantity'))
        if quantity > product.stock:
            messages.warning(request, 'Product stock is not available')
            return redirect('/customer/product/details/' + slug)
    else:
        product = Product.objects.get(slug=slug)
        quantity = 1
        if quantity > product.stock:
            messages.warning(request, 'Product stock is not available')
            return redirect('/customer/product/details/' + slug)

    customer = request.user.customer if request.user.is_authenticated else None

    try:
        cart_item = CartItem.objects.get(customer=customer, product=product)
    except CartItem.DoesNotExist:
        cart_item = None

    # Check if coupon is already applied to any of the cart items
    cart_items = CartItem.objects.filter(customer=customer)
    coupon_applied = any(cart_item.coupon_applied for cart_item in cart_items)

    if cart_item is None:
        sub_total = product.price * quantity
        cart_item = CartItem(customer=customer, product=product, quantity=quantity,
                             price=product.price, sub_total=sub_total)
    else:
        cart_item.quantity += quantity
        cart_item.sub_total += product.price * quantity

    # Update coupon code if a coupon is already applied to the cart
    if coupon_applied:
        applied_coupon = CartItem.objects.filter(customer=customer, coupon_applied=True).first().coupon
        cart_item.discount = applied_coupon.discount * cart_item.quantity
        cart_item.coupon = applied_coupon
        cart_item.coupon.amount = cart_item.coupon.amount - quantity
        cart_item.coupon.save()
        cart_item.coupon_applied = True
        cart_item.sub_total = cart_item.get_total_amount_with_coupon

    cart_item.save()

    if cart_item.quantity == quantity:
        messages.success(request, 'Product added to cart successfully')
    else:
        messages.success(request, 'Product quantity updated successfully')

    return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
# view cart function for customer
def view_cart(request):
    customer = request.user.customer
    cart_items = CartItem.objects.filter(customer=customer).order_by('-date_added')
    total = sum(item.sub_total for item in cart_items)
    total_amount_without_coupon = sum(item.get_total_amount_without_coupon for item in cart_items)
    total_amount_with_coupon = sum(item.get_total_amount_with_coupon for item in cart_items)
    #  check if any coupon is applied
    if cart_items.filter(coupon_applied=True).exists():
        code = cart_items[0].coupon.code if cart_items[0].coupon_applied is True else None
        discount = sum(item.get_discount for item in cart_items)
    else:
        code = None
        discount = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
    }
    return render(request, 'customer_cart/view_cart.html', context)


@login_required(login_url='/auth/login')
def remove_from_cart(request, slug):
    # Get the product and customer from the database
    product = Product.objects.get(slug=slug)
    customer = request.user.customer

    # Get the cart item for the product and customer, and delete it
    cart_item = CartItem.objects.get(customer=customer, product=product)
    if cart_item.coupon_applied is True and cart_item.coupon is not None:
        # restore amount to coupon
        coupon = cart_item.coupon
        coupon.amount = coupon.amount + cart_item.quantity
        coupon.save()
    cart_item.delete()

    # Show success message and redirect to cart page
    messages.success(request, 'Product removed from cart successfully')
    return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
def add_quantity(request, slug):
    # Get the product and customer from the database
    product = Product.objects.get(slug=slug)
    customer = request.user.customer

    # Get the cart item for the product and customer
    cart_item = CartItem.objects.get(customer=customer, product=product)

    # Check if the quantity can be increased, and update the cart item
    if cart_item.quantity < product.stock:
        if cart_item.coupon_applied is True and cart_item.coupon is not None:
            # restore amount to coupon
            coupon = cart_item.coupon
            coupon.amount = coupon.amount + 1
            coupon.save()
        cart_item.quantity += 1
        if cart_item.discount > 0:
            cart_item.discount = cart_item.coupon.discount * cart_item.quantity
        cart_item.sub_total += cart_item.price
        cart_item.save()
        messages.success(request, 'Product quantity updated successfully')
    else:
        messages.success(request, 'Product out of stock')

    # Redirect to cart page
    return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
def remove_quantity(request, slug):
    # Get the product and customer from the database
    product = Product.objects.get(slug=slug)
    customer = request.user.customer

    # Get the cart item for the product and customer
    cart_item = CartItem.objects.get(customer=customer, product=product)

    # Check if the quantity can be decreased, and update the cart item or delete it
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        if cart_item.coupon_applied is True and cart_item.coupon is not None:
            # restore amount to coupon
            coupon = cart_item.coupon
            coupon.amount = coupon.amount - cart_item.quantity + 1
            coupon.save()
        if cart_item.discount > 0:
            cart_item.discount = cart_item.coupon.discount * cart_item.quantity
        cart_item.sub_total -= cart_item.price
        cart_item.save()
        messages.success(request, 'Product quantity updated successfully')
    else:
        cart_item.delete()
        messages.success(request, 'Product removed from cart successfully')

    # Redirect to cart page
    return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
def update_quantity(request, slug):
    # Get the product and customer from the database
    product = Product.objects.get(slug=slug)
    customer = request.user.customer

    # Get the cart item for the product and customer
    cart_item = CartItem.objects.get(customer=customer, product=product)

    # If the form is submitted
    if request.method == "POST":
        # Get the new quantity value from the form
        quantity = int(request.POST.get('quantity'))

        # Update or delete the cart item based on the new quantity
        if quantity == 0:
            if cart_item.coupon_applied is True and cart_item.coupon is not None:
                # restore amount to coupon
                coupon = cart_item.coupon
                coupon.amount = coupon.amount + cart_item.quantity - 1
                coupon.save()
            cart_item.delete()
            messages.success(request, 'Product removed from cart successfully')
        elif quantity < 0:
            messages.success(request, 'Quantity cannot be less than 0')
        else:
            if quantity > product.stock:
                messages.success(request, 'Product stock is not available')
            else:
                if cart_item.coupon_applied is True and cart_item.coupon is not None:
                    # restore amount to coupon
                    coupon = cart_item.coupon
                    coupon.amount = coupon.amount + cart_item.quantity - quantity
                    coupon.save()
                cart_item.quantity = quantity
                if cart_item.discount > 0:
                    cart_item.discount = cart_item.coupon.discount * cart_item.quantity
                cart_item.sub_total = quantity * cart_item.price
                cart_item.total = cart_item.sub_total
                cart_item.save()
                messages.success(request, 'Product quantity updated successfully')

    # Redirect to cart page
    return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            # get coupon with condition that it is active and datetime is less than current datetime
            coupon = Coupon.objects.get(code=coupon_code, is_active=True, valid_from__lte=datetime.now(),
                                        valid_to__gte=datetime.now())
            customer = request.user.customer  # get customer
            cart_items = CartItem.objects.filter(customer=customer)  # get cart items
            subtotal = sum(item.sub_total for item in cart_items)  # get subtotal

            # Check if coupon is applicable
            if coupon.amount <= subtotal:
                # Check if coupon has already been applied to the cart items
                if any(cart_item.coupon_applied for cart_item in cart_items):
                    messages.warning(request, 'Coupon has already been applied')
                    return redirect('/customer/cart/')

                total_discount = 0
                for cart_item in cart_items:
                    # update coupon amount
                    coupon.amount = coupon.amount - cart_item.quantity
                    coupon.save()
                    cart_item.discount = coupon.discount * cart_item.quantity
                    cart_item.sub_total = cart_item.get_total_amount_with_coupon
                    cart_item.coupon = coupon
                    cart_item.coupon_applied = True
                    cart_item.save()
                    total_discount += coupon.discount * cart_item.quantity

                messages.success(request, f'Coupon {coupon.code} applied successfully. You saved (${total_discount})')
                return redirect('/customer/cart/')
            else:
                messages.warning(request, 'Coupon is not applicable for this order')
                return redirect('/customer/cart/')
        except Coupon.DoesNotExist:
            messages.warning(request, 'Invalid coupon code')
            return redirect('/customer/cart/')
    else:
        messages.warning(request, 'Invalid request')
        return redirect('/customer/cart/')


@login_required(login_url='/auth/login')
def remove_coupon(request):
    customer = request.user.customer
    cart_items = CartItem.objects.filter(customer=customer)
    coupon = Coupon.objects.get(code=cart_items[0].coupon.code)
    for cart_item in cart_items:
        # restore amount to coupon
        coupon.amount = coupon.amount + cart_item.quantity
        coupon.save()
        cart_item.discount = 0
        cart_item.sub_total = cart_item.get_total_amount_without_coupon
        cart_item.coupon = None
        cart_item.coupon_applied = False
        cart_item.save()

    messages.success(request, 'Coupon removed successfully')
    return redirect('/customer/cart/')


# add to wishlist function for customer
def add_to_wishlist(request, slug):
    # get the product from the database
    product = Product.objects.get(slug=slug)
    # check if the user is authenticated
    customer = request.user.customer
    # check if the product is already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
    if created:
        messages.success(request, 'Product added to wishlist successfully. You can view it in your wishlist')
        return redirect('/')
    else:
        messages.success(request, 'Product already in wishlist')
        return redirect('/')


# view wishlist function for customer
@login_required(login_url='/auth/login')
def view_wishlist(request):
    customer = request.user.customer
    wishlists = Wishlist.objects.filter(customer=customer).order_by('-date_added')
    context = {
        'wishlists': wishlists,
    }
    return render(request, 'customer_wishlist/view_wishlist.html', context)


# remove from wishlist function for customer
@login_required(login_url='/auth/login')
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
@login_required(login_url='/auth/login')
def add_all_to_cart_form_wishlist(request):
    customer = request.user.customer
    wishlists = customer.wishlist_set.all()
    for item in wishlists:
        product = item.product
        price = product.price
        quantity = 1
        sub_total = price * quantity
        # check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
        if created:
            cart_item.quantity = quantity
            cart_item.price = price
            cart_item.sub_total = sub_total
            cart_item.save()
            wishlists.delete()
        else:
            cart_item.quantity += quantity
            cart_item.price = price
            cart_item.sub_total += sub_total
            cart_item.save()
            wishlists.delete()
    messages.success(request, 'All products added to cart successfully')
    return redirect('/customer/cart/')


# checkout function for customer
@login_required(login_url='/auth/login/')
def checkout(request):
    # check if the cart is empty
    customer = request.user.customer
    cart_items = CartItem.objects.filter(customer=customer)
    if cart_items.count() == 0:
        messages.warning(request, 'Your cart is empty. Please add some products to your cart to checkout')
        return redirect('/customer/cart/')
    else:
        user = request.user
        customer = user.customer
        payment_methods = Payment.METHOD_CHOICES
        delivery_address = DeliveryAddress.objects.filter(customer=customer)
        cart_items = CartItem.objects.filter(customer=customer)
        # Auto create transaction_id for order
        transaction_id = datetime.now().timestamp()
        if request.method == 'POST':
            # Save delivery address that customer selected
            delivery_address_id = request.POST.get('delivery_address')
            delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
            # Save payment method that customer selected
            payment_method = request.POST.get('payment_method')
            # Save orders
            order = Orders.objects.create(
                customer=customer,
                status='Pending',
                sub_total=sum([cart_item.sub_total for cart_item in cart_items]),
                total_discount=sum([cart_item.discount for cart_item in cart_items]),
                total_amount=sum([cart_item.sub_total for cart_item in cart_items]) - sum(
                    [cart_item.discount for cart_item in cart_items]),
                delivery_address=delivery_address,
            )
            # Save OrderDetails for each item in the cart
            for cart_item in cart_items:
                OrderDetails.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    sub_total=cart_item.sub_total,
                    discount=cart_item.discount,
                    coupon=cart_item.coupon,
                    coupon_applied=cart_item.coupon_applied,
                )
            # Save payment details
            Payment.objects.create(
                customer=customer,
                order=order,
                payment_method=payment_method,
                payment_status='Pending',
                amount=sum([cart_item.sub_total for cart_item in cart_items]) - sum(
                    cart_item.discount for cart_item in cart_items),
                transaction_id=transaction_id,
            )
            # Update product stock and sold
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.sold += cart_item.quantity
                product.save()
            # Delete cart items
            cart_items.delete()
            # Send email to admin
            # Get email is admin
            customer = request.user.customer
            order = Orders.objects.filter(customer=customer, status='Pending').last()
            order_details = OrderDetails.objects.filter(order=order)
            admin = User.objects.get(is_superuser=True)
            send_email_order_admin(request, admin.email, order, order_details, customer)
            # Send email to customer
            send_email_order_customer(request, delivery_address.email, order, order_details, customer)
            send_email_order_customer(request, user.email, order, order_details, customer)
            messages.success(request, 'Order placed successfully')
            return redirect('/')

        total = sum([cart_item.sub_total for cart_item in cart_items])
        context = {
            'delivery_address': delivery_address,
            'cart_items': cart_items,
            'total': total,
            'payment_methods': payment_methods,
        }
        return render(request, 'customer_checkout/checkout.html', context)


def send_email_order_admin(request, email, order, order_details, customer):
    current_site = get_current_site(request)
    mail_subject = 'New order placed.'
    message = render_to_string('customer_checkout/email_orders_admin.html', {
        'domain': current_site.domain,
        'order': order,
        'order_details': order_details,
        'customer': customer,
        'protocol': 'http',
    })
    to_email = [email]
    from_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, from_email, to_email)
    email.content_subtype = "html"
    email.send()


def send_email_order_customer(request, email, order, order_details, customer):
    current_site = get_current_site(request)
    mail_subject = 'Order placed successfully.'
    message = render_to_string('customer_checkout/email_orders_customer.html', {
        'domain': current_site.domain,
        'order': order,
        'order_details': order_details,
        'customer': customer,
        'protocol': 'http',
    })
    to_email = [email]
    from_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, from_email, to_email)
    email.content_subtype = "html"
    email.send()


@login_required(login_url='/auth/login/')
def track_orders(request):
    customer = request.user.customer
    orders = Orders.objects.filter(customer=customer)
    order_details = OrderDetails.objects.filter(id=orders)
    context = {
        'orders': orders,
        'order_details': order_details,
    }
    return render(request, 'customer_orders/track_orders.html', context)


def get_address(request, address_id):
    try:
        address = DeliveryAddress.objects.get(id=address_id)
        return JsonResponse({
            'first_name': address.first_name,
            'last_name': address.last_name,
            'mobile': address.mobile,
            'email': address.email,
            'address': address.address,
            'city': address.city,
            'state': address.state,
            'country': address.country,
            'zip_code': address.zip_code,
        })
    except DeliveryAddress.DoesNotExist:
        return JsonResponse({'error': 'Address not found'}, status=404)
