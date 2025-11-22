from pymongo import MongoClient

MONGO_URI = "mongodb+srv://aiadmin:airoom123@cluster0.jcyujwi.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client["AIRoom"]
candidates = db["Candidates"]

print("✅ MongoDB connected")
