from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from libcommon.utils import BASE_PATH, load_config


config_path = '{0}/model/config.cfg'.format(BASE_PATH)
DB_URL = load_config(config_path).db_url

Base = declarative_base()


def create_session():
    Engine = create_engine(DB_URL, echo=False)
    SessionMaker = sessionmaker(bind=Engine, autoflush=False)
    Session = scoped_session(SessionMaker)
    return Session
