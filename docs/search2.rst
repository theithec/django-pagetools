.. _search:

======
Search
======

A simple database search.

Set ``pagetools.search.search_mods`` somewhere like this::

        search_mods = (
            ( app.models.Model1,   ('title', 'content') ),
            ( app.models.Model2, ('title', 'content','footer') ),
        )

to define which fields from which models should be searchable.

The :class:`pagetools.search.views.SearchResultView` exects one more
of the following GET paramters:

- contains_any=comma,speparated,list,of,words
- contains_all= ..
- contains_not= ..

