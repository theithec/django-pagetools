.. _app_integration:

App integration
===============

Here is how the Polls app (the one from the Django tutorial)
works together with Django-pagetools in the demo.

The only changes i made to the version from the end of the tutorial was wrapping the templates in::

        {% extends base.html %}

        {% block main %}

        old content

        {% endblock main %}



The demo contains a `main` app where the integration is done, mostly in the app config:

.. literalinclude:: ../demo/main/apps.py

There is also a templatetag for the latest question in`main`:

.. literalinclude:: ../demo/main/templatetags.py

and it gets registered in the `settings`::

    PT_TEMPLATETAG_WIDGETS = {
        'latest_question': 'main.templatetags.LatestQuestionNode',
        # ...
    }


Now a ``TemplatetagWidget`` with the name 'latest_questions' can be created
and added to a ``PagetypeArea``.

Integration so far: a single question can be added to the menu; there is an entry with all children as subentries,
a widget that shows the latest question and questions are searchable.

There is still one problem:
All question detail pages would have no highlighting for the corresponding menu entry (the ``class="active"`` is missing
on the list item).

The menu tag expects a parameter ``menukey`` - a string that indicates which entry is active.
For pagetools's models this is done in the ``pagetools.menus.views.SelectedMenuentriesMixin``,
so a subclass of ´´polls.views.DetailView´´ that inherits the mixin would solve this.

Another way is to overwrite the templates for the questions detail and index view.

detail.html::

        {% load menus_tags %}

        {% block menu %}
        {% with question|slugify as menukey %}
        {% menu "MainMenu" menukey %}
        {% endwith %}
        {% endblock menu %}



index.html::

        {% load menus_tags %}

        {% block menu %}
        {% menu "MainMenu" "pollsindex" %}
        {% endblock menu %}



Note: "pollsindex" is the slugified version of "polls:index", see above.
