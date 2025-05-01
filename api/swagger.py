from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Create schema view with security definitions
schema_view = get_schema_view(
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
)

# Add security definitions to schema
schema_view.schema._security_definitions = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter your token in the format: Bearer <token>'
    }
} 