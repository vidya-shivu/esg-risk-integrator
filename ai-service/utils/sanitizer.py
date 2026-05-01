import re

def clean_input(text):
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove script-like patterns
    text = re.sub(r'(script|javascript|onerror|onload)', '', text, flags=re.IGNORECASE)

    return text.strip()