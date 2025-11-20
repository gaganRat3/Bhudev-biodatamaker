from rest_framework import viewsets
from .models import Biodata
from .serializers import BiodataSerializer

from django.shortcuts import render, get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import HttpResponseForbidden
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def biodata_pdf_download_view(request, pk):
    """Generate and serve a PDF for the given Biodata (free template download)."""
    from .models import Biodata
    try:
        obj = Biodata.objects.get(pk=pk)
    except Biodata.DoesNotExist:
        raise Http404("Biodata not found")

    # Only allow download for free templates (e.g., template_choice 1-4)
    if str(obj.template_choice) not in {"1", "2", "3", "4"}:
        return HttpResponseForbidden("PDF download only allowed for free templates.")

    # Generate frontend-style HTML
    html_content = BiodataAdmin.build_frontend_html(BiodataAdmin, obj)

    # Convert to PDF using Playwright
    try:
        from .admin import BiodataAdmin
        pdf_buffer = BiodataAdmin.html_to_pdf_playwright(BiodataAdmin, html_content)
    except Exception as e:
        return HttpResponse(f"PDF generation failed: {e}", status=500)

    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="biodata_{obj.pk}.pdf"'
    return response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile


class DownloadSigner(TimestampSigner):
    """Simple wrapper in case we want to centralize signer settings later."""
    pass


def biodata_download_view(request, pk, token):
    signer = DownloadSigner()
    try:
        unsigned = signer.unsign(token, max_age=60 * 60 * 24 * 7)  # 7 days
    except SignatureExpired:
        return HttpResponseForbidden("Download link expired")
    except BadSignature:
        return HttpResponseForbidden("Invalid download link")

    if str(pk) != unsigned:
        return HttpResponseForbidden("Invalid download link")

    biodata = get_object_or_404(Biodata, pk=pk)
    if not biodata.is_approved:
        return HttpResponseForbidden("Biodata not approved yet")

    # Render a simple HTML page containing the biodata without watermark and
    # that triggers the browser print dialog so the user can save a PDF.
    # The template uses the project's frontend assets (css, assets) which are
    # already exposed via STATICFILES_DIRS / Django static serving in DEBUG.
    return render(request, "biodata_download.html", {"biodata": biodata})


class BiodataViewSet(viewsets.ModelViewSet):
    queryset = Biodata.objects.all().order_by('-created_at')
    serializer_class = BiodataSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def payment_verify_view(request):
    """Accept a multipart POST with 'screenshot' file and attach it to a Biodata.

    Matching order:
    - If `biodata_id` provided in POST data, attach to that record.
    - Else if the request is authenticated, attach to the most recent Biodata
      whose `user_email` matches `request.user.email`.
    - Else attach to the most recent Biodata without a payment_screenshot.

    Returns JSON {success: true, biodata_id: <id>} on success.
    """
    screenshot = request.FILES.get('screenshot')
    biodata_id = request.data.get('biodata_id') or request.data.get('biodataId')

    if not screenshot:
        return Response({'error': 'screenshot file is required'}, status=status.HTTP_400_BAD_REQUEST)

    biodata = None
    if biodata_id:
        try:
            biodata = Biodata.objects.get(pk=int(biodata_id))
        except Exception:
            biodata = None

    if not biodata and getattr(request, 'user', None) and request.user.is_authenticated:
        try:
            biodata = Biodata.objects.filter(user_email__iexact=request.user.email).order_by('-created_at').first()
        except Exception:
            biodata = None

    if not biodata:
        # Fallback: attach to latest pending/most-recent biodata without a screenshot
        biodata = Biodata.objects.filter(payment_screenshot__isnull=True).order_by('-created_at').first()

    if not biodata:
        return Response({'error': 'Could not find a Biodata record to attach the screenshot to. Provide biodata_id or ensure you are authenticated.'}, status=status.HTTP_400_BAD_REQUEST)

    # Save uploaded file to model field
    try:
        biodata.payment_screenshot.save(screenshot.name, screenshot, save=True)
    except Exception as e:
        return Response({'error': f'Failed to save screenshot: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'success': True, 'biodata_id': biodata.pk}, status=status.HTTP_200_OK)
