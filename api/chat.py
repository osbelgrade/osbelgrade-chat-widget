from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get API key from environment variable
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
   - Use MDX to style documentation pages
   - Add sample code demonstrations
   - Display images and other media
   - Write once and reuse across docs with snippets

3. SYSTEM REQUIREMENTS
   - Installation Guides
   - Error Messages
   - Troubleshooting
   - Warranty Disclaimers
   - Technical Support

4. POSTMODERN ELEMENTS
   - The Unread Manual Paradox
   - Field Studies
   - Output Functionality

5. OUTPUT FUNCTIONALITY
   - Primary Publication
   - Supplementary Materials
   - WWTC Integration
   - Timeline Flexibility

KEY FEATURES:
- MDX support for styling documentation pages
- Code sample demonstrations
- Image and media display capabilities
- Reusable snippets across documentation
- OpenAPI specification integration
- Real-time preview during editing
- Customizable design and branding
- Navigation organization tools

The site is built with Mintlify and focuses on creating world-class documentation
with modern tools and workflows.
"""

SYSTEM_PROMPT = """You are a helpful assistant for OS:Belgrade documentation.

You have complete knowledge of the OS:Belgrade documentation site including:
- Project structure and setup
- Technical documentation formats
- User interface organization
- Background processes and API generation
- System requirements and troubleshooting
- Visual identity and branding options
- All available features and capabilities

When users ask questions:
1. Provide specific, accurate information based on the documentation
2. Reference relevant sections and pages when helpful
3. Be concise but thorough
4. If something isn't in your knowledge base, say so honestly
5. Suggest related topics that might be helpful
6. Format your responses in clean markdown without excessive asterisks or special characters
7. Use proper headings (##) and bold text (**text**) for emphasis when appropriate

Keep responses friendly and practical. Focus on helping users succeed with their documentation."""

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle CORS preflight
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
        
        # Build prompt with context
        full_prompt = f"{SYSTEM_PROMPT}\n\n"
        full_prompt += f"DOCUMENTATION KNOWLEDGE:\n{SITE_KNOWLEDGE}\n\n"
        
        if conversation_history:
            full_prompt += "CONVERSATION HISTORY:\n"
            recent = conversation_history[-6:]
            for msg in recent:
                full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
            full_prompt += "\n"
        
        full_prompt += f"USER QUESTION: {user_message}\n\n"
        full_prompt += "Provide a helpful, accurate response based on the documentation knowledge above."
        
        # Call Claude API
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
                'messages': [{
                    'role': 'user',
                    'content': full_prompt
                }]
            },
            timeout=30
        )
        
        result = response.json()
        
        return jsonify(result), 200, {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500, {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }

# For Vercel serverless
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
