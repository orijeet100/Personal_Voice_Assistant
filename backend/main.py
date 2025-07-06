# from fastapi import FastAPI, Request
# from openai import OpenAI
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import uvicorn
# import os
# import json
# from dotenv import load_dotenv
# import faiss
# from sentence_transformers import SentenceTransformer
# load_dotenv()
#
#
# from fastapi.middleware.cors import CORSMiddleware
#
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8080"],  # or use ["*"] for all during local dev
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# @app.get("/")
# async def root():
#     return {"message": "Server is running"}
#
#
# # Add a simple test endpoint
# @app.get("/api/test")
# async def test():
#     return {"message": "Backend is working!"}
#
#
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# print("Loaded OPENAI API Key:", os.getenv("OPENAI_API_KEY"))
#
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id="a22eeebff9b049f38d1f162665c76c99",
#     client_secret="5d9600661fe14c4387c37fb84fbe9f1f",
#     redirect_uri="http://127.0.0.1:8888/callback",
#     scope="user-library-read user-read-playback-state user-modify-playback-state"
# ))
#
# ## No Indexing just playing top 50
# # @app.post("/api/play-request")
# # async def play_from_message(req: Request):
# #     try:
# #         data = await req.json()
# #         user_msg = data["message"]
# #         print("✅ Message received from frontend:", user_msg)
# #
# #         liked = sp.current_user_saved_tracks(limit=20)
# #         devices = sp.devices().get("devices", [])
# #
# #         # Create index-based song list
# #         songs = liked["items"]
# #         indexed_songs = [f"{i}: {t['track']['name']} - {t['track']['artists'][0]['name']}" for i, t in enumerate(songs)]
# #
# #         device_names = [d["name"] for d in devices]
# #
# #         prompt = f"""
# # You are a music assistant. Based on the user's message, select one of their liked songs by index and a device to play it on.
# #
# # User Message: "{user_msg}"
# #
# # Liked Songs (Index: Song - Artist):
# # {json.dumps(indexed_songs, indent=2)}
# #
# # Available Devices: {device_names}
# #
# # Respond ONLY in this JSON format:
# # {{
# #   "song_index": <index_of_selected_song>,
# #   "device": "<exact device name>"
# # }}
# #         """
# #
# #         response = client.chat.completions.create(
# #             model="gpt-3.5-turbo",
# #             messages=[{"role": "user", "content": prompt}],
# #             temperature=0.3
# #         )
# #
# #         result = json.loads(response.choices[0].message.content)
# #
# #         song_index = result.get("song_index")
# #         device_name = result.get("device")
# #
# #         # Validate song_index
# #         if not isinstance(song_index, int) or song_index < 0 or song_index >= len(songs):
# #             return {"status": "error", "message": "Invalid song index provided by assistant."}
# #
# #         device_id = next((d["id"] for d in devices if d["name"].lower() == device_name.lower()), None)
# #         track_uri = songs[song_index]["track"]["uri"]
# #
# #         if device_id and track_uri:
# #             track_info = songs[song_index]['track']
# #             song_name = track_info['name']
# #             artist_name = track_info['artists'][0]['name']
# #             sp.start_playback(device_id=device_id, uris=[track_uri])
# #             return {
# #                 "status": "success",
# #                 "message": f"🎵 Now playing: '{song_name}' by {artist_name}"
# #             }
# #         else:
# #             return {"status": "error", "message": "Could not match song or device"}
# #
# #     except Exception as e:
# #         print(f"❌ Error in play_from_message: {e}")
# #         return {"status": "error", "message": str(e)}
#
#
# # Load FAISS index and metadata
# faiss_index = faiss.read_index("liked_songs_faiss.index")
# with open("liked_songs_metadata.json", "r", encoding="utf-8") as f:
#     all_tracks = json.load(f)
#
# # Sentence transformer model for queries
# model = SentenceTransformer("all-MiniLM-L6-v2")
# @app.post("/api/query")
# async def play_from_message(req: Request):
#     try:
#         data = await req.json()
#         user_msg = data["message"].strip()
#
#         # Step 1: Encode user message and search top 20 matches
#         query_emb = model.encode([user_msg])
#         D, I = faiss_index.search(query_emb, k=20)
#
#         matched_tracks = [all_tracks[i] for i in I[0] if i != -1]
#         song_descriptions = [f"{t['name']} by {t['artist']}" for t in matched_tracks]
#
#
#         # Step 2: Get device list
#         devices = sp.devices().get("devices", [])
#         device_names = [d["name"] for d in devices]
#
#         # Step 3: Create prompt for GPT
#         prompt = f"""
# You are a helpful music assistant. Based on the user's request, choose the most relevant song and the correct device.
#
# User Message: "{user_msg}"
#
# Matched Songs:
# {json.dumps(song_descriptions, indent=2)}
#
# Available Devices: {device_names}
#
# Respond ONLY in this JSON format:
# {{
#   "track_name": "<exact song name>",
#   "artist_name": "<exact artist name>",
#   "device": "<exact device name>"
# }}
#         """.strip()
#
#         print("\n📨 Prompt sent to GPT:")
#         print(prompt)
#
#         # Step 4: Send prompt to GPT
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3
#         )
#         result = json.loads(response.choices[0].message.content)
#
#         track_name = result.get("track_name", "").strip()
#         artist_name = result.get("artist_name", "").strip()
#         device_name = result.get("device", "").strip()
#
#         print(f"\n🎯 GPT selected: '{track_name}' by {artist_name} on {device_name}")
#
#         # Step 5: Match to actual URI/device
#         track_uri = next(
#             (t["uri"] for t in matched_tracks if
#              t["name"].lower() == track_name.lower() and
#              t["artist"].lower() == artist_name.lower()), None
#         )
#         device_id = next((d["id"] for d in devices if d["name"].lower() == device_name.lower()), None)
#
#         if device_id and track_uri:
#             sp.start_playback(device_id=device_id, uris=[track_uri])
#             return {
#                 "status": "success",
#                 "message": f"🎵 Now playing: '{track_name}' by {artist_name}",
#                 "top_matches": [
#                     {
#                         "rank": rank + 1,
#                         "name": track["name"],
#                         "artist": track["artist"],
#                         "distance": float(dist)
#                     }
#                     for rank, (track, dist) in enumerate(zip(matched_tracks, D[0]))
#                 ]
#             }
#         else:
#             print("❌ Failed to match song URI or device.")
#             return {"status": "error", "message": "Could not match the track or device."}
#
#     except Exception as e:
#         print(f"❌ Error in play_from_message: {e}")
#         return {"status": "error", "message": str(e)}
#
#
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="debug")

from fastapi import FastAPI, Request
from crewai import Agent, Crew, Task
from dotenv import load_dotenv
import os
import json
import uvicorn
from agents.intent_agent import classify_intent
from agents.email_agent import handle_email_intent
from agents.spotify_agent import play_song_from_query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()



app = FastAPI()


# ✅ More permissive CORS setup for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Include both formats
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/query")
async def orchestrate(req: Request):
    data = await req.json()
    user_msg = data.get("message", "")
    print("🎯 Received:", user_msg)

    # Step 1: Determine Intent
    intent = classify_intent(user_msg)
    print("🤖 Detected Intent:", intent)

    # Step 2: Route to appropriate agent
    if intent == "email":
        result = handle_email_intent(user_msg)
    elif intent == "music":
        result = play_song_from_query(user_msg)
    else:
        result = {"status": "error", "message": "Unknown intent."}

    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="debug")