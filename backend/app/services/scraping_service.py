"""Web scraping services for news articles and YouTube videos."""

import re
import logging
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class ScrapingService:
    """Service for scraping content from URLs."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract content from a URL (article or YouTube video)."""
        try:
            logger.info(f"Starting content extraction from URL: {url}")
            
            if self._is_youtube_url(url):
                return self._extract_youtube_content(url)
            else:
                return self._extract_article_content(url)
        
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to extract content: {str(e)}'
            }

    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube video."""
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
        parsed_url = urlparse(url)
        return parsed_url.netloc.lower() in youtube_domains

    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try parsing as youtu.be short URL
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        
        return None

    def _extract_youtube_content(self, url: str) -> Dict[str, Any]:
        """Extract content from YouTube video."""
        try:
            video_id = self._extract_youtube_video_id(url)
            if not video_id:
                return {
                    'success': False,
                    'error': 'Could not extract video ID from YouTube URL'
                }

            logger.info(f"Extracting YouTube video content for ID: {video_id}")

            # Get video metadata
            metadata = self._get_youtube_metadata(url)
            
            # Get transcript
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
                transcript = ' '.join([item['text'] for item in transcript_list])
                
                if not transcript.strip():
                    return {
                        'success': False,
                        'error': 'No transcript available for this video'
                    }
                
            except Exception as e:
                logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
                return {
                    'success': False,
                    'error': 'Transcript not available for this video'
                }

            return {
                'success': True,
                'type': 'video',
                'title': metadata.get('title', 'YouTube Video'),
                'transcript': transcript,
                'duration': metadata.get('duration'),
                'thumbnail': metadata.get('thumbnail'),
                'url': url,
                'video_id': video_id
            }

        except Exception as e:
            logger.error(f"Error extracting YouTube content: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to extract YouTube content: {str(e)}'
            }

    def _get_youtube_metadata(self, url: str) -> Dict[str, Any]:
        """Get YouTube video metadata from page HTML."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('meta', property='og:title')
            if title_tag:
                title = title_tag.get('content')
            else:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().replace(' - YouTube', '')
            
            # Extract thumbnail
            thumbnail = None
            thumbnail_tag = soup.find('meta', property='og:image')
            if thumbnail_tag:
                thumbnail = thumbnail_tag.get('content')
            
            # Extract duration (basic)
            duration = None
            duration_meta = soup.find('meta', {'itemprop': 'duration'})
            if duration_meta:
                duration = duration_meta.get('content')
            
            return {
                'title': title or 'YouTube Video',
                'thumbnail': thumbnail,
                'duration': duration
            }
            
        except Exception as e:
            logger.warning(f"Could not extract YouTube metadata: {str(e)}")
            return {'title': 'YouTube Video'}

    def _extract_article_content(self, url: str) -> Dict[str, Any]:
        """Extract content from news article or web page."""
        try:
            logger.info(f"Extracting article content from: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()

            # Extract title
            title = self._extract_article_title(soup)
            
            # Extract main content
            content = self._extract_article_text(soup)
            
            if not content.strip():
                return {
                    'success': False,
                    'error': 'No readable content found in the article'
                }
            
            # Extract metadata
            author = self._extract_author(soup)
            publish_date = self._extract_publish_date(soup)
            
            return {
                'success': True,
                'type': 'article',
                'title': title,
                'content': content,
                'author': author,
                'publishDate': publish_date,
                'url': url
            }

        except Exception as e:
            logger.error(f"Error extracting article content: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to extract article content: {str(e)}'
            }

    def _extract_article_title(self, soup: BeautifulSoup) -> str:
        """Extract article title from HTML."""
        # Try multiple title extraction methods
        title_selectors = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            if attrs.get('property') or attrs.get('name'):
                element = soup.find(tag, attrs)
                if element and element.get('content'):
                    return element.get('content').strip()
            else:
                element = soup.find(tag)
                if element:
                    return element.get_text().strip()
        
        return 'Article'

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content from article."""
        # Content extraction strategies
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.article-body',
            '.post-content',
            '.entry-content',
            'main',
            '#content',
            '.story-body'
        ]
        
        # Try specific content containers first
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = self._clean_text(' '.join([elem.get_text() for elem in elements]))
                if len(text) > 200:  # Ensure substantial content
                    return text
        
        # Fallback: extract all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = self._clean_text(' '.join([p.get_text() for p in paragraphs]))
            if len(text) > 200:
                return text
        
        # Last resort: get all text from body
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return ''

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        author_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'article:author'}),
            ('.author', {}),
            ('.byline', {}),
            ('[rel="author"]', {})
        ]
        
        for selector, attrs in author_selectors:
            if selector.startswith('.') or selector.startswith('['):
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            else:
                element = soup.find(selector, attrs)
                if element:
                    content = element.get('content')
                    if content:
                        return content.strip()
        
        return None

    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article publish date."""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'name': 'date'}),
            ('time', {'datetime': True})
        ]
        
        for selector, attrs in date_selectors:
            element = soup.find(selector, attrs)
            if element:
                if element.name == 'time' and element.get('datetime'):
                    return element.get('datetime')
                elif element.get('content'):
                    return element.get('content')
        
        return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def close(self):
        """Close the session."""
        self.session.close()