from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')

SITE_KNOWLEDGE = """
OS:Belgrade Documentation Site - Complete Knowledge Base

PROJECT STRUCTURE:
- Project Concept: Documentation site setup and quickstart guide
- Technical Documentation Formats: Edit docs locally with real-time preview
- Core Functions: Customize design and colors to match your brand
- User Interface: Organize docs for better user navigation
- Background Processes: Auto-generate API docs from OpenAPI specs

MAIN SECTIONS:
1. SYSTEM ERRORS & PATCHES
2. VISUAL IDENTITY & BRANDING
3. SYSTEM REQUIREMENTS
4. POSTMODERN ELEMENTS
5. OUTPUT FUNCTIONALITY

KEY FEATURES:
- MDX support, code samples, images, reusable snippets
- OpenAPI specification integration
- Real-time preview, customizable design
"""

SYSTEM_PROMPT = """You are a helpful assistant for OS:Belgrade documentation. Provide specific, accurate information based on the documentation. Be concise but thorough."""

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('conversationHistory', [])
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nDOCUMENTATION KNOWLEDGE:\n{SITE_KNOWLEDGE}\n\n"
        
        if conversation_history:
            full_prompt += "CONVERSATION HISTORY:\n"
            for msg in conversation_history[-6:]:
                full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
            full_prompt += "\n"
        
        full_prompt += f"USER QUESTION: {user_message}\n\nProvide a helpful response."
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-5-20250929',
                'max_tokens': 1500,
                'messages': [{'role': 'user', 'content': full_prompt}]
            },
            timeout=30
        )
        
        return jsonify(response.json()), 200, {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {
            'Access-Control-Allow-Origin': '*'
        }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
