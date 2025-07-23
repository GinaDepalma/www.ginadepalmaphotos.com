import os
import re
import shutil
from pathlib import Path
from collections import deque

# Configuration
STATE_DIR = '_state_for_cleanup'
QUARANTINE_DIR = '_safe_to_remove'
START_FILE = 'index.html'
EXCLUDED_DIRS = {STATE_DIR, QUARANTINE_DIR, '.git', 'wp-content/cache', 'wp-content/uploads/.thumbs'}
CRAWLABLE_EXTS = {'.html', '.css', '.js'}
ALL_FILES_PATH = f'{STATE_DIR}/_all_project_files.txt'
CRAWL_QUEUE_PATH = f'{STATE_DIR}/_crawl_queue.txt'
CRAWLED_FILES_PATH = f'{STATE_DIR}/_crawled_files.txt'
LIVE_ASSETS_PATH = f'{STATE_DIR}/_live_assets.txt'
UNREACHABLE_PATH = f'{STATE_DIR}/_unreachable_files.txt'
DELETED_DIRS_PATH = f'{STATE_DIR}/_deleted_dirs.txt'
QUARANTINE_FLAG = f'{STATE_DIR}/_quarantine_complete.flag'
DIR_CLEANUP_FLAG = f'{STATE_DIR}/_dir_cleanup_complete.flag'

def initialize():
    if os.path.exists(STATE_DIR):
        print("Resuming from existing state.")
        return False  # Not new init
    os.makedirs(STATE_DIR, exist_ok=True)
    
    # Generate master list of all files
    all_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in EXCLUDED_DIRS]
        for file in files:
            if file.startswith('.'):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), '.')
            all_files.append(rel_path)
    with open(ALL_FILES_PATH, 'w') as f:
        f.write('\n'.join(sorted(all_files)) + '\n')
    
    # Initialize queues and sets
    with open(CRAWL_QUEUE_PATH, 'w') as f:
        f.write(START_FILE + '\n')
    with open(CRAWLED_FILES_PATH, 'w') as f:
        pass
    with open(LIVE_ASSETS_PATH, 'w') as f:
        f.write(START_FILE + '\n')
    
    print("Initialization complete.")
    return True

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
    rel_path = os.path.relpath(full_path, os.getcwd())
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
                    normalized.add(norm)
            except ValueError as e:
                print(f"Skipping invalid path {link}: {e}")
                continue
        
        # Filter excluded
        normalized = {p for p in normalized if not any(p.startswith(ex) for ex in EXCLUDED_DIRS)}
        
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
    unreachable = sorted(all_files - live_assets)
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
            if dir in EXCLUDED_DIRS or dir.startswith('.'):
                continue
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                deleted_dirs.append(os.path.relpath(dir_path, '.'))
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
    print("| Notes             | Review _safe_to_remove before permanent deletion. |")
    
    print("\n**TASK COMPLETE. Automated cleanup finished. Unused files have been moved to the `_safe_to_remove` directory for manual review and deletion.**")
    
    # Clean up state
    shutil.rmtree(STATE_DIR)

# Run the process
initialize()
live_assets = crawl()
analyze(live_assets)
quarantine()
cleanup_dirs()
report_and_finalize()