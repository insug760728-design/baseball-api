import os
import sys
import uvicorn

if __name__ == '__main__':
    port = int(os.getenv("PORT", 9050))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting server on http://{host}:{port}", flush=True)
    uvicorn.run("app.main:app", host=host, port=port, reload=False, log_level="info")
