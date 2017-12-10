lunchbot
========

Simple Skype bot which helps to choose restaurant for lunch.

Configuration
-------------

Before start you need to obtain Application Id and password. Please check `Register a bot with the Bot Framework`_.

Copy ``lunchbot.cfg.example`` to ``lunchbot.cfg`` and ``data.txt.example`` to ``data.txt``.

Edit ``lunchbot.cfg`` and ``data.txt`` according to comments.

.. _Register a bot with the Bot Framework: https://docs.microsoft.com/en-us/bot-framework/portal-register-bot

Development
-----------

Install package in development mode (recommended to use `virtualenv`)::

    python setup.py develop

Set environment variables::

    export FLASK_APP=lunchbot
    export FLASK_DEBUG=1
    export LUNCHBOT_SETTINGS=lunchbot.cfg

Run application::

    flask run

Deployment
----------

To deploy `lunchbot` you will need Linux host with `Docker` and `docker-compose` installed.

Go to directory with project's sources copied. Create here ``lunchbot.cfg`` and ``data.txt`` files. Run::

    docker-compose up -d

Service will listen on port `5000` on the loopback interface.

You will need to use some HTTP server as reverse proxy. For example Nginx::

    upstream lunchbot-site {
            server localhost:5000;
    }

    server {
            listen 80;

            # Make site accessible from http://bot.example.com/
            server_name bot.example.com;

            location / {
                proxy_set_header        Host $http_host;
                proxy_set_header        X-Real-IP $remote_addr;
                proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header        X-Forwarded-Proto $scheme;

                client_max_body_size    10m;
                client_body_buffer_size 128k;
                proxy_connect_timeout   60s;
                proxy_send_timeout      90s;
                proxy_read_timeout      90s;
                proxy_buffering         off;
                proxy_temp_file_write_size 64k;
                proxy_pass http://lunchbot-site;
                proxy_redirect          off;
            }

            # redirect server error pages to the static page /50x.html
            #
            error_page 500 502 503 504 /50x.html;
            location = /50x.html {
                    root /usr/share/nginx/html;
            }

            listen 443 ssl; # managed by Certbot
            ssl_certificate /etc/letsencrypt/live/bot.example.com/fullchain.pem; # managed by Certbot
            ssl_certificate_key /etc/letsencrypt/live/bot.example.com/privkey.pem; # managed by Certbot
            include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
            ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

            if ($scheme != "https") {
                return 301 https://$host$request_uri;
            } # managed by Certbot
    }

License
-------

Licensed under MIT License.
