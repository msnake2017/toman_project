from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from core.models import Product, Image
from ..apis.v1 import router
from ..authentication import create_access_token, create_refresh_token
from ..exceptions import ApiValidationError

User = get_user_model()


class ApiTests(TestCase):

    def setUp(self):

        self.client = TestClient(router)
        self.user = User.objects.create_user(username="testuser", password="password")

        self.product = Product.objects.create(
            user=self.user,
            title="Test Product",
            description="Test Description",
            price=10,
        )

        self.access_token = create_access_token({'id': self.user.pk})
        self.refresh_token = create_refresh_token({'id': self.user.pk})

        self.file = SimpleUploadedFile("picture.jpeg", b"file_content", content_type="image/jpeg")

        self.image = Image.objects.create(
            object_id=self.product.id,
            content_type=ContentType.objects.get_for_model(Product),
            image=self.file
        )

    def test_get_access_token(self):
        data = {"username": "testuser", "password": "password"}
        response = self.client.post("/login/access-token/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())

        data['password'] = "wrong_password"

        try:
            self.client.post("/login/access-token/", json=data)
        except ApiValidationError as e:
            self.assertIn('Incorrect password', str(e))

    def test_get_access_token_from_refresh_token(self):
        data = {"refresh_token": self.refresh_token}
        response = self.client.post("/login/refresh-token/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())

        data = {'refresh_token': 'bad_refresh_token'}

        try:
            self.client.post("/login/refresh-token/", json=data)
        except ApiValidationError as e:
            self.assertIn("Invalid refresh token", str(e))

    def test_get_products(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.get("/products", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)

    def test_get_product(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.get(f"/products/{self.product.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.product.title)

        response = self.client.get(f"/products/0", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_product(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.delete(f"/products/{self.product.id}", headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
        self.assertEqual(Image.objects.all().count(), 0)

        response = self.client.delete(f"/products/{self.product.id}", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_create_product(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"title": "New Product", "description": "Description", "price": 10}
        response = self.client.post("/products/", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)

        data = {"title": "New Product", "description": "Description"}

        response = self.client.post("/products/", json=data, headers=headers)
        self.assertEqual(response.status_code, 422)

    def test_update_product(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"title": "Updated Product", "description": "Updated Description", "price": 10}
        response = self.client.put(f"/products/{self.product.id}/", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Updated Product")

        data.pop("description")
        response = self.client.put(f"/products/{self.product.id}/", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)

        data['price'] = 0
        try:
            self.client.put(f"/products/{self.product.id}/", json=data, headers=headers)
        except ApiValidationError as e:
            self.assertIn('Invalid price', str(e))

    def test_delete_product_image(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.delete(f"/products/{self.product.id}/images/{self.image.id}/", headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())
