"""Claude AI service for content validation and summarization."""

import logging
import json
from typing import Dict, Any, List
from anthropic import Anthropic
from flask import current_app

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Anthropic Claude API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or current_app.config.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.timeout = current_app.config.get('LLM_REQUEST_TIMEOUT', 60)

    def validate_content(self, content: str, title: str = None) -> Dict[str, Any]:
        """Validate content for inappropriate material using Claude."""
        try:
            logger.info("Starting content validation with Claude")
            
            if not content or len(content.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Content is empty or invalid'
                }

            # Prepare validation prompt
            validation_prompt = self._create_validation_prompt(content, title)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": validation_prompt
                }]
            )

            # Parse validation results
            result_text = response.content[0].text.strip()
            validation_result = self._parse_validation_response(result_text)
            
            # Determine if content is accepted
            checks = validation_result.get('checks', {})
            is_accepted = all(not check for check in checks.values())
            
            # Get rejection reason if any
            rejection_reasons = [key.replace('_', ' ') for key, value in checks.items() if value]
            reason = 'Content passed all validation checks' if is_accepted else f'Content contains: {", ".join(rejection_reasons)}'
            
            logger.info(f"Content validation completed. Accepted: {is_accepted}")
            
            return {
                'success': True,
                'accepted': is_accepted,
                'checks': checks,
                'reason': reason,
                'confidence': validation_result.get('confidence', 'medium')
            }

        except Exception as e:
            logger.error(f"Error validating content with Claude: {str(e)}")
            return {
                'success': False,
                'error': f'Content validation failed: {str(e)}'
            }

    def generate_summary(self, content: str, title: str = None) -> Dict[str, Any]:
        """Generate a summary of the content using Claude."""
        try:
            logger.info("Starting summary generation with Claude")
            
            if not content or len(content.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Content is empty or invalid'
                }

            # Prepare summarization prompt
            summary_prompt = self._create_summarization_prompt(content, title)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": summary_prompt
                }]
            )

            summary_text = response.content[0].text.strip()
            
            # Clean up the summary
            summary_text = self._clean_summary(summary_text)
            
            word_count = len(summary_text.split())
            
            logger.info(f"Summary generated successfully. Word count: {word_count}")
            
            return {
                'success': True,
                'summary': summary_text,
                'wordCount': word_count,
                'generatedAt': self._get_current_timestamp()
            }

        except Exception as e:
            logger.error(f"Error generating summary with Claude: {str(e)}")
            return {
                'success': False,
                'error': f'Summary generation failed: {str(e)}'
            }

    def _create_validation_prompt(self, content: str, title: str = None) -> str:
        """Create prompt for content validation."""
        prompt = f"""
You are a content moderation expert. Please analyze the following content and determine if it contains any inappropriate material.

{"Title: " + title if title else ""}

Content to analyze:
{content[:5000]}{'...' if len(content) > 5000 else ''}

Please evaluate the content for the following categories and respond in JSON format:

{{
    "checks": {{
        "pornography": boolean (true if content contains explicit sexual content),
        "profanity": boolean (true if content contains excessive profanity or vulgar language),
        "hate_speech": boolean (true if content promotes hatred toward specific groups),
        "discrimination": boolean (true if content promotes discrimination),
        "racism": boolean (true if content contains racist language or ideology),
        "political_bias": boolean (true if content shows extreme political bias or propaganda)
    }},
    "confidence": "high|medium|low",
    "notes": "Brief explanation of findings"
}}

Be thorough but not overly strict. Educational content discussing these topics should generally be allowed unless explicitly promoting harmful behavior.
"""
        return prompt

    def _create_summarization_prompt(self, content: str, title: str = None) -> str:
        """Create prompt for content summarization."""
        prompt = f"""
Please create a clear, concise summary of the following content. The summary should:

1. Capture the main points and key information
2. Be accessible and easy to understand
3. Be appropriate for American Sign Language (ASL) translation
4. Use clear, simple language without jargon
5. Be approximately 100-200 words

{"Title: " + title if title else ""}

Content to summarize:
{content[:8000]}{'...' if len(content) > 8000 else ''}

Please provide only the summary text without any additional commentary or formatting.
"""
        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's validation response into structured data."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # Fallback parsing if JSON extraction fails
            logger.warning("Could not extract JSON from validation response, using fallback")
            return self._fallback_parse_validation(response_text)
        
        except json.JSONDecodeError:
            logger.warning("Failed to parse validation JSON, using fallback")
            return self._fallback_parse_validation(response_text)

    def _fallback_parse_validation(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for validation response."""
        # Default safe checks (assume content is clean unless explicitly flagged)
        checks = {
            'pornography': False,
            'profanity': False,
            'hate_speech': False,
            'discrimination': False,
            'racism': False,
            'political_bias': False
        }
        
        # Look for explicit flags in the response
        response_lower = response_text.lower()
        
        if any(word in response_lower for word in ['pornography', 'explicit sexual', 'sexual content']):
            checks['pornography'] = True
        
        if any(word in response_lower for word in ['profanity', 'vulgar', 'excessive swearing']):
            checks['profanity'] = True
            
        if any(word in response_lower for word in ['hate speech', 'hatred', 'promoting hate']):
            checks['hate_speech'] = True
            
        if any(word in response_lower for word in ['discrimination', 'discriminatory']):
            checks['discrimination'] = True
            
        if any(word in response_lower for word in ['racism', 'racist', 'racial']):
            checks['racism'] = True
            
        if any(word in response_lower for word in ['political bias', 'propaganda', 'extreme bias']):
            checks['political_bias'] = True
        
        return {
            'checks': checks,
            'confidence': 'medium',
            'notes': 'Parsed from text response'
        }

    def _clean_summary(self, summary: str) -> str:
        """Clean and format the summary text."""
        # Remove any markdown formatting or extra whitespace
        import re
        
        # Remove markdown-style formatting
        summary = re.sub(r'\*\*(.*?)\*\*', r'\1', summary)  # Bold
        summary = re.sub(r'\*(.*?)\*', r'\1', summary)      # Italic
        summary = re.sub(r'`(.*?)`', r'\1', summary)        # Code
        
        # Clean up whitespace
        summary = re.sub(r'\s+', ' ', summary)
        summary = summary.strip()
        
        # Remove common prefixes that Claude might add
        prefixes_to_remove = [
            'Here is a summary:',
            'Summary:',
            'Here\'s a summary:',
            'The summary is:',
            'Here is the summary:'
        ]
        
        for prefix in prefixes_to_remove:
            if summary.lower().startswith(prefix.lower()):
                summary = summary[len(prefix):].strip()
        
        return summary

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    def test_connection(self) -> bool:
        """Test the Claude API connection."""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": "Hello"
                }]
            )
            return True
        except Exception as e:
            logger.error(f"Claude API connection test failed: {str(e)}")
            return False