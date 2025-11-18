from rest_framework import viewsets
from .models import Biodata
from .serializers import BiodataSerializer

from django.shortcuts import render, get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import HttpResponseForbidden


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
