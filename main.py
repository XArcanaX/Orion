import os
import signal
from dotenv import load_dotenv
from tools import client_tools

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

load_dotenv()

agent_id = os.getenv("AGENT_ID")
if agent_id is None or agent_id.strip() == "":
    raise ValueError("AGENT_ID n'est pas défini dans l'environnement (.env).")

api_key = os.getenv("ELEVENLABS_API_KEY")  # peut rester None si l'agent est public

elevenlabs = ElevenLabs(api_key=api_key)

conversation = Conversation(
    elevenlabs,
    agent_id,
    client_tools=client_tools,
    requires_auth=bool(api_key),
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=lambda response: print(f"Agent: {response}"),
    callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
)

# Démarre la session (sans user_id pour rester compatible avec toutes les versions)
conversation.start_session()

signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

conversation_id = conversation.wait_for_session_end()
print(f"Conversation ID: {conversation_id}")
