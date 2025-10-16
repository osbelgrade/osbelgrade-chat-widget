from flask import Flask, request, jsonify
import requests
import os
from bs4 import BeautifulSoup

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

SITE PAGES AVAILABLE:
- Home/Index: https://osbelgrade.mintlify.app/
- Quickstart: https://osbelgrade.mintlify.app/quickstart
- Development: https://osbelgrade.mintlify.app/development
- Chapters: core-functions, user-interface, background-processes, system-errors, version-history
- Essentials: images, audio, snippets, downloads
- AI Tools: zora, branding, share, claude-code, windsurf
- Admin: about, tools, wwtc, reticulate
- Changelog: https://osbelgrade.mintlify.app/changelog

The site is built with Mintlify and focuses on creating world-class documentation
with modern tools and workflows.
"""

SYSTEM_PROMPT = """You are Zora, a helpful AI assistant for OS:Belgrade documentation.

You have complete knowledge of the OS:Belgrade documentation site including:
- Project structure and setup
- Technical documentation formats
- User interface organization
- Background processes and API generation
- System requirements and troubleshooting
- Visual identity and branding options
- All available features and capabilities

IMPORTANT CAPABILITY:
When users ask about specific topics, pages, or content that you don't have detailed information about, you can fetch pages directly from the live site at https://osbelgrade.mintlify.app/

If a user asks about:
- Roadmap, version history, or future plans
- Specific features or tools mentioned in navigation
- Poems or frequently updated content
- Any page you're uncertain about

You should indicate in your response that you'll fetch the latest information. Use phrases like:
"Let me get you the latest information from that page..."

When users ask questions:
1. If you have the information, answer directly and accurately
2. If you need more details from a specific page, mention you're fetching current info
3. Be concise but thorough
4. Format responses in clean markdown with proper headings and bold text
5. Always be friendly and helpful

Keep responses friendly and practical. Focus on helping users succeed with their documentation."""

def fetch_page_content(url):
    """Fetch content from a specific OS:Belgrade page"""
    try:
        # Add user agent to avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, nav, footer
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get main content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        content = '\n'.join(lines)
        
        # Limit to reasonable size
        return content[:3000] if len(content) > 3000 else content
    
    except Exception as e:
        return f"Error fetching page: {str(e)}"

def enhance_prompt_with_live_content(user_message, base_prompt):
    """Detect if we need to fetch live content and add it to the prompt"""
    
    # Keywords that suggest we need live content
    fetch_triggers = [
        'roadmap', 'version', 'history', 'changelog', 'latest', 'current',
        'poem', 'poetry', 'zora', 'about', 'tools', 'wwtc', 'reticulate'
    ]
    
    # Check if message contains trigger words
    message_lower = user_message.lower()
    should_fetch = any(trigger in message_lower for trigger in fetch_triggers)
    
    enhanced_prompt = base_prompt
    
    if should_fetch:
        # Try to determine which page to fetch
        page_url = None
        
        if 'roadmap' in message_lower or 'version' in message_lower or 'history' in message_lower:
            page_url = 'https://osbelgrade.mintlify.app/chapters/version-history'
        elif 'changelog' in message_lower:
            page_url = 'https://osbelgrade.mintlify.app/changelog'
        elif 'quickstart' in message_lower or 'getting started' in message_lower:
            page_url = 'https://osbelgrade.mintlify.app/quickstart'
        elif 'zora' in message_lower and 'ai' in message_lower:
            page_url = 'https://osbelgrade.mintlify.app/ai-tools/zora'
        elif 'about' in message_lower:
            page_url = 'https://osbelgrade.mintlify.app/about'
        else:
            # Default to home page
            page_url = 'https://osbelgrade.mintlify.app/'
        
        # Fetch the content
        live_content = fetch_page_content(page_url)
        
        # Add to prompt
        enhanced_prompt += f"\n\nLATEST CONTENT FROM {page_url}:\n{live_content}\n\n"
    
    return enhanced_prompt

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
        
        # Build base prompt
        base_prompt = f"{SYSTEM_PROMPT}\n\n"
        base_prompt += f"DOCUMENTATION KNOWLEDGE:\n{SITE_KNOWLEDGE}\n\n"
        
        # Enhance with live content if needed
        full_prompt = enhance_prompt_with_live_content(user_message, base_prompt)
        
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
