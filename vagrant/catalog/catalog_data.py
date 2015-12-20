from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db import Category, Base, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
user = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user)
session.commit()

# a category for catalog
category1 = Category(user_id=1, name="Golf")
session.add(category1)
session.commit()

# two items in the category
item1 = Item(user_id=1, name="Golf Club Set",
             image_path="golf_set.jpg",
             description="A Full Set With A Great Combination Of Distance and \
             Forgiveness Right Out Of The Box. Offers the performance men want \
             for their game and an eye-catching look that suits their style. \
             This set comes with 12 pieces (9 clubs, 2 headcovers, and 1 bag).",
             category=category1)
session.add(item1)
session.commit()

item1 = Item(user_id=1, name="Putter",
             image_path="putter.jpg",
             description="The putter features a precise white finish which \
             stands out when the putter is in the address position on the green.\
              This contrast of the white color against the green grass really \
              helps maintain focus on the alignment lines that help ensure that \
              your putter is on target at start.",
             category=category1)
session.add(item1)
session.commit()

# a category for catalog
category1 = Category(user_id=1, name="Tennis")
session.add(category1)
session.commit()

# two items in the category
item1 = Item(user_id=1, name="Tennis Balls",
             image_path="tennis_ball.jpg",
             description="Pressureless Balls Never Go Dead. Ideal for practice \
             and throwing machines. The bounce is true and always the same. \
             Made with real felt.",
             category=category1)
session.add(item1)
session.commit()

item1 = Item(user_id=1, name="Willson Racquet",
             image_path="racquet.jpg",
             description="Wilson is the Official Ball of the US Open and \
             partner of the USTA. The US Open 19 inch Junior Tennis Racket is \
             approved for 10 and Under Tennis and is extremely lightweight and \
             easy to swing",
             category=category1)
session.add(item1)
session.commit()

# print all categories and items
categories = session.query(Category).all()
for category in categories:
    print category.name

items = session.query(Item).all()
for item in items:
    print item.name

print "Added catalog items!"
