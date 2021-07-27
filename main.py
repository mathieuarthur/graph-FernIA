import os
import graphene
import jwt
from graphene.types.field import Field
from graphene.types.objecttype import ObjectType
from graphene.types.scalars import Boolean, ID, Int, String
from graphene.types.structures import List
from pymongo import MongoClient
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "https://localhost",
    "https://localhost:8080",
    "https://localhost:80",
    "http://localhost:8080",
    "http://localhost:80"
]

CONNECTION_STRING = os.environ.get("DBSTRING")

client = MongoClient(CONNECTION_STRING)

db = client["Saucisse"]

us = db["users"]

img = db["images"]

class User(ObjectType):
    _id = ID()
    username = String()
    isAdmin = Boolean()
    password = String()
    isSuspended = Boolean()

class Image(ObjectType):
    _id = ID()
    userId = String()
    image = String()
    vote = Int()

class Query(ObjectType):
    
    users = List(User)

    def resolve_users(self, info):
        query = list(us.find())
        return query

    user = Field(User, username = String(required = True))

    def resolve_user(self, info, username):
        query = us.find_one({"username": username})
        return query

    login = String(username = String(required = True), password = String(required = True))

    def resolve_login(self, info, username, password):
        key = os.environ.get("key")

        query = us.find_one({"username": username})
        suspended = query.get("isSuspended")

        if(password == query.get("password")):
            if(not suspended):
                encoded_jwt = jwt.encode({"username": username}, key, algorithm="HS256")
                return encoded_jwt
            else:
                return "Account suspended"
        else:
            return "Password not valid"
    
    images = List(Image)

    def resolve_images(self, info):
        query = list(img.find())
        return query
    
    imagesUser = List(Image, username = String(required = True))

    def resolve_imagesUser(self, info, username):
        userId = us.find_one({"username": username})
        userId = userId.get("_id")
        query = img.find({"userId": userId})
        return query
    
class Mutation(ObjectType):
    
    addImage = Field(Image, username = String(required = True), image = String(required = True))

    def resolve_addImage(self, info, username, image):
        userId = us.find_one({"username": username})
        userId = userId.get("_id")
        query = img.insert_one({"image": image, "userId": userId})
        return query
    
    register = Field(User, username = String(required = True), password = String(required = True), isAdmin = Boolean(default_value = False), isSuspended = Boolean(default_value = False))

    def resolve_register(self, info, username, password, isAdmin, isSuspended):
        query = us.insert_one({"username": username, "password": password, "isAdmin": isAdmin, "isSuspended": isSuspended})
        return query

    deleteUser = Field(User, username = String(required = True))

    def resolve_deleteUser(self, info, username):
        query = us.delete_one({"username": username})
        return query

    updateSuspend = Field(User, username = String(required = True), isSuspended = Boolean(required = True))

    def resolve_updateSuspend(self, info, username, isSuspended):
        query = us.find_one_and_update({"username": username}, {"$set": {"isSuspended": isSuspended}})
        return query

    vote = Field(Image, vote = String(required = True), imageId = ID(required = True))

    def resolve_vote(self, info, vote, imageId):
        voteCount = img.find_one({"_id": imageId})
        voteCount = voteCount.get("vote")

        if (vote == "up"):
            voteCount += 1
            img.find_one_and_update({"_id": imageId}, {"$set": {"vote": voteCount}})
            return "upvote"

        elif (vote == "down"):
            voteCount -= 1
            img.find_one_and_update({"_id": imageId}, {"$set": {"vote": voteCount}})
            return "downvote"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/api", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))