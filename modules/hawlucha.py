import re
from colorama import Fore
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk
import webbrowser
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk  # for icons
import json
from collections import defaultdict
import requests as r
from bs4 import BeautifulSoup
from tabulate import tabulate

keywords = [
    "username", "user", "userid", "user_id", "user_name", "login", "login_id",
    "account", "account_name", "uid", "email", "email_address", "email_id",
    "first_name", "last_name", "full_name", "nickname", "useraccount", "display_name",
    "profile_name", "userlogin", "credentials", "principal", "api_user", "username_field",
    "password", "pass", "passphrase", "passkey", "secret", "secret_key", "auth", "auth_code",
    "authentication", "passwd", "pwd", "password_hash", "password_hashing", "user_password",
    "encrypted_password", "old_password", "new_password", "confirm_password", "retype_password",
    "reset_password", "password_reset", "password_recovery", "password_reset_link",
    "password_reset_token", "login_password", "temporary_password", "recovery_code",
    "api_key", "api_secret", "api_token", "auth_token", "access_token", "api_access_key",
    "bearer_token", "oauth_token", "oauth_key", "session_token", "session_key",
    "client_secret", "client_id", "client_key", "token", "access_key", "api_access",
    "api_credentials", "api_auth", "token_key", "jwt", "jwt_secret", "jwt_token", "api_id",
    "api_user", "api_pass", "api_passcode", "app_key", "app_secret", "user_token",
    "user_secret", "refresh_token", "session_cookie", "access_secret", "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY", "GCP_PROJECT_ID", "GCP_SERVICE_ACCOUNT", "DB_PASSWORD",
    "DB_USERNAME", "DB_HOST", "DB_PORT", "MYSQL_PASSWORD", "POSTGRES_PASSWORD", "REDIS_PASSWORD",
    "DATABASE_URL", "DATABASE_PASS", "DATABASE_USER", "DB_CONFIG", "MONGO_URI", "MONGO_PASS",
    "MONGO_USER", "RDS_PASSWORD", "S3_BUCKET", "S3_SECRET_KEY", "GITHUB_TOKEN", "SLACK_API_TOKEN",
    "API_SECRET_KEY", "ENV_SECRET", "SERVER_KEY", "SSH_KEY", "SSH_PRIVATE_KEY", "SSH_PUBLIC_KEY",
    "PGP_PRIVATE_KEY", "PGP_PUBLIC_KEY", "GOOGLE_CLOUD_KEY", "GITHUB_ACCESS_TOKEN",
    "TWITTER_API_KEY", "TWITTER_API_SECRET", "JWT_SECRET", "OAUTH_CLIENT_SECRET", "OAUTH_CLIENT_ID",
    "config", "configuration", "settings", "config_file", "config_json", "config_yaml", "config_env",
    "settings_file", "secret_config", "secretfile", "credentials_file", "api_credentials", "keyring",
    "keystore", "passwordfile", "keyfile", "backup", "backup_password", "backup_credentials",
    "old_password", "backup_key", "backup_secret", "archived_password", "backup_config",
    "previous_password", "old_config", "recovery_password", "default_password", "default_credentials",
    "backup_auth"
]

valid_extensions = {
        '.xls', '.xml', '.xlsx', '.json', '.pdf', '.sql', '.doc', '.docx', '.pptx', '.txt', '.zip', 
        '.tar.gz', '.tgz', '.bak', '.7z', '.rar', '.log', '.cache', '.secret', '.db', '.backup', '.yml',
        '.gz', '.config', '.csv', '.yaml', '.md', '.md5', '.tar', '.xz', '.7zip', '.p12', '.pem', '.key',
        '.crt', '.csr', '.sh', '.pl', '.py', '.java', '.class', '.jar', '.war', '.ear', '.sqlitedb',
        '.sqlite3', '.dbf', '.db3', '.accdb', '.mdb', '.sqlcipher', '.gitignore', '.env', '.ini', '.conf',
        '.properties', '.plist', '.cfg'
    }

def normalize_version(version):
    """
    Normalize shorthand version inputs to full XX.XX.XX format.
    Examples:
        '3' -> '3.0.0'
        '3.7' -> '3.7.0'
        '3.7.2' -> '3.7.2'
    """
    parts = version.split(".")
    while len(parts) < 3:
        parts.append("0")
    return ".".join(parts[:3])

def check_for_recursion(constraint):
    """
    Checks if a constraint needs recurion and returns the number of rounds needed to parse it
    """
    lower_than_count = constraint.count("<")
    greater_than_count = constraint.count(">")

    return lower_than_count+greater_than_count

def find_first_matched(target_chars, string):
    """
    Find the first character or substring from target_chars that appears in the string.

    Args:
        target_chars (list): A list of characters or substrings to search for.
        string (str): The string to search in.

    Returns:
        str: The first matched character or substring.
        None: If no characters or substrings are matched.
    """
    # Sort target_chars to check longer substrings first (so '<=' and '>=' are matched before '<' and '>')
    target_chars.sort(key=lambda x: -len(x))  # Sort by length in descending order
    matches = ((char, string.find(char)) for char in target_chars if string.find(char) != -1)

    # Get the first match (smallest index)
    first_match = min(matches, key=lambda x: x[1], default=(None, -1))
    return first_match[0]


def version_extractor(constraint, start_character):
    # Find the start and end positions of the version
    start = constraint.find(start_character) + 1
    end = min(
        (constraint.find(op, start) for op in ("<", ">") if constraint.find(op, start) != -1),
        default=len(constraint)
    )
    version = constraint[start:end].strip()
    version = version.replace("=", "")
    version = version.replace("-beta", "")
    return version

def parse_global_constraints(constraints):
    """
    Parse constraint strings into a list of tuples.
    Each tuple contains the comparator and the normalized version.
    Examples:
    '<2.4.1' -> ('<', '2.4.1')
    """
    global_parsed = []
    for constraint in constraints.split(","):
        constraint = constraint.strip()
        local_parsed = []
        rounds = check_for_recursion(constraint)
        target_chars = ["<", ">", "<=", ">="]
        for i in range(rounds):
            result = find_first_matched(target_chars, constraint)
            if result == ">=":
                comparator = ">="
                version = version_extractor(constraint, comparator)
                remove = f"{comparator}{version}"
                local_parsed.append((comparator, normalize_version(version)))
                constraint = constraint.replace(version, "") # we remove to avoid duplicates
            elif result == "<=":
                comparator = "<="
                version = version_extractor(constraint, comparator)
                remove = f"{comparator}{version}"
                local_parsed.append((comparator, normalize_version(version)))
                constraint = constraint.replace(remove, "") #we remove to avoid duplicates
            elif result == ">":
                comparator = ">"
                version = version_extractor(constraint, comparator)
                remove = f"{comparator}{version}"
                local_parsed.append((comparator, normalize_version(version)))
                constraint = constraint.replace(remove, "") #we remove to avoid duplicates
            elif result == "<":
                comparator = "<"
                version = version_extractor(constraint, comparator)
                remove = f"{comparator}{version}"
                local_parsed.append((comparator, normalize_version(version)))
                constraint = constraint.replace(remove, "") #we remove to avoid duplicates
            else:
                print(f"Unkown operand in constraint: {constraint}")
        global_parsed.append(local_parsed)
    return global_parsed

def is_version_allowed(target_version, constraints):
    """
    Check if a version is allowed under the given constraints.

    Args:
    version (str): The version string to check.
    constraints (list): A list of tuples containing comparator and version strings.

    Returns:
    bool: True if the version is allowed, False otherwise.
    """
    global_result = True #only set it to true if complies with all constraints
    local_result = True
    for constraint in constraints:
        for comparator, constraint_version in constraint:
            if comparator == "<" and not target_version < constraint_version:
                local_result =  False
                global_result = False
            elif comparator == ">" and not target_version > constraint_version:
                local_result =  False
                global_result = False
            elif comparator == "<=" and not target_version <= constraint_version:
                local_result =  False
                global_result = False
            elif comparator == ">=" and not target_version >= constraint_version:
                local_result =  False
                global_result = False

        """if local_result:
            print(f"Version {target_version} is inside {constraint}")
        else:
            print(f"Version {target_version} is not inside {constraint}") 
        """
    return global_result

def check_vulnerabilities(target_version, constraints_string):
    # Parse constraints
    constraints = parse_global_constraints(constraints_string)

    #print("Constraints:", constraints)

    target_version = normalize_version(target_version)

    if target_version != "0.0.0":
        result = is_version_allowed(target_version, constraints)
        return result

    elif target_version == "0.0.0":
        return True
    
    else:
        print(f"Invalid target version: {target_version}, format must be XX.XX.XX")
        return False


def print_table(headers, data):
    """
    Helper function to pretty print the results
    """
    #print(f"\n{headers[0]}{" "*20}{headers[1]}{" "*20}{headers[2]}")
    #print("-" * 90)
    table_entries = []
    for item in data:
        #print(item)
        if len(item) != 0:
            table_entry = []
            severity = item[0][0]
            table_entry.append(severity)
            vulnerability = item[0][1:20]
            table_entry.append(vulnerability)
            #versions = item[1]
            if len(item) == 3:
                link = "https://security.snyk.io"+item[2]
            else:
                link = "Not found"
            table_entry.append(link)
            table_entries.append(table_entry)
            #print(f"{severity}{" "*20}{vulnerability}{" "*20}{link}\n")

    print(tabulate(table_entries, headers=headers, tablefmt="grid"))
    print(f"\nVulnerabilities found >>> {len(data)}")
    input("\nAwaiting to return to main menu...")

def snyk_check():

    #Notes(7/1/2025)
    """
    1. All data is on only 1 HTML page
    2. We parse HTML code rather than using an API
    """
    #Global variables
    print("snyk URL sample: https://security.snyk.io/package/composer/moodle%2Fmoodle")
    url = input("Please enter the snyk URL that you want to check: ")
    #url sample: https://security.snyk.io/package/composer/moodle%2Fmoodle
    version = input("Please enter the target version or enter to view all: ")
    if len(version) == 0:
        version = "0.0.0" #magic version number to print all vulns

    column_headers = ["Severity","Vulnerability", "Link"]
    global_data = []

    version = normalize_version(version)

    print(f"\n\tURL >>> {url}")
    print(f"\tVersion tested >>> {version}")

    response = r.get(url=url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table')
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                cell_data = [cell.text.strip() for cell in cells]

                if len(cell_data) == 0:
                    continue

                i = [cell.find("a") for cell in cells]
                for a_tag in i:
                    if a_tag and a_tag.has_attr("href") and "vuln" in a_tag["href"]:
                        cell_data.append(a_tag["href"])
                
                constraints_string = cell_data[1]
                if check_vulnerabilities(version, constraints_string):
                    global_data.append(cell_data)

            if len(global_data) <= 1:
                print("No vulnerailities found!")
            else:
                print_table(column_headers, global_data)
        else:
            print("table not found!")
    else:
        print(f"Error >>> URL: {url} returned Response code: {response.status_code}")

def scope_view(json_file):
    include_dict, exclude_dict = parse_json(json_file)
    output = format_output(include_dict, exclude_dict)
    print(output)

def parse_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    include_dict = defaultdict(list)
    exclude_dict = defaultdict(list)

    # Helper function to clean host and file path, remove special characters
    def clean_host_file(item):
        host = re.sub(r'\\', '', item.get('host', '')).replace('^', '').replace('$', '')
        file_path = re.sub(r'\\', '', item.get('file', '')).replace('^', '').replace('$', '')

        # Replace ".*" with "/*" in file paths for more universal path handling
        file_path = file_path.replace('.*', '/*')

        # Handle wildcard hosts (e.g. "^.+\\.example\\.com$" -> "*.example.com")
        if host.startswith('.+'):
            host = f"*.{host[3:]}"
        
        return host, file_path

    # Process the include list
    for item in data.get('target', {}).get('scope', {}).get('include', []):
        if item.get('enabled', False):  # Safely check for 'enabled' field
            host, file_path = clean_host_file(item)
            include_dict[host].append(file_path)

    # Process the exclude list
    for item in data.get('target', {}).get('scope', {}).get('exclude', []):
        if item.get('enabled', False):
            host, file_path = clean_host_file(item)
            exclude_dict[host].append(file_path)

    return include_dict, exclude_dict

def normalize_path(path):
    """
    Normalizes paths by ensuring they either always have or always don't have a trailing '/*'.
    In this case, we will standardize paths by ensuring they end with '/*'.
    """
    if not path.endswith('/*'):
        return path.rstrip('/') + '/*'
    return path

def domain_without_wildcard(domain):
    """
    Given a domain like *.example.com, return the non-wildcard version (example.com).
    If the domain is already non-wildcard, return it as is.
    """
    if domain.startswith('*.'):
        return domain[2:]
    return domain

def format_output(include_dict, exclude_dict):
    output_lines = []
    seen_paths = set()  # To keep track of already printed paths
    wildcard_domains = set()  # To keep track of wildcard domains (e.g. *.domain.com)

    # Helper function to clean double slashes and check for duplicates
    def clean_and_add(domain, path, color_code):
        # Normalize the path by ensuring it ends with '/*' for consistency
        normalized_path = normalize_path(path)
        
        # Construct the full domain + path
        full_path = f"{domain}{normalized_path}"
        
        # Replace double slashes with single slashes
        cleaned_path = re.sub(r'//+', '/', full_path)

        # Check if the path was already printed (based on normalized form)
        if cleaned_path not in seen_paths:
            seen_paths.add(cleaned_path)  # Mark this path as printed
            output_lines.append(f"{color_code}{cleaned_path}\033[0m")

    # Process include dict (green paths)
    for domain in sorted(include_dict):
        # Check if the domain is a wildcard (e.g., *.domain.com)
        if domain.startswith('*.'):
            wildcard_domains.add(domain_without_wildcard(domain))

        for path in sorted(include_dict[domain]):
            # If we have both the wildcard and non-wildcard version, skip the non-wildcard
            base_domain = domain_without_wildcard(domain)
            if base_domain in wildcard_domains and not domain.startswith('*.'):
                continue  # Skip adding non-wildcard if wildcard exists
            
            clean_and_add(domain, path, "\033[92m")  # Green for include

    # Process exclude dict (red paths)
    for domain in sorted(exclude_dict):
        for path in sorted(exclude_dict[domain]):
            normalized_exclude_path = normalize_path(path)
            if domain not in include_dict or normalized_exclude_path not in [normalize_path(p) for p in include_dict[domain]]:
                clean_and_add(domain, path, "\033[91m")  # Red for exclude

    return "\n".join(output_lines)

def guess_params(urls_to_process):
    """
    Function used to find guessable(numeric) parameters values on URLs
    """
    guess_urls = set()
    priority2 = set()
    priority1 = set()
    for url in urls_to_process:
        if any(char.isdigit() for char in url):
            guess_urls.add(url)
        else:
            continue

    display_treeview(priority1, priority2, guess_urls)


def ext_keyword_check(urls_to_process):
    """
    Function used to find keywords, extensions and filename in URLs
    """
    names = set()
    priority2 = set()
    priority1 = set()
    guess_urls = set()
    global valid_extensions, keywords

    for extension in valid_extensions:
        name = extension[1:]
        names.add(name)

    #Attempt to find extensions
    #print(f"{Fore.RED}=== PRIORITY 2 ===")
    #priority2.add("=== PRIORITY 2 ===")
    for item in urls_to_process:
        path = urlparse(item).path
        extension = '.' + path.split('.')[-1] if '.' in path else ''
        if extension in valid_extensions:
            priority2.add(item)
        """if any(name in item for name in names):
            priority2.add(item)"""
    #for thing_to_print in things_to_print:
        #print(f"{Fore.RED}{thing_to_print}\n")

    #Attempt to find keywords
    #things_to_print.add("=== PRIORITY 1 ===")
    #print(f"{Fore.YELLOW}=== PRIORITY 1 ===")
    for item in urls_to_process:
        if any(keyword in item for keyword in keywords):
            priority1.add(item)
            #print(f"{Fore.YELLOW}{item}\n")

    display_treeview(priority1, priority2, guess_urls)

# Function to handle URL click event and open in browser
def open_url(event):
    selected_item = tree.focus()  # Get the selected item
    if not selected_item:
        return
    url = tree.item(selected_item, "values")[1]  # Get URL from the selected row
    if url.startswith("http"):
        webbrowser.open(url)  # Open URL in default browser

# Function to load icons for priority display
def load_icons():
    icons = {
        "priority1": ImageTk.PhotoImage(Image.open("img/priority1.png").resize((16, 16))),
        "priority2": ImageTk.PhotoImage(Image.open("img/priority2.jpg").resize((16, 16))),
        "header": ImageTk.PhotoImage(Image.open("img/hawlucha.png").resize((16, 16))),
    }
    return icons

def has_tag(item_id, tag):
    return tag in tree.item(item_id, "tags")

# Function to display Treeview with separate priority sections
def display_treeview(priority1, priority2, guess_urls, both=False):
    """
    Function to display Treeview with separate priority sections
    priority1: priority 1 urls(keywords)
    priority2: priority 2 urls(extensions)
    guess_urls: urls with guessable(numeric) parameters
    both: boolean parameter to instruct if perform both displays or only 1
    """
    global tree
    root = tk.Tk()
    root.title("Filtered URLs")
    root.geometry("800x500")

    #load icons
    icons = load_icons()

    # Create Treeview widget with headers
    tree = ttk.Treeview(root, columns=("Extension", "URL"), show="headings")
    tree.heading("Extension", text="Extension")
    tree.heading("URL", text="Filtered URLs")

    # Adjust column width based on longest URL
    max_url_length = 1000
    url_column_width = min(max(300, max_url_length * 7), 700)  # limit max width to 700
    tree.column("URL", width=url_column_width, anchor="w")
    tree.column("Extension", width=100, anchor="center")

    # Insert Priority 1 URLs
    if priority1:
        tree.insert("", tk.END, values=("", "=== PRIORITY 1 ==="), image=icons["header"], tags=("header",))
        for url in priority1:
            path = urlparse(url).path
            ext = '.' + path.split('.')[-1] if '.' in path else '.html'
            tree.insert("", tk.END, values=(ext, url), image=icons["priority1"], tags=("priority1",))

    # Insert Priority 2 URLs
    if priority2:
        tree.insert("", tk.END, values=("", "=== PRIORITY 2 ==="), tags=("header",))
        for url in priority2:
            path = urlparse(url).path
            ext = '.' + path.split('.')[-1] if '.' in path else '.html'
            tree.insert("", tk.END, values=(ext, url), image=icons["priority2"], tags=("priority2",))
    if guess_urls:
        tree.insert("", tk.END, values=("", "=== POSSIBLY GUESSABLE URLs(nums) ==="), tags=("header"))
        for url in guess_urls:
            path = urlparse(url).path
            ext = '.' + path.split('.')[-1] if '.' in path else '.html'
            tree.insert("", tk.END, values=(ext, url), image=icons["priority2"], tags=("guessable urls",))


    # Add style for headers and other rows
    style = ttk.Style(root)
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    style.configure("Treeview", rowheight=25)
    tree.tag_configure("header", font=("Helvetica", 10, "bold"), foreground="blue")
    
    if both:
            tree.tag_configure("priority1", background="orange", foreground='black')
            tree.tag_configure("priority2", background="yellow", foreground='black')
            tree.tag_configure("guessable urls", background="turquoise1", foreground='black')
    else:
        if has_tag(tree.get_children()[1], "priority1") and has_tag(tree.get_children()[2], "priority2"):
            tree.tag_configure("priority1", background="orange", foreground='black')
            tree.tag_configure("priority2", background="yellow", foreground='black')
        elif has_tag(tree.get_children()[3], "guessable urls"):
            tree.tag_configure("guessable urls", background="turquoise1", foreground='black')
        
    style.map("Treeview", background=[("selected", "darkred")], foreground=[("selected", "white")])

    # Attach Treeview and scrollbar to the Tkinter window
    tree.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Add a ScrolledText widget for displaying the full URL on selection
    scrolled_text = ScrolledText(root, height=3, wrap="none")
    scrolled_text.pack(fill="x")
    
    # Function to display the selected URL in the ScrolledText widget
    def show_full_url(event):
        selected_item = tree.focus()
        if selected_item:
            url = tree.item(selected_item, "values")[1]
            scrolled_text.delete("1.0", tk.END)
            scrolled_text.insert(tk.END, url)

    # Bind events for double-click to open URL and single-click to display full URL
    tree.bind("<Double-1>", open_url)
    tree.bind("<<TreeviewSelect>>", show_full_url)

    root.mainloop()
