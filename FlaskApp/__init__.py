from flask import Flask, after_this_request, request
import io
import gzip
import functools
import redis
from . import config


app = Flask(__name__)
app.config['SERVER_NAME'] = config.SERVER_NAME


# not my code, http://flask.pocoo.org/snippets/122/
def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                    'Content-Encoding' in response.headers):
                return response
            gzip_buffer = io.BytesIO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


@app.route('/task')
@gzipped
def task():
    db = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    if request.args.get('id'):
        data = db.get(request.args.get('id'))
        if data:
            return data
    return '<h3>404 Not Found</h3>'
