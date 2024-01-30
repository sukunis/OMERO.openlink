#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import re_path 
from . import views


urlpatterns = [


    # index 'home page' of the openlink app
    re_path(r'^$', views.openlink, name='openlink_index'),

    re_path(r'^deleteOpenLink/?',views.delete, name='openlink-delete'),

    #show debugoutput: replace in url "webclient" by "omero_openlink/debugoutput"
    #re_path(r'^debugoutput/$',views.debugoutput,name='debugoutput'),


]
