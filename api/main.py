from multiprocessing import synchronize
from random import randrange
import time
from xmlrpc.client import boolean
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import session
from  . import models
from .database import SessionLocal, engine, get_db
#from sqlalchemy import Boolean


models.Base.metadata.create_all(bind=engine)

app = FastAPI()





# Post references the Basemodel to
# provide data type check and validate them
class Post(BaseModel):
    title: str
    content: str
    published:boolean = True

# connect to postgres library
while True:
    try:
        conn = psycopg2.connect(host="localhost",database="fastAPI",
        user="postgres",password="Thisme", cursor_factory=RealDictCursor)

        cursor = conn.cursor()
        print(":: DATABASE CONNECTION SUCCESSFUL")
        break

    except Exception as error:
        print("::Connection to database failed::".upper())
        print("Error : ",error)
        time.sleep(2)
myPosts = [
    {"title": "MicroServices", "content": "web architecture", "id": 1},
    {"title": "Infrastructure", "content": "Cloud services", "id": 2},
    {"title": "Data Structures", "content": "importance of DS", "id": 3},
    {"title": "Complexities of Algo", "content": "Analyze Algorithms", "id": 4},
    {
        "title": "CRUD Apps",
        "content": "How to design decentralized CRUD app",
        "published": False,
        "id": 5,
    },
    {
        "title": "Mobile Apps",
        "content": "How to CRUD android app",
        "published": False,
        "id": 6,
    },
    {"title":"Jetpack Compose",
     "content":"Design Complex androd UIs with jetpack compose by writing composable objects"}
]


# def findPost(id: int):
#     for update_idx, post in enumerate(myPosts):
#         if post["id"] == int(id):
#             print(f"id is:{id}")

#             return update_idx, post

def findPost(id:int):
    for post in myPosts:
        if post["id"] == int(id):
            print(f"id is:{id}")
            return post

def findPostupdate_Idx(id: int):
    for i, p in enumerate(myPosts):
        if p["id"] == int(id):
            return i





@app.get("/home")
async def root():
    return {"mssg", "data"}

@app.get("/sqlalchemy")
def test_posts(db: session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{"status":posts}



@app.get("/posts")
def getPosts(db: session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()
    # conn.commit()
    post = db.query(models.Post).all()
    #print(posts)
    return {"mssg": post}


@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def createPosts(post: Post, db:session = Depends(get_db)):
    # using psycopg2 to create a new post in the database.
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s,%s,%s) RETURNING * """
    # , (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # ------------------------

    # using ORM to create new post
    newPost = models.Post(**post.dict)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)

    # post = post.dict()
    # post["id"] = randrange(0, 100)
    # myPosts.append(post)

    # extract publish status
    # print(post.published)
    return {"mssg": newPost}

@app.get("/posts/latest")
def getLatestPost():
    return {"data": myPosts[-1]}
    # return {"data": myPosts[len(myPosts)-1]}


@app.get("/posts/{id}")
def getPost(id: int, db: session = Depends(get_db)):  # , response:Response):
    # using psycopg2 to query the postgres database
    # cursor.execute("""SELECT * FROM posts""")
    # cursor.execute("""SELECT * FROM posts WHERE id = {} """.format(id))
    # post = cursor.fetchone()

    # conn.commit()

    # Using ORM to query postgres DB
    post = db.query(models.Post).filter(models.Post.id == id).first()

    #post = findPost(id)
    #print(post)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} not FOUND !!!!",
        )
        # response.status_code = HTTPException
        # return {"message":f"post with id {id} not Found !!!"}
    # print(post)
    return {"post detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(id: int, db:session = Depends(get_db)):
# using psycopg2 to delete a post from the database

    # cursor.execute(""" DELETE FROM posts WHERE id = {} RETURNING * """.format(id))
    # post_idx = cursor.fetchone()
    # conn.commit()
# using ORM to delete a post
    post_idx = db.query(models.Post).filter(models.Post.id == id).first()
    #update_idx = findPostupdate_Idx(id)
    if post_idx == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} doesn't exit",
        )
    post_idx.delete(synchronize_session=False)
    db.commit()

   # myPosts.pop(update_idx)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # return {"mssg": f"post with id {id} successfully deleted!!"}

@app.put("/posts/{id}")
def putPost(id:int, post:Post):
    cursor.execute("""UPDATE posts SET title = %s,
                content = %s, 
                published = %s  WHERE id = %s RETURNING *
                """,(post.title, post.content, post.published,str(id)))
    update_idx = cursor.fetchone()
    conn.commit()

    #update_idx = findPostupdate_Idx(id)
    if update_idx == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} doesn't exit",
        )
    #postDict = post.dict()
    #postDict["id"] = id
    #myPosts[update_idx] = postDict
    return{"mssg":update_idx}