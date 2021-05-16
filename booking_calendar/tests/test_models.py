from django.test import TestCase

from booking_calendar.models import WorkType

class WorkTypeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        WorkType.objects.create(name='full', comment='Need more time.')

    def test_name_label(self):
        work = WorkType.objects.get(id=1)
        field_label = work._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_comment_label(self):
        work = WorkType.objects.get(id=1)
        field_label = work._meta.get_field('comment').verbose_name
        self.assertEqual(field_label, 'comment')

    def test_name_max_length(self):
        work = WorkType.objects.get(id=1)
        max_length = work._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_comment_max_length(self):
        work = WorkType.objects.get(id=1)
        max_length = work._meta.get_field('comment').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        work = WorkType.objects.get(id=1)
        expected_object_name = f'{work.name}'
        self.assertEqual(str(work), expected_object_name)
