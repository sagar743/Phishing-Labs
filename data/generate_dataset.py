"""
Builds the training dataset for Phishing Labs.

NOTE ON DATA SOURCE:
A real live-scraped phishing feed (PhishTank/OpenPhish) requires ongoing
internet scraping that's outside the scope of a college practical and
would go stale immediately. Instead, this script builds a labeled dataset
from:
  - ~95 real, well-known legitimate domains (public knowledge), expanded
    into realistic URL variations (subdomains, paths, query strings).
  - Synthetically generated phishing-style URLs built from well-documented
    real-world phishing patterns: raw IP addresses, brand-name typosquats,
    '@' redirection tricks, excessive subdomains, suspicious TLDs, and
    suspicious keyword stuffing (secure/verify/login/confirm/etc).

This keeps the project fully reproducible offline and is transparent about
being a representative dataset for teaching feature-based classification,
not a live threat-intel feed. This is documented in the README as well.
"""

import os
import sys
import random
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from feature_extraction import extract_features

random.seed(42)

# ---------------------------------------------------------------------------
# 1. Legitimate domains (real, well-known)
# ---------------------------------------------------------------------------
LEGIT_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "amazon.com",
    "twitter.com", "instagram.com", "linkedin.com", "reddit.com", "netflix.com",
    "microsoft.com", "apple.com", "github.com", "stackoverflow.com", "paypal.com",
    "ebay.com", "yahoo.com", "bing.com", "adobe.com", "dropbox.com",
    "spotify.com", "zoom.us", "salesforce.com", "oracle.com", "ibm.com",
    "intel.com", "samsung.com", "sony.com", "nike.com", "adidas.com",
    "walmart.com", "target.com", "bestbuy.com", "cnn.com", "bbc.com",
    "nytimes.com", "forbes.com", "bloomberg.com", "wsj.com", "espn.com",
    "imdb.com", "wordpress.com", "blogger.com", "medium.com", "quora.com",
    "pinterest.com", "tumblr.com", "flickr.com", "vimeo.com", "twitch.tv",
    "discord.com", "slack.com", "trello.com", "notion.so", "airbnb.com",
    "uber.com", "lyft.com", "doordash.com", "indeed.com", "glassdoor.com",
    "coursera.org", "udemy.com", "khanacademy.org", "edx.org", "mit.edu",
    "harvard.edu", "stanford.edu", "w3schools.com", "mozilla.org", "python.org",
    "npmjs.com", "docker.com", "kubernetes.io", "digitalocean.com", "heroku.com",
    "godaddy.com", "namecheap.com", "cloudflare.com", "akamai.com", "britannica.com",
    "nationalgeographic.com", "weather.com", "accuweather.com", "irs.gov", "usa.gov",
    "nasa.gov", "who.int", "un.org", "worldbank.org", "hdfcbank.com",
    "icicibank.com", "sbi.co.in", "axisbank.com", "irctc.co.in", "amazon.in",
    "flipkart.com", "myntra.com", "zomato.com", "swiggy.com", "paytm.com",
    "phonepe.com", "olacabs.com", "makemytrip.com", "timesofindia.indiatimes.com",
    "hindustantimes.com", "ndtv.com", "indiatoday.in", "amityuniversity.in",
]

LEGIT_SUBDOMAINS = ["", "www.", "shop.", "blog.", "mail.", "support.", "news.", "app."]
LEGIT_PATHS = [
    "", "/", "/home", "/about", "/products", "/login", "/account", "/help",
    "/contact", "/search?q=news", "/article/2026/tech", "/user/profile",
    "/en/index.html", "/store/category/electronics",
]


def generate_legit_urls(n):
    urls = set()
    attempts = 0
    while len(urls) < n and attempts < n * 20:
        attempts += 1
        domain = random.choice(LEGIT_DOMAINS)
        sub = random.choice(LEGIT_SUBDOMAINS)
        path = random.choice(LEGIT_PATHS)
        # Real sites are mostly HTTPS but not exclusively - a small minority
        # of plain/legacy pages still resolve over HTTP. Keeping some overlap
        # here stops the model from learning "http = phishing" as a shortcut.
        scheme = "http" if random.random() < 0.08 else "https"
        # occasionally add realistic query/tracking params, which adds
        # digits and special characters to some legitimate URLs too
        if random.random() < 0.25:
            path += f"?utm_source={random.choice(['newsletter','ads','social'])}&id={random.randint(100,9999)}"
        url = f"{scheme}://{sub}{domain}{path}"
        urls.add(url)
    return list(urls)


# ---------------------------------------------------------------------------
# 2. Synthetic phishing-style URLs (documented real-world patterns)
# ---------------------------------------------------------------------------
BRANDS = [
    "paypal", "amazon", "apple", "microsoft", "google", "facebook", "netflix",
    "bankofamerica", "chase", "wellsfargo", "instagram", "hdfcbank", "icicibank",
    "sbi", "paytm", "flipkart", "outlook", "linkedin",
]
TYPOSQUATS = {
    "paypal": ["paypa1", "paypal-secure", "paypaI"],
    "amazon": ["amaz0n", "arnazon", "amazon-secure"],
    "apple": ["apple-id", "app1e", "apple-verify"],
    "microsoft": ["micros0ft", "microsft", "microsoft-support"],
    "google": ["g00gle", "googie", "google-security"],
    "facebook": ["faceb00k", "facebok", "facebook-login"],
}
KEYWORDS = ["secure", "verify", "login", "update", "confirm", "account",
            "signin", "alert", "suspended", "reset", "billing", "support"]
SUSPICIOUS_TLDS = [".tk", ".ru", ".info", ".xyz", ".ga", ".cf", ".ml", ".top", ".ooo"]


def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def random_token(length=6):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def generate_phishing_url():
    pattern = random.choice(["ip", "typosquat", "at_symbol", "subdomain_chain",
                              "hyphen_stack", "keyword_stuff"])
    brand = random.choice(BRANDS)
    word = random.choice(KEYWORDS)
    word2 = random.choice(KEYWORDS)
    tld = random.choice(SUSPICIOUS_TLDS)
    # Modern phishing kits increasingly use free HTTPS certs, so a plain
    # "no HTTPS = phishing" rule isn't realistic either - mix it in here.
    scheme = "https" if random.random() < 0.3 else "http"

    if pattern == "ip":
        return f"{scheme}://{random_ip()}/{brand}-{word}/login.php"

    elif pattern == "typosquat":
        fake = random.choice(TYPOSQUATS.get(brand, [f"{brand}0"]))
        return f"{scheme}://{fake}{tld}/{word}"

    elif pattern == "at_symbol":
        legit = random.choice(LEGIT_DOMAINS)
        return f"{scheme}://{legit}@{brand}-{word}{tld}/{random_token(4)}"

    elif pattern == "subdomain_chain":
        return f"{scheme}://{word}.{word2}.{brand}.com.{random_token(5)}{tld}"

    elif pattern == "hyphen_stack":
        return f"{scheme}://{brand}-{word}-{word2}-{random_token(4)}{tld}/index.html"

    else:  # keyword_stuff
        return (f"{scheme}://{brand}{tld}/{word}-{word2}-{random_token(6)}"
                f"?ref={random_token(8)}&id={random.randint(1000,9999)}")


def generate_phishing_urls(n):
    urls = set()
    attempts = 0
    while len(urls) < n and attempts < n * 20:
        attempts += 1
        urls.add(generate_phishing_url())
    return list(urls)


# ---------------------------------------------------------------------------
# 3. Build raw_urls.csv, then phishing_dataset.csv
# ---------------------------------------------------------------------------
def main():
    n_per_class = 650

    legit_urls = generate_legit_urls(n_per_class)
    phishing_urls = generate_phishing_urls(n_per_class)

    rows = [(u, 0) for u in legit_urls] + [(u, 1) for u in phishing_urls]
    random.shuffle(rows)

    raw_df = pd.DataFrame(rows, columns=["url", "label"])
    raw_path = os.path.join(os.path.dirname(__file__), "raw_urls.csv")
    raw_df.to_csv(raw_path, index=False)
    print(f"Saved {len(raw_df)} raw URLs to {raw_path}")
    print(raw_df["label"].value_counts())

    feature_rows = []
    for _, row in raw_df.iterrows():
        feats = extract_features(row["url"])
        feats["label"] = int(row["label"])
        feature_rows.append(feats)

    feat_df = pd.DataFrame(feature_rows)
    feat_path = os.path.join(os.path.dirname(__file__), "phishing_dataset.csv")
    feat_df.to_csv(feat_path, index=False)
    print(f"Saved {len(feat_df)} feature rows to {feat_path}")


if __name__ == "__main__":
    main()
