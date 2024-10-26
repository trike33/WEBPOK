import json
import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse
from PIL import Image, ImageTk
import webbrowser

# Load URLs from JSON file
def load_urls(inputfile):
    with open(inputfile, "r") as f:
        return json.load(f)

# Parse URL to extract hierarchical components (domain and path segments)
def parse_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    path_segments = parsed.path.strip("/").split("/") if parsed.path else []
    return domain, path_segments

# Main Tkinter Application
class URLTreeviewApp:
    def __init__(self, root, inputfile):
        self.root = root
        self.root.title("Hierarchical URL Viewer with Icons and Clickable URLs")

        # Configure the Treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#E6F4EA",  # Light green background
                        foreground="black",
                        rowheight=30,
                        fieldbackground="#E6F4EA")
        style.map("Treeview", background=[("selected", "#A0D8A4")])

        # Set up the Treeview
        self.tree = ttk.Treeview(root, columns=("URL",), show="tree", height=15)
        self.tree.heading("#0", text="URL Structure", anchor="w")
        self.tree.column("#0", width=600, anchor="w")

        # Add a scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Load icons
        self.load_icons()

        # Load URLs and insert them hierarchically
        self.insert_urls(inputfile)

        # Bind click event to make URLs clickable
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_icons(self):
        # Load images and assign them to a dictionary
        self.icons = {
            "domain": ImageTk.PhotoImage(Image.open("img/domain_icon.png").resize((16, 16))),
            "folder": ImageTk.PhotoImage(Image.open("img/folder_icon.png").resize((16, 16))),
            "url": ImageTk.PhotoImage(Image.open("img/url_icon.png").resize((16, 16))),
        }

    def insert_urls(self, inputfile):
        urls = load_urls(inputfile)
        domains = {}  # Dictionary to hold domain nodes

        for url in urls:
            domain, path_segments = parse_url(url)

            # Insert domain node if it doesn't exist
            if domain not in domains:
                domain_node = self.tree.insert("", "end", text=domain, open=True,
                                               image=self.icons["domain"], tags=("domain",))
                domains[domain] = domain_node
                self.tree.tag_configure("domain", background="#C3E6C3", foreground="black")

            # Insert path segments as child nodes
            parent = domains[domain]
            for i, segment in enumerate(path_segments):
                existing = self.tree.get_children(parent)
                node = None
                for child in existing:
                    if self.tree.item(child, "text") == segment:
                        node = child
                        break
                # If the segment doesn't exist, create a new one
                if not node:
                    color_tag = "folder" if i < len(path_segments) - 1 else "url"
                    icon = self.icons["folder"] if i < len(path_segments) - 1 else self.icons["url"]
                    node = self.tree.insert(parent, "end", text=segment, image=icon, tags=(color_tag,))
                    self.tree.tag_configure("folder", background="#DFF2DF", foreground="black")
                    self.tree.tag_configure("url", background="#E6F4EA", foreground="black")
                parent = node

            # Save the full URL in the node for easy access
            self.tree.set(parent, "URL", url)

    def on_double_click(self, event):
        item_id = self.tree.focus()  # Get the selected item
        url = self.tree.set(item_id, "URL")  # Get the full URL stored in this item
        if url:
            webbrowser.open(url)  # Open the URL in the default web browser

def initialize_tkinter_treecko(inputfile):
    # Initialize Tkinter root
    root = tk.Tk()
    app = URLTreeviewApp(root, inputfile)
    root.mainloop()
