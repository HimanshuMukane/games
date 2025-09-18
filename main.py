import uvicorn
import socket
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from main.api import api_router
from fastapi.responses import RedirectResponse
from main.utils.db import create_tables
from main.utils.config import settings

app = FastAPI(title="Fun Thursday API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup
@app.on_event("startup")
def startup():
    create_tables()

# Mount static files (JS, CSS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers (API + frontend)
app.include_router(api_router)


def get_local_ip():
    """Get LAN IP address of the machine (network IP)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))   # connect to Google DNS just to get routing info
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    host = "0.0.0.0"   # bind to all interfaces
    port = settings.PORT

    local_url = f"http://127.0.0.1:{port}"
    network_url = f"http://{get_local_ip()}:{port}"

    print("\n🚀 Server running at:")
    print(f"   Local:   {local_url}")
    print(f"   Network: {network_url}\n")

    uvicorn.run(app, host=host, port=port, reload=False)
