from datetime import datetime, timedelta
import os
from random import randint
from booking.models import Order
from booking.models import Profile
from booking.models import PriceList
from base.services import save_generated_image
from booking.models import JobType
from config import settings


class ExampleBookingData:
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    DESCRIPTION = "Duis aute irure dolor in \
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla \
pariatur."

    def create_job_type(self):
        for index in range(1, 11):
            jobtype, created = JobType.objects.get_or_create(id=index)
            if created:
                jobtype.name = f"Test job #{index}"
                jobtype.description = self.DESCRIPTION
                jobtype.time_interval = timedelta(minutes=randint(5, 25))

                name = f"job-{index}.png"
                save_generated_image(
                    os.path.join(settings.MEDIA_ROOT, name),
                    f"Lorem ipsum dolor \nsit amet, consectetur \n\
adipiscing elit, sed \ndo eiusmod tempor incididunt \nut labore\
 et dolore \nmagna aliqua.\n\nRandomly generated\n\
Image for example job #{index}",
                )
                jobtype.image = name
                jobtype.save()

    def create_price_list(self):
        for index in range(1, 11):
            pricelist = PriceList.objects.filter(id=index).first()
            if not pricelist:
                PriceList.objects.create(
                    id=index,
                    profile=Profile.objects.filter(user=2).first(),
                    job=JobType.objects.get(id=index),
                    price=randint(15, 125),
                )

    def create_order(self):
        for index in range(1, 6):
            order, created = Order.objects.get_or_create(id=index)
            if created:
                order.client = Profile.objects.filter(user=4).first()
                order.work_type.set(
                    [JobType.objects.get(id=index), JobType.objects.get(id=index + 5)]
                )
                order.client_comment = "Thank you!"
                order.master = Profile.objects.filter(user=2).first()

            order.booking_date = datetime.now() + timedelta(days=1 + index)
            order.save()

    def create_data(self):
        self.create_job_type()
        self.create_price_list()
        self.create_order()
