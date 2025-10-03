from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API de test"}

if __name__ == "__main__":
    print("Démarrage de l'API sur http://localhost:8000")
    uvicorn.run("simple_api:app", host="0.0.0.0", port=8000, reload=True)
