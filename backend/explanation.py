def generate_explanation(features):
    """Turns raw feature values into plain-language reasons a person can read."""
    reasons = []

    if features['has_ip'] == 1:
        reasons.append("IP address used instead of a domain name")
    if features['has_at_symbol'] == 1:
        reasons.append("URL contains an '@' symbol")
    if features['url_length'] > 75:
        reasons.append("URL is unusually long")
    if features['num_hyphens'] > 3:
        reasons.append("URL contains multiple hyphens")
    if features['num_dots'] > 4:
        reasons.append("URL contains an unusually high number of dots")
    if features['num_subdomains'] > 2:
        reasons.append("URL has multiple subdomains")
    if features['num_special_chars'] > 5:
        reasons.append("URL contains several unusual special characters")
    if features['has_https'] == 0:
        reasons.append("Connection is not using HTTPS")

    if not reasons:
        reasons.append("No major suspicious patterns detected in the URL structure")

    return reasons
