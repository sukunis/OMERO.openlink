OMERO.openlink
==============

An OMERO.web plugin that creates openly accessible links (URLS for raw files) to your data in OMERO and a batch file to download the data with 'curl'.

Main application:

* Bundle data of different groups/projects/datasets
* Fast web download
* Data sharing via link

Requirements
============
- OMERO.web 5.6.0 or newer
- nginx server configurations

Installation
============

This section assumes that an OMERO.web is already installed and you will use the nginx server to provide the URL's.

Prerequisite
----------------
Variable **OPENLINK_DIR**:
You have to define a directory on your OMERO.server (here */path/to/open_link_dir*), where your nginx server has access. The system user omero-server requires read and write access to this directory for link generation. If you want to use the plugin, omero-web also needs read and write access. Please specify the full path to this directory under OPENLINK_DIR.

Install the app using `pip <https://pip.pypa.io/en/stable/>`_
-------------------------------------------------------------
NB: You need to ensure that you are running pip from the python environment where omero-web is installed. Depending on your install, you may need to call pip with, for example: /path/to_web_venv/venv/bin/pip install ...

::

    $pip install -U omero-openlink


Add OpenLink app to your installed web apps:

::

    $omero config append omero.web.apps '"omero_openlink"'


Display the OpenLink pane in the right pane

::

    $omero config append omero.web.ui.right_plugins '["OpenLink", "omero_openlink/webclient_plugins/right_plugin.openlink.js.html", "openlink_tab"]'


Additional configuration settings:

::

    # path of prepared OPENLINK_DIR, here as eaxmple */storage/openlink*
    $omero config set omero.web.openlink.dir '/storage/openlink'
    # set the url alias of your OMERO.web server without leading http://. Here as example we use the address of the openmicroscopy demo server
    $omero config set omero.web.openlink.servername 'demo.openmicroscopy.org'
    # http or https
    $omero config set omero.web.openlink.type_http 'https'

Reload your system and restart the OMERO.web server:

Nginx configuration
-------------------

This section assumes that an you use an nginx server.
You can configure your nginx in two way's:

*Option 1:*
Add a new location to your nginx configuration file (etc/nginx/conf.d/omeroweb.conf) like:

::

    location  /openlink {
            proxy_read_timeout 36000;  # 10 hours
            limit_rate 10000M;  # 10 GByte
            gzip on;
            gzip_min_length 10240;
            disable_symlinks off;  # enable symlinks
            autoindex on;
            autoindex_format html; # html, xml, json, or jsonp
            autoindex_exact_size off; # on off
            autoindex_localtime on; # on off  (UTC)
            alias /storage/openlink/;  # the links will be created here
    }


*Option 2:*
Or create a new website for nginx by create a new file (e.g. openlink.conf) in /etc/nginx/conf.d/ with:

::

    server {
        listen 80;
        server_name SERVER_NAME;  # url alias to this nginx site

        location /openlink {

            proxy_read_timeout 36000;  # 10 hours
            limit_rate 10000M;  # 10 GByte
            gzip on;
            gzip_min_length 10240;
            disable_symlinks off;  # enable symlinks
            autoindex on;
            autoindex_format html; # html, xml, json, or jsonp
            autoindex_exact_size off; # on off
            autoindex_localtime on; # on off  (UTC)
            alias /storage/openlink/;  # the links will be created here
        }
    }


Enable openlink creation
---------------------------
This section assumes that an OMERO.server is already installed.

Openlink can be created using a script that runs on the OMERO.server. This script needs to be uploaded to the OMERO.server and its dependencies installed in the OMERO.server virtual environment.

The script can be uploaded using two alternative workflows, both of which require you to have the correct admin privileges. To find where OMERO.openlink has been installed using pip, run:

::

    $pip show omero-openlink

The command will display the absolute path to the directory where the application is installed e.g. ~/<virtualenv_name>/lib/python3.6/site-packages. Go to that directory.


Before uploading please edit the configuration section of omero_openlink/scripts/omero/util_scripts/Create_OpenLink.py.

*Note* OPENLINK_DIR, SERVER_NAME,TYPE_HTTP should have the same values like specified in the config of OMERO.web. Because the script is running on the OMERO.server, there is no way to transfer the config parameters automatically.

::

    # Directory for links that the nginx server also has access to
    OPENLINK_DIR= "/path/to/open_link_dir"

    # name of nginx website
    SERVER_NAME = "omero-data.myfacility.com"

    # type of hypertext transfer protocol (http or https)
    TYPE_HTTP="https"

    # email originator
    ADMIN_EMAIL = "myemail@yourfacilitydomain"

    # length of hash string used in the openlink url
    LENGTH_HASH = 12


*Option 1:* Connect to the OMERO server and upload the script via the CLI. It is important to be in the correct directory when uploading so that the script is uploaded with the full path: omero/utils_scripts/Create_OpenLink.py:

::

    $cd omero_openlink/scripts
    $omero script upload omero/util_scripts/Create_OpenLink.py --official


*Option 2:* Alternatively, before starting the OMERO.server, copy the script from the figure install /omero_openlink/scripts/omero/util_scripts/Create_OpenLink.py to the OMERO.server path/to/OMERO.server/lib/scripts/omero/util_scripts. Then restart the OMERO.server.

*Option 3:* Upload the script through the OMERO web interface: For this, log into your OMERO web interface as admin, select the scripts icon and click on the "Upload Script" button. Select the Create_OpenLink.py script from the directory where you copied it to locally and upload it into the directory omero/util_scripts.


Validation
==========

Validation of configuration in *Create_OpenLink.py*
----------------------------------------------------
In order to check whether the values for x have been entered correctly, please test the link that was entered in the log file under URL and also check the entered url's in the batch_download.curl that is available there.

Validation of configuration *omero-openlink*
--------------------------------------------
There is a debug output available for the plugin. Go to subdirectory omero_openlink of the installation directory of *omero-openlink*

::

    $ cd omero-openlink/omero_openlink

open the *urls.py* and delete the leading # in the line

::

    #url(r'^debugoutput/$',views.debugoutput,name='debugoutput'),

After restarting the web server, find the debug output for your Openlink plugin by replacing webclient by oemro_openlink/debugoutput in the URL of the omero.web
(for example: https://server.openmicroscopy.org/webclient -> https://server.openmicroscopy.org/omero_openlink/debugoutput). This output shows you:

 * what is defined under OPENLINK_DIR, SERVER_NAME
 * check if OPENLINK_DIR is accessible
 * check permission of OPENLINK_DIR for omero-web user
 * overview of OpenLink Areas of currently logged-in user


License
==========

OMERO.openlink is released under the AGPL.





