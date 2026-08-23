from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

database_url = "postgresql://user:password@localhost/db"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    db.close()

@app.get("/")
def read_root():
    return {"message": "AI Voice Calling Agent Backend"}
