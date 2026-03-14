from fastapi import Depends
from sqlmodel import Session, select
from db.sqlite import get_session, Observation

@router.post("/observation")
def add_observation(obs: Observation, session: Session = Depends(get_session)):
    session.add(obs)
    session.commit()
    session.refresh(obs)
    return obs