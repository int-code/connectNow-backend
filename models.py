from database import Base
from sqlalchemy import Column, Integer,VARCHAR, TEXT, TIMESTAMP, text, BOOLEAN

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  name = Column(VARCHAR, nullable=True)
  email = Column(VARCHAR, nullable=False)
  password = Column(VARCHAR, nullable=False)
  bio = Column(TEXT, nullable=True)
  profile_pic = Column(VARCHAR, nullable=True)
  profile_pic_path = Column(VARCHAR, nullable=True)
  username = Column(VARCHAR, nullable = False)
  created_at = Column(TIMESTAMP(timezone=False), server_default=text('now()'))


class Skill(Base):
  __tablename__ = 'skill'
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  name = Column(VARCHAR, nullable=False)

class Project(Base):
  __tablename__ = 'project'
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  admin_id = Column(Integer, nullable=False)
  name = Column(VARCHAR, nullable=False)
  description = Column(TEXT, nullable=True)
  pic_url = Column(VARCHAR, nullable=True)
  pic_path = Column(VARCHAR, nullable=True)
  status = Column(VARCHAR, nullable=False)
  created_at = Column(TIMESTAMP(timezone=False), server_default=text('now()'))


class UserSkill(Base):
  __tablename__ = 'user_Skill'
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  user_id = Column(Integer, nullable=False)
  skill_id = Column(Integer, nullable=False)

class ProjectSkill(Base):
  __tablename__ = 'project_Skill'
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  project_id = Column(Integer, nullable=False)
  skill_id = Column(Integer, nullable=False)

class Members(Base):
  __tablename__ = "project_members"
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  project_id = Column(Integer, nullable=False)
  user_id = Column(Integer, nullable=False)
  role = Column(VARCHAR, nullable=False)
  joined_at = Column(TIMESTAMP(timezone=False), server_default=text('now()'))


class Interest(Base):
  __tablename__ = "interest"
  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  project_id = Column(Integer, nullable=False)
  user_id = Column(Integer, nullable=False)
  status = Column(VARCHAR, nullable=False)

class Verification(Base):
  __tablename__ = "verification"

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  email = Column(VARCHAR, nullable=False)
  code = Column(VARCHAR, nullable=False)
  used = Column(BOOLEAN, nullable=False)
  created_at = Column(TIMESTAMP(timezone=False), server_default=text('now()'))

class UsernameOnHold(Base):
  __tablename__ = "username_on_hold"

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  username = Column(VARCHAR, nullable=False)