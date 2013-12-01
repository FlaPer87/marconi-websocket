# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import json

from falcon.request import Request
from falcon.response import Response
import six
from ws4py import websocket


class MarconiWebsocket(websocket.WebSocket):

    falcon_app = None

    def received_message(self, message):

        try:
            data = json.loads(unicode(message.data))
        except Exception as exc:
            print(message.data)

        body = data.get('body', '')
        if isinstance(body, six.text_type):
            body = body.encode('utf-8')

        headers = data.get('headers', {})

        body = io.BytesIO(body)

        env = self.environ.copy()
        env.update({'PATH_INFO': data['path'],
                    'SERVER_PROTOCOL': 'HTTP/1.1',
                    'REQUEST_METHOD': data['method'],

                    # NOTE(flaper87): Body is optional. If present
                    # it has to be a serialized json.
                    'wsgi.input': body,

                    'HTTP_ACCEPT': 'application/json'})

        for header, value in headers.items():
            env['HTTP_' + header.upper()] = value

        req = Request(env)
        resp = Response()

        responder, params, na_responder = self.falcon_app._get_responder(req.path, req.method)
        responder(req, resp, **params)
        self.send(json.dumps({'headers': resp._headers,
                              'status': resp.status,
                              'body': resp.body_encoded}))
