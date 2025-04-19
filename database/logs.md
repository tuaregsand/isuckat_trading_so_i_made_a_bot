rabbitmq-1   | 2025-04-17 01:00:59.669692+00:00 [info] <0.9.0> Time to start RabbitMQ: 4139 ms
trader-1     | 
trader-1     | > trader@0.1.0 start
trader-1     | > ts-node src/index.ts
trader-1     | 
rabbitmq-1   | 2025-04-17 01:01:01.482524+00:00 [info] <0.695.0> accepting AMQP connection <0.695.0> (172.19.0.5:48034 -> 172.19.0.2:5672)
rabbitmq-1   | 2025-04-17 01:01:01.485307+00:00 [info] <0.695.0> connection <0.695.0> (172.19.0.5:48034 -> 172.19.0.2:5672): user 'guest' authenticated and granted access to vhost '/'
collector-1  | INFO:root:Starting watch_pumpfun
collector-1  | INFO:root:Starting watch_raydium
collector-1  | INFO:root:Connected to Pump.fun WebSocket
brain-1      | INFO:     Started server process [1]
brain-1      | INFO:     Waiting for application startup.
brain-1      | INFO:root:Brain starting up: initializing connections
rabbitmq-1   | 2025-04-17 01:01:01.933253+00:00 [info] <0.709.0> accepting AMQP connection <0.709.0> (172.19.0.4:40468 -> 172.19.0.2:5672)
rabbitmq-1   | 2025-04-17 01:01:01.935795+00:00 [info] <0.709.0> connection <0.709.0> (172.19.0.4:40468 -> 172.19.0.2:5672): user 'guest' authenticated and granted access to vhost '/'
brain-1      | INFO:     Application startup complete.
brain-1      | INFO:uvicorn.error:Application startup complete.
brain-1      | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
brain-1      | INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
collector-1  | INFO:root:Pumpfun event received: mint=None
collector-1  | ERROR:root:Error polling raydium: 'str' object has no attribute 'get'
trader-1     | /app/node_modules/ts-node/src/index.ts:859
trader-1     |     return new TSError(diagnosticText, diagnosticCodes, diagnostics);
trader-1     |            ^
trader-1     | TSError: ⨯ Unable to compile TypeScript:
trader-1     | src/index.ts(5,25): error TS7016: Could not find a declaration file for module '@cryptoscan/pumpfun-sdk/dist/cjs'. '/app/node_modules/@cryptoscan/pumpfun-sdk/dist/cjs/index.js' implicitly has an 'any' type.
trader-1     |   Try `npm i --save-dev @types/cryptoscan__pumpfun-sdk` if it exists or add a new declaration (.d.ts) file containing `declare module '@cryptoscan/pumpfun-sdk/dist/cjs';`
trader-1     | 
trader-1     |     at createTSError (/app/node_modules/ts-node/src/index.ts:859:12)
trader-1     |     at reportTSError (/app/node_modules/ts-node/src/index.ts:863:19)
trader-1     |     at getOutput (/app/node_modules/ts-node/src/index.ts:1077:36)
trader-1     |     at Object.compile (/app/node_modules/ts-node/src/index.ts:1433:41)
trader-1     |     at Module.m._compile (/app/node_modules/ts-node/src/index.ts:1617:30)
trader-1     |     at Module._extensions..js (node:internal/modules/cjs/loader:1252:10)
trader-1     |     at Object.require.extensions.<computed> [as .ts] (/app/node_modules/ts-node/src/index.ts:1621:12)
trader-1     |     at Module.load (node:internal/modules/cjs/loader:1076:32)
trader-1     |     at Function.Module._load (node:internal/modules/cjs/loader:911:12)
trader-1     |     at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:81:12) {
trader-1     |   diagnosticCodes: [ 7016 ]
trader-1     | }

trader-1 exited with code 1
brain-1      | INFO:     172.19.0.1:59502 - "GET / HTTP/1.1" 304 Not Modified
brain-1      | INFO:     172.19.0.1:59502 - "GET /main.js HTTP/1.1" 304 Not Modified
brain-1      | INFO:     172.19.0.1:59502 - "GET /config HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:59506 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     ('172.19.0.1', 59518) - "WebSocket /stream" [accepted]
brain-1      | INFO:uvicorn.error:('172.19.0.1', 59518) - "WebSocket /stream" [accepted]
brain-1      | INFO:     connection open
brain-1      | INFO:uvicorn.error:connection open
brain-1      | INFO:     172.19.0.1:55524 - "POST /wallet/import HTTP/1.1" 500 Internal Server Error
brain-1      | ERROR:    Exception in ASGI application
brain-1      | Traceback (most recent call last):
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
brain-1      |     result = await app(self.scope, self.receive, self.send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
brain-1      |     return await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/applications.py", line 269, in __call__
brain-1      |     await super().__call__(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/applications.py", line 124, in __call__
brain-1      |     await self.middleware_stack(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 184, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 162, in __call__
brain-1      |     await self.app(scope, receive, _send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 93, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 82, in __call__
brain-1      |     await self.app(scope, receive, sender)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
brain-1      |     raise e
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 670, in __call__
brain-1      |     await route.handle(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 266, in handle
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 65, in app
brain-1      |     response = await func(request)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 227, in app
brain-1      |     raw_response = await run_endpoint_function(
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 160, in run_endpoint_function
brain-1      |     return await dependant.call(**values)
brain-1      |   File "/app/./brain.py", line 178, in import_wallet
brain-1      |     seed_bytes = Bip39SeedGenerator(phrase).Generate()
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_seed_generator.py", line 70, in __init__
brain-1      |     Bip39MnemonicValidator(lang).Validate(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/utils/mnemonic/mnemonic_validator.py", line 60, in Validate
brain-1      |     self.m_mnemonic_decoder.Decode(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 71, in Decode
brain-1      |     mnemonic_bin_str = self.__DecodeAndVerifyBinaryStr(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 119, in __DecodeAndVerifyBinaryStr
brain-1      |     raise ValueError(f"Mnemonic words count is not valid ({mnemonic_obj.WordsCount()})")
brain-1      | ValueError: Mnemonic words count is not valid (1)
brain-1      | ERROR:uvicorn.error:Exception in ASGI application
brain-1      | Traceback (most recent call last):
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
brain-1      |     result = await app(self.scope, self.receive, self.send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
brain-1      |     return await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/applications.py", line 269, in __call__
brain-1      |     await super().__call__(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/applications.py", line 124, in __call__
brain-1      |     await self.middleware_stack(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 184, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 162, in __call__
brain-1      |     await self.app(scope, receive, _send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 93, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 82, in __call__
brain-1      |     await self.app(scope, receive, sender)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
brain-1      |     raise e
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 670, in __call__
brain-1      |     await route.handle(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 266, in handle
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 65, in app
brain-1      |     response = await func(request)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 227, in app
brain-1      |     raw_response = await run_endpoint_function(
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 160, in run_endpoint_function
brain-1      |     return await dependant.call(**values)
brain-1      |   File "/app/./brain.py", line 178, in import_wallet
brain-1      |     seed_bytes = Bip39SeedGenerator(phrase).Generate()
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_seed_generator.py", line 70, in __init__
brain-1      |     Bip39MnemonicValidator(lang).Validate(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/utils/mnemonic/mnemonic_validator.py", line 60, in Validate
brain-1      |     self.m_mnemonic_decoder.Decode(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 71, in Decode
brain-1      |     mnemonic_bin_str = self.__DecodeAndVerifyBinaryStr(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 119, in __DecodeAndVerifyBinaryStr
brain-1      |     raise ValueError(f"Mnemonic words count is not valid ({mnemonic_obj.WordsCount()})")
brain-1      | ValueError: Mnemonic words count is not valid (1)
brain-1      | INFO:     172.19.0.1:55540 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:55548 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:61222 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:61232 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:57558 - "POST /wallet/import HTTP/1.1" 500 Internal Server Error
brain-1      | ERROR:    Exception in ASGI application
brain-1      | Traceback (most recent call last):
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
brain-1      |     result = await app(self.scope, self.receive, self.send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
brain-1      |     return await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/applications.py", line 269, in __call__
brain-1      |     await super().__call__(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/applications.py", line 124, in __call__
brain-1      |     await self.middleware_stack(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 184, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 162, in __call__
brain-1      |     await self.app(scope, receive, _send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 93, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 82, in __call__
brain-1      |     await self.app(scope, receive, sender)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
brain-1      |     raise e
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 670, in __call__
brain-1      |     await route.handle(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 266, in handle
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 65, in app
brain-1      |     response = await func(request)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 227, in app
brain-1      |     raw_response = await run_endpoint_function(
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 160, in run_endpoint_function
brain-1      |     return await dependant.call(**values)
brain-1      |   File "/app/./brain.py", line 178, in import_wallet
brain-1      |     seed_bytes = Bip39SeedGenerator(phrase).Generate()
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_seed_generator.py", line 70, in __init__
brain-1      |     Bip39MnemonicValidator(lang).Validate(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/utils/mnemonic/mnemonic_validator.py", line 60, in Validate
brain-1      |     self.m_mnemonic_decoder.Decode(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 71, in Decode
brain-1      |     mnemonic_bin_str = self.__DecodeAndVerifyBinaryStr(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 119, in __DecodeAndVerifyBinaryStr
brain-1      |     raise ValueError(f"Mnemonic words count is not valid ({mnemonic_obj.WordsCount()})")
brain-1      | ValueError: Mnemonic words count is not valid (1)
brain-1      | ERROR:uvicorn.error:Exception in ASGI application
brain-1      | Traceback (most recent call last):
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
brain-1      |     result = await app(self.scope, self.receive, self.send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
brain-1      |     return await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/applications.py", line 269, in __call__
brain-1      |     await super().__call__(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/applications.py", line 124, in __call__
brain-1      |     await self.middleware_stack(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 184, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/middleware/errors.py", line 162, in __call__
brain-1      |     await self.app(scope, receive, _send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 93, in __call__
brain-1      |     raise exc
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/exceptions.py", line 82, in __call__
brain-1      |     await self.app(scope, receive, sender)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
brain-1      |     raise e
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 670, in __call__
brain-1      |     await route.handle(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 266, in handle
brain-1      |     await self.app(scope, receive, send)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/starlette/routing.py", line 65, in app
brain-1      |     response = await func(request)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 227, in app
brain-1      |     raw_response = await run_endpoint_function(
brain-1      |   File "/usr/local/lib/python3.9/site-packages/fastapi/routing.py", line 160, in run_endpoint_function
brain-1      |     return await dependant.call(**values)
brain-1      |   File "/app/./brain.py", line 178, in import_wallet
brain-1      |     seed_bytes = Bip39SeedGenerator(phrase).Generate()
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_seed_generator.py", line 70, in __init__
brain-1      |     Bip39MnemonicValidator(lang).Validate(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/utils/mnemonic/mnemonic_validator.py", line 60, in Validate
brain-1      |     self.m_mnemonic_decoder.Decode(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 71, in Decode
brain-1      |     mnemonic_bin_str = self.__DecodeAndVerifyBinaryStr(mnemonic)
brain-1      |   File "/usr/local/lib/python3.9/site-packages/bip_utils/bip/bip39/bip39_mnemonic_decoder.py", line 119, in __DecodeAndVerifyBinaryStr
brain-1      |     raise ValueError(f"Mnemonic words count is not valid ({mnemonic_obj.WordsCount()})")
brain-1      | ValueError: Mnemonic words count is not valid (1)
brain-1      | INFO:     172.19.0.1:57570 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:57586 - "POST /wallet HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:57586 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:root:Received start command: launching consumer task
brain-1      | INFO:     172.19.0.1:57586 - "POST /start HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:57586 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:root:Consumed raw signal: pumpfun
brain-1      | INFO:     172.19.0.1:60272 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:60280 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:55014 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:55018 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:64362 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:64370 - "GET /status HTTP/1.1" 200 OK
brain-1      | INFO:     172.19.0.1:65270 - "GET /status HTTP/1.1" 200 OK