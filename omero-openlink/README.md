# omero-openlink

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

### Installation Plugin:
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





