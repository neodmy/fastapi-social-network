from typing import Optional
from random import randrange

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

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
    return {"data": my_posts}


@app.get("/posts/{id}")
def get_post(id: int):
    found_post = find_post(id)
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return {"data": found_post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 10000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    new_post = update_one_post(id, post.dict())
    return {"data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    delete_one_post(post_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
