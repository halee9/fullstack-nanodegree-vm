from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies import Base, Shelter, Puppy

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# 1. Query all of the puppies and return the results in ascending alphabetical order
puppies = session.query(Puppy).order_by(Puppy.name).all()

# 2. Query all of the puppies that are less than 6 months old organized by the youngest first
puppies = session.query(Puppy).filter(Puppy.dateOfBirth > '2015-04-01').order_by(Puppy.dateOfBirth.desc()).all()

# 3. Query all puppies by ascending weight
puppies = session.query(Puppy).order_by(Puppy.weight).all()

# 4. Query all puppies grouped by the shelter in which they are staying
puppies = session.query(Puppy).order_by(Puppy.shelter_id).all()
for puppy in puppies:
    print puppy.shelter.name, puppy.name
