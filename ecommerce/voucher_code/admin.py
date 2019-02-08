from django.contrib import admin

from models import VoucherCode, VoucherPurchase

class VoucherCodeAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'expiration_date' ,'is_available')

class VoucherPurchaseAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'given_to', 'product_title')


admin.site.register(VoucherCode, VoucherCodeAdmin)

admin.site.register(VoucherPurchase, VoucherPurchaseAdmin)

