import json
import os
from dotenv import load_dotenv
load_dotenv()
import faiss
import spotipy
from openai import OpenAI
from spotipy.oauth2 import SpotifyOAuth
from sentence_transformers import SentenceTransformer




def play_song_from_query(user_msg: str):
    # Load FAISS index and song metadata
    faiss_index = faiss.read_index("liked_songs_faiss.index")
    with open("liked_songs_metadata.json", "r", encoding="utf-8") as f:
        all_tracks = json.load(f)

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # OpenAI + Spotify Setup
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="a22eeebff9b049f38d1f162665c76c99",
        client_secret="5d9600661fe14c4387c37fb84fbe9f1f",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-library-read user-read-playback-state user-modify-playback-state"
    ))

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    user_msg = user_msg.strip()

    # Step 1: Semantic search
    query_emb = model.encode([user_msg])
    D, I = faiss_index.search(query_emb, k=20)
    matched_tracks = [all_tracks[i] for i in I[0] if i != -1]
    song_descriptions = [f"{t['name']} by {t['artist']}" for t in matched_tracks]

    print("\n🎯 Top matches:")
    for rank, (track, dist) in enumerate(zip(matched_tracks, D[0])):
        print(f"{rank+1}. {track['name']} by {track['artist']} (dist: {dist:.4f})")

    # Step 2: Get device info
    devices = sp.devices().get("devices", [])
    device_names = [d["name"] for d in devices]

    # Step 3: Construct prompt
    prompt = f"""
You are a helpful music assistant. Based on the user's request, choose the most relevant song and the correct device.

User Message: "{user_msg}"

Matched Songs:
{json.dumps(song_descriptions, indent=2)}

Available Devices: {device_names}

Respond ONLY in this JSON format:
{{
"track_name": "<exact song name>",
"artist_name": "<exact artist name>",
"device": "<exact device name>"
}}
    """.strip()

    # Step 4: GPT response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    result = json.loads(response.choices[0].message.content)

    track_name = result.get("track_name", "").strip()
    artist_name = result.get("artist_name", "").strip()
    device_name = result.get("device", "").strip()

    print(f"\n🎵 GPT selected: {track_name} by {artist_name} on {device_name}")

    # Step 5: Match URI and play
    track_uri = next(
        (t["uri"] for t in matched_tracks if
         t["name"].lower() == track_name.lower() and
         t["artist"].lower() == artist_name.lower()), None
    )
    device_id = next((d["id"] for d in devices if d["name"].lower() == device_name.lower()), None)

    if device_id and track_uri:
        sp.start_playback(device_id=device_id, uris=[track_uri])
        return {
            "status": "success",
            "message": f"🎵 Now playing: '{track_name}' by {artist_name}",
            "top_matches": [
                {
                    "rank": rank + 1,
                    "name": track["name"],
                    "artist": track["artist"],
                    "distance": float(dist)
                }
                for rank, (track, dist) in enumerate(zip(matched_tracks, D[0]))
            ]
        }
    else:
        return {"status": "error", "message": "Could not match the track or device."}
