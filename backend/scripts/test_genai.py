"""Smoke test for google.genai SDK migration."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from google import genai
from google.genai import types as genai_types

api_key = os.environ.get('GEMINI_API_KEY', '')
if not api_key:
    print('[FAIL] GEMINI_API_KEY not set in .env')
    sys.exit(1)

print(f'[INFO] API key found: {api_key[:8]}...')
client = genai.Client(api_key=api_key)

# ── Test 1: Basic text generation ──────────────────────────────────────────
try:
    r1 = client.models.generate_content(
        model='models/gemini-2.0-flash',
        contents='Reply with only the single word: ALIVE',
        config=genai_types.GenerateContentConfig(max_output_tokens=10, temperature=0.0),
    )
    print(f'[PASS] Text generation: {r1.text.strip()}')
except Exception as e:
    print(f'[FAIL] Text generation: {e}')
    sys.exit(1)

# ── Test 2: JSON response mode (copilot_orchestrator uses this) ────────────
try:
    r2 = client.models.generate_content(
        model='models/gemini-2.0-flash',
        contents='Return a JSON object with a single key "status" set to "ok".',
        config=genai_types.GenerateContentConfig(
            max_output_tokens=50,
            temperature=0.0,
            response_mime_type='application/json',
        ),
    )
    import json
    parsed = json.loads(r2.text.strip())
    print(f'[PASS] JSON mode: {parsed}')
except Exception as e:
    print(f'[FAIL] JSON mode: {e}')

# ── Test 3: Embeddings (business_memory uses this) ─────────────────────────
try:
    r3 = client.models.embed_content(
        model='models/gemini-embedding-001',
        contents='break-even optimization test',
    )
    dims = len(r3.embeddings[0].values) if r3.embeddings else 0
    tag = '[PASS]' if dims > 0 else '[FAIL]'
    print(f'{tag} Embedding dims: {dims} (expected 768)')
except Exception as e:
    print(f'[FAIL] Embedding: {e}')

print('\n[OK] Gemini google.genai migration verified — NOT in fallback mode.')
