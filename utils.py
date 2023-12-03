def google_search_query(query,youtube = False):
    
    query = query.replace(' ', '+')
    if(youtube):
        search_url = f'https://www.youtube.com/results?search_query={query}'
    else:
        search_url = f'https://www.google.com/search?q={query}'
    return search_url