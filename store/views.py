from django.shortcuts import render, get_object_or_404

from .models import Product, Order, OrderItem


def home(request):
    products = Product.objects.all()

    return render(
        request,
        "index.html",
        {
            "products": products
        }
    )


def buy_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")

        quantity = int(
            request.POST.get("quantity", 1)
        )

        total_amount = product.price * quantity

        order = Order.objects.create(
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            total_amount=total_amount,
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )

        return render(
            request,
            "order_success.html",
            {
                "order": order,
                "product": product,
            }
        )

    return render(
        request,
        "order.html",
        {
            "product": product
        }
    )