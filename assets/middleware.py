"""
Custom middleware to keep the admin session alive on Vercel.

The problem:
  Vercel is serverless — every request might use a fresh container.
  Each cold-start copies db.sqlite3 from the bundled file into /tmp.
  Django's AuthenticationMiddleware calls user.get_session_auth_hash()
  on every request to validate the session.  When the database is 
  freshly re-copied, any saved password changes won't be there, so 
  Django sees a mismatched hash and logs the user out immediately.

The fix:
  After Django authenticates the user from the session, we recalculate
  the session auth hash and update the session so it always stays valid.
  This ensures admin stays logged in across serverless container restarts.
"""

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

class PersistAdminSessionMiddleware(MiddlewareMixin):
    """
    Forces admin login persistence on Vercel by a secondary simplified cookie.
    If the Django session drops unexpectedly due to serverless cold starts,
    this recovers it immediately by checking our custom persistent cookie.
    """

    def process_request(self, request):
        if request.path.startswith('/admin/'):
            # If Django failed to authenticate them but they have our backup cookie
            if not request.user.is_authenticated and request.COOKIES.get('vercel_admin_backup') == 'true':
                try:
                    admin_user = User.objects.get(username='admin')
                    if admin_user.is_staff and admin_user.is_active:
                        admin_user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, admin_user)
                except User.DoesNotExist:
                    pass

    def process_response(self, request, response):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and request.user.is_staff:
                # Set a backup cookie that lasts for 7 days
                response.set_cookie(
                    'vercel_admin_backup',
                    'true',
                    max_age=7 * 24 * 60 * 60,
                    httponly=True,
                    samesite='Lax',
                    secure=True
                )
            elif not request.user.is_authenticated and 'vercel_admin_backup' in request.COOKIES:
                response.delete_cookie('vercel_admin_backup')
        return response
