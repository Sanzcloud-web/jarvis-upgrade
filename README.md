JARVIS is a French-first assistant that wraps OpenAI’s Chat Completions API, keeps running conversation context, and can automatically invoke an ecosystem of auto-discovered desktop tools to fulfill requests with minimal user prompts.
The chat interface boots in voice mode when possible, falls back to text gracefully, and exposes friendly console commands for managing the session.

Key Features
Conversational AI with tool automation – Intention analysis enriches each user prompt, enabling OpenAI to chain specialized tools (file I/O, editors, system commands, utilities, and more) without manual selection.

Voice-first experience – Speech recognition listens for the “jarvis” wake word, text-to-speech replies through pyttsx3 or OS fallbacks, and the assistant can keep the mic open for continuous hands-free exchanges.

Screen understanding – Built-in tooling captures the desktop, returns base64 payloads, and requests an OpenAI Vision follow-up so JARVIS can describe what’s on-screen or help with visible content.

File & directory automation – Create, edit, append, move, copy, search, and delete files or folders using structured tool schemas designed for predictable automation flows.

System productivity with safeguards – Execute commands behind a safety filter, inspect system metrics, open apps or URLs, list processes, and run smart file searches, all guarded by a security manager for risky operations.

Personalized greetings & tool tips – The CLI greets users based on local data, exposes contextual help, and offers quick tests to validate tool availability.

Architecture
Component	Responsibility
ChatInterface	Session loop, command parsing, voice/text routing, welcome UX.
OpenAIClient	API authentication, intent analysis, tool orchestration, and post-tool follow-ups for final answers.
ToolManager & auto-loader	Discovers tool classes across the codebase, maps function schemas, and executes tool calls with metadata.
Voice stack	VoiceManager wires the recognizer and synthesizer, SpeechRecognizer handles wake-word listening & response mode, TextToSpeech adapts to each OS with fallbacks.
System utilities	Platform detection, command adaptation, and dependency checks centralize OS-specific behavior.
Tool suites	File operations, directory tooling, screen vision, system commands, and other utilities expose structured schemas for the LLM to call.
Getting Started
Prerequisites
Python environment with the dependencies listed in requirements.txt (openai, python-dotenv, SpeechRecognition, pyttsx3, PyAudio, numpy, gTTS, keyboard, psutil, Pillow, pyautogui).

Microphone for voice mode, speakers for audio responses.

Environment variables
Create a .env file (or set environment variables) containing:

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini  # optional; defaults to gpt-4o-mini
These values are loaded at startup and validated before any API calls.

Installation
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
The dependency list is defined in requirements.txt.

Run the assistant
python main.py
main.py instantiates ChatInterface and starts the interactive loop.

Usage
Launch experience
On startup JARVIS attempts to initialize the voice stack automatically, greets you with personalized context, and explains how to switch between voice and text modes if audio isn’t available.

Core console commands
quit / exit – end the session.

clear – reset conversation history.

voice – toggle voice mode (retries initialization if needed).

test-voice – run the speech in/out diagnostic.

outils – list the discovered tool catalog.

outil <name> – inspect a specific tool schema.

test outils – run a curated tool smoke test suite.

recherche … or web: … – trigger quick informational queries.
Each command is parsed in process_command, with additional helper flows for voice interactions and search.

Voice control tips
Say “jarvis …” followed by your request; the recognizer strips the wake word before forwarding the instruction.

When JARVIS ends a reply with a question mark, response mode lets you answer immediately without repeating the wake word until the timeout lapses.

Press Ctrl+C to interrupt speech output or stop the background listener; the voice manager handles cleanup gracefully.

Tool catalog highlights
File operations: create, read, edit, append, copy, move, and delete files with directory overrides.

Directory operations: list contents, create/remove/copy folders, search recursively, and measure folder size.

System commands: execute guarded shell commands, gather CPU/memory/disk/process stats, open applications or URLs, and delegate smart file searches.

Screen vision: capture the screen, optionally save the file, and return data for OpenAI Vision follow-up analysis.
Use outils to browse categories or outil <name> to inspect parameters, descriptions, and requirements pulled from the auto-discovered schemas.

Tech Stack
Python application architecture with modular packages for chat control, tools, and voice services.

OpenAI API for language reasoning and optional screen analysis (chat + vision endpoints).

Voice technologies: SpeechRecognition + PyAudio for capture, pyttsx3 plus OS-native fallbacks for TTS, and optional gTTS/keyboard helpers from the dependency list.

Desktop automation & sensing: pyautogui and Pillow for screenshots, psutil for system metrics, numpy for data utilities, all wired into tool implementations.

Configuration & utilities: python-dotenv for secrets management and a platform-aware SystemDetector to adjust commands per operating system.
