from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import config


Base = declarative_base()

class Category(Base): # this is a model
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    #seed the database with some categories

class Unsorted(Base): # this is a model
    __tablename__ = 'unsorted'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)

class Sorted(Base): #this is a model
    __tablename__ = 'sorted'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship("Category", backref="sorted_notifications")
    importance_level = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    notification_id = Column(Integer, ForeignKey('unsorted.id'))
    notification = relationship(Unsorted, backref="sorted_notifications")

def setup_database(): # this function sets up the database
    """Sets up the database, creating tables based on defined models."""
    engine = create_engine(config.DATABASE_URI)
    Base.metadata.create_all(engine)
    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    
    if not session.query(Category).count():
        default_categories = ["General", "Work", "Personal", "Social", "Promotions", "Miscellaneous"]
        for category_name in default_categories:
            new_category = Category(name=category_name)
            session.add(new_category)
        session.commit()
        print("default categories added to the database.")
    
    session.close()
    print("Database setup completed.")

def drop_all(): # this function drops all tables
    """Drops all tables, cleaning the database."""
    engine = create_engine(config.DATABASE_URI)
    Base.metadata.drop_all(engine)
    print("Database dropped.")

if __name__ == "__main__":
    setup_database()