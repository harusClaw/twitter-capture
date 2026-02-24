#!/usr/bin/env python3
"""
Twitter Media Extractor

Extracts images, videos, and GIFs from Twitter/X URLs.
Uses httpx for fast meta tag extraction from fixupx.com (primary method).
Falls back to Playwright for complex cases.
"""

import logging
import re
import httpx

logger = logging.getLogger(__name__)


def extract_from_meta_tags(html: str, url: str) -> dict | None:
    """Extract tweet data from HTML meta tags."""
    
    # Extract image URLs from og:image and twitter:image meta tags
    image_urls = []
    
    # Pattern 1: <meta property="og:image" content="...">
    for match in re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html):
        if match and match not in image_urls:
            image_urls.append(match)
    
    # Pattern 2: <meta content="..." property="og:image"> (alternate order)
    for match in re.findall(r'<meta[^>]+content=["\']([^"\']+)[\"\'][^>]+property=["\']og:image["\']', html):
        if match and match not in image_urls:
            image_urls.append(match)
    
    # Also check twitter:image
    for match in re.findall(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)[\"\']', html):
        if match and match not in image_urls:
            image_urls.append(match)
    
    for match in re.findall(r'<meta[^>]+content=["\']([^"\']+)[\"\'][^>]+name=["\']twitter:image["\']', html):
        if match and match not in image_urls:
            image_urls.append(match)
    
    # Extract title and description
    username = 'Unknown'
    handle = '@unknown'
    text = ''
    
    # og:title: "Username (@handle)"
    title_match = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)[\"\']', html)
    if title_match:
        title = title_match.group(1)
        # Parse "Username (@handle)" format
        handle_match = re.search(r'\((@[a-zA-Z0-9_]+)\)', title)
        if handle_match:
            handle = handle_match.group(1)
            username = title.replace(handle, '').strip()
        else:
            username = title
    
    # Fallback: extract handle from URL
    if handle == '@unknown':
        url_match = re.search(r'/([a-zA-Z0-9_]+)/status/', url)
        if url_match:
            handle = '@' + url_match.group(1)
            username = url_match.group(1)
    
    # og:description: tweet text
    desc_match = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)[\"\']', html)
    if desc_match:
        text = desc_match.group(1)
    
    if image_urls:
        logger.info(f"Extracted from meta tags: {username} - Images: {len(image_urls)}")
        return {
            'username': username,
            'handle': handle,
            'text': text,
            'media_urls': image_urls,
            'video_urls': [],
            'timestamp': 'Unknown'
        }
    
    return None


async def extract_tweet_data(url: str) -> dict | None:
    """
    Extract tweet data from Twitter/X URLs.
    
    Returns dict with:
    - username: Display name
    - handle: @username
    - text: Tweet text
    - media_urls: List of image URLs
    - video_urls: List of video/GIF URLs
    - timestamp: Tweet time
    """
    try:
        # Convert to fixupx.com URL
        fx_url = url.replace('twitter.com', 'fixupx.com').replace('x.com', 'fixupx.com')
        
        # PRIMARY METHOD: Use httpx to fetch HTML and extract meta tags
        # This is faster and avoids JavaScript redirect issues
        logger.info(f"Fetching {fx_url} with httpx...")
        
        async with httpx.AsyncClient(follow_redirects=False, timeout=30.0) as client:
            response = await client.get(fx_url)
            
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} from fixupx.com")
                return None
            
            html = response.text
            
            # Check for Twitter error page (no meta tags, just error message)
            if 'Something went wrong' in html and 'og:image' not in html:
                logger.warning(f"Twitter error page detected: {fx_url}")
                return {'error': 'twitter_error', 'message': 'Twitter returned an error. The tweet may be deleted, private, or age-restricted.'}
            
            # Extract from meta tags
            meta_data = extract_from_meta_tags(html, fx_url)
            
            if meta_data and meta_data.get('media_urls'):
                return meta_data
            
            # If no images in meta tags but page loaded, might be video-only
            # Fall back to Playwright for complex extraction
            logger.info("No images in meta tags, falling back to Playwright...")
        
        # FALLBACK: Use Playwright for full article rendering
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            await page.goto(fx_url, wait_until='domcontentloaded', timeout=30000)
            
            # Extract data from meta tags in rendered page
            meta_data = await page.evaluate('''() => {
                const getMetaContent = (property) => {
                    const meta = document.querySelector(`meta[property="${property}"]`) ||
                                document.querySelector(`meta[name="${property}"]`);
                    return meta ? meta.getAttribute('content') : null;
                };
                
                const ogImage = getMetaContent('og:image');
                const twitterImage = getMetaContent('twitter:image');
                const ogTitle = getMetaContent('og:title');
                const ogDescription = getMetaContent('og:description');
                const twitterCreator = getMetaContent('twitter:creator');
                
                const allImages = [];
                document.querySelectorAll('meta[property="og:image"], meta[name="twitter:image"]').forEach(meta => {
                    const content = meta.getAttribute('content');
                    if (content && !allImages.includes(content)) {
                        allImages.push(content);
                    }
                });
                
                let username = 'Unknown';
                let handle = '@unknown';
                
                if (twitterCreator) {
                    handle = twitterCreator;
                    username = twitterCreator.replace('@', '');
                } else if (ogTitle) {
                    const match = ogTitle.match(/(.+?)\\s+\\((@[a-zA-Z0-9_]+)\\)/);
                    if (match) {
                        username = match[1].trim();
                        handle = match[2];
                    }
                }
                
                return {
                    username: username,
                    handle: handle,
                    text: ogDescription || '',
                    media_urls: allImages,
                    has_meta: !!(ogImage || twitterImage)
                };
            }''')
            
            if meta_data.get('has_meta') and meta_data.get('media_urls'):
                await browser.close()
                await playwright.stop()
                return {
                    'username': meta_data['username'],
                    'handle': meta_data['handle'],
                    'text': meta_data['text'],
                    'media_urls': meta_data['media_urls'],
                    'video_urls': [],
                    'timestamp': 'Unknown'
                }
            
            # Try to find full article
            page_content = await page.content()
            
            if 'something went wrong' in page_content.lower():
                await browser.close()
                await playwright.stop()
                return {'error': 'twitter_error', 'message': 'Twitter returned an error. The tweet may be deleted, private, or age-restricted.'}
            
            await page.wait_for_selector('article[role="article"]', timeout=10000)
            
            tweet_data = await page.evaluate('''() => {
                const article = document.querySelector('article[role="article"]');
                if (!article) return null;
                
                let username = 'Unknown';
                let handle = '@unknown';
                
                const nameElement = article.querySelector('[data-testid="User-Name"]');
                if (nameElement) {
                    const spans = Array.from(nameElement.querySelectorAll('span'));
                    const texts = spans.map(s => s.textContent.trim()).filter(t => t.length > 0);
                    
                    for (const text of texts) {
                        if (!text.startsWith('@') && text.length > 0) {
                            username = text;
                            break;
                        }
                    }
                    
                    for (const text of texts) {
                        if (text.startsWith('@')) {
                            handle = text;
                            break;
                        }
                    }
                }
                
                if (handle === '@unknown') {
                    const urlMatch = window.location.pathname.match(/\\/([a-zA-Z0-9_]+)\\/status\\//);
                    if (urlMatch) {
                        handle = '@' + urlMatch[1];
                    }
                }
                
                let text = '';
                const textContainer = article.querySelector('div[lang]');
                if (textContainer) {
                    const textSpans = textContainer.querySelectorAll('span');
                    if (textSpans.length > 0) {
                        text = Array.from(textSpans).map(span => span.textContent).join('').trim();
                    } else {
                        text = textContainer.textContent.trim();
                    }
                }
                
                const mediaImgs = Array.from(article.querySelectorAll('img[src*="pbs.twimg.com"]'))
                    .map(img => img.src)
                    .filter(src => src && src.length > 0)
                    .filter(src => !src.includes('profile_images'))
                    .filter(src => !src.includes('amplify_video_thumb'))
                    .filter(src => !src.includes('/emoji/'))
                    .filter(src => !src.includes('_normal.'))
                    .slice(0, 4);
                
                const videos = [];
                
                const videoElements = article.querySelectorAll('video');
                videoElements.forEach(video => {
                    if (video.src) videos.push(video.src);
                    const sources = video.querySelectorAll('source');
                    sources.forEach(source => {
                        if (source.src) videos.push(source.src);
                    });
                });
                
                const allElements = article.querySelectorAll('*');
                allElements.forEach(el => {
                    const src = el.getAttribute('src');
                    if (src && src.includes('video.twimg.com') && !videos.includes(src)) {
                        videos.push(src);
                    }
                    const dataSrc = el.getAttribute('data-src');
                    if (dataSrc && dataSrc.includes('video.twimg.com') && !videos.includes(dataSrc)) {
                        videos.push(dataSrc);
                    }
                });
                
                const gifImgElements = article.querySelectorAll('img[src*="tweet_video"]');
                gifImgElements.forEach(img => {
                    let src = img.getAttribute('src') || img.getAttribute('data-src');
                    if (src && src.includes('tweet_video')) {
                        const match = src.match(/tweet_video(?:_thumb)?\\/([a-zA-Z0-9_-]+)(?:\\.jpg|\\.mp4|\\.gif)?/);
                        if (match) {
                            const videoId = match[1];
                            const videoUrl = `https://video.twimg.com/tweet_video/${videoId}.mp4`;
                            if (!videos.includes(videoUrl)) {
                                videos.push(videoUrl);
                            }
                        }
                    }
                });
                
                const videoContainers = article.querySelectorAll('[data-video-url]');
                videoContainers.forEach(el => {
                    const videoUrl = el.getAttribute('data-video-url');
                    if (videoUrl && videoUrl.includes('video.twimg.com') && !videos.includes(videoUrl)) {
                        videos.push(videoUrl);
                    }
                });
                
                const uniqueVideos = [...new Set(videos)];
                
                const timeElement = article.querySelector('time');
                const timestamp = timeElement ? timeElement.textContent.trim() : new Date().toLocaleString();
                
                return {
                    username: username,
                    handle: handle,
                    text: text,
                    media_urls: mediaImgs,
                    video_urls: uniqueVideos,
                    timestamp: timestamp
                };
            }''')
            
            await browser.close()
            await playwright.stop()
            
            if tweet_data:
                logger.info(f"Extracted tweet (article mode): {tweet_data.get('username')}")
                return tweet_data
            
            logger.warning(f"No tweet data extracted from {fx_url}")
            return None
            
        except Exception as e:
            logger.error(f"Playwright error: {e}")
            await browser.close()
            await playwright.stop()
            return None
        
    except Exception as e:
        logger.error(f"Error extracting tweet data: {e}")
        return None
