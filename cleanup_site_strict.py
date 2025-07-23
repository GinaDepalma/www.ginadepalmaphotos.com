import os
import re
import shutil
from pathlib import Path
from collections import deque

# Configuration
STATE_DIR = '_state_for_cleanup_strict'  # New dir to avoid conflicting with previous runs
QUARANTINE_DIR = '_safe_to_remove_strict'
START_FILE = 'index.html'
EXCLUDED_PREFIXES = ['wp-content/cache/', 'wp-content/uploads/', '.git/']
CRAWLABLE_EXTS = {'.html', '.css', '.js'}
ALL_FILES_PATH = f'{STATE_DIR}/_all_project_files.txt'
CRAWL_QUEUE_PATH = f'{STATE_DIR}/_crawl_queue.txt'
CRAWLED_FILES_PATH = f'{STATE_DIR}/_crawled_files.txt'
LIVE_ASSETS_PATH = f'{STATE_DIR}/_live_assets.txt'
UNREACHABLE_PATH = f'{STATE_DIR}/_unreachable_files.txt'
DELETED_DIRS_PATH = f'{STATE_DIR}/_deleted_dirs.txt'
QUARANTINE_FLAG = f'{STATE_DIR}/_quarantine_complete.flag'
DIR_CLEANUP_FLAG = f'{STATE_DIR}/_dir_cleanup_complete.flag'

# Spam keywords to filter out injected spam links (Turkish casino terms)
SPAM_KEYWORDS = [
    'bahis', 'casino', 'bonus', 'giris', 'deneme', 'kazanc', 'slot', 'yuksek', 'eglence', 'potansiyeli',
    've', 'sunan', 'bonanza', 'mostbet', 'casibom', 'glory', 'pinup', 'bahsegel', 'admiral', 'gates',
    'olympus', 'uptown', 'sekabet', 'sweet', 'aviator', 'pay and play', 'znaki', 'amsterdam', 'uzrates',
    'izmirkoleji', 'bil-cag', '1sekabetgiris', 'ozgalore', 'siteniekle', 'betistgirisadresleri'
]

def initialize():
    if os.path.exists(STATE_DIR):
        print("Resuming from existing state.")
    else:
        os.makedirs(STATE_DIR, exist_ok=True)
        print("Creating new state directory.")

    # Always generate or regenerate the master list if missing, excluding prefixes
    if not os.path.exists(ALL_FILES_PATH):
        all_files = []
        for root, dirs, files in os.walk('.'):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), '.').replace('\\', '/')
                if any(rel_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
                    continue
                all_files.append(rel_path)
        with open(ALL_FILES_PATH, 'w') as f:
            f.write('\n'.join(sorted(all_files)) + '\n')
        print("Generated master file list (excluded uploads).")

    # If other init files are missing, create them with strict menu-based queue
    if not os.path.exists(CRAWL_QUEUE_PATH) or not os.path.exists(CRAWLED_FILES_PATH) or not os.path.exists(LIVE_ASSETS_PATH):
        # Parse index.html for side menu links using regex (for Bridge theme vertical menu)
        menu_links = set()
        if os.path.exists(START_FILE):
            with open(START_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Find the vertical menu block (improved to match ul or nav with vertical_menu in class)
            menu_block_pattern = r'<(ul|nav)[^>]*class=["\']?(?:.*\bvertical_menu\b.*)["\']?>(.*?)</\1>'
            menu_blocks = re.findall(menu_block_pattern, content, re.DOTALL | re.IGNORECASE)
            for tag, block in menu_blocks:
                # Extract <a href="...">text</a>
                link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
                for href, text in re.findall(link_pattern, block, re.IGNORECASE):
                    href = href.strip()
                    if href and not href.startswith(('http', '//', '#', 'mailto:', 'tel:', 'javascript:')) and '://' not in href:
                        # Normalize
                        if href.startswith('/'):
                            href = href.lstrip('/')
                        if href.endswith('/'):
                            href += 'index.html'
                        if os.path.exists(href):
                            menu_links.add(href)
                            print(f"Extracted menu link: {text.strip()} - {href}")
        else:
            print(f"Warning: {START_FILE} not found; starting with only index.html.")

        # Initialize with index.html and menu links
        initial_queue = [START_FILE] + sorted(menu_links)
        with open(CRAWL_QUEUE_PATH, 'w') as f:
            f.write('\n'.join(initial_queue) + '\n')
        with open(CRAWLED_FILES_PATH, 'w') as f:
            pass
        with open(LIVE_ASSETS_PATH, 'w') as f:
            f.write('\n'.join(initial_queue) + '\n')  # Mark initial as live
        print(f"Initialized strict queue with {len(initial_queue)} items from side menu.")

def extract_links(file_path):
    if not os.path.exists(file_path):
        return set()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    links = set()
    
    # HTML attributes: href, src, data-src (double/single quotes)
    attr_patterns = [
        r'(?:href|src|data-src)=["\']([^"\']+)["\']',
        r'srcset=["\']([^"\']+)["\']'  # Parse srcset URLs
    ]
    for pattern in attr_patterns:
        for match in re.findall(pattern, content):
            if 'srcset' in pattern:
                # Split srcset and take URLs (ignore descriptors)
                for part in match.split(','):
                    url = part.strip().split()[0]
                    if url:
                        links.add(url)
            else:
                links.add(match)
    
    # CSS: url(), @import
    css_patterns = [
        r'url\(["\']?([^)"\']+)["\']?\)',  # url(...)
        r'@import ["\']([^"\']+)["\']'     # @import "..."
    ]
    for pattern in css_patterns:
        links.update(re.findall(pattern, content))
    
    # JS: string literals that look like paths (starting with / or relative)
    js_pattern = r'["\'](/[^"\']*)["\']'
    links.update(re.findall(js_pattern, content))
    
    # Sanitize: remove query params, fragments, non-local
    sanitized = set()
    for link in links:
        link = re.sub(r'\?.*', '', link)  # Remove query
        link = re.sub(r'#.*', '', link)   # Remove fragment
        link = link.strip()
        if not link or '://' in link or link.startswith(('//', 'mailto:', 'tel:', 'javascript:')):
            continue
        # Decode URL encoding
        link = link.replace('%20', ' ').replace('%2F', '/')
        sanitized.add(link)
    
    return sanitized

def normalize_path(base_dir, link):
    if link.endswith('/'):
        link += 'index.html'
    if link.startswith('/'):
        return link.lstrip('/')
    full_path = os.path.normpath(os.path.join(base_dir, link))
    rel_path = os.path.relpath(full_path, os.getcwd()).replace('\\', '/')
    return rel_path

def crawl():
    live_assets = set(Path(LIVE_ASSETS_PATH).read_text().splitlines()) if os.path.exists(LIVE_ASSETS_PATH) else set()
    crawled = set(Path(CRAWLED_FILES_PATH).read_text().splitlines()) if os.path.exists(CRAWLED_FILES_PATH) else set()
    queue = deque(Path(CRAWL_QUEUE_PATH).read_text().splitlines()) if os.path.exists(CRAWL_QUEUE_PATH) else deque()
    
    while queue:
        current = queue.popleft()
        if current in crawled:
            continue
        
        print(f"Processing: {current}")
        base_dir = os.path.dirname(current)
        links = extract_links(current)
        normalized = set()
        for link in links:
            if not link:
                continue
            try:
                norm = normalize_path(base_dir, link)
                if not norm.startswith('..'):
                    # Skip if matches spam keyword
                    if any(keyword in norm.lower() for keyword in SPAM_KEYWORDS):
                        print(f"Skipping spam path: {norm}")
                        continue
                    # Skip if in excluded prefix
                    if any(norm.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
                        continue
                    normalized.add(norm)
            except ValueError as e:
                print(f"Skipping invalid path {link}: {e}")
                continue
        
        # Filter excluded
        normalized = {p for p in normalized if not any(p.startswith(prefix) for prefix in EXCLUDED_PREFIXES)}
        
        live_assets.update(normalized)
        crawled.add(current)
        
        # Add crawlable to queue
        new_crawlable = {p for p in normalized if Path(p).suffix in CRAWLABLE_EXTS and p not in crawled and p not in queue}
        queue.extend(new_crawlable)
        
        # Save state incrementally
        with open(LIVE_ASSETS_PATH, 'w') as f:
            f.write('\n'.join(sorted(live_assets)) + '\n')
        with open(CRAWLED_FILES_PATH, 'a') as f:
            f.write(current + '\n')
        with open(CRAWL_QUEUE_PATH, 'w') as f:
            f.write('\n'.join(queue) + '\n')
    
    print("Crawl complete.")
    return live_assets

def analyze(live_assets):
    if os.path.exists(UNREACHABLE_PATH):
        return
    all_files = set(Path(ALL_FILES_PATH).read_text().splitlines())
    unreachable = [f for f in sorted(all_files - live_assets) if not any(f.startswith(prefix) for prefix in EXCLUDED_PREFIXES)]
    with open(UNREACHABLE_PATH, 'w') as f:
        f.write('\n'.join(unreachable) + '\n')
    print("Analysis complete.")

def quarantine():
    if os.path.exists(QUARANTINE_FLAG):
        return
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    unreachable = Path(UNREACHABLE_PATH).read_text().splitlines()
    for file in unreachable:
        if os.path.exists(file):
            dest = Path(QUARANTINE_DIR) / file
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Copy with backup if exists
            if dest.exists():
                backup_num = 1
                while (backup_dest := dest.with_suffix(f'{dest.suffix}~{backup_num}')).exists():
                    backup_num += 1
                shutil.copy2(file, backup_dest)
            else:
                shutil.copy2(file, dest)
            os.remove(file)
    Path(QUARANTINE_FLAG).touch()
    print("Quarantine complete.")

def cleanup_dirs():
    if os.path.exists(DIR_CLEANUP_FLAG):
        return
    deleted_dirs = []
    for root, dirs, files in os.walk('.', topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            rel_dir = os.path.relpath(dir_path, '.').replace('\\', '/')
            if rel_dir.startswith('.') or any(rel_dir.startswith(prefix.rstrip('/')) for prefix in EXCLUDED_PREFIXES):
                continue
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                deleted_dirs.append(rel_dir)
    with open(DELETED_DIRS_PATH, 'w') as f:
        f.write('\n'.join(sorted(deleted_dirs)) + '\n')
    Path(DIR_CLEANUP_FLAG).touch()
    print("Directory cleanup complete.")

def report_and_finalize():
    unreachable = Path(UNREACHABLE_PATH).read_text().splitlines() if os.path.exists(UNREACHABLE_PATH) else []
    deleted_dirs = Path(DELETED_DIRS_PATH).read_text().splitlines() if os.path.exists(DELETED_DIRS_PATH) else []
    
    print("\nSummary Report:")
    print("| Category          | Details |")
    print("|-------------------|---------|")
    print(f"| Quarantined Files | {', '.join(unreachable) if unreachable else 'None'} |")
    print(f"| Deleted Dirs      | {', '.join(deleted_dirs) if deleted_dirs else 'None'} |")
    print(f"| Total Moved       | {len(unreachable)} |")
    print("| Notes             | Review _safe_to_remove_strict before permanent deletion. Spam/SEO pages should now be quarantined if not in side menu. wp-content/uploads is preserved. |")
    
    print("\n**TASK COMPLETE. Automated cleanup finished. Unused files have been moved to the `_safe_to_remove_strict` directory for manual review and deletion.**")
    
    # Clean up state
    shutil.rmtree(STATE_DIR)

# Run the process
initialize()
live_assets = crawl()
analyze(live_assets)
quarantine()
cleanup_dirs()
report_and_finalize()