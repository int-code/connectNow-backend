from database import Base, engine
import models

# Create all tables in the database
Base.metadata.create_all(bind=engine)