import asyncio
import os
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == '__main__':
    port = int(os.getenv("PORT", 9050))
    config = uvicorn.Config("app.main:app", host="127.0.0.1", port=port, reload=False, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
