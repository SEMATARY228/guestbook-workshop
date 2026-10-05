from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from config import settings

load_dotenv()


def connect():
    database_url = settings.database_url
    return psycopg.connect(database_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id SERIAL PRIMARY KEY, author TEXT, text TEXT)"
        )
    yield


app = FastAPI(lifespan=lifespan)


class Message(BaseModel):
    author: str
    text: str


@app.get("/")
def index():
    greeting = settings.greeting
    return {"message": greeting}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/messages")
def list_messages():
    with connect() as conn:
        rows = conn.execute(
            "SELECT author, text FROM messages ORDER BY id DESC"
        ).fetchall()
    return [{"author": author, "text": text} for author, text in rows]


@app.post("/messages")
def add_message(message: Message):
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages (author, text) VALUES (%s, %s)",
            (message.author, message.text),
        )
    return {"ok": True}
