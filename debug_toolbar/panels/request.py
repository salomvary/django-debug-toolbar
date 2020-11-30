from django.http import Http404
from django.urls import resolve
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel
from debug_toolbar.utils import get_sorted_request_variable, get_name_from_obj


class RequestPanel(Panel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """

    template = "debug_toolbar/panels/request.html"

    title = _("Request")

    @property
    def nav_subtitle(self):
        """
        Show abbreviated name of view function as subtitle
        """
        view_func = self.get_stats().get("view_func", "")
        return view_func.rsplit(".", 1)[-1]

    def generate_stats(self, request, response):
        self.record_stats(
            {
                "get": get_sorted_request_variable(request.GET),
                "post": get_sorted_request_variable(request.POST),
                "cookies": get_sorted_request_variable(request.COOKIES),
            }
        )

        view_info = {
            "view_func": _("<no view>"),
            "view_args": "None",
            "view_kwargs": "None",
            "view_urlname": "None",
        }
        try:
            match = resolve(request.path)
            func, args, kwargs = match
            view_info["view_func"] = get_name_from_obj(func)
            view_info["view_args"] = args
            view_info["view_kwargs"] = kwargs
            view_info["view_urlname"] = getattr(match, "url_name", _("<unavailable>"))
        except Http404:
            pass
        self.record_stats(view_info)

        if hasattr(request, "session"):
            self.record_stats(
                {
                    "session": [
                        (k, request.session.get(k))
                        for k in sorted(request.session.keys())
                    ]
                }
            )
