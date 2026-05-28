import os
import uvicorn


if __name__ == "__main__":
    # setup_db()
    uvicorn.run("app.server:app", host="0.0.0.0", port=6767, reload=os.getenv("ENV", "development") == "development")

