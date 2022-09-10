from django.contrib import admin

from membership.models import Plan, Subscription, StripeTransactionHistory


class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "stripe_plan_id", "is_active")
    exclude = ("stripe_plan_id", "stripe_product_id")


admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription)
admin.site.register(StripeTransactionHistory)
