from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
)
from datetime import datetime

Base = declarative_base()


class GithubProject(Base):
    __tablename__ = "github_projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    url = Column(String(500))
    category = Column(String(100))
    description = Column(Text)
    stars = Column(Integer)
    forks = Column(Integer)
    score = Column(Float)
    ai_score = Column(Float)
    tech_tags = Column(Text)
    readme_summary = Column(Text)
    updated = Column(DateTime, default=datetime.now)


class StarHistory(Base):
    __tablename__ = "star_history"

    id = Column(Integer, primary_key=True)
    project = Column(String(200))
    stars = Column(Integer)
    record_time = Column(DateTime, default=datetime.now)


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    url = Column(String(500))
    summary = Column(Text)
    created = Column(DateTime, default=datetime.now)


class TrendingRepo(Base):
    __tablename__ = "trending_repos"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    url = Column(String(500))
    description = Column(Text)
    language = Column(String(100))
    stars = Column(Integer)
    stars_today = Column(Integer)
    since = Column(String(20))
    record_time = Column(DateTime, default=datetime.now)
