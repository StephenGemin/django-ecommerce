CATEGORY_CHOICES = (
    ("All", "All"),
    ("Outerwear", "Outerwear"),
    ("Shirt", "Shirt"),
    ("Sport", "Sport"),
    ("Sportwear", "Sport-wear"),
)

LABEL_CHOICES = (
    ("D", "danger"),
    ("P", "primary"),
    ("S", "secondary"),
)

PAYMENT_CHOICES = (
    ("Stripe", "Stripe"),
    ("PayPal", "PayPal"),
    ("BitCoin", "BitCoin"),
)

COUPON_DISCOUNT_UOM = (
    ("percent", "%"),
    ("absolute", "$"),
)

ADDRESS_CHOICES = (
    ("B", "billing"),
    ("S", "shipping"),
)
