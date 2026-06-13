import os
import uvicorn

from app.db.db import db_handler

if __name__ == "__main__":
    db_handler.init_db()
    uvicorn.run("app.server:app", host="0.0.0.0", port=6767, reload=os.getenv("ENV", "development") == "development")

