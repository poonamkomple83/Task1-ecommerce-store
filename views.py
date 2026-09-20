from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from .models import Product, Order, OrderItem


def home(request):

    products = Product.objects.all()

    return render(
        request,
        "store/home.html",
        {
            "products": products
        }
    )


def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product
        }
    )


def add_to_cart(request, product_id):

    if request.method != "POST":
        return redirect(
            "product_detail",
            product_id
        )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )
    except ValueError:
        quantity = 1

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:

        messages.error(
            request,
            "Not enough stock available."
        )

        return redirect(
            "product_detail",
            product_id
        )

    cart = request.session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    current_quantity = cart.get(
        product_key,
        0
    )

    new_quantity = current_quantity + quantity

    if new_quantity > product.stock:
        new_quantity = product.stock

    cart[product_key] = new_quantity

    request.session["cart"] = cart

    request.session.modified = True

    messages.success(
        request,
        f"{product.name} added to cart."
    )

    return redirect("cart")


def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    cart_items = []

    grand_total = Decimal("0")

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        total = product.price * quantity

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "total": total
            }
        )

        grand_total += total

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "grand_total": grand_total
        }
    )


def remove_from_cart(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    if product_key in cart:

        del cart[product_key]

    request.session["cart"] = cart

    request.session.modified = True

    messages.success(
        request,
        "Product removed from cart."
    )

    return redirect("cart")


def register(request):

    if request.method == "POST":

        form = UserCreationForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("home")

    else:

        form = UserCreationForm()

    return render(
        request,
        "store/register.html",
        {
            "form": form
        }
    )


def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user
            )

            messages.success(
                request,
                "Login successful."
            )

            return redirect("home")

    else:

        form = AuthenticationForm()

    return render(
        request,
        "store/login.html",
        {
            "form": form
        }
    )


def user_logout(request):

    if request.method == "POST":

        logout(request)

    return redirect("home")


@login_required
def checkout(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    cart_items = []

    grand_total = Decimal("0")

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

            return redirect("cart")

        total = product.price * quantity

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "total": total
            }
        )

        grand_total += total

    if request.method == "POST":

        order = Order.objects.create(
            user=request.user,
            total_amount=grand_total,
            status="Pending"
        )

        for item in cart_items:

            product = item["product"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                price=product.price
            )

            product.stock -= item["quantity"]

            product.save()

        request.session["cart"] = {}

        request.session.modified = True

        return render(
            request,
            "store/order_success.html",
            {
                "order": order
            }
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "grand_total": grand_total
        }
    )
