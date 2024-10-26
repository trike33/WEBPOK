import re
from colorama import Fore
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk
import webbrowser
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk  # for icons

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

def ext_keyword_check(urls_to_process):
    """
    Function used to find keywords, extensions and filename in URLs
    """
    names = set()
    priority2 = set()
    priority1 = set()
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

    display_treeview(priority1, priority2)

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

# Function to display Treeview with separate priority sections
def display_treeview(priority1, priority2):
    global tree
    root = tk.Tk()
    root.title("Filtered URLs by Priority")
    root.geometry("800x500")

    #load icons
    icons = load_icons()

    # Create Treeview widget with headers
    tree = ttk.Treeview(root, columns=("Extension", "URL"), show="headings")
    tree.heading("Extension", text="Extension")
    tree.heading("URL", text="Filtered URLs")

    # Adjust column width based on longest URL
    max_url_length = max(len(url[0]) for url in priority1.union(priority2))
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

    # Add style for headers and other rows
    style = ttk.Style(root)
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    style.configure("Treeview", rowheight=25)
    tree.tag_configure("header", font=("Helvetica", 10, "bold"), foreground="blue")
    tree.tag_configure("priority1", background="orange", foreground='black')
    tree.tag_configure("priority2", background="yellow", foreground='black')
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