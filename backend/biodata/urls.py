from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BiodataViewSet
from .views import biodata_download_view, biodata_html_view, biodata_pdf_view, payment_verify_view, upload_pdf_and_send_email

router = DefaultRouter()
router.register(r'biodata', BiodataViewSet, basename='biodata')

urlpatterns = [
    path('', include(router.urls)),
    path('download/<int:pk>/<str:token>/', biodata_download_view, name='biodata-download'),
    path('download/<int:pk>/', biodata_html_view, name='biodata-html-download'),
    # Direct PDF generation endpoint (used by frontend to download .pdf)
    path('biodata/<int:pk>/download/', biodata_pdf_view, name='biodata-pdf-download'),
    path('payment/verify/', payment_verify_view, name='payment-verify'),
    path('upload_pdf_and_send_email/', upload_pdf_and_send_email, name='upload-pdf-and-send-email'),
    # Removed free email endpoint: free PDF will not send email
]
