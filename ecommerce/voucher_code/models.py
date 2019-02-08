from django.db import models
import datetime

class VoucherCode(models.Model):
    voucher = models.CharField(max_length=100, unique=True, null=False)
    expiration_date = models.DateField(default=None, null=True, blank=True)   
    is_available = models.BooleanField(default=True)
    class Meta(object):
        app_label = "voucher_code"
    def __unicode__(self):
        return self.voucher

class VoucherPurchase(models.Model):
    voucher = models.ForeignKey(VoucherCode)
    given_to = models.CharField(max_length=100, unique=False, null=False)
    product_title = models.CharField(max_length=500, unique=False)
    class Meta(object):
        app_label = "voucher_code"
    def __unicode__(self):
        return str(self.voucher)

