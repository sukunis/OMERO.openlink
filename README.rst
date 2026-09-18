OMERO.openlink
==============

An OMERO.web plugin that creates openly accessible links (URLS for raw files) to your data in OMERO and a batch file to download the data with 'curl'.

Main application:

* Bundle data of different groups/projects/datasets
* Fast web download
* Data sharing via link

⚙️ Prerequisites & Requirements
============

Before starting the setup, ensure you meet the following system requirements

- **OMERO.web:** 5.6.0 or newer
- **Web Server:** A functional Nginx server is required to serve the generated links.
- **Shared Directory:** You must designate a common directory on the OMERO server (``OPENLINK_DIR``) that is readable and writable by both the omero-server user and the user running OMERO.web.


Critical Configuration Variables
------------------

The following variables must be defined and synchronized across the **OMERO.web configuration**, the **Nginx configuration**, and the **Create_OpenLink.py** script.

+----------------+-------+------------------------------------------------------------------------+------------------------+
| Variable       | Scope | Description                                                            | Example Value          |
+================+=======+========================================================================+========================+
| OPENLINK_DIR   | All   | The absolute path on the OMERO server where link files will be stored  | /storage/openlink_data |
|                |       | and the NGINX server has access to. The system user of omero-server    |                        |
|                |       | requires read and write access, as well omero-web.                     |                        |
+----------------+-------+------------------------------------------------------------------------+------------------------+
| SERVER_NAME    | All   | The external URL alias for the data access (without http://).          | data.myorg.de          |
+----------------+-------+------------------------------------------------------------------------+------------------------+
| TYPE_HTTP      | All   | Protocol used for external access.                                     | https                  |
+----------------+-------+------------------------------------------------------------------------+------------------------+
| NGINX_LOCATION | All   | The path segment Nginx uses for the data (e.g., /openlink)             | /openlink              |
|                |       | -> would result in the url https://data.myorg.de/openlink              |                        |
+----------------+-------+------------------------------------------------------------------------+------------------------+


Installation
============

Step 1: Install the OMERO.web environment
---------------------------------

**Note:** Ensure you are executing these commands from the Python virtual environment where OMERO.web is installed. Depending on your install, you may need to call pip with, for example: /path/to_web_venv/venv/bin/pip install ...

1. **Install Package via PIP**

   >>> pip install -U omero-openlink

2. **Register the App:** Add the plugin to the list of enabled web applications:

   >>> omero config append omero.web.apps '"omero_openlink"'

3. **Display the Plugin Pane:** Add the OpenLink tab to the right-hand sidebar:

   >>> omero config append omero.web.ui.right_plugins '["OpenLink", "omero_openlink/webclient_plugins/right_plugin.openlink.js.html", "openlink_tab"]'

4. **Set Configuration Parameters:** Define the global variables using the values established in the Prequisites table::

    # Set the physical directory for links
    >>> omero config set omero.web.openlink.dir 'OPENLINK_DIR'
    # Set the base URL alias
    >>> omero config set omero.web.openlink.servername 'SERVER_NAME'
    # Set protocol
    >>> omero config set omero.web.openlink.type_http 'TYPE_HTTP'
    # Set the NGINX path segment 
    >>> omero config set omero.web.openlink.nginx_location 'NGINX_LOCATION'

5. **Restart:** Reload your entire system and restart the OMERO.web server to load the plugin.

Step 2: Configure External Access (Nginx)
-------------------

This step configures Nginx to correctly proxy and serve the link files from the directory defined in ``OPENLINK_DIR``.

**Note:** You must use the exact ``SERVER_NAME`` and ``OPENLINK_DIR`` defined in the Prerequisites section.

Choose **ONE** configuration option based on your Nginx setup:

Option A: Adding a Location Block (Recommended for existing setups)
```````````````````````````

Add a new location to your nginx configuration file (``/etc/nginx/conf.d/omeroweb.conf``) like::

   location  NGINX_LOCATION {
            proxy_read_timeout 36000;  # 10 hours
            limit_rate 10000M;  # 10 GByte
            gzip on;
            gzip_min_length 10240;
            disable_symlinks off;  # enable symlinks
            autoindex on;
            autoindex_format html; # html, xml, json, or jsonp
            autoindex_exact_size off; # on off
            autoindex_localtime on; # on off  (UTC)
            alias OPENLINK_DIR;  # the links will be created here
    }

Your data will be accessible under SERVERNAME/NGINX_LOCATION (Example: data.myorg.de/openlink).

Option B: Creating a Dedicated Server Block
````````````````````````````

Create a new website for Nginx by create a new configuration file (e.g. ``openlink.conf``) in ``/etc/nginx/conf.d``::

    server {
        listen 80;
        server_name SERVER_NAME;  # url alias to this nginx site

        location NGINX_LOCATION {
            proxy_read_timeout 36000;  # 10 hours
            limit_rate 10000M;  # 10 GByte
            gzip on;
            gzip_min_length 10240;
            disable_symlinks off;  # enable symlinks
            autoindex on;
            autoindex_format html; # html, xml, json, or jsonp
            autoindex_exact_size off; # on off
            autoindex_localtime on; # on off  (UTC)
            alias OPENLINK_DIR;  # the links will be created here
        }
    }

**Note:** 

To use a special style (like the example in ``scripts/nginx/autoIndexStyle.xslt``) for your openlink data representation,
please copy the style file to ``/etc/nginx`` and use the following configuration:::

    autoindex_format  xml;
    xslt_stylesheet /etc/nginx/autoindexStyle.xslt       path="$uri" schema="$scheme" host="$host";


**Security Recommendation**:

To prevent directory listing when a user navigates to the base URL, create a simple ``index.html`` file in ``OPENLINK_DIR`` instructing users to use the OMERO system to generate links.


Example for ``index.html``::

    <!DOCTYPE html>
    <html lang="de">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Omero Downloads</title>
      </head>
      <body>
      <a href="https://data.myorg.de/openlink">Please go first to the Omero-System to create DownloadLinks!</a>
      </body>
    </html>






Step 3: Generating Data Links on the OMERO.server (Server side)
---------------------------

This step uses the a OMERO.script (python) on the server to create the links associated with your data.
This script needs to be uploaded to the OMERO.server and its dependencies installed in the OMERO.server virtual environment.

**Note:**
Update all variables in the configuration section of ``Create_Openlink.py`` to match the Nginx/Web settings listed in the Prerequisites table before upload. Because the script is running on the OMERO.server, there is no way to transfer the config parameters automatically.

Example configuration section ``Create_Openlink.py``::


    # Directory for links that the nginx server also has access to as specifed in OMERO web config
    OPENLINK_DIR = "/path/to/open_link_dir"
    
    # name of nginx website as specifed in OMERO web config
    SERVER_NAME = "omero-data.myfacility.com"
    
    # type of hypertext transfer protocol (http or https) as specifed in OMERO web config
    TYPE_HTTP = "https"
    
    # email originator
    ADMIN_EMAIL = "myemail@yourfacilitydomain"
    
    # filename with links to single files
    LINKS_FILE = "links_to_data.txt"
    
    # length of hash string used in the openlink url
    LENGTH_HASH = 12
    
    # email server IP adress
    SMTP_IP = "127.0.0.1"
    
    # nginx location for openlink data as specifed in OMERO web config
    NGINX_LOCATION = ""  # '/openlink'

**Deployment Options (Choose ONE):**

Option 1: CLI Upload (Recommended)
``````````````

1. Locate the script installation path using

   >>> pip show omero-openlink

2. Navigate to the script directory, edit configuration and upload

   >>> cd SCRIPT_INSTALL_PATH/scripts/omero_openlink/scripts/omero/util_scripts/
   # edit Create_OpenLink.py
   # to upload to section omero/util_scripts use:
   >>> omero script upload omero/util_scripts/Create_OpenLink.py --official 



Option 2: Direct File Copy
``````````````

Alternatively, before starting the OMERO.server, copy the script from the figure install /omero_openlink/scripts/omero/util_scripts/Create_OpenLink.py to the OMERO.server path/to/OMERO.server/lib/scripts/omero/util_scripts. Then restart the OMERO.server.


Option 3: Web Interface Upload
````````````````

Upload the script through the OMERO web interface: For this, log into your OMERO web interface as admin, select the scripts icon and use the "Upload Script" buttonto place the script in the correct directory structure (``omero/util_scripts/``).


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





