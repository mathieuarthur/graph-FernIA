import graphene
import jwt
from graphene.types.field import Field
from graphene.types.objecttype import ObjectType
from graphene.types.scalars import Boolean, ID, String
from graphene.types.structures import List
from pymongo import MongoClient
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

CONNECTION_STRING = "mongodb+srv://LeMecWeird:aled123@cluster0.nyyus.mongodb.net/Saucisse"

client = MongoClient(CONNECTION_STRING)

db = client["Saucisse"]

us = db["users"]

img = db["images"]

class User(ObjectType):
    _id = ID()
    username = String()
    isAdmin = Boolean()
    password = String()

class Image(ObjectType):
    _id = ID()
    userId = String()
    image = String()

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
        key = "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"

        query = us.find_one({"username": username})

        if(password == query.get("password")):
            encoded_jwt = jwt.encode({"username": username}, key, algorithm="HS256")
            return encoded_jwt
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
    
    register = Field(User, username = String(required = True), password = String(required = True), isAdmin = Boolean(default_value = False))

    def resolve_register(self, info, username, password, isAdmin):
        query = us.insert_one({"username": username, "password": password, "isAdmin": isAdmin})
        return query

app = FastAPI()

app.add_route("/api", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))