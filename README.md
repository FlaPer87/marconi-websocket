marconiewebsocket
=================

Websocket transport for Marconi

This transport is experimental! Use it under your own risk!

Seriously
=========

It just proxies Marconi's wsgi transport through websocket by sending json-serialized HTTP requests and translating them to actual wsgi request. Just play with it but, don't fucking use it in production. Not yet! ;)

I mean, Seriously
=================

IT'S A POC (Proof of Concept). Like Sunday's R&D project... BY ALL MEANS, DO NOT USE IT...

AUTHOR, LICENSE, ETC
====================

Flavio Percoco (@flaper87). This stuff is all Apache 2 licensed!


ROADMAP
=======

Fully support Marconi's API, implement Marconi's transports tests - I mean, actually use them. The 'proxy method' will be replaced in the near future by the new Marconi's API layer.
