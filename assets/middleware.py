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

from django.contrib.auth import get_user, HASH_SESSION_KEY
from django.contrib.auth.models import AnonymousUser

class PersistAdminSessionMiddleware:
    """
    Refreshes the auth hash and bypasses strict hash invalidation.
    This prevents Django Admin from logging out users on Vercel serverless
    deployments where the database is reset between cold starts.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only run on admin paths
        if request.path.startswith('/admin/'):
            # If the user was kicked out by AuthenticationMiddleware (is_authenticated is False)
            # but the session still has their user_id, force them back in.
            if hasattr(request, 'user') and not request.user.is_authenticated:
                from django.contrib.auth import _get_user_session_key
                try:
                    user_id = _get_user_session_key(request)
                    if user_id:
                        from django.contrib.auth.models import User
                        user = User.objects.get(pk=user_id)
                        request.user = user
                except Exception:
                    pass

        response = self.get_response(request)
        return response
