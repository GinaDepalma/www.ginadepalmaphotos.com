import os
import re
from bs4 import BeautifulSoup
import shutil
from datetime import datetime

# Configuration
SITE_ROOT = '.'  # Current directory as site root
EXCLUDED_PREFIXES = ['wp-content/cache/', 'wp-content/uploads/', '.git/', '_state_for_cleanup', '_safe_to_remove']

def remove_blog_and_footer_blocks():
    modified_files = []
    for root, dirs, files in os.walk(SITE_ROOT):
        # Skip excluded directories
        rel_root = os.path.relpath(root, SITE_ROOT).replace('\\', '/')
        if any(rel_root.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue
        
        if 'index.html' in files:
            file_path = os.path.join(root, 'index.html')
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            modified = False
            
            # Remove the "Latest From Our Blog" block (div with class="column2 footer_col2")
            blog_blocks = soup.find_all('div', class_='column2 footer_col2')
            for block in blog_blocks:
                block.decompose()
                modified = True
                print(f"Removed 'Latest From Our Blog' block from {file_path}")
            
            # Remove the "| Managed By Dan Webmaster" from textwidget div
            textwidgets = soup.find_all('div', class_='textwidget')
            for div in textwidgets:
                # Iterate over contents and remove from " | Managed By " onward
                contents = list(div.contents)
                for i, child in enumerate(contents):
                    if isinstance(child, str) and '| Managed By' in child:
                        # Remove this text node and the following <a> if present
                        div.contents = div.contents[:i]
                        modified = True
                        print(f"Removed '| Managed By Dan Webmaster' block from {file_path}")
                        break
            
            if modified:
                # Backup original
                backup_path = file_path + '.bak'
                if not os.path.exists(backup_path):
                    shutil.copy(file_path, backup_path)
                    print(f"Backed up original to {backup_path}")
                
                # Write modified HTML
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                modified_files.append(file_path)
    
    return modified_files

def report(modified_files):
    print("\nSummary Report:")
    print(f"Modified Files: {len(modified_files)}")
    if modified_files:
        print("Files modified:")
        for file in modified_files:
            print(f"- {file}")
    else:
        print("No blocks found to remove.")
    print("| Notes             | Review modified index.html files. Original files backed up with .bak extension. |")
    
    print("\n**TASK COMPLETE. Specified blocks removed from index.html files where found.**")

# Run the process
print(f"Starting removal of specified blocks at {datetime.now().strftime('%I:%M %p PDT on %B %d, %Y')}...")
modified_files = remove_blog_and_footer_blocks()
report(modified_files)