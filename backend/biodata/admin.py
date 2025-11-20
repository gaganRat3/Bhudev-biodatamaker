from django.contrib import admin, messages
import logging
import logging
from .models import Biodata


from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html

@admin.register(Biodata)
class BiodataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'user_name', 'user_email', 'template_choice', 'is_approved', 'created_at', 'payment_screenshot_thumb'
    )
    readonly_fields = ('created_at', 'updated_at', 'payment_screenshot_preview')
    exclude = ('download_link',)
    list_filter = ('is_approved', 'template_choice')
    search_fields = ('title', 'user_name', 'user_email', 'user_phone')

    actions = ['approve_biodata', 'export_to_excel']

    def payment_screenshot_thumb(self, obj):
        # Robust thumbnail for list view. Try storage URL first, fall back to MEDIA_URL + name.
        if obj.payment_screenshot:
            try:
                url = obj.payment_screenshot.url
            except Exception:
                # Some storage backends may not provide .url; build from MEDIA_URL
                from django.conf import settings
                name = getattr(obj.payment_screenshot, 'name', '')
                url = f"{getattr(settings, 'MEDIA_URL', '/media/')}{name.lstrip('/')}" if name else None

            if url:
                return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height:40px;max-width:60px;"/></a>', url, url)
        return "-"
    payment_screenshot_thumb.short_description = 'Payment Screenshot'

    def export_to_excel(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="biodata_export.csv"'
        writer = csv.writer(response)
        fields = ['id', 'title', 'user_name', 'user_email', 'template_choice', 'is_approved', 'created_at', 'payment_screenshot']
        writer.writerow(fields)
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.title,
                obj.user_name,
                obj.user_email,
                obj.template_choice,
                obj.is_approved,
                obj.created_at,
                (getattr(obj.payment_screenshot, 'url', '') if getattr(obj, 'payment_screenshot', None) else '')
            ])
        return response
    export_to_excel.short_description = "Export selected to Excel (CSV)"
    # Set up file logger
    logger = logging.getLogger("biodata_admin")
    file_handler = logging.FileHandler("biodata_admin.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    def approve_biodata(self, request, queryset):
        sent_count = 0
        for obj in queryset:
            # Always run the workflow, even if already approved, for debugging
            obj.is_approved = True
            from django.core.signing import TimestampSigner
            from django.urls import reverse
            signer = TimestampSigner()
            token = signer.sign(str(obj.pk))
            download_path = reverse('biodata-download', args=[obj.pk, token])
            obj.download_link = request.build_absolute_uri(download_path)
            obj.save()
            logging.info(f"[ADMIN ACTION] Attempting to send approval email to: {obj.user_email!r} for biodata id {obj.pk}")
            self.message_user(request, f"[DEBUG] Attempting to send approval email to: {obj.user_email!r} for biodata id {obj.pk}")
            if obj.user_email:
                from django.core.mail import EmailMessage
                debug_mode = request.GET.get('debug_email', None)
                try:
                    if debug_mode == 'plain':
                        # Send a plain text email only
                        self.logger.info("approve_biodata action started (plain email)")
                        print("[DEBUG] approve_biodata action started (plain email)")
                        email = EmailMessage(
                            subject="Debug: Plain Email Test",
                            body=f"This is a plain text test email for biodata id {obj.pk}.",
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com'),
                            to=[obj.user_email]
                        )
                        email.send(fail_silently=False)
                        self.message_user(request, f"[DEBUG] Plain email sent to {obj.user_email}")
                        self.logger.info(f"Plain email sent to {obj.user_email}")
                        print(f"[DEBUG] Plain email sent to {obj.user_email}")
                    else:
                        # Generate PDF directly from frontend-style HTML (NO templates needed!)
                        self.logger.info("approve_biodata action started (Frontend PDF generation)")
                        print("[DEBUG] approve_biodata action started (Frontend PDF generation)")
                        from io import BytesIO
                        from django.conf import settings
                        import os
                        
                        # Generate complete frontend-style HTML
                        html_content = self.build_frontend_html(obj)
                        
                        # Convert to PDF using Playwright (perfect browser rendering)
                        pdf_buffer = self.html_to_pdf_playwright(html_content)
                        
                        # Send email with PDF
                        email = EmailMessage(
                            subject="Your Biodata PDF is Attached!",
                            body=f"Dear {obj.user_name},\n\nYour biodata PDF is attached as requested.",
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com'),
                            to=[obj.user_email]
                        )
                        email.attach(f"biodata_{obj.pk}.pdf", pdf_buffer.read(), 'application/pdf')
                        email.send(fail_silently=False)
                        sent_count += 1
                        self.logger.info(f"Approval email with PDF sent to {obj.user_email}")
                        print(f"[DEBUG] Approval email with PDF sent to {obj.user_email}")
                        self.message_user(request, f"[DEBUG] Approval email with PDF sent to {obj.user_email}")
                except Exception as e:
                    self.message_user(request, f"[ERROR] Exception during email send: {e}", level=messages.ERROR)
                    logging.exception(f"[ADMIN ACTION] Exception during email send for biodata id {obj.pk}")
            else:
                self.message_user(request, f"[DEBUG] No user_email set for biodata id {obj.pk}", level=messages.WARNING)
        self.message_user(request, f"Approved {queryset.count()} biodata entries. Emails sent: {sent_count}")
    approve_biodata.short_description = "Approve selected biodata and send email"

    def build_frontend_html(self, obj):
        """Build complete frontend-style HTML matching JS template-page.js logic"""
        import os, base64, mimetypes
        from django.conf import settings
        
        # Map template_choice to border image
        border_images = {
            "1": "White.png",
            "2": "bg0.png",
            "3": "bg6.png",
            "4": "bg8.jpg",
            "5": "bg9.jpg",
            "6": "bg10.jpg",
        }
        border_image = border_images.get(str(obj.template_choice), "White.png")
        border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', border_image)
        
        # Embed border image as base64
        border_data_uri = ""
        try:
            if os.path.exists(border_path):
                with open(border_path, 'rb') as bf:
                    b = bf.read()
                mime, _ = mimetypes.guess_type(border_path)
                if not mime:
                    mime = 'image/jpeg'
                b64 = base64.b64encode(b).decode('ascii')
                border_data_uri = f"data:{mime};base64,{b64}"
        except Exception as e:
            print(f"[DEBUG] Could not load border image: {e}")
        
        # Embed profile image as base64
        profile_image_data_uri = ""
        try:
            if getattr(obj, 'profile_image', None) and getattr(obj.profile_image, 'name', None):
                media_path = os.path.join(settings.MEDIA_ROOT, obj.profile_image.name)
                if os.path.exists(media_path):
                    with open(media_path, 'rb') as img_file:
                        img_data = img_file.read()
                    mime_type, _ = mimetypes.guess_type(media_path)
                    if not mime_type:
                        mime_type = 'image/jpeg'
                    img_b64 = base64.b64encode(img_data).decode('ascii')
                    profile_image_data_uri = f"data:{mime_type};base64,{img_b64}"
        except Exception as e:
            print(f"[DEBUG] Could not load profile image: {e}")

        # Get biodata data
        personal_details = obj.data.get('PersonalDetails', {}) if getattr(obj, 'data', None) else {}
        family_details = obj.data.get('FamilyDetails', {}) if getattr(obj, 'data', None) else {}
        habits_details = obj.data.get('HabitsDeclaration', {}) if getattr(obj, 'data', None) else {}
        
        # Route to specific template builder
        if str(obj.template_choice) == "5":
            # Template 5 has special right-side layout
            return self.generate_template5_html(
                obj, border_data_uri, profile_image_data_uri,
                personal_details, family_details, habits_details
            )
        else:
            # Templates 1-4, 6 use centered layout
            return self.generate_standard_template_html(
                obj, border_data_uri, profile_image_data_uri,
                personal_details, family_details, habits_details
            )

    def generate_standard_template_html(self, obj, border_image_base64, profile_image_base64, personal, family, habits):
        """Generate frontend-matching HTML for Templates 1-4, 6 (centered profile photo at top)"""
        
        # Profile image HTML (centered, circular)
        profile_html = ""
        if profile_image_base64:
            profile_html = f'<img src="{profile_image_base64}" class="biodata-profile-image" alt="Profile" />'
        
        # Format sections - Split items into left/right columns
        def format_section_items(details_dict):
            items = [(k, v) for k, v in (details_dict or {}).items() if v and str(v).strip()]
            left_html = ""
            right_html = ""
            for i, (key, value) in enumerate(items):
                key_title = key.replace('_', ' ').title()
                item = f'''<div class="detail-item">
                    <span class="detail-label">{key_title}</span>
                    <span class="detail-value">{value}</span>
                </div>'''
                if i % 2 == 0:
                    left_html += item
                else:
                    right_html += item
            return f'<div class="detail-column-left">{left_html}</div><div class="detail-column-right">{right_html}</div>'
        
        personal_html = format_section_items(personal)
        family_html = format_section_items(family)
        habits_html = format_section_items(habits)
        
        # Get name from PersonalDetails instead of user_name
        display_name = personal.get('name', '') or personal.get('Name', '') or obj.user_name or ''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Biodata - {obj.user_name}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 5mm;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: "Times New Roman", serif;
            background: white;
            margin: 0;
            padding: 0;
        }}
        #template-content {{
            width: 100%;
            min-height: 287mm;
            background: white;
            box-sizing: border-box;
            margin: 0;
            position: relative;
            padding: 60px 80px;
            background-image: url("{border_image_base64}");
            background-size: 100% 100%;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .biodata-template {{
            max-width: 100%;
            margin: 0;
            background: transparent;
            padding: 20px 0 0 0;
            position: relative;
            z-index: 1;
            color: #2c3e50;
        }}
        .biodata-profile-image {{
            width: 110px;
            height: 110px;
            border-radius: 50%;
            object-fit: cover;
            margin: 20px auto 10px;
            display: block;
            border: 3px solid #8b4513;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .biodata-name {{
            text-align: center;
            font-size: 1.25rem;
            font-weight: bold;
            color: #2c3e50;
            margin: 0 0 20px 0;
            letter-spacing: 1px;
        }}
        .section-pill {{
            background: linear-gradient(135deg, #e67e22, #d35400);
            color: white;
            padding: 7px 18px;
            border-radius: 20px;
            font-weight: 600;
            margin: 0 auto 14px;
            display: block;
            width: fit-content;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(230, 126, 34, 0.4);
        }}
        .biodata-section {{
            margin-bottom: 18px;
        }}
        .detail-columns {{
            width: 100%;
            margin-top: 8px;
            padding: 0;
            position: relative;
            overflow: hidden;
        }}
        .detail-columns::before {{
            content: '';
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 1px;
            background-color: #bdc3c7;
            margin-left: -0.5px;
        }}
        .detail-column-left {{
            width: 48%;
            float: left;
            padding-right: 11px;
        }}
        .detail-column-right {{
            width: 48%;
            float: right;
            padding-left: 11px;
        }}
        .detail-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 2px 0;
            margin-bottom: 2px;
        }}
        .detail-label {{
            color: #2c3e50;
            font-weight: 600;
            font-size: 0.85rem;
            width: 48%;
            line-height: 1.4;
        }}
        .detail-value {{
            color: #34495e;
            font-size: 0.85rem;
            width: 48%;
            text-align: right;
            font-weight: 500;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div id="template-content">
        <div class="biodata-template">
            {profile_html}
            
            {f'<div class="biodata-name">{display_name}</div>' if display_name else ''}
            
            {f'<div class="biodata-section"><div class="section-pill">PERSONAL DETAILS</div><div class="detail-columns">{personal_html}</div></div>' if personal else ''}
            {f'<div class="biodata-section"><div class="section-pill">FAMILY DETAILS</div><div class="detail-columns">{family_html}</div></div>' if family else ''}
            {f'<div class="biodata-section"><div class="section-pill">HABITS & DECLARATION</div><div class="detail-columns">{habits_html}</div></div>' if habits else ''}
        </div>
    </div>
</body>
</html>'''
        return html

    def generate_template5_html(self, obj, border_image_base64, profile_image_base64, personal, family, habits):
        """Generate frontend-matching HTML for Template 5 (matches frontend: red border, blue section headers, Om symbol, BIO DATA, right-side profile photo, two-column layout)"""
        display_name = personal.get('name', '') or personal.get('Name', '') or obj.user_name or ''
        # Profile image HTML (right-side, rectangular)
        if profile_image_base64:
            profile_html = f'<img src="{profile_image_base64}" style="width:150px;height:180px;object-fit:cover;border:2px solid #000;margin-bottom:20px;display:block;" alt="Profile" />'
        else:
            profile_html = '<div style="width:150px;height:180px;background:#f0f0f0;border:2px solid #000;display:flex;align-items:center;justify-content:center;color:#666;font-size:12px;text-align:center;margin-bottom:20px;">Profile<br>Photo</div>'
        def format_section_items(details_dict):
            items = [(k, v) for k, v in (details_dict or {}).items() if v and str(v).strip()]
            left_html = ""
            right_html = ""
            for i, (key, value) in enumerate(items):
                key_title = key.replace('_', ' ').title()
                item = f'''<div style="margin-bottom:8px;font-size:12px;line-height:1.4;">
                    <div style="color:#4169e1;margin-bottom:2px;font-weight:bold;">{key_title}</div>
                    <div style="color:#000;">{value}</div>
                </div>'''
                if i % 2 == 0:
                    left_html += item
                else:
                    right_html += item
            return left_html, right_html
        personal_left, personal_right = format_section_items(personal)
        family_left, family_right = format_section_items(family)
        habits_left, habits_right = format_section_items(habits)
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Biodata - {display_name}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 5mm;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background: white;
        }}
        #template-content {{
            width: 700px;
            margin: 20px auto;
            border: 8px solid #dc143c;
            padding: 0;
            background: #fff;
            min-height: 800px;
            position: relative;
            box-sizing: border-box;
        }}
        .biodata-header {{
            text-align: center;
            margin-bottom: 15px;
            padding-top: 30px;
        }}
        .biodata-logo {{
            font-size: 24px;
            color: #dc143c;
            font-weight: bold;
        }}
        .biodata-title {{
            font-size: 18px;
            color: #dc143c;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .main-content {{
            width: 100%;
            display: flex;
            box-sizing: border-box;
            padding: 40px 20px 30px 20px;
        }}
        .content-left {{
            flex: 1;
            padding: 0 10px;
        }}
        .content-right {{
            width: 200px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .section-title {{
            background: #4169e1;
            color: #fff;
            padding: 8px 15px;
            font-weight: bold;
            font-size: 14px;
            margin: 20px 0 10px 0;
            width: fit-content;
            text-transform: uppercase;
        }}
        .section-title:first-of-type {{
            margin-top: 0;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div id="template-content">
        <div class="biodata-header">
            <div class="biodata-logo">🕉</div>
            <div class="biodata-title">BIO DATA</div>
        </div>
        <div class="main-content">
            <div class="content-left">
                <div class="section-title">PERSONAL DETAILS</div>
                <div class="details-grid">
                    <div>{personal_left}</div>
                    <div>{personal_right}</div>
                </div>
                <div class="section-title">FAMILY DETAILS</div>
                <div class="details-grid">
                    <div>{family_left}</div>
                    <div>{family_right}</div>
                </div>
                <div class="section-title">HABITS & DECLARATION</div>
                <div class="details-grid">
                    <div>{habits_left}</div>
                    <div>{habits_right}</div>
                </div>
            </div>
            <div class="content-right">
                {profile_html}
            </div>
        </div>
    </div>
</body>
</html>'''
        return html

    def payment_screenshot_preview(self, obj):
        """Show a larger preview in the change form (readonly)."""
        if not obj or not getattr(obj, 'payment_screenshot', None):
            return "No screenshot uploaded"
        try:
            url = obj.payment_screenshot.url
        except Exception:
            from django.conf import settings
            name = getattr(obj.payment_screenshot, 'name', '')
            url = f"{getattr(settings, 'MEDIA_URL', '/media/')}{name.lstrip('/')}" if name else None
        if not url:
            return "No screenshot available"
        return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height:220px;max-width:320px;border:1px solid #ccc;"/></a>', url, url)
    payment_screenshot_preview.short_description = 'Payment Screenshot Preview'

    def _format_detail_grid(self, details_dict):
        """Format details as grid items matching frontend"""
        items = [(k, v) for k, v in (details_dict or {}).items() if v and str(v).strip()]
        html_items = ""
        for key, value in items:
            key_title = key.replace('_', ' ').title()
            html_items += f'''<div class="detail-item">
                <span class="detail-label">{key_title}</span>
                <span class="detail-value">{value}</span>
            </div>'''
        return html_items

    def html_to_pdf_playwright(self, html_content):
        """Convert HTML to PDF using Playwright (Chrome) for perfect rendering"""
        from io import BytesIO
        import tempfile
        import os
        
        try:
            from playwright.sync_api import sync_playwright
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_path = f.name
            
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(f'file:///{temp_path}')
                    page.wait_for_timeout(1000)  # Wait for fonts/images to load
                    pdf_bytes = page.pdf(
                        format='A4',
                        print_background=True,
                        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                    )
                    browser.close()
                    return BytesIO(pdf_bytes)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except ImportError:
            raise Exception("Playwright not installed")
