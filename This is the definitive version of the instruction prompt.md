Hello. This is your new, complete set of instructions for a single, autonomous task. You will start fresh, analyze the website to find all orphaned files, and then move them to a quarantine directory for manual review.

This process is designed to be **resumable**. If you are interrupted, I will give you this exact same prompt again, and you will pick up exactly where you left off. You will achieve this by using files on disk to store your state.

You will operate **fully autonomously**. Do not ask for approval or wait for a "Continue" command. Execute the next logical step and then conclude your turn. If more work remains, your final sentence should be "More work remains."

### **Core Principles**

*   **You Are the Loop:** Your shell cannot run `while` loops. Therefore, you will act as the loop. In each turn, you will determine the current state and execute only the *next single step* in the process. For steps that require processing a file from a queue, you must manually read the first line of the queue file and use that filename in the subsequent commands.
*   **Disk is Your Memory:** Your state is stored in a dedicated directory named `_state_for_cleanup/`. You must read from and write to this directory in every step.
*   **Simplicity is Safety:** You must use the simplest, most reliable shell commands (`mkdir`, `cat`, `grep`, `sed`, `sort`, `comm`, `xargs`, `awk`, `dirname`, `realpath`, `cp`, `rm`, `>`, `>>`). You are forbidden from using shell variables (`$()`), `if` statements, or `while` loops.

---

### **The Resumable State Machine Workflow**

You will now begin this process. On this run, and on any subsequent run, you will start your logic from the top of this state machine.

**STATE 1: INITIALIZATION**
*   **Check:** Does the directory `_state_for_cleanup/` exist?
*   **If NO:**
    1.  Announce: "State 1: Initializing a new crawl and creating state directory."
    2.  Create the state directory.
        ```bash
        mkdir -p _state_for_cleanup
        ```
    3.  Generate a master list of all project files, excluding special directories.
        ```bash
        find . -path './_state_for_cleanup' -prune -o -path './_safe_to_remove' -prune -o -path './.*' -prune -o -type f -print | sed 's|^\./||' > _state_for_cleanup/_all_project_files.txt
        ```
    4.  Initialize the state files. The crawl starts with `index.html`.
        ```bash
        echo "index.html" > _state_for_cleanup/_crawl_queue.txt
        > _state_for_cleanup/_crawled_files.txt
        echo "index.html" > _state_for_cleanup/_live_assets.txt
        ```
    5.  Conclude your turn by stating: "Initialization complete. More work remains."

**STATE 2: CRAWLING (The Main Loop)**
*   **Check:** Does `_state_for_cleanup/` exist AND is `_state_for_cleanup/_crawl_queue.txt` NOT empty?
*   **If YES:**
    1.  Announce: "State 2: Processing the next file from the queue."
    2.  Get the file to process. **You will need to manually read the first line** of `_state_for_cleanup/_crawl_queue.txt` and use that filename in the commands below. Let's call it `CURRENT_FILE`.
    3.  **Extract and Sanitize Paths.** This pipeline extracts all linked assets, removes query strings and anchors, and filters out all external/protocol links.
        ```bash
        cat CURRENT_FILE | grep -o -E 'href="[^"]+"|src="[^"]+"' | sed -e 's/href=//' -e 's/src=//' -e 's/"//g' | sed 's/?.*//' | sed 's/#.*//' | grep -v '://' | grep -v -E '^(//|mailto:|tel:|javascript:;)' | grep -v '^$' > _temp_assets_local.txt
        ```
    4.  **Resolve "Pretty Links".** This handles directory links (e.g., `about-us-6/`) by appending `index.html`.
        ```bash
        sed 's|/$|/index.html|' _temp_assets_local.txt > _temp_assets_processed.txt
        ```
    5.  **Normalize Root-Relative Paths.** Isolate paths starting with `/` and prepare them by removing the leading slash.
        ```bash
        grep '^/' _temp_assets_processed.txt | sed 's|^/||' > _temp_assets_normalized.txt
        ```
    6.  **Normalize Standard Relative Paths.** First, save `CURRENT_FILE`'s directory name to a temporary file.
        ```bash
        dirname CURRENT_FILE > _temp_dir.txt
        ```
    7.  Now, combine the directory with the standard relative paths using `awk` and `realpath`. The `awk` script reads the directory from `_temp_dir.txt` and prepends it to each path from `_temp_assets_processed.txt`.
        ```bash
        grep -v '^/' _temp_assets_processed.txt | awk 'BEGIN { getline dir < "_temp_dir.txt" } { if ($0) print dir "/" $0 }' | xargs realpath --canonicalize-missing -s | sed 's|^\./||' >> _temp_assets_normalized.txt
        ```
    8.  Add the fully resolved asset paths to the master list of live assets and de-duplicate.
        ```bash
        cat _temp_assets_normalized.txt >> _state_for_cleanup/_live_assets.txt
        sort -u -o _state_for_cleanup/_live_assets.txt _state_for_cleanup/_live_assets.txt
        ```
    9.  Identify new crawlable files (`.html`, `.css`) and add them to the queue if they haven't been seen before.
        ```bash
        grep -E '\.html$|\.css$' _temp_assets_normalized.txt > _temp_crawl_candidates.txt
        comm -23 <(sort _temp_crawl_candidates.txt) <(sort _state_for_cleanup/_crawled_files.txt) | comm -23 - <(sort _state_for_cleanup/_crawl_queue.txt) >> _state_for_cleanup/_crawl_queue.txt
        ```
    10. Mark `CURRENT_FILE` as processed.
        ```bash
        head -n 1 _state_for_cleanup/_crawl_queue.txt >> _state_for_cleanup/_crawled_files.txt
        sed -i '1d' _state_for_cleanup/_crawl_queue.txt
        ```
    11. Clean up all temporary files for this turn.
        ```bash
        rm _temp_assets_local.txt _temp_assets_processed.txt _temp_assets_normalized.txt _temp_dir.txt _temp_crawl_candidates.txt
        ```
    12. Conclude your turn by stating: "Processed `CURRENT_FILE`. More work remains."

**STATE 3: ANALYSIS**
*   **Check:** Is `_state_for_cleanup/_crawl_queue.txt` empty AND does `_state_for_cleanup/_unreachable_files.txt` NOT exist?
*   **If YES:**
    1.  Announce: "State 3: Crawl complete. Analyzing for unreachable files."
    2.  Sort both lists for accurate comparison.
        ```bash
        sort -u -o _state_for_cleanup/_all_project_files.txt _state_for_cleanup/_all_project_files.txt
        sort -u -o _state_for_cleanup/_live_assets.txt _state_for_cleanup/_live_assets.txt
        ```
    3.  Find orphaned files by comparing the 'all files' list with the 'live assets' list.
        ```bash
        comm -23 _state_for_cleanup/_all_project_files.txt _state_for_cleanup/_live_assets.txt > _state_for_cleanup/_unreachable_files.txt
        ```
    4.  Conclude your turn by stating: "Analysis complete. Generated unreachable files list. More work remains."

**STATE 4: QUARANTINE**
*   **Check:** Does `_state_for_cleanup/_unreachable_files.txt` exist AND does `_state_for_cleanup/_quarantine_complete.flag` NOT exist?
*   **If YES:**
    1.  Announce: "State 4: Moving unreachable files to the _safe_to_remove directory."
    2.  Create the quarantine directory.
        ```bash
        mkdir -p _safe_to_remove
        ```
    3.  Copy the unreachable files to the quarantine directory, preserving their directory structure. Then, remove the originals.
        ```bash
        xargs -a _state_for_cleanup/_unreachable_files.txt cp --parents -t _safe_to_remove
        xargs -a _state_for_cleanup/_unreachable_files.txt rm -f
        ```
    4.  Create a flag file to mark this state as complete.
        ```bash
        touch _state_for_cleanup/_quarantine_complete.flag
        ```
    5.  Conclude your turn by stating: "File quarantine is complete. More work remains."

**STATE 5: FINAL CLEANUP**
*   **Check:** Does `_state_for_cleanup/_quarantine_complete.flag` exist?
*   **If YES:**
    1.  Announce: "State 5: Final cleanup."
    2.  Clean up any now-empty directories from the main project structure.
        ```bash
        find . -mindepth 1 -path './_state_for_cleanup' -prune -o -path './_safe_to_remove' -prune -o -type d -empty -delete
        ```
    3.  Read the list of quarantined files from `_state_for_cleanup/_unreachable_files.txt` to prepare the final report.
    4.  Clean up the state directory itself.
        ```bash
        rm -r _state_for_cleanup
        ```
    5.  Proceed immediately to the Final Reporting Protocol.

### **Final Reporting Protocol**

*   After completing the final cleanup, generate a summary report.
*   The report must contain:
    1.  A list of all unreachable files that were moved to the `_safe_to_remove` directory (this was the content of `_state_for_cleanup/_unreachable_files.txt`).
*   Conclude with the non-negotiable message:
    > **TASK COMPLETE. Automated cleanup finished. Unused files have been moved to the `_safe_to_remove` directory for manual review and deletion.**