"""Project middleware."""
import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


_STATIC_RE = re.compile(r"^/static/")


class NoCacheStaticMiddleware(MiddlewareMixin):
    """Send no-cache headers for any URL under STATIC_URL.

    Prevents the browser from serving a stale custom.css / tailwind.css
    after we ship a change during development.
    """

    def process_response(self, request, response):
        if _STATIC_RE.match(request.path):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response
