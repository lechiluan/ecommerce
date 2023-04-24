from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
from .forms import FeedbackForm
from main.models import Customer, Category, Brand, Product, Coupon, Feedback, CartItem, DeliveryAddress, Orders, \
    OrderDetails, Wishlist, Payment, Review
from django.contrib.auth.models import User
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


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
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'Register newsletter.'
    message = render_to_string('registration/register/email_newsletter.html', {
        'domain': current_site.domain,
        'email': email,
        'protocol': protocol,
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
    reviews = Review.objects.filter(product=product, review_status=True).order_by('-date_added')
    get_review_count_for_product = Review.objects.filter(product=product).count()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    recommended_products = Product.objects.all().order_by('-view_count')[:4]

    # Update view count
    product.view_count += 1
    product.save()

    discount_price = product.old_price - product.price
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        reviews_customer = Review.objects.filter(product=product, customer=customer, review_status=True)
    else:
        customer = None
        reviews_customer = None
    context = {
        'discount_price': discount_price,
        'customer': customer,
        'reviews_customer': reviews_customer,
        'reviews': reviews,
        'product': product,
        'get_review_count_for_product': get_review_count_for_product,
        'related_products': related_products,
        'recommended_products': recommended_products,
    }
    return render(request, 'customer_help/customer_product_details.html', context)


# Search product and filter product
def product_search(request):
    if request.method == 'POST':
        # get the search query from the request
        search_query = request.POST.get('search')
        sort_by = request.POST.get('sort_by')
        filter_by_brand = request.POST.get('filter_by_brand')
        filter_by_category = request.POST.get('filter_by_category')
        products = Product.objects.all().order_by('-sold')
        sort_price = request.POST.get('sort_price')

        # apply brand filter if selected
        if filter_by_brand and filter_by_category:
            products = products.filter(brand__id=filter_by_brand, category__id=filter_by_category)

        elif filter_by_brand:
            products = products.filter(brand__id=filter_by_brand)

        # apply category filter if selected
        elif filter_by_category:
            products = products.filter(category__id=filter_by_category)

        # apply search filter if search query exists
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(
                    category__name__icontains=search_query) | Q(
                    brand__name__icontains=search_query) | Q(slug__icontains=search_query)
            )
        # apply sorting based on selected option
        if sort_by == 'newest':
            products = products.order_by('-created_date')
        elif sort_by == 'best_seller':
            products = products.order_by('-sold')
        elif sort_by == 'most_viewed':
            products = products.order_by('-view_count')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')

        if sort_price == 'less_100':
            products = products.filter(price__lte=100)
        elif sort_price == '100_500':
            products = products.filter(price__gte=100, price__lte=500)
        elif sort_price == '500_1000':
            products = products.filter(price__gte=500, price__lte=1000)
        elif sort_price == '1000_2000':
            products = products.filter(price__gte=1000, price__lte=2000)
        elif sort_price == 'greater_2000':
            products = products.filter(price__gte=2000)

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
            'sort_price': sort_price,
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
        products = Product.objects.all().order_by('-sold')
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


@login_required(login_url='/auth/login/')
def add_review(request, slug):
    if request.method == 'POST':
        product = Product.objects.get(slug=slug)
        customer = request.user.customer
        name = request.POST.get('name')
        rate = request.POST.get('rating')
        message_review = request.POST.get('message')
        try:
            review = Review.objects.get(product=product, customer=customer)
            review.name = name
            review.rate = rate
            review.message_review = message_review
            review.review_status = 'True'
            review.save()
            # Update product rating
            review_rate_average = Review.objects.filter(product=product).aggregate(Avg('rate'))
            product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
            # Update product review count
            product.review_count = Review.objects.filter(product=product).count()
            product.save()
            messages.success(request, 'Review updated successfully. Thanks for your review to improve our service.')
            return redirect('/customer/product/details/{}/'.format(slug))
        except Review.DoesNotExist:
            review = Review.objects.create(product=product, customer=customer, name=name, rate=rate,
                                           message_review=message_review)
            review.save()
            # Update product rating
            review_rate_average = Review.objects.filter(product=product).aggregate(Avg('rate'))
            product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
            # Update product review count
            product.review_count = Review.objects.filter(product=product).count()
            product.save()
            messages.success(request, 'Review updated successfully. Thanks for your review to improve our service.')
            return redirect('/customer/product/details/{}/'.format(slug))
    else:
        return redirect('/customer/product/details/{}/'.format(slug))


@login_required(login_url='/auth/login/')
def edit_review(request, review_id):
    review = Review.objects.get(id=review_id)
    product = review.product
    if request.method == 'POST':
        review.name = request.POST.get('name')
        review.rate = request.POST.get('rating')
        review.message_review = request.POST.get('message')
        review.review_status = 'True'
        review.save()
        review_rate_average = Review.objects.filter(product=product).aggregate(Avg('rate'))
        product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
        # Update product review count
        product.review_count = Review.objects.filter(product=product).count()
        product.save()
        messages.success(request, 'Review updated successfully')
        return redirect('/customer/product/details/{}/'.format(review.product.slug))
    else:
        return redirect('/customer/product/details/{}/'.format(review.product.slug))


@login_required(login_url='/auth/login/')
def delete_review(request, review_id):
    review = Review.objects.get(id=review_id)
    review.delete()
    # Update product rating
    review_rate_average = Review.objects.filter(product=review.product).aggregate(Avg('rate'))
    review.product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
    # Update product review count
    review.product.review_count = Review.objects.filter(product=review.product).count()
    review.product.save()
    messages.success(request, 'Review deleted successfully')
    return redirect('/customer/product/details/' + review.product.slug)


@login_required(login_url='/auth/login/')
def add_to_cart(request, slug):
    if request.method == 'POST':
        product = Product.objects.get(slug=slug)
        quantity = int(request.POST.get('quantity'))
        if quantity > product.stock:
            messages.warning(request, 'Product stock is not available')
            return redirect('/customer/product/details/{}/'.format(slug))
    else:
        product = Product.objects.get(slug=slug)
        quantity = 1
        if quantity > product.stock:
            messages.warning(request, 'Product stock is not available')
            return redirect('/customer/product/details/{}/'.format(slug))

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


@login_required(login_url='/auth/login/')
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

    recommended_products = Product.objects.all().order_by('-view_count')[:4]

    context = {
        'cart_items': cart_items,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
        'recommended_products': recommended_products,
    }
    return render(request, 'customer_cart/view_cart.html', context)


@login_required(login_url='/auth/login/')
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
    next_url = request.GET.get('next', '/customer/cart/')
    return redirect(next_url)


@login_required(login_url='/auth/login/')
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
    next_url = request.GET.get('next', '/customer/cart/')
    return redirect(next_url)


@login_required(login_url='/auth/login/')
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
    next_url = request.GET.get('next', '/customer/cart/')
    return redirect(next_url)


@login_required(login_url='/auth/login/')
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
    next_url = request.GET.get('next', '/customer/cart/')
    return redirect(next_url)


@login_required(login_url='/auth/login/')
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
                    next_url = request.GET.get('next', '/customer/cart/')
                    return redirect(next_url)

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
                next_url = request.GET.get('next', '/customer/cart/')
                return redirect(next_url)
            else:
                messages.warning(request, 'Coupon is not applicable for this order')
                next_url = request.GET.get('next', '/customer/cart/')
                return redirect(next_url)
        except Coupon.DoesNotExist:
            messages.warning(request, 'Invalid coupon code')
            next_url = request.GET.get('next', '/customer/cart/')
            return redirect(next_url)
    else:
        messages.warning(request, 'Invalid request')
        next_url = request.GET.get('next', '/customer/cart/')
        return redirect(next_url)


@login_required(login_url='/auth/login/')
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
    next_url = request.GET.get('next', '/customer/cart/')
    return redirect(next_url)


# add to wishlist function for customer
@login_required(login_url='/auth/login/')
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
@login_required(login_url='/auth/login/')
def view_wishlist(request):
    customer = request.user.customer
    wishlists = Wishlist.objects.filter(customer=customer).order_by('-date_added')
    recommended_products = Product.objects.all().order_by('-view_count')[:4]
    context = {
        'wishlists': wishlists,
        'recommended_products': recommended_products
    }
    return render(request, 'customer_wishlist/view_wishlist.html', context)


# remove from wishlist function for customer
@login_required(login_url='/auth/login/')
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
@login_required(login_url='/auth/login/')
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
            total_profit = sum(
                [(cart_item.product.price - cart_item.product.price_original) * cart_item.quantity - cart_item.discount
                 for cart_item in
                 cart_items])

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
            order.profit_order = total_profit
            order.save()

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
                total=sum([cart_item.sub_total for cart_item in cart_items]) - sum(
                    cart_item.discount for cart_item in cart_items),
                transaction_id=int(transaction_id),
            )
            # Update product stock and sold
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.sold += cart_item.quantity
                product.profit += (cart_item.product.price - cart_item.product.price_original) \
                                  * cart_item.quantity - cart_item.discount
                product.save()
            # Delete cart items
            cart_items.delete()
            # Send email to admin
            customer = request.user.customer
            order = Orders.objects.filter(customer=customer, status='Pending').last()
            order_details = OrderDetails.objects.filter(order=order)
            admin = User.objects.get(is_superuser=True)
            send_email_order_admin(request, admin.email, order, order_details, customer)
            # Send email to customer
            send_email_order_customer(request, delivery_address.email, order, order_details, customer)
            send_email_order_customer(request, user.email, order, order_details, customer)
            messages.success(request, 'Order placed successfully')
            context = {
                'order': order,
            }
            return render(request, 'customer_cart/orders_success.html', context)
        # Display Cart Items in the checkout page
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
        recommended_products = Product.objects.all().order_by('-view_count')[:4]
        context = {
            'cart_items': cart_items,
            'total': total,
            'code': code,
            'discount': discount,
            'total_amount_without_coupon': total_amount_without_coupon,
            'total_amount_with_coupon': total_amount_with_coupon,
            'delivery_address': delivery_address,
            'payment_methods': payment_methods,
            'recommended_products': recommended_products,
        }
        return render(request, 'customer_checkout/checkout.html', context)


def send_email_order_admin(request, email, order, order_details, customer):
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'New order placed.'
    message = render_to_string('customer_checkout/email_orders_admin.html', {
        'domain': current_site.domain,
        'order': order,
        'order_details': order_details,
        'customer': customer,
        'protocol': protocol,
    })
    to_email = [email]
    from_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, from_email, to_email)
    email.content_subtype = "html"
    email.send()


def send_email_order_customer(request, email, order, order_details, customer):
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'Order placed successfully.'
    message = render_to_string('customer_checkout/email_orders_customer.html', {
        'domain': current_site.domain,
        'order': order,
        'order_details': order_details,
        'customer': customer,
        'protocol': protocol,
    })
    to_email = [email]
    from_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, from_email, to_email)
    email.content_subtype = "html"
    email.send()


@login_required(login_url='/auth/login/')
def track_orders(request):
    customer = request.user.customer
    orders = Orders.objects.filter(customer=customer).order_by('-id')
    page_object = paginator(request, orders)
    context = {'orders': page_object}

    return render(request, 'customer_orders/track_orders.html', context)


@login_required(login_url='/auth/login/')
def track_orders_search(request):
    customer = request.user.customer
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/order/')
        else:
            orders = Orders.objects.filter(customer=customer, id__icontains=search_query).order_by('-id') | \
                     Orders.objects.filter(customer=customer,
                                           delivery_address__address__icontains=search_query).order_by('-id')

            page_object = paginator(request, orders)

        if not orders:
            messages.success(request, 'No orders found {} !'.format(search_query))

    else:
        orders = Orders.objects.filter(customer=customer).order_by('-id')
        page_object = paginator(request, orders)
    context = {'orders': page_object,
               'search_query': search_query}
    return render(request, 'customer_orders/track_orders.html', context)


@login_required(login_url='/auth/login/')
def track_order_details(request, order_id):
    customer = request.user.customer
    order = Orders.objects.get(customer=customer, id=order_id)
    order_details = OrderDetails.objects.filter(order=order)
    total = sum(item.sub_total for item in order_details)
    total_amount_without_coupon = sum(item.get_total_amount_without_coupon for item in order_details)
    total_amount_with_coupon = sum(item.get_total_amount_with_coupon for item in order_details)
    #  check if any coupon is applied
    if order_details.filter(coupon_applied=True).exists():
        code = order_details[0].coupon.code if order_details[0].coupon_applied is True else None
        discount = sum(item.get_discount for item in order_details)
    else:
        code = None
        discount = 0
    delivery_address = DeliveryAddress.objects.get(id=order.delivery_address.id)
    payment = Payment.objects.get(order=order)
    context = {
        'order': order,
        'order_details': order_details,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
        'delivery_address': delivery_address,
        'payment': payment,
    }
    return render(request, 'customer_orders/track_orders_details.html', context)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


# download invoice
@login_required(login_url='/auth/login/')
def download_invoice(request, order_id):
    customer = request.user.customer
    order = Orders.objects.get(customer=customer, id=order_id)
    order_details = OrderDetails.objects.filter(order=order)
    total = sum(item.sub_total for item in order_details)
    total_amount_without_coupon = sum(item.get_total_amount_without_coupon for item in order_details)
    total_amount_with_coupon = sum(item.get_total_amount_with_coupon for item in order_details)
    #  check if any coupon is applied
    if order_details.filter(coupon_applied=True).exists():
        code = order_details[0].coupon.code if order_details[0].coupon_applied is True else None
        discount = sum(item.get_discount for item in order_details)
    else:
        code = None
        discount = 0
    delivery_address = DeliveryAddress.objects.get(id=order.delivery_address.id)
    payment = Payment.objects.get(order=order)
    context = {
        'order': order,
        'order_details': order_details,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
        'delivery_address': delivery_address,
        'payment': payment,
    }
    pdf = render_to_pdf('customer_orders/invoice.html', context)
    filename = 'lclshop_invoice_{}.pdf'.format(order_id)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


@login_required(login_url='/auth/login/')
def cancel_order(request, order_id):
    try:
        customer = request.user.customer
        order = Orders.objects.get(customer=customer, id=order_id, status='Pending')
    except ObjectDoesNotExist:
        messages.warning(request, 'The order {} you are trying to delete does not exist!'.format(order_id))
        return redirect('/customer/track_orders/')
    # Update Product Sold Count, Stock, Profit

    for order_detail in OrderDetails.objects.filter(order_id=order_id):
        product = Product.objects.get(id=order_detail.product_id)
        product.sold -= order_detail.quantity
        product.stock += order_detail.quantity
        product.profit -= (order_detail.product.price - order_detail.product.price_original) \
                          * order_detail.quantity - order_detail.discount
        product.save()

    # Delete order
    order.delete()
    messages.success(request, 'Order {} deleted successfully!'.format(order_id))
    return redirect('/customer/track_orders/')


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


def get_default_address(request):
    try:
        address = DeliveryAddress.objects.get(customer=request.user.customer, is_default=True)
        return JsonResponse({
            'id': address.id,
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
