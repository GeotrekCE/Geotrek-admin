def add_http_prefix(url):
    if url.startswith('http'):
        return url
    else:
        return 'http://' + url
