"""
MCP Client module that uses OpenAI as an AI agent to communicate with LARA MCP Server.
"""
import os
import json
import time
from typing import List, Dict, Optional, Any
import openai
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import MCP_SERVER_URL, LARA_ACCESS_KEY_ID, LARA_ACCESS_KEY_SECRET


class MCPClient:
    """MCP Client that communicates directly with LARA MCP Server."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the MCP client."""
        # OpenAI API key is kept for potential future use but not required for MCP communication
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # LARA MCP Server configuration
        self.mcp_server_url = MCP_SERVER_URL
        self.access_key_id = LARA_ACCESS_KEY_ID
        self.access_key_secret = LARA_ACCESS_KEY_SECRET
        
        # Validate LARA credentials
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("LARA access credentials not configured. Check LARA_ACCESS_KEY_ID and LARA_ACCESS_KEY_SECRET in .env file.")
    
    def _create_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a properly formatted MCP request."""
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),  # Unique ID
            "method": method,
            "params": params or {}
        }
        return request
    
    def _send_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP request to LARA server using direct HTTP communication."""
        try:
            import requests
            
            # Set up headers for LARA authentication
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'x-lara-access-key-id': self.access_key_id,
                'x-lara-access-key-secret': self.access_key_secret
            }
            
            # Send the MCP request to the LARA server
            response = requests.post(
                self.mcp_server_url,
                json=request,
                headers=headers,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Handle Server-Sent Events (SSE) response
                response_text = response.text
                
                # Look for the last data line in SSE format
                lines = response_text.strip().split('\n')
                last_data_line = None
                
                for line in lines:
                    if line.startswith('data: '):
                        last_data_line = line[6:]  # Remove 'data: ' prefix
                
                if last_data_line:
                    try:
                        # Parse the JSON from the data line
                        return json.loads(last_data_line)
                    except json.JSONDecodeError:
                        return {"result": last_data_line, "raw_response": True}
                else:
                    # Fallback to regular JSON parsing
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"result": response_text, "raw_response": True}
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to send MCP request: {str(e)}"}
    
    def test_connection(self) -> bool:
        """Test connection to LARA MCP server."""
        try:
            # Try to get server info first
            request = self._create_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "VideoSubtitleProcessor",
                    "version": "1.0.0"
                }
            })
            response = self._send_mcp_request(request)
            
            if "error" not in response:
                print("✅ MCP connection test successful")
                return True
            else:
                print(f"❌ MCP connection test failed: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ MCP connection test error: {e}")
            return False
    
    def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "fr") -> Optional[str]:
        """Translate text using LARA MCP server."""
        try:
            # Try different MCP methods for translation
            methods_to_try = [
                ("tools/call", {
                    "name": "translate",
                    "arguments": {
                        "text": [{"text": text, "translatable": True}],  # Server expects array of objects with translatable field
                        "source": source_lang,
                        "target": target_lang
                    }
                }),
                ("tools/call", {
                    "name": "translate",
                    "arguments": {
                        "text": [{"text": text, "translatable": True}],  # Server expects array of objects with translatable field
                        "from": source_lang,
                        "to": target_lang
                    }
                }),
                ("tools/call", {
                    "name": "translate_text",
                    "arguments": {
                        "text": [{"text": text, "translatable": True}],  # Server expects array of objects with translatable field
                        "source": source_lang,
                        "target": target_lang
                    }
                })
            ]
            
            for method, params in methods_to_try:
                request = self._create_mcp_request(method, params)
                response = self._send_mcp_request(request)
                
                if "error" not in response:
                    # Extract translated text from response
                    if "result" in response:
                        if isinstance(response["result"], dict):
                            # Check for content field first
                            if "content" in response["result"]:
                                content = response["result"]["content"]
                                if isinstance(content, list) and len(content) > 0:
                                    # Extract text from content
                                    text_content = content[0].get("text", "")
                                    if text_content:
                                        # Try to parse JSON if it's a string
                                        try:
                                            import json
                                            parsed = json.loads(text_content)
                                            if isinstance(parsed, list) and len(parsed) > 0:
                                                translated_text = parsed[0].get("text", text)
                                                # Apply encoding fix for French characters
                                                return self._fix_french_encoding(translated_text)
                                        except json.JSONDecodeError:
                                            # If not JSON, return as is with encoding fix
                                            return self._fix_french_encoding(text_content)
                            
                            # Try different possible result field names
                            for field in ["translated_text", "translation", "result"]:
                                if field in response["result"]:
                                    translated_text = response["result"][field]
                                    print(f"🔧 DEBUG: Raw translation from server: '{translated_text}'")
                                    # Apply encoding fix for French characters
                                    fixed_text = self._fix_french_encoding(translated_text)
                                    print(f"🔧 DEBUG: Final translation after fix: '{fixed_text}'")
                                    return fixed_text
                        else:
                            translated_text = response["result"]
                            # Apply encoding fix for French characters
                            return self._fix_french_encoding(translated_text)
                    elif "content" in response:
                        translated_text = response["content"]
                        # Apply encoding fix for French characters
                        return self._fix_french_encoding(translated_text)
            
            # If all methods fail, return original text
            print(f"❌ Translation failed: No working method found")
            return text
                
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return text
    
    def translate_batch(self, texts: List[str], source_lang: str = "en", target_lang: str = "fr") -> List[Optional[str]]:
        """Translate multiple texts using LARA MCP server through OpenAI agent."""
        try:
            # Create MCP batch translation request
            request = self._create_mcp_request("translate_batch", {
                "texts": texts,
                "source_language": source_lang,
                "target_language": target_lang
            })
            
            response = self._send_mcp_request(request)
            
            if "error" in response:
                print(f"❌ Batch translation failed: {response['error']}")
                # Fallback to individual translations
                return [self.translate_text(text, source_lang, target_lang) for text in texts]
            
            # Extract translated texts from response
            if "result" in response:
                if isinstance(response["result"], dict):
                    return response["result"].get("translated_texts", texts)
                elif isinstance(response["result"], list):
                    return response["result"]
                else:
                    return texts
            else:
                return texts
                
        except Exception as e:
            print(f"❌ Batch translation error: {e}")
            # Fallback to individual translations
            return [self.translate_text(text, source_lang, target_lang) for text in texts]
    
    def translate_subtitle_file(self, subtitle_path: Path, target_lang: str = "fr") -> Optional[Path]:
        """Translate an entire subtitle file using LARA MCP server."""
        try:
            # Read subtitle file
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse SRT content and extract text
            subtitle_texts = self._extract_srt_texts(content)
            
            if not subtitle_texts:
                print(f"No subtitle text found in {subtitle_path}")
                return None
            
            # Translate all subtitle texts
            print(f"Translating {len(subtitle_texts)} subtitle entries...")
            translated_texts = self.translate_batch(subtitle_texts, target_lang=target_lang)
            
            if not translated_texts:
                print("Translation failed")
                return None
            
            # Create translated subtitle file
            translated_content = self._create_translated_srt(content, translated_texts)
            output_path = subtitle_path.parent / f"{subtitle_path.stem}_{target_lang}.srt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"✅ Translated subtitle saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Subtitle file translation error: {e}")
            return None
    
    def _extract_srt_texts(self, srt_content: str) -> List[str]:
        """Extract text content from SRT format."""
        texts = []
        lines = srt_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and timestamp lines
            if not line or line.isdigit() or '-->' in line:
                i += 1
                continue
            
            # This should be subtitle text
            texts.append(line)
            i += 1
        
        return texts
    
    def _create_translated_srt(self, original_content: str, translated_texts: List[str]) -> str:
        """Create translated SRT content with original timestamps."""
        lines = original_content.strip().split('\n')
        translated_lines = []
        text_index = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                translated_lines.append(line)
                i += 1
                continue
            
            if line.isdigit() or '-->' in line:
                # Keep timestamp and numbering
                translated_lines.append(line)
                i += 1
                continue
            
            # Replace subtitle text with translation
            if text_index < len(translated_texts) and translated_texts[text_index]:
                translated_lines.append(translated_texts[text_index])
                text_index += 1
            else:
                # Keep original if translation failed
                translated_lines.append(line)
                text_index += 1
            
            i += 1
        
        return '\n'.join(translated_lines)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the MCP client."""
        return {
            "openai_configured": bool(self.openai_api_key),
            "lara_configured": bool(self.access_key_id and self.access_key_secret),
            "mcp_server_url": self.mcp_server_url,
            "access_key_id_present": bool(self.access_key_id),
            "access_key_secret_present": bool(self.access_key_secret)
        }
    
    def get_credential_status(self) -> Dict[str, Any]:
        """Get detailed credential status information (compatibility method)."""
        status = self.get_status()
        # Add additional fields that the core processor expects
        status.update({
            'configured': status['lara_configured'],
            'credential_quality': 'valid' if status['lara_configured'] else 'missing',
            'headers_configured': True  # MCP client doesn't use HTTP headers
        })
        return status

    def translate_srt_content(self, srt_content: str, source_lang: str = "en", target_lang: str = "fr") -> str:
        """Translate SRT content while preserving timing and formatting."""
        try:
            # Parse SRT content into entries
            entries = self._parse_srt_entries(srt_content)
            
            if not entries:
                print("❌ No SRT entries found to translate")
                return srt_content
            
            print(f"📝 Found {len(entries)} SRT entries to translate")
            
            # Extract only the text content (without timing and formatting)
            text_entries = []
            for entry in entries:
                if 'text' in entry:
                    # Clean the text by removing HTML tags and extra whitespace
                    clean_text = self._clean_srt_text(entry['text'])
                    if clean_text.strip():
                        text_entries.append(clean_text)
            
            if not text_entries:
                print("❌ No translatable text found in SRT")
                return srt_content
            
            print(f"🌐 Translating {len(text_entries)} text entries in chunks...")
            
            # Translate in chunks with progress updates
            chunk_size = 20  # Process 20 entries at a time
            translated_texts = []
            
            for i in range(0, len(text_entries), chunk_size):
                chunk = text_entries[i:i + chunk_size]
                chunk_end = min(i + chunk_size, len(text_entries))
                
                print(f"  📦 Processing chunk {i//chunk_size + 1}/{(len(text_entries) + chunk_size - 1)//chunk_size} (entries {i+1}-{chunk_end})")
                
                # Translate this chunk
                for j, text in enumerate(chunk):
                    translated = self.translate_text(text, source_lang, target_lang)
                    if translated and translated != text:
                        # Apply encoding fix for French characters
                        fixed_translated = self._fix_french_encoding(translated)
                        translated_texts.append(fixed_translated)
                    else:
                        translated_texts.append(text)  # Keep original if translation failed
                
                # Small delay to avoid overwhelming the server
                import time
                time.sleep(0.1)
            
            print(f"✅ Translation completed! Processed {len(translated_texts)} entries")
            
            # Reconstruct SRT content with translated text
            return self._reconstruct_srt_with_translations(entries, translated_texts)
            
        except Exception as e:
            print(f"❌ SRT translation error: {e}")
            return srt_content
    
    def _fix_french_encoding(self, text: str) -> str:
        """Fix common French encoding issues."""
        if not text:
            return text
        
        # Debug: Log the original text and its bytes
        print(f"🔧 DEBUG: Fixing encoding for: '{text}'")
        print(f"🔧 DEBUG: Text bytes: {text.encode('utf-8')}")
        
        # Common encoding fixes for French characters
        encoding_fixes = {
            'Ã©': 'é',  # é
            'Ã¨': 'è',  # è
            'Ã ': 'à',  # à
            'Ã¢': 'â',  # â
            'Ãª': 'ê',  # ê
            'Ã®': 'î',  # î
            'Ã´': 'ô',  # ô
            'Ã¹': 'ù',  # ù
            'Ã»': 'û',  # û
            'Ã§': 'ç',  # ç
            'Ã«': 'ë',  # ë
            'Ã¯': 'ï',  # ï
            'Ã¶': 'ö',  # ö
            'Ã¼': 'ü',  # ü
            'Ã¦': 'æ',  # æ
            'Å"': 'œ',  # œ
            'Â«': '«',  # «
            'Â»': '»',  # »
            'Â°': '°',  # °
            'Â±': '±',  # ±
            'Â²': '²',  # ²
            'Â³': '³',  # ³
            'Â¼': '¼',  # ¼
            'Â½': '½',  # ½
            'Â¾': '¾',  # ¾
            'Â ': '',   # Remove standalone Â characters
            'Â?': '?',  # Fix Â followed by question mark
            'Â!': '!',  # Fix Â followed by exclamation
            'Â.': '.',  # Fix Â followed by period
            'Â,': ',',  # Fix Â followed by comma
        }
        
        # Apply fixes
        fixed_text = text
        for corrupted, correct in encoding_fixes.items():
            if corrupted in fixed_text:
                print(f"🔧 DEBUG: Replacing '{corrupted}' with '{correct}'")
                fixed_text = fixed_text.replace(corrupted, correct)
        
        # Additional fix: Remove any standalone Â character followed by punctuation
        import re
        # Pattern to match Â followed by any punctuation
        pattern = r'Â([?!.,:;])'
        if re.search(pattern, fixed_text):
            print(f"🔧 DEBUG: Found Â + punctuation pattern, applying regex fix")
            fixed_text = re.sub(pattern, r'\1', fixed_text)
        
        # Fix for specific UTF-8 encoding issue: Â + non-breaking space + punctuation
        # This handles the case where Â is followed by \xc2\xa0 (non-breaking space) and punctuation
        pattern2 = r'Â\s*([?!.,:;])'
        if re.search(pattern2, fixed_text):
            print(f"🔧 DEBUG: Found Â + whitespace + punctuation pattern, applying regex fix")
            fixed_text = re.sub(pattern2, r'\1', fixed_text)
        
        # Debug: Log the fixed text
        if fixed_text != text:
            print(f"🔧 DEBUG: Fixed text: '{fixed_text}'")
        else:
            print(f"🔧 DEBUG: No encoding issues found")
        
        return fixed_text
    
    def _parse_srt_entries(self, srt_content: str) -> List[Dict]:
        """Parse SRT content into structured entries."""
        entries = []
        lines = srt_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for entry number
            if line.isdigit():
                entry = {'number': line}
                i += 1
                
                # Get timing line
                if i < len(lines):
                    entry['timing'] = lines[i].strip()
                    i += 1
                
                # Get text lines until empty line or next number
                text_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    text_lines.append(lines[i].strip())
                    i += 1
                
                if text_lines:
                    entry['text'] = '\n'.join(text_lines)
                    entries.append(entry)
            
            i += 1
        
        return entries
    
    def _clean_srt_text(self, text: str) -> str:
        """Clean SRT text by removing HTML tags and extra formatting."""
        import re
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace and normalize
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _reconstruct_srt_with_translations(self, original_entries: List[Dict], translated_texts: List[str]) -> str:
        """Reconstruct SRT content with translated text while preserving original structure."""
        if len(original_entries) != len(translated_texts):
            print("⚠️ Warning: Entry count mismatch, using original content")
            return self._entries_to_srt(original_entries)
        
        # Create new entries with translated text
        new_entries = []
        for i, entry in enumerate(original_entries):
            new_entry = entry.copy()
            if 'text' in entry and i < len(translated_texts):
                # Replace text with translated version
                new_entry['text'] = translated_texts[i]
            new_entries.append(new_entry)
        
        return self._entries_to_srt(new_entries)
    
    def _entries_to_srt(self, entries: List[Dict]) -> str:
        """Convert entries back to SRT format."""
        srt_lines = []
        
        for entry in entries:
            srt_lines.append(entry['number'])
            srt_lines.append(entry['timing'])
            if 'text' in entry:
                srt_lines.append(entry['text'])
            srt_lines.append('')  # Empty line between entries
        
        return '\n'.join(srt_lines)


def main():
    """Test the MCP client."""
    print("🔍 Testing MCP Client with Direct HTTP Communication")
    print("=" * 50)
    
    try:
        # Initialize client
        client = MCPClient()
        
        # Show status
        status = client.get_status()
        print(f"\n📋 Client Status:")
        print(f"   OpenAI Configured: {'✅ Yes' if status['openai_configured'] else '❌ No'}")
        print(f"   LARA Configured: {'✅ Yes' if status['lara_configured'] else '❌ No'}")
        print(f"   MCP Server URL: {status['mcp_server_url']}")
        print(f"   Access Key ID: {'✅ Present' if status['access_key_id_present'] else '❌ Missing'}")
        print(f"   Access Key Secret: {'✅ Present' if status['access_key_secret_present'] else '❌ Missing'}")
        
        if not status['lara_configured']:
            print("\n❌ LARA credentials not configured!")
            print("Please check LARA_ACCESS_KEY_ID and LARA_ACCESS_KEY_SECRET in your .env file")
            return
        
        # Test connection
        print(f"\n🔗 Testing connection to LARA MCP server...")
        if client.test_connection():
            print("✅ Successfully connected to LARA MCP Server")
            
            # Test translation
            test_text = "Hello, how are you?"
            print(f"\n🌐 Testing translation: '{test_text}'")
            translated = client.translate_text(test_text)
            if translated:
                print(f"✅ Translation successful: '{test_text}' → '{translated}'")
            else:
                print("❌ Translation failed")
        else:
            print("❌ Failed to connect to LARA MCP Server")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
