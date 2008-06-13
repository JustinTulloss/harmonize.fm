"""
Some simple hacks to extract years and totaltracks from whatever you feel like
throwing at it. Pretty much takes a best guess.
"""

def totaltracks(file):
    if file.get('totaltracks'):
        return int(file.get('totaltracks'))
    if file.get('tracknumber'):
        if str(file.get('tracknumber')).find('/')>=0:
            return int(str(file.get('tracknumber')).rpartition('/')[2])

def get_year(release):
    try:
        return release.getEarliestReleaseDate().split('-')[0]
    except:
        return None

