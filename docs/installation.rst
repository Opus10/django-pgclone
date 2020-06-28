Installation
============

Install django-pgclone with::

    pip3 install django-pgclone

After this, add ``pgclone`` to the ``INSTALLED_APPS``
setting of your Django project.

``django-pgclone`` depends on ``django-pgconnection``. Although
this dependency is automatically installed, one must add ``pgconnection``
to ``settings.INSTALLED_APPS`` and also configure the
``settings.DATABASES`` setting like so::

    import pgconnection

    DATABASES = pgconnection.configure({
        'default': # normal database config goes here...
    })
