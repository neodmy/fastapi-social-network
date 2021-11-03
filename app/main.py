import os
from typing import Optional
from operator import itemgetter

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

from store.pg_store import PgStore

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favorite foods", "content": "I like pizzas", "id": 2}
]

store = PgStore(host=os.environ.get("DATABASE_HOST"),
                database=os.environ.get("DATABASE_NAME"),
                user=os.environ.get("DATABASE_USER"),
                password=os.environ.get("DATABASE_PASSWORD")) \
    .init_connection()
cursor, conn = itemgetter("cursor", "conn")(store)


def find_post(post_id):
    found_post = next((post for post in my_posts if post["id"] == post_id), None)
    return found_post


def find_post_idx(post_id):
    post_idx = next((idx for idx, post in enumerate(my_posts) if post["id"] == post_id), None)
    if post_idx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} was not found")
    return post_idx


def update_one_post(post_id, new_post):
    post_idx = find_post_idx(post_id)
    updated_post = {**{"id": post_id}, **new_post}
    my_posts[post_idx] = updated_post
    return updated_post


def delete_one_post(post_id):
    post_idx = find_post_idx(post_id)
    my_posts.pop(post_idx)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    found_post = cursor.fetchone()
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return {"data": found_post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()

    return {"data": new_post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    conn.commit()
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    deleted_post = cursor.fetchone()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
