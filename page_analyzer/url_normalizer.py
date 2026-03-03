from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """
    Normalize URL to scheme://netloc format.
    
    Args:
        url: URL string to normalize
        
    Returns:
        Normalized URL string
        
    Examples:
        >>> normalize_url('https://example.com/path?query=1')
        'https://example.com'
    """
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'
