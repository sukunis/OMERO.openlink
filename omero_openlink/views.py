#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat


from omeroweb.webclient.decorators import login_required, render_response

import logging
import sys
import os
import re
import datetime
import shutil
import glob
from operator import itemgetter

from . import openlink_settings

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        logger.error('No Pillow installed,\
            line plots and split channel will fail!')

OPENLINK_DIR = openlink_settings.OPENLINK_DIR.rstrip("/")
TYPE_HTTP = openlink_settings.TYPE_HTTP
SERVER_NAME = f'{TYPE_HTTP}://{openlink_settings.SERVER_NAME}'.rstrip("/")


CMD_CURL = "curl -s %s/%s/%s | curl -K-"
CONTENT_FILE = "content.json"
CURL_FILE = "batch_download.curl"
GET_SLOTNAME_PATTERN = r'^rn_[A-Z,0-9]+_\d+_(.+)'
SKIP_FILES = [CONTENT_FILE, CURL_FILE]


@login_required()
def debugoutput(request, conn=None, **kwargs):
    data = [{
        'OpenLink Dir': OPENLINK_DIR,
        'Server Name': SERVER_NAME
    }]
    # test openlink directory access
    if os.path.exists(OPENLINK_DIR):
        perm = oct(os.stat(OPENLINK_DIR).st_mode)[-3:]
        data[0]["Permission mask OPENLINK_DIR (in octal)"] = perm
    else:
        data.append("ERROR: can't access OPENLINK_DIR")

    # list openlink_dir content
    # dircontent = os.listdir(OPENLINK_DIR)
    # data.append({",".join([str(elem) for elem in dircontent])})
    try:
        user = conn.getUser()
        slotParentDir = getAreasOfUser(str(user.getId()))
        if slotParentDir is not None:
            data.append({
                "Current User ID": str(user.getId()),
                "Current User Name": user.getName()
            })

            for p in slotParentDir:
                areaName = parseAccessAreaNames(os.path.basename(p))
                data.append({
                    "SLOT user path": p,
                    "SLOT user name": areaName
                })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        data.append({'ERROR': 'while reading slot dir: ' +
                     f'{str(e)}\n {exc_type} {exc_tb.tb_lineno}'})

    return JsonResponse(data, safe=False)


def parseAccessAreaNames(p):
    try:
        name = re.search(GET_SLOTNAME_PATTERN, p).group(1)
    except AttributeError:
        name = None  # apply your error handling
        print("ERROR at scan access areas by slot name")
    return name


def getAreasOfUser(id):
    """
    Scan ACCESS_AREA directories, filter out userID from directory name
    :param id: user id in OMERO
    :return: list of directories in ACCESS_AREA that belongs to given id
    """

    if not os.path.exists(OPENLINK_DIR):
        return None
    return glob.glob(os.path.join(OPENLINK_DIR, f"rn*_{id}_*"))


def get_area_size(path):
    """Return total size of files in path and subdirs. If
    is_dir() or stat() fails, print an error message to stderr
    and assume zero size (for example, file has been deleted).
    """
    total = 0
    for entry in os.scandir(path):
        if entry not in SKIP_FILES:
            try:
                is_dir = entry.is_dir(follow_symlinks=True)
            except OSError as error:
                print('Error calling is_dir():', error)
                continue
            if is_dir:
                total += get_area_size(entry.path)
            else:
                try:
                    total += entry.stat(follow_symlinks=True).st_size
                except OSError as error:
                    print('Error calling stat():', error)

    return total


@login_required()
def openlink(request, conn=None, **kwargs):
    values = []
    debug = ""
    try:
        user = conn.getUser()
        slotParentDir = getAreasOfUser(str(user.getId()))

        if slotParentDir is not None:
            for p in slotParentDir:
                debug = "%s...[%s]..." % (debug, p)
                areaName = parseAccessAreaNames(os.path.basename(p))
                if areaName is not None:
                    timestamp = os.path.getctime(p)
                    dt = datetime.datetime.fromtimestamp(timestamp)
                    # Convert it to an aware datetime object in UTC time.
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                    # Convert it to your local timezone (still aware)
                    dt = dt.astimezone()
                    # Print it with a directive of choice
                    thisDate = dt.strftime("%d %b %Y (%I:%M:%S %p)")
                    data = {'date': thisDate, 'area': areaName,
                            'timestamp': timestamp,
                            'hashname': os.path.basename(p),
                            'url': f"{SERVER_NAME}/{os.path.basename(p)}/",
                            'cmd': CMD_CURL % (
                                SERVER_NAME,
                                os.path.basename(p).replace(" ", "%20"),
                                CURL_FILE),
                            'size': filesizeformat(get_area_size(p))
                          }
                    values.append(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        debug = "%s...[ERROR: \n%s[%s]]..." % (debug, str(e), exc_tb.tb_lineno)
        print('ERROR: while reading openlink dir: %s\n ' % (str(e)))

    values = sorted(values, key=itemgetter('timestamp'), reverse=True)
    return render(request,
                  'omero_openlink/index.html',
                  {'slots': values, 'debug': debug})


@login_required()
def delete(request, conn=None, **kwargs):
    if request.method == "POST":
        hashname = request.POST.get('hashname_id')
        myPath = '%s/%s' % (OPENLINK_DIR, hashname)
        if os.path.exists(myPath):
            try:
                shutil.rmtree(myPath)
            except OSError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print('ERROR: while delete openlink area: %s\n ' % (str(e)))
                return JsonResponse(['ERROR:while delete openlink area',
                                     str(e), exc_tb.tb_lineno],
                                    safe=False)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER') +
                                '#openlink_tab')
