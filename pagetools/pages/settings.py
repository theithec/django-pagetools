'''
Created on 15.12.2013

@author: Tim Heithecker
'''
from django.conf import settings

MAILFORM_RECEIVERS = getattr(settings,
                             'PT_MAILFORM_RECEIVERS',
                             [a[1] for a in settings.ADMINS]
                             )

MAILFORM_SENDER = getattr(settings,
                          'PT_MAILFORM_SENDER',
                          'form@localhost'
                          )
