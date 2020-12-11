# OMERO.openlink  <img src="/images/icon.png?raw=true" width="70" height="70">   

An OMERO.web app and script for sharing data and prepare data for web download.

You can generate URL's for specific data for batch web download, share data with other collaborates that are not in your group or member of our OMERO system or for third party use. All operations are available in OMERO.web.

### Features
- Create coded URL for html page with read only URL links to your data
- You can add data to an existing page
- You can delete whole page
- Fast batch download for all data of one openlink area with **curl** (skip already downloaded files, compressed for transfer)

OMERO.openlink is composed of two components:

***Create_OpenLink.py*** (generation)
A server side script that generates soft links to your data and creates a **curl** file for batch download of this data.
You can share only your own data or the data of a non-private group , if you are the owner of this group (the owner of the data will be informed by mail).

NOTE:
If you prefer another download manager, you can change the generated commands in the Python script.

***omero-openlink*** (visualization)
An OMERO.web plugin that lists the links to generated areas of softlinks via the nginx server. Provides the corresponding curl command to start the download. With the plugin the areas can also be deleted via OMERO.web.

## Requirements:
- OMERO.web 5.6.0 or newer
- nginx server configurations

## Installing
This section assumes that an OMERO.web is already installed and you will use the nginx server to provide the data links.

### Prerequisite:
Variable **OPENLINK_DIR**:
You have to define a directory on your OMERO.server (here */path/to/open_link_dir*), where your nginx server has access. The system user omero-server requires read and write access to this directory for link generation. If you want to use the plugin, omero-web also needs read and write access. Please specify the full path to this directory under OPENLINK_DIR.

Variable **SERVER_NAME**:
The url alias of your OMERO.web server without leading http://.


### Installation *Create_OpenLink.py*:

Download *Create_OpenLink.py* and open it to add your specifications under the configuration section:

```
#-------------------------------------------------
#------------ Configuration ----------------------
#-------------------------------------------------

# Directory for links that the nginx server also has access to
OPENLINK_DIR= "/path/to/open_link_dir"

# name of nginx website
SERVER_NAME = "omero-data.myfacility.com"

# email originator
ADMIN_EMAIL = "myemail@yourfacilitydomain"

# length of hash string used in the openlink url
LENGTH_HASH = 12
#--------------------------------------------------

```

Upload the script *Create_OpenLink.py* to OMERO.server ( [howto](https://docs.openmicroscopy.org/omero/5.6.3/developers/scripts/user-guide.html#upload-script))


### Installation Plugin omero-openlink:
Download omero-openlink to your OMERO.web system.
Go to omero-openlink and install the plugin  using [pip](https://pip.pypa.io/en/stable/):

    $ cd omero-openlink
    $ pip install -e .

Add OpenLink app to your installed web apps:

    $ omero config append omero.web.apps '"omero_openlink"'

Display the OpenLink pane in the right pane

    $ omero config append omero.web.ui.right_plugins '["OpenLink", "omero_openlink/webclient_plugins/right_plugin.openlink.js.html", "openlink_tab"]'

Configuration settings (with *omero config set*):

- ``omero.web.openlink.dir`` OPENLINK_DIR
- ``omero.web.openlink.servername`` SERVER_NAME


#### Nginx configuration:

Add a new location to your nginx configuration file (etc/nginx/conf.d/omeroweb.conf):
```
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
        alias OPENLINK_DIR/;  # the links will be created here
}
```

Or create a new website for nginx by create a new file (e.g. openlink.conf) in /etc/nginx/conf.d/ with:

```
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
        alias OPENLINK_DIR/;  # the links will be created here
    }
}
```
Reload your system and restart the OMERO server:

    $ omero admin restart

## License

OMERO.openlink is released under the AGPL.








