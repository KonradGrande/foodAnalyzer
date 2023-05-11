from django.test import TestCase
from django.contrib.auth.models import User
from .ranker import Ranker


class TestRanker(TestCase):
    fixtures = ["testdata.json"]

    def setUp(self):
        self.user = User.objects.get(username="testuser")

    def test_ranking(self):
        results = Ranker(self.user).get_ranking()

        for result in results:
            print(result.name, result.reactivity)

        self.assertEqual(results[0].name, "lactose")
        self.assertEqual(results[0].reactivity, 4)
        self.assertEqual(results[1].name, "gluten")
        self.assertEqual(results[1].reactivity, 3)
        self.assertEqual(results[2].name, "water")
        self.assertEqual(results[2].reactivity, 3)
        self.assertEqual(results[3].name, "salt")
        self.assertEqual(results[3].reactivity, 3)
        self.assertEqual(results[4].name, "olive oil")
        self.assertEqual(results[4].reactivity, 3)
        self.assertEqual(results[5].name, "egg")
        self.assertEqual(results[5].reactivity, 3)
        self.assertEqual(results[6].name, "oatmeal")
        self.assertEqual(results[6].reactivity, 2)
        self.assertEqual(results[7].name, "salmon")
        self.assertEqual(results[7].reactivity, 1)
