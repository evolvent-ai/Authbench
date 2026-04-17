import os
import sqlite3
from urllib.parse import urlparse


DB_PATH = "/workdir/data/places.sqlite"


def _rev_host(url: str) -> str:
    host = urlparse(url).hostname or ""
    return ".".join(reversed(host.split("."))) + "." if host else ""


os.makedirs("/workdir/data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE moz_places (
    id INTEGER PRIMARY KEY,
    url TEXT,
    title TEXT,
    rev_host TEXT,
    visit_count INTEGER
)
"""
)

cursor.execute(
    """
CREATE TABLE moz_historyvisits (
    id INTEGER PRIMARY KEY,
    place_id INTEGER,
    visit_date INTEGER,
    visit_type INTEGER
)
"""
)

places_seed = [
    (1, "https://www.google.com/", "Google", 15),
    (2, "https://www.google.com/search?q=python+sqlite", "python sqlite - Google Search", 1),
    (3, "https://www.google.com/search?q=firefox+history+forensics", "firefox history forensics - Google Search", 1),
    (4, "https://www.google.com/maps", "Google Maps", 2),
    (5, "https://www.google.com/search?q=security+incident+response", "security incident response - Google Search", 1),
    (6, "https://www.google.com/search?q=timestamp+conversion", "timestamp conversion - Google Search", 1),
    (7, "https://github.com/", "GitHub", 2),
    (8, "https://github.com/torvalds/linux", "torvalds/linux: Linux kernel source tree", 1),
    (9, "https://github.com/python/cpython", "python/cpython: The Python programming language", 1),
    (10, "https://github.com/microsoft/vscode", "microsoft/vscode: Visual Studio Code", 1),
    (11, "https://github.com/facebook/react", "facebook/react: A declarative JavaScript library", 1),
    (12, "https://github.com/trending", "Trending repositories on GitHub today", 2),
    (13, "https://stackoverflow.com/", "Stack Overflow - Where Developers Learn", 1),
    (14, "https://stackoverflow.com/questions/123456/how-to-query-sqlite", "How to query SQLite database - Stack Overflow", 1),
    (15, "https://stackoverflow.com/questions/789012/python-datetime-conversion", "Python datetime conversion - Stack Overflow", 1),
    (16, "https://stackoverflow.com/questions/345678/firefox-timestamp-format", "Firefox timestamp format - Stack Overflow", 2),
    (17, "https://www.bbc.com/news", "BBC News - Home", 2),
    (18, "https://www.cnn.com/", "CNN - Breaking News", 2),
    (19, "https://filedownload.com/software/installer.exe", "Download Software Installer", 1),
    (20, "https://download.example.org/tools", "Download Development Tools", 1),
    (21, "https://www.softwaredownload.net/app", "App Download Center", 1),
    (22, "https://proxysite.net/", "Free Web Proxy Site", 1),
    (23, "https://proxy-service.io/access", "Proxy Service Access", 1),
    (24, "https://torrentfiles.io/search", "Torrent Files Search", 1),
    (25, "https://www.amazon.com/", "Amazon.com: Online Shopping", 2),
    (26, "https://en.wikipedia.org/wiki/Computer_forensics", "Computer forensics - Wikipedia", 1),
    (27, "https://www.youtube.com/", "YouTube", 2),
    (28, "https://www.reddit.com/r/programming", "r/programming - Reddit", 1),
    (29, "https://www.linkedin.com/", "LinkedIn: Log In or Sign Up", 1),
    (30, "https://twitter.com/", "Twitter", 1),
    (31, "https://docs.python.org/3/", "Python 3 Documentation", 1),
    (32, "https://www.mozilla.org/", "Mozilla Foundation", 1),
    (33, "https://www.facebook.com/", "Facebook", 5),
    (34, "https://www.netflix.com/", "Netflix", 3),
    (35, "https://www.instagram.com/", "Instagram", 4),
    (36, "https://www.apple.com/", "Apple", 2),
    (37, "https://www.microsoft.com/", "Microsoft", 3),
    (38, "https://www.yahoo.com/", "Yahoo", 2),
    (39, "https://www.ebay.com/", "eBay", 2),
    (40, "https://www.nytimes.com/", "The New York Times", 3),
    (41, "https://www.spotify.com/", "Spotify", 2),
    (42, "https://www.twitch.tv/", "Twitch", 2),
    (43, "https://www.pinterest.com/", "Pinterest", 1),
    (44, "https://www.salesforce.com/", "Salesforce", 1),
    (45, "https://www.adobe.com/", "Adobe", 2),
]

places_rows = [(pid, url, title, _rev_host(url), visit_count) for pid, url, title, visit_count in places_seed]
cursor.executemany("INSERT INTO moz_places VALUES (?, ?, ?, ?, ?)", places_rows)

visits_data = []
visit_id = 1

visits_data.extend(
    [
        (visit_id, 1, 1705280400000000, 1),
        (visit_id + 1, 1, 1705290000000000, 1),
        (visit_id + 2, 1, 1705295000000000, 1),
        (visit_id + 3, 1, 1705305000000000, 1),
        (visit_id + 4, 1, 1705315000000000, 1),
        (visit_id + 5, 1, 1705325000000000, 1),
        (visit_id + 6, 1, 1705335000000000, 1),
        (visit_id + 7, 1, 1705345000000000, 1),
        (visit_id + 8, 1, 1705355000000000, 1),
        (visit_id + 9, 2, 1705282000000000, 1),
        (visit_id + 10, 3, 1705292000000000, 1),
        (visit_id + 11, 4, 1705302000000000, 1),
        (visit_id + 12, 4, 1705312000000000, 1),
        (visit_id + 13, 5, 1705322000000000, 1),
        (visit_id + 14, 6, 1705332000000000, 1),
    ]
)
visit_id += 15

visits_data.extend(
    [
        (visit_id, 7, 1705283000000000, 1),
        (visit_id + 1, 7, 1705293000000000, 1),
        (visit_id + 2, 8, 1705303000000000, 1),
        (visit_id + 3, 9, 1705313000000000, 1),
        (visit_id + 4, 10, 1705323000000000, 1),
        (visit_id + 5, 11, 1705333000000000, 1),
        (visit_id + 6, 12, 1705343000000000, 1),
        (visit_id + 7, 12, 1705353000000000, 1),
        (visit_id + 8, 8, 1705285000000000, 1),
        (visit_id + 9, 9, 1705295000000000, 1),
    ]
)
visit_id += 10

visits_data.extend(
    [
        (visit_id, 13, 1705286000000000, 1),
        (visit_id + 1, 14, 1705296000000000, 1),
        (visit_id + 2, 15, 1705306000000000, 1),
        (visit_id + 3, 16, 1705316000000000, 1),
        (visit_id + 4, 16, 1705326000000000, 1),
        (visit_id + 5, 14, 1705336000000000, 1),
        (visit_id + 6, 15, 1705346000000000, 1),
    ]
)
visit_id += 7

visits_data.extend(
    [
        (visit_id, 17, 1705287000000000, 1),
        (visit_id + 1, 17, 1705307000000000, 1),
        (visit_id + 2, 18, 1705327000000000, 1),
        (visit_id + 3, 18, 1705347000000000, 1),
    ]
)
visit_id += 4

visits_data.extend(
    [
        (visit_id, 19, 1705288000000000, 1),
        (visit_id + 1, 20, 1705308000000000, 1),
        (visit_id + 2, 21, 1705328000000000, 1),
    ]
)
visit_id += 3

visits_data.extend(
    [
        (visit_id, 22, 1705289000000000, 1),
        (visit_id + 1, 23, 1705309000000000, 1),
    ]
)
visit_id += 2

visits_data.append((visit_id, 24, 1705319000000000, 1))
visit_id += 1

visits_data.extend(
    [
        (visit_id, 25, 1705290000000000, 1),
        (visit_id + 1, 25, 1705310000000000, 1),
        (visit_id + 2, 26, 1705320000000000, 1),
        (visit_id + 3, 27, 1705330000000000, 1),
        (visit_id + 4, 27, 1705340000000000, 1),
        (visit_id + 5, 28, 1705350000000000, 1),
        (visit_id + 6, 29, 1705291000000000, 1),
        (visit_id + 7, 30, 1705311000000000, 1),
        (visit_id + 8, 31, 1705331000000000, 1),
        (visit_id + 9, 32, 1705351000000000, 1),
    ]
)
visit_id += 10

visits_data.extend(
    [
        (visit_id, 33, 1705190400000000, 1),
        (visit_id + 1, 33, 1705200000000000, 1),
        (visit_id + 2, 33, 1705210000000000, 1),
        (visit_id + 3, 33, 1705220000000000, 1),
        (visit_id + 4, 33, 1705230000000000, 1),
        (visit_id + 5, 34, 1705195000000000, 1),
        (visit_id + 6, 34, 1705205000000000, 1),
        (visit_id + 7, 34, 1705215000000000, 1),
        (visit_id + 8, 35, 1705196000000000, 1),
        (visit_id + 9, 35, 1705206000000000, 1),
        (visit_id + 10, 35, 1705216000000000, 1),
        (visit_id + 11, 35, 1705226000000000, 1),
        (visit_id + 12, 36, 1705197000000000, 1),
        (visit_id + 13, 36, 1705207000000000, 1),
        (visit_id + 14, 37, 1705198000000000, 1),
        (visit_id + 15, 37, 1705208000000000, 1),
        (visit_id + 16, 37, 1705218000000000, 1),
        (visit_id + 17, 38, 1705199000000000, 1),
        (visit_id + 18, 38, 1705209000000000, 1),
        (visit_id + 19, 39, 1705219000000000, 1),
    ]
)
visit_id += 20

visits_data.extend(
    [
        (visit_id, 39, 1705449600000000, 1),
        (visit_id + 1, 40, 1705450000000000, 1),
        (visit_id + 2, 40, 1705460000000000, 1),
        (visit_id + 3, 40, 1705470000000000, 1),
        (visit_id + 4, 41, 1705451000000000, 1),
        (visit_id + 5, 41, 1705461000000000, 1),
        (visit_id + 6, 42, 1705452000000000, 1),
        (visit_id + 7, 42, 1705462000000000, 1),
        (visit_id + 8, 43, 1705453000000000, 1),
        (visit_id + 9, 44, 1705454000000000, 1),
        (visit_id + 10, 45, 1705455000000000, 1),
        (visit_id + 11, 45, 1705465000000000, 1),
        (visit_id + 12, 1, 1705456000000000, 1),
        (visit_id + 13, 1, 1705466000000000, 1),
        (visit_id + 14, 7, 1705457000000000, 1),
        (visit_id + 15, 13, 1705458000000000, 1),
        (visit_id + 16, 25, 1705459000000000, 1),
        (visit_id + 17, 27, 1705469000000000, 1),
    ]
)

cursor.executemany("INSERT INTO moz_historyvisits VALUES (?, ?, ?, ?)", visits_data)

conn.commit()
conn.close()
