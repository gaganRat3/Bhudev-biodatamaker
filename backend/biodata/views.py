## Removed send_free_email_view: free PDF will not send email. Premium logic untouched.
from rest_framework import viewsets
from .models import Biodata
from .serializers import BiodataSerializer

from django.shortcuts import render, get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import HttpResponseForbidden
from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
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


def biodata_pdf_view(request, pk):
    """Generate PDF for an approved biodata.

    This view tries to use WeasyPrint to render the biodata HTML into a PDF
    and return it with Content-Disposition: attachment so the browser downloads
    it directly. If WeasyPrint isn't installed, return 501 so the frontend can
    fall back to the HTML-based flow.
    """
    biodata = get_object_or_404(Biodata, pk=pk)
    if not biodata.is_approved:
        return HttpResponseForbidden("Biodata not approved yet")


    # Determine border image path (match frontend logic)
    border_map = {
        '1': '/assets/border/White.png',
        '2': '/assets/border/bg0.png',
        '3': '/assets/border/bg3.jpg',
        '4': '/assets/border/bg8.jpg',
        '5': '/assets/border/bg9.jpg',
    }
    border_image_path = border_map.get(str(biodata.template_choice or '1'), '/assets/border/White.png')

    # Profile image path (if present)
    profile_image_path = biodata.profile_image.url if biodata.profile_image else None

    # Split fields into two columns for each section (like frontend)
    def split_dict(d):
        if not d:
            return [], []
        items = list(d.items())
        mid = (len(items) + 1) // 2
        return items[:mid], items[mid:]

    personal_left, personal_right = split_dict(biodata.data.get('PersonalDetails', {}))
    family_left, family_right = split_dict(biodata.data.get('FamilyDetails', {}))
    habits_left, habits_right = split_dict(biodata.data.get('HabitsDeclaration', {}))

    context = {
        "biodata": biodata,
        "border_image_path": border_image_path,
        "profile_image_path": profile_image_path,
        "personal_left": personal_left,
        "personal_right": personal_right,
        "family_left": family_left,
        "family_right": family_right,
        "habits_left": habits_left,
        "habits_right": habits_right,
    }
    try:
        html = render_to_string("biodata_download.html", context)
    except Exception as e:
        return HttpResponseServerError(f"Error rendering template: {e}")

    try:
        # Import WeasyPrint lazily; if not installed we signal backend doesn't support PDF
        from weasyprint import HTML

        pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="biodata_{biodata.pk}.pdf"'
        return response
    except ImportError:
        return HttpResponse("PDF generation not available on server.", status=501)
    except Exception as e:
        return HttpResponseServerError(f"PDF generation failed: {e}")


def biodata_html_view(request, pk):
    """Render the biodata download HTML page (no token). This is a friendly
    fallback that the frontend opens when server-side PDF generation isn't
    available. It behaves like the tokenized view but doesn't require a token.
    """
    biodata = get_object_or_404(Biodata, pk=pk)
    if not biodata.is_approved:
        return HttpResponseForbidden("Biodata not approved yet")
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
