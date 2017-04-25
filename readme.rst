=====
About
=====

This is a sample https://www.yandex.com/ scraper.
It requires:
Python == 3.5.x.
Redis https://redis.io/topics/quickstart

Usage
=====

Scrape search results via script and save output to database. Retrieve via Flask server::

    run.py -k <keywords> -o <pages> -c <callback_url> or -r <read>

    python3 run.py -k 'samsung' -p 5 -c http://127.0.0.1:5000/test
    python3 run.py -r 11

To access data with provided urls start Flask server by running::

    python3 run_server.py

Setup
=====

Create python virtual environment::

    $ make pyenv

This command will download and install all project dependencies to `pyenv/`
directory.