import csv
from datetime import datetime
from django.core.management import BaseCommand
from ecommerce.voucher_code.models import VoucherCode

class Command(BaseCommand):
    help = 'Load a voucher code csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                is_avail = False
                temp_date = datetime.strptime(row['Expires'], "%d-%m-%Y %H:%M").date()
                if row['Status'] == "Available":
                    is_avail = True
                voucher_code = VoucherCode.objects.create(
                    voucher=row['Voucher Code'], 
                    expiration_date=temp_date,
                    is_available=is_avail
                )
