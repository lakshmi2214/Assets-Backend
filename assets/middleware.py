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

from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY, BACKEND_SESSION_KEY


class PersistAdminSessionMiddleware:
    """
    Refreshes the auth hash stored in the session on every request.
    This prevents Django Admin from logging out users on Vercel serverless
    deployments where the database is reset between cold starts.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only run on admin paths
        if request.path.startswith('/admin/') and hasattr(request, 'user') and request.user.is_authenticated:
            # Refresh the session auth hash so it always matches the current DB state
            try:
                current_hash = request.user.get_session_auth_hash()
                if request.session.get(HASH_SESSION_KEY) != current_hash:
                    request.session[HASH_SESSION_KEY] = current_hash
                    request.session.modified = True
            except Exception:
                pass  # Never break the request over this

        response = self.get_response(request)
        return response
