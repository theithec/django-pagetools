import json
import operator
import os
from functools import reduce
from typing import Any, Dict, List

from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.html import strip_tags

from pagetools.search import extra_filter, search_mods
from pagetools.views import PaginatorMixin

from . import settings
from .forms import AdvSearchForm


class SearchResultsView(PaginatorMixin):
    template_name = "search/search_results.html"
    context_object_name = "results"
    search_params: Dict[str, Any] = {}
    _search_mods: List = search_mods[:]
    form_cls = AdvSearchForm
    form = None
    _thisdir = os.path.dirname(os.path.realpath(__file__))
    if settings.SEARCH_REPLACEMENTS:
        with open(os.path.join(_thisdir, settings.SEARCH_REPLACEMENTS_FILE), encoding="utf8") as fobj:
            replacements = json.load(fobj)

    def get(self, request, *args, **kwargs):
        self.form = self.form_cls(request.GET)
        if self.form.is_valid():
            cleaned_data = self.form.cleaned_data
            self.search_params = cleaned_data

            model_pks = cleaned_data.get("models")
            if model_pks:
                int_pks = [int(s) for s in model_pks]
                self._search_mods = [search_mods[i] for i in int_pks]
        return super().get(request)

    def filtered_queryset(self, mod):
        cls = mod[0]
        fields = mod[1]
        qs = extra_filter(cls.objects.all())
        cnots = self.search_params.get("contains_not", "").split()
        if cnots:
            notlist = [
                Q(**{"%s__icontains" % field: self._convert(cnot, field, mod)}) for cnot in cnots for field in fields
            ]
            combined_notlist = reduce(operator.or_, notlist)
            qs = qs.exclude(combined_notlist)
        return qs

    def _convert(self, term, field, mod):
        if not settings.SEARCH_REPLACEMENTS:
            return term

        replace = mod[2].get("replacements", {}) if len(mod) > 2 else {}
        if field in replace:
            for key, val in self.replacements.items():
                term = term.replace(key, val)

        return term

    def result_(self, sterms, combine_op):
        result = set()
        if not sterms:
            return result
        for mod in self._search_mods:
            fields = mod[1]
            queryset = self.filtered_queryset(mod)
            qlists = []
            for sterm in sterms:
                if len(sterm) < 3:
                    continue
                qlist = reduce(
                    operator.or_,
                    [Q(**{"%s__icontains" % field: self._convert(sterm, field, mod)}) for field in fields],
                )
                qlists.append(qlist)

            if qlists:
                combined_qlist = reduce(combine_op, qlists)
                queryset2 = queryset.filter(combined_qlist)
                result |= set(queryset2)
        return result

    def _stripped(self, txt):
        txt = strip_tags(str(txt)).lower()
        return txt

    def get_queryset(self, **_kwargs):
        if not self.search_params:
            return tuple()

        results = []
        exact = self.search_params.get("contains_exact")
        terms_all = self.search_params.get("contains_all", "").split()
        if len(terms_all) > 1 and not exact:
            exact = " ".join(terms_all)
        results_exact = []
        if exact:
            exact = exact.lower()
            for mod in self._search_mods:
                fields = mod[1]
                queryset = self.filtered_queryset(mod)
                for field in fields:
                    cfield = self._convert(exact, field, mod)
                    exact_results = [r for r in queryset if cfield in self._stripped(getattr(r, field))]
                    results_exact.extend([res for res in exact_results if res not in results_exact])
        results.append(results_exact)
        if terms_all:
            results.append(self.result_(terms_all, operator.and_))
        terms_any = self.search_params.get("contains_any", "").split()
        if terms_any:
            results.append(self.result_(terms_any, operator.or_))
        results = list(filter(None, results))
        if not results:
            return tuple()
        reduced = []
        for res in results:
            reduced.extend([obj for obj in res if obj not in reduced])
        return list(reduced)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_url"] = reverse("search")
        context["form"] = self.form
        return context


search = SearchResultsView.as_view()
