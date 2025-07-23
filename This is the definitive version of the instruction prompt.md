
Hello. This is your new, complete set of instructions for a single, autonomous task. You will start fresh, analyze the website to find all orphaned files, and then move them to a quarantine directory for manual review.

This process is designed to be **resumable**. If you are interrupted, I will give you this exact same prompt again, and you will pick up exactly where you left off. You will achieve this by using files on disk to store your state.

You will operate **fully autonomously**. Do not ask for approval or wait for a "Continue" command. Execute the next logical step and then conclude your turn. If more work remains, your final sentence should be "More work remains."

### **Core Principles**

*   **You Are the Loop:** Your shell cannot run `while` loops. Therefore, you will act as the loop. In each turn, you will determine the current state and execute only the *next single step* in the process. You must operate on one file at a time where indicated.
*   **Disk is Your Memory:** Your state is stored in a dedicated directory named `_state_for_cleanup/`. You must read from and write to this directory in every step.
*   **Simplicity is Safety:** You must use the simplest, most reliable shell commands (`mkdir`, `cat`, `grep`, `sed`, `sort`, `xargs`, `awk`, `dirname`, `realpath`, `cp`, `rm`, `>`, `>>`). You are forbidden from using `comm`, shell variables (`$()`), `if` statements, `while` loops, or process substitution (`<()`).

---

### **The Resumable State Machine Workflow**

**STATE 1: INITIALIZATION**
*   **Check:** Does the directory `_state_for_cleanup/` exist?
*   **If NO:**
    1.  Announce: "State 1: Initializing a new crawl and creating state directory."
    2.  Create the state directory.
        ```bash
        mkdir -p _state_for_cleanup
        ```
    3.  Generate a master list of all project files.
        ```bash
        find . -path './_state_for_cleanup' -prune -o -path './_safe_to_remove' -prune -o -path './.*' -prune -o -type f -print | sed 's|^\./||' > _state_for_cleanup/_all_project_files.txt
        ```
    4.  Initialize the state files.
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
    2.  Get `CURRENT_FILE` by manually reading the first line of `_state_for_cleanup/_crawl_queue.txt`.
    3.  **Extract, Sanitize, and Filter Paths.** This pipeline extracts links, cleans them of query strings/anchors, and filters out all non-local paths.
        ```bash
        cat CURRENT_FILE | grep -o -E 'href="[^"]+"|src="[^"]+"' | sed -e 's/href=//' -e 's/src=//' -e 's/"//g' | sed 's/?.*//' | sed 's/#.*//' | grep -v '://' | grep -v -E '^(//|mailto:|tel:|javascript:;)' | grep -v '^$' > _temp_assets_local.txt
        ```
    4.  **Resolve "Pretty Links" and Normalize Paths.** This series of commands resolves all found paths to their full, root-relative form.
        ```bash
        sed 's|/$|/index.html|' _temp_assets_local.txt > _temp_assets_processed.txt
        grep '^/' _temp_assets_processed.txt | sed 's|^/||' > _temp_assets_normalized.txt
        dirname CURRENT_FILE > _temp_dir.txt
        grep -v '^/' _temp_assets_processed.txt | awk 'BEGIN { getline dir < "_temp_dir.txt" } { if ($0) print dir "/" $0 }' | xargs realpath --canonicalize-missing -s | sed 's|^\./||' >> _temp_assets_normalized.txt
        ```
    5.  Add the fully resolved paths to the `_live_assets.txt` list and de-duplicate it.
        ```bash
        cat _temp_assets_normalized.txt >> _state_for_cleanup/_live_assets.txt
        sort -u -o _state_for_cleanup/_live_assets.txt _state_for_cleanup/_live_assets.txt
        ```
    6.  **Identify and Add New Crawlable Files (Robust Method).** First, get a list of potential candidates.
        ```bash
        grep -E '\.html$|\.css$' _temp_assets_normalized.txt | sort -u > _temp_crawl_candidates.txt
        ```
    7.  **Process one candidate at a time.** Manually read the first line of `_temp_crawl_candidates.txt`. For that single filename, check if it already exists in `_crawled_files.txt` or `_crawl_queue.txt`.
        ```bash
        # Conceptual: You will perform this logic for the first file in _temp_crawl_candidates.txt
        # Example for a candidate file named "new_page.html":
        # grep -q -x "new_page.html" _state_for_cleanup/_crawled_files.txt
        # grep -q -x "new_page.html" _state_for_cleanup/_crawl_queue.txt
        # If both checks fail (return non-zero), then append it:
        # echo "new_page.html" >> _state_for_cleanup/_crawl_queue.txt
        ```    8.  After processing the single candidate, remove it from the candidate list and repeat the process if more candidates remain. If no candidates remain, proceed to the next step.
    9.  Mark `CURRENT_FILE` as processed.
        ```bash
        head -n 1 _state_for_cleanup/_crawl_queue.txt >> _state_for_cleanup/_crawled_files.txt
        sed -i '1d' _state_for_cleanup/_crawl_queue.txt
        ```
    10. Clean up all temporary files.
        ```bash
        rm _temp_assets_local.txt _temp_assets_processed.txt _temp_assets_normalized.txt _temp_dir.txt _temp_crawl_candidates.txt
        ```
    11. Conclude your turn by stating: "Processed `CURRENT_FILE`. More work remains."

**STATE 3: ANALYSIS**
*   **Check:** Is `_state_for_cleanup/_crawl_queue.txt` empty AND does `_state_for_cleanup/_unreachable_files.txt` NOT exist?
*   **If YES:**
    1.  Announce: "State 3: Crawl complete. Analyzing for unreachable files."
    2.  Sort and compare the master file list with the live assets list to find orphans.
        ```bash
        sort -u -o _state_for_cleanup/_all_project_files.txt _state_for_cleanup/_all_project_files.txt
        sort -u -o _state_for_cleanup/_live_assets.txt _state_for_cleanup/_live_assets.txt
        comm -23 _state_for_cleanup/_all_project_files.txt _state_for_cleanup/_live_assets.txt > _state_for_cleanup/_unreachable_files.txt
        ```
    3.  Conclude your turn by stating: "Analysis complete. Generated unreachable files list. More work remains."

**STATE 4: QUARANTINE**
*   **Check:** Does `_state_for_cleanup/_unreachable_files.txt` exist AND does `_state_for_cleanup/_quarantine_complete.flag` NOT exist?
*   **If YES:**
    1.  Announce: "State 4: Moving unreachable files to the _safe_to_remove directory."
    2.  Create the quarantine directory.
        ```bash
        mkdir -p _safe_to_remove
        ```
    3.  Copy the unreachable files to quarantine, preserving structure, then remove the originals.
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
    2.  Clean up any now-empty directories from the project.
        ```bash
        find . -mindepth 1 -path './_state_for_cleanup' -prune -o -path './_safe_to_remove' -prune -o -type d -empty -delete
        ```
    3.  Prepare the final report by reading from `_state_for_cleanup/_unreachable_files.txt`.
    4.  Clean up the state directory.
        ```bash
        rm -r _state_for_cleanup
        ```
    5.  Proceed immediately to the Final Reporting Protocol.

### **Final Reporting Protocol**

*   After completing the final cleanup, generate a summary report.
*   The report must contain:
    1.  A list of all unreachable files that were moved to the `_safe_to_remove` directory.
*   Conclude with the non-negotiable message:
    > **TASK COMPLETE. Automated cleanup finished. Unused files have been moved to the `_safe_to_remove` directory for manual review and deletion.**