#!/bin/bash
# Quick Test Guide for Biodata Fixes

echo "========================================="
echo "Testing Biodata System Fixes"
echo "========================================="
echo ""

# Check if backend is running
echo "[STEP 1] Verify Backend is Running"
curl -s http://127.0.0.1:8000/api/biodata/ -H "Authorization: Token your_token" | head -20
echo ""
echo "If you see JSON output above, backend is running ✓"
echo ""

echo "[STEP 2] Test Duplicate Record Prevention"
echo "Follow these manual steps:"
echo "1. Open http://127.0.0.1:8000 (or your frontend URL)"
echo "2. Fill the biodata form with:"
echo "   - Name: Test User"
echo "   - Birth Date: 1990-01-01"
echo "   - Profile Image: Upload any image"
echo "3. Submit form"
echo "4. Check Django admin: Should see 1 record"
echo "5. Go to upgrade/payment page"
echo "6. Submit payment with transaction ID"
echo "7. Check Django admin: Should STILL see 1 record (UPDATED, not new)"
echo ""

echo "[STEP 3] Verify Image in Email PDF"
echo "Watch backend terminal for these logs:"
echo "  [BUILD_HTML] Biodata id X: profile_image=profiles/..."
echo "  [BUILD_HTML] media_path=... exists=True"
echo "  [BUILD_HTML] Profile image embedded successfully"
echo ""
echo "If exists=False, check if file is in backend/media/profiles/"
echo ""

echo "[STEP 4] Check Files Modified"
echo "Key changes made:"
echo "  ✓ js/biodata-form.js - PATCH logic added"
echo "  ✓ js/api.js - patchBiodata method added"
echo "  ✓ backend/biodata/views.py - payment verification now requires biodata_id"
echo "  ✓ backend/biodata/serializers.py - debug logging added"
echo "  ✓ backend/biodata/admin.py - image embedding debug logging added"
echo ""

echo "[STEP 5] Monitor Logs While Testing"
echo "Terminal commands:"
echo "  $ cd backend"
echo "  $ python manage.py runserver"
echo "Then watch console output for [BUILD_HTML], [CREATE], [TO_INTERNAL_VALUE] messages"
echo ""

echo "========================================="
echo "Testing complete!"
echo "========================================="
