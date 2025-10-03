#!/usr/bin/env python3
"""
Serveur de test minimal pour CereBloom
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="CereBloom Test")

@app.get("/")
async def root():
    return {"message": "CereBloom Test Server OK"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cerebloom-test"}

if __name__ == "__main__":
    print("🚀 Test Server - Démarrage...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
