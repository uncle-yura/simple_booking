from django.test import TestCase

from booking.models import JobType,PriceList,Profile,Order,User

from decimal import Decimal

import datetime


class JobTypeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        JobType.objects.create(
            name='full', 
            description='Need more time.', 
            time_interval=datetime.timedelta(minutes=15))

    def test_name_label(self):
        work = JobType.objects.get(id=1)
        field_label = work._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_description_label(self):
        work = JobType.objects.get(id=1)
        field_label = work._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_time_interval_label(self):
        work = JobType.objects.get(id=1)
        field_label = work._meta.get_field('time_interval').verbose_name
        self.assertEqual(field_label, 'time interval')

    def test_name_max_length(self):
        work = JobType.objects.get(id=1)
        max_length = work._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_description_max_length(self):
        work = JobType.objects.get(id=1)
        max_length = work._meta.get_field('description').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        work = JobType.objects.get(id=1)
        expected_object_name = f'{work.name}'
        self.assertEqual(str(work), expected_object_name)


class PriceListModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user=User.objects.create(username='testuser', password='12345')
        job = JobType.objects.create(name='full', description='Need more time.' , time_interval=datetime.timedelta(minutes=15))
        PriceList.objects.create(
            profile=user.profile, 
            job=job, 
            price=15.24)

    def test_object_name_is_name(self):
        price = PriceList.objects.get(id=1)
        expected_object_name = f'{price}'
        self.assertEqual(str(price), expected_object_name)

    def test_price_decimal(self):
        pricelist = PriceList.objects.get(id=1)
        self.assertEqual(pricelist.price, Decimal('15.24'))

    def test_price_label(self):
        work = PriceList.objects.get(id=1)
        field_label = work._meta.get_field('price').verbose_name
        self.assertEqual(field_label, 'price')


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user=User.objects.create(username='testuser', password='12345')
        user.profile.phone_number="+380123456789"
        user.profile.comment = "Test comment"
        user.profile.discount = 0.5
        user.profile.gcal_key = "123456789012345678901234567890123456789012345678901234"
        user.profile.gcal_link = "123456789012345678901234567890123456789012"
        user.profile.timetable = Profile.TIME_TABLE.ALL
        user.save()


    def test_phone_number_label(self):
        profile = Profile.objects.get(id=1)
        field_label = profile._meta.get_field('phone_number').verbose_name
        self.assertEqual(field_label, 'phone number')

    def test_phone_number_max_length(self):
        profile = Profile.objects.get(id=1)
        max_length = profile._meta.get_field('phone_number').max_length
        self.assertEqual(max_length, 17)

    def test_gcal_link_label(self):
        profile = Profile.objects.get(id=1)
        field_label = profile._meta.get_field('gcal_link').verbose_name
        self.assertEqual(field_label, 'gcal link')

    def test_gcal_link_max_length(self):
        profile = Profile.objects.get(id=1)
        max_length = profile._meta.get_field('gcal_link').max_length
        self.assertEqual(max_length, 42)

    def test_gcal_key_label(self):
        profile = Profile.objects.get(id=1)
        field_label = profile._meta.get_field('gcal_key').verbose_name
        self.assertEqual(field_label, 'gcal key')

    def test_gcal_key_max_length(self):
        profile = Profile.objects.get(id=1)
        max_length = profile._meta.get_field('gcal_key').max_length
        self.assertEqual(max_length, 54)

    def test_object_name_is_name(self):
        profile = Profile.objects.get(id=1)
        expected_object_name = f'{profile}'
        self.assertEqual(str(profile), expected_object_name)

    def test_discount_label(self):
        profile = Profile.objects.get(id=1)
        field_label = profile._meta.get_field('discount').verbose_name
        self.assertEqual(field_label, 'discount')

    def test_discount_decimal(self):
        profile = Profile.objects.get(id=1)
        self.assertEqual(profile.discount, Decimal('0.5'))


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user1=User.objects.create(username='testuser1', password='12345')
        user2=User.objects.create(username='testuser2', password='12345')
        job = JobType.objects.create(name='full', description='Need more time.' , time_interval=datetime.timedelta(minutes=15))
        Order.objects.create(
            client=user1.profile,
            master=user2.profile,
            booking_date="2021-03-12",
            client_comment="Test comment",
            state=Order.STATE_TABLE.CANCELED)
        Order.objects.get(id=1).work_type.set((job,))


    def test_object_name_is_name(self):
        order = Order.objects.get(id=1)
        expected_object_name = f'{order}'
        self.assertEqual(str(order), expected_object_name)

    def test_client_comment_label(self):
        work = Order.objects.get(id=1)
        field_label = work._meta.get_field('client_comment').verbose_name
        self.assertEqual(field_label, 'client comment')

    def test_client_comment_max_length(self):
        work = Order.objects.get(id=1)
        max_length = work._meta.get_field('client_comment').max_length
        self.assertEqual(max_length, 200)
