"""
Translation module using LARA MCP Server.
"""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import requests
from config import MCP_SERVER_URL, SOURCE_LANGUAGE, TARGET_LANGUAGE


class LARATranslator:
    """Handles translation using LARA MCP Server."""
    
    def __init__(self, server_url: str = None, access_key_id: str = None, access_key_secret: str = None):
        self.server_url = server_url or MCP_SERVER_URL
        self.access_key_id = access_key_id or os.getenv("LARA_ACCESS_KEY_ID")
        self.access_key_secret = access_key_secret or os.getenv("LARA_ACCESS_KEY_SECRET")
        self.session = requests.Session()
        
        # Validate credentials and set up session
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Set up credentials and validate them."""
        # Try to get credentials from multiple sources
        if not self.access_key_id:
            self.access_key_id = os.getenv("LARA_ACCESS_KEY_ID")
        if not self.access_key_secret:
            self.access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET")
        
        # Check if credentials are properly configured
        if self.access_key_id and self.access_key_secret:
            # Validate credential format (basic checks)
            if len(self.access_key_id.strip()) > 0 and len(self.access_key_secret.strip()) > 0:
                self.session.headers.update({
                    'x-lara-access-key-id': self.access_key_id.strip(),
                    'x-lara-access-key-secret': self.access_key_secret.strip(),
                    'Content-Type': 'application/json'
                })
                self._credentials_valid = True
            else:
                self._credentials_valid = False
                print("Warning: LARA access credentials are empty or whitespace-only")
        else:
            self._credentials_valid = False
            missing_creds = []
            if not self.access_key_id:
                missing_creds.append("LARA_ACCESS_KEY_ID")
            if not self.access_key_secret:
                missing_creds.append("LARA_ACCESS_KEY_SECRET")
            print(f"Warning: LARA access credentials not configured. Missing: {', '.join(missing_creds)}")
    
    def _check_credentials(self) -> bool:
        """Check if credentials are valid and available."""
        if not self._credentials_valid:
            return False
        
        # Additional validation: check if credentials are not just placeholder values
        if (self.access_key_id == "<YOUR_ACCESS_KEY_ID>" or 
            self.access_key_secret == "<YOUR_ACCESS_KEY_SECRET>"):
            print("Warning: LARA access credentials appear to be placeholder values")
            return False
        
        return True
    
    def get_credential_status(self) -> Dict[str, any]:
        """Get detailed credential status information."""
        status = {
            'configured': self._credentials_valid,
            'access_key_id_present': bool(self.access_key_id),
            'access_key_secret_present': bool(self.access_key_secret),
            'server_url': self.server_url,
            'headers_configured': 'x-lara-access-key-id' in self.session.headers
        }
        
        if self._credentials_valid:
            status['credential_quality'] = 'valid'
        elif self.access_key_id and self.access_key_secret:
            status['credential_quality'] = 'invalid_format'
        else:
            status['credential_quality'] = 'missing'
        
        return status
    
    def test_connection(self) -> bool:
        """Test connection to the LARA MCP server."""
        # First check if credentials are valid
        if not self._check_credentials():
            print("Cannot test connection: LARA credentials are not properly configured")
            return False
        
        try:
            # LARA MCP server health check endpoint
            response = self.session.get(f"{self.server_url}/health")
            if response.status_code == 200:
                print("✅ LARA MCP server connection successful")
                return True
            else:
                print(f"❌ LARA MCP server health check failed with status {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = None) -> Optional[str]:
        """Translate a single text string using LARA MCP server."""
        # Check credentials first
        if not self._check_credentials():
            raise ValueError("Cannot translate: LARA credentials are not properly configured")
        
        source_lang = source_lang or SOURCE_LANGUAGE
        target_lang = target_lang or TARGET_LANGUAGE
        
        # LARA MCP server translation endpoint
        payload = {
            "text": text,
            "source_language": source_lang,
            "target_language": target_lang
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/translate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('translated_text', text)
                print(f"✅ Translation successful: '{text}' → '{translated_text}'")
                return translated_text
            else:
                print(f"❌ Translation failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Translation request failed: {e}")
            return None
    
    def translate_batch(self, texts: List[str], source_lang: str = None, target_lang: str = None) -> List[Optional[str]]:
        """Translate a batch of texts using LARA MCP server."""
        # Check credentials first
        if not self._check_credentials():
            raise ValueError("Cannot translate: LARA credentials are not properly configured")
        
        source_lang = source_lang or SOURCE_LANGUAGE
        target_lang = target_lang or TARGET_LANGUAGE
        
        # LARA MCP server batch translation endpoint
        payload = {
            "texts": texts,
            "source_language": source_lang,
            "target_language": target_lang
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/translate_batch",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_texts = result.get('translated_texts', texts)
                print(f"✅ Batch translation successful: {len(texts)} texts translated")
                return translated_texts
            else:
                print(f"❌ Batch translation failed with status {response.status_code}: {response.text}")
                # Fallback to individual translations
                return [self.translate_text(text, source_lang, target_lang) for text in texts]
                
        except requests.RequestException as e:
            print(f"❌ Batch translation request failed: {e}")
            # Fallback to individual translations
            return [self.translate_text(text, source_lang, target_lang) for text in texts]
    
    def translate_subtitle_file(self, subtitle_path: Path, output_path: Path = None) -> Optional[Path]:
        """Translate an entire subtitle file."""
        if not subtitle_path.exists():
            print(f"Subtitle file not found: {subtitle_path}")
            return None
        
        # Read subtitle file
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(subtitle_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"Could not read subtitle file with any encoding: {subtitle_path}")
                return None
        
        # Parse SRT format and extract text
        subtitle_blocks = self._parse_srt(content)
        if not subtitle_blocks:
            print(f"No subtitle blocks found in {subtitle_path}")
            return None
        
        # Extract text for translation
        texts_to_translate = [block['text'] for block in subtitle_blocks]
        
        print(f"Translating {len(texts_to_translate)} subtitle blocks...")
        
        # Translate texts
        translated_texts = self.translate_batch(texts_to_translate)
        
        # Create translated subtitle content
        translated_content = self._create_translated_srt(subtitle_blocks, translated_texts)
        
        # Write translated subtitle file
        if output_path is None:
            output_path = subtitle_path.parent / f"{subtitle_path.stem}_translated.srt"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"Translated subtitle saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error writing translated subtitle: {e}")
            return None
    
    def _parse_srt(self, content: str) -> List[Dict]:
        """Parse SRT content and extract subtitle blocks."""
        blocks = []
        lines = content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check if this is a subtitle number
            if line.isdigit():
                # Parse subtitle block
                try:
                    # Subtitle number
                    number = int(line)
                    i += 1
                    
                    # Timestamp line
                    if i < len(lines):
                        timestamp = lines[i].strip()
                        i += 1
                    else:
                        break
                    
                    # Text lines
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    if text_lines:
                        blocks.append({
                            'number': number,
                            'timestamp': timestamp,
                            'text': ' '.join(text_lines)
                        })
                    
                except (ValueError, IndexError):
                    i += 1
                    continue
            else:
                i += 1
        
        return blocks
    
    def _create_translated_srt(self, original_blocks: List[Dict], translated_texts: List[str]) -> str:
        """Create SRT content from original blocks and translated texts."""
        if len(original_blocks) != len(translated_texts):
            print("Warning: Number of original blocks doesn't match translated texts")
            return ""
        
        srt_content = []
        
        for i, block in enumerate(original_blocks):
            srt_content.append(str(block['number']))
            srt_content.append(block['timestamp'])
            srt_content.append(translated_texts[i] if translated_texts[i] else block['text'])
            srt_content.append('')  # Empty line between blocks
        
        return '\n'.join(srt_content)
    
    def reload_credentials(self):
        """Reload credentials from environment variables."""
        print("🔄 Reloading LARA credentials...")
        self.access_key_id = os.getenv("LARA_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET")
        self._setup_credentials()
        
        if self._credentials_valid:
            print("✅ Credentials reloaded successfully")
        else:
            print("❌ Failed to reload valid credentials")
        
        return self._credentials_valid


def main():
    """Main function for testing translation."""
    print("🔍 LARA MCP Server Translator Test")
    print("=" * 50)
    
    translator = LARATranslator()
    
    # Show credential status
    status = translator.get_credential_status()
    print(f"\n📋 Credential Status:")
    print(f"   Configured: {status['configured']}")
    print(f"   Access Key ID: {'✅ Present' if status['access_key_id_present'] else '❌ Missing'}")
    print(f"   Access Key Secret: {'✅ Present' if status['access_key_secret_present'] else '❌ Missing'}")
    print(f"   Server URL: {status['server_url']}")
    print(f"   Headers Configured: {status['headers_configured']}")
    print(f"   Quality: {status['credential_quality']}")
    
    if not status['configured']:
        print("\n❌ Credentials not properly configured!")
        print("Please check your .env file and ensure:")
        print("   - LARA_ACCESS_KEY_ID is set")
        print("   - LARA_ACCESS_KEY_SECRET is set")
        print("   - Values are not empty or placeholder text")
        return
    
    # Test connection
    print(f"\n🔗 Testing connection to {status['server_url']}...")
    if translator.test_connection():
        print("✅ Successfully connected to LARA MCP Server")
        
        # Test single translation
        test_text = "Hello, how are you?"
        print(f"\n🌐 Testing single translation: '{test_text}'")
        try:
            translated = translator.translate_text(test_text)
            if translated:
                print(f"✅ Translation successful: '{test_text}' → '{translated}'")
            else:
                print("❌ Translation failed")
        except Exception as e:
            print(f"❌ Translation error: {e}")
        
        # Test batch translation
        test_texts = ["Good morning", "Good afternoon", "Good evening"]
        print(f"\n🌐 Testing batch translation: {test_texts}")
        try:
            translated_texts = translator.translate_batch(test_texts)
            if translated_texts:
                print(f"✅ Batch translation successful: {translated_texts}")
            else:
                print("❌ Batch translation failed")
        except Exception as e:
            print(f"❌ Batch translation error: {e}")
        
    else:
        print("❌ Failed to connect to LARA MCP Server")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Verify your .env file exists and has correct values")
        print("   2. Check that LARA_ACCESS_KEY_ID and LARA_ACCESS_KEY_SECRET are not empty")
        print("   3. Ensure the server URL is correct")
        print("   4. Try running 'python translator.py' to test the module directly")


if __name__ == "__main__":
    main()
