from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    image_url = Column(String, nullable=True)

# Pydantic schemas
class BlogPostBase(BaseModel):
    title: str
    content: str
    image_url: str | None = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostRead(BlogPostBase):
    id: int
    class Config:
        orm_mode = True

# CRUD operations
def get_blog_post(db: Session, post_id: int):
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()

def get_blog_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(BlogPost).offset(skip).limit(limit).all()

def create_blog_post(db: Session, blog_post: BlogPostCreate):
    db_blog_post = BlogPost(**blog_post.dict())
    db.add(db_blog_post)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

def update_blog_post(db: Session, post_id: int, updated_data: BlogPostBase):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if db_post:
        db_post.title = updated_data.title
        db_post.content = updated_data.content
        db_post.image_url = updated_data.image_url
        db.commit()
        db.refresh(db_post)
        return db_post
    return None

def delete_blog_post(db: Session, post_id: int):
    db_post = get_blog_post(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/blogposts/", response_model=BlogPostRead)
def create_blog_post_handler(blog_post: BlogPostCreate, db: Session = Depends(get_db)):
    return create_blog_post(db=db, blog_post=blog_post)

@app.get("/blogposts/", response_model=List[BlogPostRead])
def read_blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_blog_posts(db, skip=skip, limit=limit)

@app.get("/blogposts/{post_id}", response_model=BlogPostRead)
def read_blog_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_blog_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_post

@app.put("/blogposts/{post_id}", response_model=BlogPostRead)
def update_blog_post_handler(post_id: int, blog_post: BlogPostBase, db: Session = Depends(get_db)):
    updated_post = update_blog_post(db, post_id=post_id, updated_data=blog_post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return updated_post

@app.delete("/blogposts/{post_id}", response_model=bool)
def delete_blog_post_handler(post_id: int, db: Session = Depends(get_db)):
    success = delete_blog_post(db, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return success

# Initial database setup
Base.metadata.create_all(bind=engine)
