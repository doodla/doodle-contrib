#!/usr/bin/env python3
import os
import sys

import nginx

args = sys.argv[1:]

app_dir = args[0]
try:
    app_name = args[1]
except IndexError:
    app_name = app_dir

SYSTEMD_PATH = '/etc/systemd/system/'

NGINX_CONF = '/etc/nginx/conf.d/app.conf'

NGINX_SNIPPETS = '/etc/nginx/snippets/apps/'


def create_snippet():
    snippet_data = """
location /{app_name} {{
    include proxy_params;
    proxy_pass http://unix:/home/doodla/{app_dir}/{app_dir}.sock;
}}

location /{app_name}/static {{
    alias /home/doodla/{app_dir}/static;
}}

location /{app_name}/media {{
    alias /home/doodla/{app_dir}/media;
}}
    """.format(app_dir=app_dir, app_name=app_name)

    os.chdir(NGINX_SNIPPETS)

    with open('{}.conf'.format(app_dir), mode='w') as f:
        f.write(snippet_data)
        print('Snippet Written')


def create_systemd_service():
    service_data = """
[Unit]
Description={app_name} gunicorn daemon
After=network.target

[Service]
User=doodla
Group=www-data
WorkingDirectory=/home/doodla/{app_dir}
ExecStart=/home/doodla/{app_dir}/venv/bin/gunicorn --workers 3 --bind unix:/home/doodla/{app_dir}/{app_dir}.sock app.wsgi:application

[Install]
WantedBy=multi-user.target
    """.format(app_dir=app_dir, app_name=app_name)

    os.chdir(SYSTEMD_PATH)
    with open('{}.service'.format(app_dir), mode='w') as f:
        f.write(service_data)
        print('Service Written')


print('App Name : {}'.format(app_dir))


def update_nginx_block():
    conf_path = "snippets/apps/{}.conf".format(app_dir)
    c = nginx.loadf(NGINX_CONF)

    block = c.children[-1]

    block.add(nginx.Key('include', conf_path))

    nginx.dumpf(c, NGINX_CONF)
    print('Block Added')


create_systemd_service()
create_snippet()
update_nginx_block()
