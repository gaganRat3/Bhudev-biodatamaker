from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BiodataViewSet
from .views import biodata_download_view, payment_verify_view, biodata_pdf_download_view

router = DefaultRouter()
router.register(r'biodata', BiodataViewSet, basename='biodata')

urlpatterns = [
    path('', include(router.urls)),
    path('download/<int:pk>/<str:token>/', biodata_download_view, name='biodata-download'),
    path('biodata/<int:pk>/download/', biodata_pdf_download_view, name='biodata-pdf-download'),
    path('payment/verify/', payment_verify_view, name='payment-verify'),
]
