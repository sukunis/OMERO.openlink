#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views


urlpatterns = [


    # index 'home page' of the openlink app
    url(r'^$', views.openlink, name='openlink_index'),

    url(r'^deleteOpenLink/?',views.delete, name='openlink-delete'),

    #show debugoutput: replace in url "webclient" by "omero_openlink/debugoutput"
    #url(r'^debugoutput/$',views.debugoutput,name='debugoutput'),


]
