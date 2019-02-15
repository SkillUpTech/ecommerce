import logging

import waffle
from django.dispatch import receiver
from oscar.core.loading import get_class
from ecommerce.core.models import User

from ecommerce.courses.utils import mode_for_seat
from ecommerce.extensions.analytics.utils import silence_exceptions, track_segment_event
from ecommerce.extensions.checkout.utils import get_credit_provider_details, get_receipt_page_url
from ecommerce.notifications.notifications import send_notification
from ecommerce.voucher_code.models import VoucherCode, VoucherPurchase
from django.conf import settings

logger = logging.getLogger(__name__)
post_checkout = get_class('checkout.signals', 'post_checkout')

# Number of orders currently supported for the email notifications
ORDER_LINE_COUNT = 1


@receiver(post_checkout, dispatch_uid='tracking.post_checkout_callback')
@silence_exceptions('Failed to emit tracking event upon order completion.')
def track_completed_order(sender, order=None, **kwargs):  # pylint: disable=unused-argument
    """Emit a tracking event when an order is placed."""
    if order.total_excl_tax <= 0:
        return

    properties = {
        'orderId': order.number,
        'total': str(order.total_excl_tax),
        'currency': order.currency,
        'products': [
            {
                # For backwards-compatibility with older events the `sku` field is (ab)used to
                # store the product's `certificate_type`, while the `id` field holds the product's
                # SKU. Marketing is aware that this approach will not scale once we start selling
                # products other than courses, and will need to change in the future.
                'id': line.partner_sku,
                'sku': mode_for_seat(line.product),
                'name': line.product.course.id if line.product.course else line.product.title,
                'price': str(line.line_price_excl_tax),
                'quantity': line.quantity,
                'category': line.product.get_product_class().name,
            } for line in order.lines.all()
        ],
    }
    track_segment_event(order.site, order.user, 'Order Completed', properties)

@receiver(post_checkout, dispatch_uid='send_completed_order_email')
@silence_exceptions("Failed to send order completion email.")
def send_course_purchase_email(sender, order=None, **kwargs):  # pylint: disable=unused-argument
    """Send course purchase notification email when a course is purchased."""
    if waffle.switch_is_active('ENABLE_NOTIFICATIONS'):
        # We do not currently support email sending for orders with more than one item..
        if len(order.lines.all()) == ORDER_LINE_COUNT:
            product = order.lines.first().product
            title = product.title.replace("in Seat","").replace("(and ID verification)","")
            if product.is_seat_product:
                voucher_code = None
                voucher_expiration_date = None
                try:
                    voucher_code_obj =  VoucherCode.objects.filter(is_available=True)[:1].get()
                    voucher_code = voucher_code_obj.voucher
                    voucher_expiration_date = voucher_code_obj.expiration_date
                    voucher_code_obj.is_available = False
                    voucher_code_obj.save()
                    voucher_purchase_obj = VoucherPurchase()
                    voucher_purchase_obj.voucher = voucher_code_obj
                    voucher_purchase_obj.given_to = order.user.email
                    voucher_purchase_obj.product_title = product.title
                    voucher_purchase_obj.save()
                except:
                    logger.info('Voucher code not available') 
                receipt_page_url = get_receipt_page_url(
                    order_number=order.number,
                    site_configuration=order.site.siteconfiguration
               )

                send_notification(
                     order.user,
                     'COURSE_PURCHASED',
                     {
                            'voucher_code': voucher_code,
                            'voucher_expiration_date': voucher_expiration_date,
                            'course_title': title,
                            'receipt_page_url': receipt_page_url,
                            'support_email':settings.SUPPORT_EMAIL
                    },
                        order.site
                 )
                support_user = User.objects.get(email=settings.SUPPORT_EMAIL)
                send_notification(
                    support_user,
                    'NOTIFY_ADMIN',
                     {
                            'student': order.user.get_full_name(),
                            'course_title': title,
                            'contact_email': order.user.email
                    },
                        order.site
                )
            
        else:
            logger.info('Currently support receipt emails for order with one item.')
