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

from wsgiref import simple_server

from oslo.config import cfg
from ws4py.server import wsgirefserver
from ws4py.server import wsgiutils

import marconi.openstack.common.log as logging
from marconi.queues import transport
from marconi.queues.transport import validation
from marconi.queues.transport.wsgi.public import driver as pub_driver
from marconi.queues.transport.wsgi.public import driver as adm_driver
from marconi_ws import websocket


_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),

    cfg.IntOpt('port', default=9000,
               help='Port on which the self-hosting server will listen'),
]

_OPTIONS_GROUP = 'drivers:transport:marconi_ws'

LOG = logging.getLogger(__name__)


class Driver(transport.DriverBase):

    def __init__(self, conf, storage, cache, control):
        super(Driver, self).__init__(conf, storage, cache, control)

        self._conf.register_opts(_OPTIONS, group=_OPTIONS_GROUP)
        self._transport_conf = self._conf[_OPTIONS_GROUP]
        self._validate = validation.Validator(self._conf)

        # NOTE(flaper87): if admin_mode is enabled, use the
        # admin API instead.

        # FIXME(flaper87): This will stick around until the
        # new API layer is ready. At some point, we won't need
        # to proxy the wsgi transport anymore.
        if self.__conf.admin_mode:
            driver = pub_driver.Driver(conf, storage, cache, control)
        else:
            driver = adm_driver.Driver(conf, storage, cache, control)

        websocket.MarconiWebsocket.falcon_app = driver.app
        self.app = wsgiutils.WebSocketWSGIApplication(handler_cls=websocket.MarconiWebsocket)

    def listen(self):
        msgtmpl = _(u'Serving on host %(bind)s:%(port)s')

        LOG.info(msgtmpl,
                 {'bind': self._transport_conf.bind,
                  'port': self._transport_conf.port})

        wref_server = wsgirefserver.WSGIServer
        wref_handler = wsgirefserver.WebSocketWSGIRequestHandler

        httpd = simple_server.make_server(self._transport_conf.bind,
                                          self._transport_conf.port,
                                          server_class=wref_server,
                                          handler_class=wref_handler,
                                          app=self.app)
        httpd.initialize_websockets_manager()
        httpd.serve_forever()
