from fastapi import FastAPI, Path, HTTPException
from typing import Annotated
from pydantic import BaseModel, field_serializer
from datetime import datetime

from .dao import tournaments, matches

app = FastAPI()


class Tournament(BaseModel):
    id: str
    name: str
    description: str
    year: int
    start_date: datetime

    @field_serializer('start_date')
    def serialize_dt(self, start_date: datetime, _info):
        # return start_date.timestamp()
        return start_date.isoformat()


class Match(BaseModel):
    id: str
    name: str
    description: str
    date: datetime
    tournament_id: str
    players: int = 2
    result: list = []

    @field_serializer('date')
    def serialize_dt(self, date: datetime, _info):
        return date.isoformat()


class Score(BaseModel):
    player_id: int
    points: int = 1


@app.get("/")
async def root():
    return {"message": "ok"}


@app.get("/tournaments", response_model=list[Tournament])
async def tournaments_list():
    ts = tournaments.get_items_from_db()
    return ts


@app.post("/tournaments", status_code=201)
async def create_tournament(tournament: Tournament):
    try:
        ts = tournaments.create_tournament(tournament.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot create item: {e}")
    return ts


@app.get("/tournaments/{item_id}", response_model=Tournament)
async def tournaments_item(item_id: Annotated[str, Path(title="Item id")]):
    try:
        t = tournaments.get_item_from_db(item_id)
        return t
    except RuntimeError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.put("/tournaments/{item_id}", response_model=Tournament)
async def put_tournament(item_id: Annotated[str, Path(title="Item id")], tournament: Tournament):
    try:
        t = tournaments.update_tournament(item_id, tournament.model_dump())
        return t
    except RuntimeError as e:
        if 'not found' in str(e):
            raise HTTPException(status_code=404, detail=f"Item not found: {e}")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid item: {e}")


@app.get("/matches", response_model=list[Match])
async def match_list():
    match_list = matches.get_items_from_db()
    return match_list


@app.get("/matches/{item_id}", response_model=Match)
async def match_item(item_id: Annotated[str, Path(title="Item id")]):
    try:
        t = matches.get_item_from_db(item_id)
        return t
    except RuntimeError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.post("/matches", status_code=201)
async def create_match(match: Match):
    try:
        ts = matches.create_match(match.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot create item: {e}")
    return ts


@app.post("/matches/{match_id}/scores")
async def create_score(match_id: Annotated[str, Path(title="Match id")], score: Score):
    try:
        t = matches.score_point(match_id, score.model_dump())
        return t
    except RuntimeError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.put("/matches/{match_id}/scores")
async def update_score(match_id: Annotated[str, Path(title="Match id")], score: Score):
    try:
        t = matches.update_score(match_id, score.model_dump())
        return t
    except RuntimeError:
        raise HTTPException(status_code=404, detail="Item not found")
