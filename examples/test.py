import json

from ws4py.client.threadedclient import WebSocketClient


class DummyClient(WebSocketClient):

    def opened(self):
        msg = {'path': '/v1/queues/fizbat/',
               'method': 'PUT',
               'body': '{}'}

        self.send(json.dumps(msg))

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print m
        if len(m) == 175:
            self.close(reason='Bye bye')

if __name__ == '__main__':
    try:
        ws = DummyClient('ws://localhost:9000/', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ws.close()
