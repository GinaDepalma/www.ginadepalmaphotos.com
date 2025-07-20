Hello. This is your new, complete set of instructions for a single, autonomous task. You will start fresh, analyze the website to find all orphaned files, and then delete them.

This process is designed to be **resumable**. If you are interrupted, I will give you this exact same prompt again, and you will pick up exactly where you left off. You will achieve this by using files on disk to store your state.

You will operate **fully autonomously**. Do not ask for approval or wait for a "Continue" command. Execute the next logical step and then conclude your turn. If more work remains, your final sentence should be "More work remains."

### **Core Principles**

*   **You Are the Loop:** Your shell cannot run `while` loops. Therefore, you will act as the loop. In each turn, you will determine the current state and execute only the *next single step* in the process.
*   **Disk is Your Memory:** Your state is stored in a dedicated directory named `_state_for_cleanup/`. You must read from and write to this directory in every step.
*   **Simplicity is Safety:** You must use the simplest, most reliable shell commands (`mkdir`, `cat`, `grep`, `sed`, `sort`, `comm`, `rm`, `>`, `>>`). You are forbidden from using shell variables (`$()`), `if` statements, or `while` loops.

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
    3.  Generate a master list of all project files, correctly excluding all dot-prefixed directories AND the new state directory.
        ```bash
        find . -type d -name ".*" -prune -o -type d -name "_state_for_cleanup" -prune -o -print > _state_for_cleanup/_all_project_files.txt
        ```
    4.  Initialize the state files inside the new directory.
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
    2.  Get the file to process (the first line of the queue). You will need to read this filename yourself from `_state_for_cleanup/_crawl_queue.txt` and use it in the following commands. Let's call it `CURRENT_FILE`.
    3.  Extract all raw asset strings from `CURRENT_FILE` into a temporary file in the root.
        ```bash
        cat CURRENT_FILE | grep -o -E 'href="([^"]+)"|src="([^"]+)"|url\(([^)]+)\)' > _temp_assets.txt
        ```
    4.  Mark `CURRENT_FILE` as processed by updating the state files.
        ```bash
        echo "CURRENT_FILE" >> _state_for_cleanup/_crawled_files.txt
        sed -i '1d' _state_for_cleanup/_crawl_queue.txt
        ```
    5.  Now, read `_temp_assets.txt`, and for each valid, local asset path you find, perform two appends to the state files: one to `_live_assets.txt` and one (if it's a new `.html` or `.css` file) to `_crawl_queue.txt`.
        ```bash
        # (Conceptual step: you will generate a series of 'echo "path" >> _state_for_cleanup/...' commands here)
        ```
    6.  De-duplicate the state files to keep them clean.
        ```bash
        sort -u -o _state_for_cleanup/_live_assets.txt _state_for_cleanup/_live_assets.txt
        sort -u -o _state_for_cleanup/_crawl_queue.txt _state_for_cleanup/_crawl_queue.txt
        ```
    7.  Clean up the temporary file.
        ```bash
        rm _temp_assets.txt
        ```
    8.  Conclude your turn by stating: "Processed `CURRENT_FILE`. More work remains."

**STATE 3: ANALYSIS**
*   **Check:** Is `_state_for_cleanup/_crawl_queue.txt` empty AND does `_state_for_cleanup/_unreachable_files.txt` NOT exist?
*   **If YES:**
    1.  Announce: "State 3: Crawl complete. Analyzing for unreachable files."
    2.  Use the `comm` command with the correct paths to compare the master list with the live assets.
        ```bash
        sort _state_for_cleanup/_all_project_files.txt -o _state_for_cleanup/_all_project_files.txt
        sort _state_for_cleanup/_live_assets.txt -o _state_for_cleanup/_live_assets.txt
        comm -23 _state_for_cleanup/_all_project_files.txt _state_for_cleanup/_live_assets.txt > _state_for_cleanup/_unreachable_files.txt
        ```
    3.  Conclude your turn by stating: "Analysis complete. Generated unreachable files list. More work remains."

**STATE 4: DELETION**
*   **Check:** Does `_state_for_cleanup/_unreachable_files.txt` exist?
*   **If YES:**
    1.  Announce: "State 4: Deleting unreachable files."
    2.  Read the contents of `_state_for_cleanup/_unreachable_files.txt`. For each file and directory listed, execute the appropriate `rm` or `rm -r` command.
        ```bash
        # (Conceptual step: you will generate and execute a series of 'rm' commands here)
        ```
    3.  After all commands are executed, clean up the state directory itself.
        ```bash
        rm -r _state_for_cleanup
        ```
    4.  Proceed immediately to the Final Report.

### **Final Reporting Protocol**

*   After completing the deletion, generate a final summary report.
*   The report must contain:
    1.  A list of all unreachable files and directories that were successfully deleted.
*   Conclude with the non-negotiable message:
    > **TASK COMPLETE. Automated cleanup finished. The repository is now clean.**