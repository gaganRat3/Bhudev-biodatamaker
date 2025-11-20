from django.db import models



class Biodata(models.Model):
    title = models.CharField(max_length=255, blank=True)
    data = models.JSONField(default=dict, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    payment_screenshot = models.ImageField(upload_to='payments/', null=True, blank=True)
    # New fields for workflow
    template_choice = models.CharField(max_length=100, blank=True)
    user_name = models.CharField(max_length=100, blank=True)
    user_email = models.EmailField(blank=True)
    user_phone = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    download_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Biodata {self.pk} - {self.title or self.user_name or self.created_at.isoformat()}"
