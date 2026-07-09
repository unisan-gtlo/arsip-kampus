import re

DRIVE_LINK_PATTERNS = [
    r"/file/d/([a-zA-Z0-9_-]+)",
    r"id=([a-zA-Z0-9_-]+)",
    r"/d/([a-zA-Z0-9_-]+)",
]


def parse_drive_link(drive_link: str):
    """Extract (file_id, preview_link) from a pasted Google Drive share link.

    Returns (None, None) if the link doesn't match a known Drive URL format.
    """
    for pattern in DRIVE_LINK_PATTERNS:
        match = re.search(pattern, drive_link)
        if match:
            file_id = match.group(1)
            return file_id, f"https://drive.google.com/file/d/{file_id}/preview"
    return None, None
