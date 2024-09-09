from fastapi.testclient import TestClient
from blog_app import app, get_db, Base, engine
from sqlalchemy.orm import sessionmaker

# Create a new test database session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_blog.db"
test_engine = engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_blog_post():
    response = client.post("/blogposts/", json={"title": "Test Post", "content": "Test Content"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"
    assert "id" in data

def test_read_blog_posts():
    response = client.get("/blogposts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_blog_post():
    # create a post first
    post_response = client.post("/blogposts/", json={"title": "New Post", "content": "Content"})
    post_id = post_response.json()["id"]
    response = client.get(f"/blogposts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Post"
    assert data["content"] == "Content"

def test_update_blog_post():
    # create a post first
    post_response = client.post("/blogposts/", json={"title": "Another Post", "content": "Content"})
    post_id = post_response.json()["id"]
    response = client.put(f"/blogposts/{post_id}", json={"title": "Updated Post", "content": "Updated Content"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Post"
    assert data["content"] == "Updated Content"

def test_delete_blog_post():
    # create a post first
    post_response = client.post("/blogposts/", json={"title": "Post to Delete", "content": "Content"})
    post_id = post_response.json()["id"]
    response = client.delete(f"/blogposts/{post_id}")
    assert response.status_code == 200
    assert response.json() == True
    # verify it's deleted
    response = client.get(f"/blogposts/{post_id}")
    assert response.status_code == 404
