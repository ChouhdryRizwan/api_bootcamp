from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from model import Hero, HeroCreate, HeroResponse, HeroUpdate, Team, TeamCreate, TeamResponse, TeamUpdate, HeroResponsewithTeam
from env import my_url


DB_URL = my_url
engine = create_engine(my_url)

def create_table():
    SQLModel.metadata.create_all(engine)

app  = FastAPI()

# Create Session
def get_deb():
    with Session(engine) as session:
        yield session
        
@app.on_event("startup")    
def startup_event():
    create_table()

# Default Route
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Get all Data
@app.get("/heroes", response_model=list[Hero])
def get_heros(session: Annotated[Session, Depends(get_deb)], set_offset:int = Query(default=0, le=4), set_limit:int = Query(default=2, le=4)):
    heroes = session.exec(select(Hero).offset(set_offset).limit(set_limit)).all()
    return heroes
    
# Set Data    
@app.post("/heroes", response_model=HeroResponse)
def create_hero(hero: HeroCreate, db: Annotated[Session, Depends(get_deb)]):
        hero_to_insert = Hero.model_validate(hero)
        db.add(hero_to_insert)
        db.commit()
        db.refresh(hero_to_insert)
        return hero_to_insert    
    
# Get single Data
@app.get("/heroes/{hero_id}", response_model=HeroResponsewithTeam)
def get_hero(hero_id: int, session: Annotated[Session, Depends(get_deb)]):
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero
    
@app.patch("/heroes/{hero_id}", response_model=HeroResponse)
def update_hero(hero_id: int, hero: HeroUpdate, session: Annotated[Session, Depends(get_deb)]):
        hero_to_update = session.get(Hero, hero_id)
        if not hero_to_update:
            raise HTTPException(status_code=404, detail="Hero not found")
        hero_data = hero.dict(exclude_unset=True)
        
        for key, value in hero_data.items():
            setattr(hero_to_update, key, value)
        session.add(hero_to_update)
        session.commit()
        session.refresh(hero_to_update)
        return hero_to_update 
    

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: Annotated[Session, Depends(get_deb)]):
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        session.delete(hero)
        session.commit()
        return {"message": "Hero deleted successfully"}
    
    

# Team Routes

#Get 
@app.get("/teams", response_model=list[Team])
def get_teams(session: Annotated[Session, Depends(get_deb)], set_offset:int = Query(default=0, le=4), set_limit:int = Query(default=2, le=4)):
    teams = session.exec(select(Team).offset(set_offset).limit(set_limit)).all()
    return teams    

#Set
@app.post("/teams", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Annotated[Session, Depends(get_deb)]):
        team_to_insert = Team.model_validate(team)
        db.add(team_to_insert)
        db.commit()
        db.refresh(team_to_insert)
        return team_to_insert
    

#Single
@app.get("/teams/{team_id}", response_model=Team)
def get_team(team_id: int, session: Annotated[Session, Depends(get_deb)]):
        team = session.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team    
    
#Update
@app.patch("/teams/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, team: TeamUpdate, session: Annotated[Session, Depends(get_deb)]):
        team_to_update = session.get(Team, team_id)
        if not team_to_update:
            raise HTTPException(status_code=404, detail="Team not found")
        team_data = team.dict(exclude_unset=True)

        for key, value in team_data.items():
            setattr(team_to_update, key, value)
        session.add(team_to_update)
        session.commit()
        session.refresh(team_to_update)
        return team_to_update

#Delete
@app.delete("/teams/{team_id}")
def delete_team(team_id: int, session: Annotated[Session, Depends(get_deb)]):
        team = session.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        session.delete(team)
        session.commit()
        return {"message": "Team deleted successfully"}        