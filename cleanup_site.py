import os
import re
import shutil
from bs4 import BeautifulSoup
from datetime import datetime  # Added import for datetime

# Configuration
SITE_ROOT = '.'  # Current directory as site root
EXCLUDED_PREFIXES = ['wp-content/cache/', 'wp-content/uploads/', '.git/', '_state_for_cleanup', '_safe_to_remove']
MENU_ITEM_TO_REMOVE = 'Contact'  # The exact text of the menu item to remove, linked to contact-4 folder

def remove_contact_menu():
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
            
            # Find menu blocks (vertical menu or similar)
            menu_lists = soup.find_all(['ul', 'nav'], class_=re.compile(r'(vertical_menu|main-menu|nav-menu|side_menu|menu_area|qode_vertical_menu)', re.IGNORECASE))
            modified = False
            for menu in menu_lists:
                for li in menu.find_all('li'):
                    a = li.find('a')
                    if a and a.text.strip() == MENU_ITEM_TO_REMOVE:
                        # Check if the href points to contact-4 or a related path
                        href = a.get('href', '').strip()
                        if href and ('contact-4' in href or 'contact-4/index.html' in href):
                            li.decompose()  # Remove the <li> element
                            modified = True
                            print(f"Removed 'Contact' menu item (linked to contact-4) from {file_path}")
            
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

def quarantine_contact_folder():
    contact_folder = 'contact-4'
    if os.path.exists(contact_folder) and not any(contact_folder.startswith(prefix.rstrip('/')) for prefix in EXCLUDED_PREFIXES):
        dest = os.path.join(QUARANTINE_DIR, contact_folder)
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
        if os.path.exists(dest):
            backup_num = 1
            while os.path.exists(f"{dest}~{backup_num}"):
                backup_num += 1
            dest = f"{dest}~{backup_num}"
        shutil.move(contact_folder, dest)
        print(f"Quarantined folder: {contact_folder}")
        return [contact_folder]
    return []

def report(modified_files, quarantined_folders):
    print("\nSummary Report:")
    print(f"Modified Files: {len(modified_files)}")
    if modified_files:
        print("Files modified:")
        for file in modified_files:
            print(f"- {file}")
    print(f"Quarantined Folders: {len(quarantined_folders)}")
    if quarantined_folders:
        print("Folders quarantined:")
        for folder in quarantined_folders:
            print(f"- {folder}")
    else:
        print("No 'contact-4' folder found to quarantine.")
    print("| Notes             | Review _safe_to_remove_menu_folders before permanent deletion. 'Contact' menu items and contact-4 folder removed where found; wp-content/uploads is preserved. |")
    
    print("\n**TASK COMPLETE. 'Contact' menu items and contact-4 folder removed where found. Original files backed up with .bak extension, folder moved to _safe_to_remove_menu_folders.**")

# Run the process
print(f"Starting removal of 'Contact' menu items and contact-4 folder at {datetime.now().strftime('%I:%M %p PDT on %B %d, %Y')}...")
QUARANTINE_DIR = '_safe_to_remove_menu_folders'  # Define here for use in quarantine
modified_files = remove_contact_menu()
quarantined_folders = quarantine_contact_folder()
report(modified_files, quarantined_folders)