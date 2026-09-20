import re
from urllib.parse import urlparse


def extract_features(url):
    """Takes a raw URL string and returns a dict of 10 numeric features
    used by the phishing classifier."""
    url = str(url).strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    domain = parsed.netloc.split(":")[0]  # strip port if present

    features = {}
    features['url_length'] = len(url)
    features['domain_length'] = len(domain)
    features['num_dots'] = url.count('.')
    features['num_hyphens'] = url.count('-')
    features['num_digits'] = sum(c.isdigit() for c in url)
    features['num_special_chars'] = len(re.findall(r'[^a-zA-Z0-9.\-/:]', url))
    features['has_https'] = 1 if parsed.scheme == 'https' else 0
    features['has_ip'] = 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0
    features['has_at_symbol'] = 1 if '@' in url else 0
    features['num_subdomains'] = max(domain.count('.') - 1, 0) if domain else 0

    return features


if __name__ == "__main__":
    test_url = "http://192.168.1.1/paypal-login@secure.verify-account.com"
    print(extract_features(test_url))
