import fastapi
import uvicorn
import contacts.routes as contacts_routes
import auth.routes
import auth.exceptions

app = fastapi.FastAPI()

app.include_router(contacts_routes.router, prefix="/api")
app.include_router(auth.routes.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000
    )