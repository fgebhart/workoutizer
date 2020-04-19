from django.urls import reverse
from django.test import TestCase


class DashboardViewTests(TestCase):
    def test_view(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        print(response)
        self.assertContains(response, "asdf")
        # self.assertQuerysetEqual(response.context['latest_question_list'], [])
