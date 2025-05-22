from django.test import TestCase, override_settings


class CorsMiddlewareTestCase(TestCase):
    @override_settings(DEBUG=True)
    def test_allow_origin_in_debug(self):
        """Allow origin is activated in Debug mode"""
        response = self.client.get("/")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_dont_allow_origin_not_in_debug(self):
        """Allow origin is not activated in standard mode"""
        response = self.client.get("/")
        self.assertNotIn("Access-Control-Allow-Origin", response)
