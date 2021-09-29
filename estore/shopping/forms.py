from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from . import constants


class CheckoutForm(forms.Form):
    # TODO: add functionality for these fields
    # shipping_address = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(attrs={"placeholder": "1234 Main St", "class": "form-control"}),
    # )
    # shipping_address2 = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(attrs={"placeholder": "Apartment or suite", "class": "form-control"}),
    # )
    # shipping_country = CountryField(
    #     blank_label="(select country)").formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={"class": "custom-select d-block w-100"})
    # )
    # shipping_postal_code = forms.CharField(
    #     required=False,
    #     max_length=6,
    #     widget=forms.TextInput(attrs={"class": "form-control"})
    # )

    billing_address = forms.CharField(
        required=False,  # TODO: temporary
        widget=forms.TextInput(
            attrs={"placeholder": "1234 Main St", "class": "form-control"}
        ),
    )
    billing_address2 = forms.CharField(
        required=False,  # TODO: temporary
        widget=forms.TextInput(
            attrs={"placeholder": "Apartment or suite", "class": "form-control"}
        ),
    )
    billing_country = CountryField(blank_label="(select country)").formfield(
        required=False,  # TODO: temporary
        widget=CountrySelectWidget(attrs={"class": "custom-select d-block w-100"}),
    )
    billing_postal_code = forms.CharField(
        required=False,  # TODO: temporary
        max_length=6,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    same_shipping_address = forms.BooleanField(
        required=False, widget=forms.CheckboxInput()
    )
    set_default_billing = forms.BooleanField(
        required=False, widget=forms.CheckboxInput()
    )

    # TODO: add functionality for commented fields
    # set_default_shipping = forms.BooleanField(required=False)
    # use_default_shipping = forms.BooleanField(required=False)
    # use_default_billing = forms.BooleanField(required=False)

    # TODO: temporary required value ... change back to True later
    payment_option = forms.ChoiceField(
        choices=constants.PAYMENT_CHOICES, required=False, widget=forms.RadioSelect()
    )


class CouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Promo code",
                "aria-label": "Recipient's username",
                "aria-describedly": "basic-addon2",
            }
        )
    )
