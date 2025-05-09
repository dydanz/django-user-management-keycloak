from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.conf import settings

class SwaggerSchemaView(object):
    @staticmethod
    def get_schema_view():
        return get_schema_view(
            openapi.Info(
                title="Django User Management API",
                default_version='v1',
                description="REST API for Django User Management with Keycloak integration",
                terms_of_service="https://www.example.com/terms/",
                contact=openapi.Contact(email="contact@example.com"),
                license=openapi.License(name="MIT License"),
            ),
            public=True,
            permission_classes=(AllowAny,),
            authentication_classes=(),
        )

api_schema_view = SwaggerSchemaView.get_schema_view()