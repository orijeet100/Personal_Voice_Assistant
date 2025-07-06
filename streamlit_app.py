import streamlit as st
from st_audiorec import st_audiorec
from openai import OpenAI
import tempfile
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Spotify config
spotify_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
sp = spotipy.Spotify(auth=spotify_token)

st.title("🎙️ Voice Assistant: Spotify + Whisper")

if "history" not in st.session_state:
    st.session_state.history = []

# Record
st.markdown("#### Click below to record")
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format="audio/wav")

    # Save temp audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "rb") as file:
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )
            user_text = transcript.text
            st.success(f"🗣️ You said: {user_text}")

            # Remove temp file
            # os.remove(tmpfile_path)

            # Append to history
            st.session_state.history.append({"user": user_text})

            # Route command to Spotify agent
            if "play" in user_text.lower():
                song_name = user_text.lower().replace("play", "").strip()

                # Search Liked Songs (workaround since Liked Songs API is limited)
                results = sp.current_user_saved_tracks(limit=5)
                found = False
                for item in results["items"]:
                    track = item["track"]
                    if song_name.lower() in track["name"].lower():
                        sp.start_playback(uris=[track["uri"]])
                        assistant_reply = f"🎵 Playing **{track['name']}** from your Liked Songs!"
                        found = True
                        break
                if not found:
                    assistant_reply = f"❌ Couldn’t find **{song_name}** in your liked songs."
            else:
                assistant_reply = "🤖 I'm only trained to play songs from your Liked Songs for now!"

            # Append assistant reply
            st.session_state.history[-1]["assistant"] = assistant_reply

        except Exception as e:
            st.error(f"Transcription failed: {e}")

st.markdown("---")
st.markdown("### 💬 Conversation History")

for msg in st.session_state.history[-5:][::-1]:
    st.markdown(f"**🧑 You:** {msg['user']}")
    if 'assistant' in msg:
        st.markdown(f"**🤖 Assistant:** {msg['assistant']}")
    else:
        st.markdown(f"**🤖 Assistant:** _No response generated._")

