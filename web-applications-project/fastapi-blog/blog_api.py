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
    """SQLAlchemy ORM model representing a blog post in the database.

    Attributes:
        id (int): Auto-incremented primary key.
        title (str): Title of the blog post, indexed for fast lookup.
        content (str): Full text body of the blog post.
        image_url (str | None): Optional URL pointing to a cover image.
    """

    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    image_url = Column(String, nullable=True)

# Pydantic schemas
class BlogPostBase(BaseModel):
    """Shared fields used by both request and response schemas."""

    title: str
    content: str
    image_url: str | None = None

class BlogPostCreate(BlogPostBase):
    """Schema for creating a new blog post (inherits all fields from BlogPostBase)."""
    pass

class BlogPostRead(BlogPostBase):
    """Schema for reading a blog post, including the database-assigned ``id``."""

    id: int
    class Config:
        orm_mode = True

# CRUD operations
def get_blog_post(db: Session, post_id: int):
    """Retrieve a single blog post by its primary key.

    Args:
        db (Session): Active SQLAlchemy database session.
        post_id (int): Primary key of the blog post to retrieve.

    Returns:
        BlogPost | None: The matching ORM instance, or ``None`` if not found.
    """
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()

def get_blog_posts(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of blog posts.

    Args:
        db (Session): Active SQLAlchemy database session.
        skip (int): Number of records to skip (offset). Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 100.

    Returns:
        list[BlogPost]: List of ORM instances for the requested page.
    """
    return db.query(BlogPost).offset(skip).limit(limit).all()

def create_blog_post(db: Session, blog_post: BlogPostCreate):
    """Persist a new blog post to the database.

    Args:
        db (Session): Active SQLAlchemy database session.
        blog_post (BlogPostCreate): Validated data for the new post.

    Returns:
        BlogPost: The newly created ORM instance, including its generated ``id``.
    """
    db_blog_post = BlogPost(**blog_post.dict())
    db.add(db_blog_post)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

def update_blog_post(db: Session, post_id: int, updated_data: BlogPostBase):
    """Update an existing blog post with new field values.

    Args:
        db (Session): Active SQLAlchemy database session.
        post_id (int): Primary key of the blog post to update.
        updated_data (BlogPostBase): New field values to apply.

    Returns:
        BlogPost | None: The updated ORM instance, or ``None`` if the post
        was not found.
    """
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
    """Delete a blog post from the database.

    Args:
        db (Session): Active SQLAlchemy database session.
        post_id (int): Primary key of the blog post to delete.

    Returns:
        bool: ``True`` if the post was found and deleted, ``False`` otherwise.
    """
    db_post = get_blog_post(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False

# FastAPI app
app = FastAPI()

def get_db():
    """Yield a database session and ensure it is closed after the request.

    Intended for use as a FastAPI dependency via ``Depends(get_db)``.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/blogposts/", response_model=BlogPostRead)
def create_blog_post_handler(blog_post: BlogPostCreate, db: Session = Depends(get_db)):
    """Create a new blog post.

    Args:
        blog_post (BlogPostCreate): Validated request body containing the new
            post's title, content, and optional image URL.
        db (Session): Injected database session.

    Returns:
        BlogPostRead: The created blog post including its generated ``id``.
    """
    return create_blog_post(db=db, blog_post=blog_post)

@app.get("/blogposts/", response_model=List[BlogPostRead])
def read_blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of all blog posts.

    Args:
        skip (int): Number of posts to skip. Defaults to 0.
        limit (int): Maximum number of posts to return. Defaults to 100.
        db (Session): Injected database session.

    Returns:
        list[BlogPostRead]: List of blog posts for the requested page.
    """
    return get_blog_posts(db, skip=skip, limit=limit)

@app.get("/blogposts/{post_id}", response_model=BlogPostRead)
def read_blog_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a single blog post by ID.

    Args:
        post_id (int): Primary key of the post to retrieve.
        db (Session): Injected database session.

    Returns:
        BlogPostRead: The requested blog post.

    Raises:
        HTTPException: 404 if no post with the given ID exists.
    """
    db_post = get_blog_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_post

@app.put("/blogposts/{post_id}", response_model=BlogPostRead)
def update_blog_post_handler(post_id: int, blog_post: BlogPostBase, db: Session = Depends(get_db)):
    """Update an existing blog post.

    Args:
        post_id (int): Primary key of the post to update.
        blog_post (BlogPostBase): New field values for the post.
        db (Session): Injected database session.

    Returns:
        BlogPostRead: The updated blog post.

    Raises:
        HTTPException: 404 if no post with the given ID exists.
    """
    updated_post = update_blog_post(db, post_id=post_id, updated_data=blog_post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return updated_post

@app.delete("/blogposts/{post_id}", response_model=bool)
def delete_blog_post_handler(post_id: int, db: Session = Depends(get_db)):
    """Delete a blog post by ID.

    Args:
        post_id (int): Primary key of the post to delete.
        db (Session): Injected database session.

    Returns:
        bool: ``True`` on successful deletion.

    Raises:
        HTTPException: 404 if no post with the given ID exists.
    """
    success = delete_blog_post(db, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return success

# Initial database setup
Base.metadata.create_all(bind=engine)
