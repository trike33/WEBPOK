import json
from collections import defaultdict
from urllib.parse import urlparse
import os
from colorama import Fore, Style

def write_to_json(url_set, file_name):
    """Saves a set of URLs to a JSON file by converting it to a list."""
    with open(file_name, 'a') as file:
        json.dump(list(url_set), file, indent=4)
        file.close()


def build_tree(url_list):
    """Function to build a tree structure from a list of URLs."""
    tree = lambda: defaultdict(tree)  # Tree structure using nested defaultdict
    root = tree()

    for url in sorted(url_list):
        parsed_url = urlparse(url)
        scheme_and_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"  # Combine scheme and domain
        path_parts = parsed_url.path.strip('/').split('/')  # Break path into components
        
        current_level = root[scheme_and_domain]
        for part in path_parts:
            current_level = current_level[part]

    return root

def print_tree(node, indent=""):
    """Recursive function to print the tree structure."""
    for key, value in sorted(node.items()):
        if isinstance(value, defaultdict):
            # Check if it's a directory (either it has subdirectories or it's a directory without extension)
            if '.' not in key:
                if '://' in key:
                    # This is the scheme + domain (print it as a full URL without a trailing slash)
                    print(Fore.GREEN + indent + key)
                else:
                    # This is a directory (print with trailing slash)
                    print(Fore.GREEN + indent + key + '/')
            else:
                # This is a file (print as-is)
                print(Fore.GREEN + indent + key)
            print_tree(value, indent + "-----")
        else:
            # If it's the last element (a file)
            print(Fore.GREEN + indent + key)

def load_and_print_urls(file_name):
    """Loads URLs from a JSON file, builds the tree, and prints the tree structure."""
    with open(file_name, 'r') as file:
        urls = json.load(file)  # Load the JSON as a list
        file.close()
    
    tree = build_tree(urls)  # Build the tree
    print_tree(tree)  # Print the tree structure

def find_duplicates_in_json(file_name):
    """Finds and returns a list of duplicate URLs in the JSON file."""
    with open(file_name, 'r') as file:
        urls = json.load(file)  # Load the list of URLs from the JSON file

    seen = set()  # To store unique URLs
    duplicates = set()  # To store duplicates

    for url in urls:
        if url in seen:
            duplicates.add(url)  # If URL is already seen, add to duplicates
        else:
            seen.add(url)  # Otherwise, add to seen set

    return list(duplicates)  # Convert the set of duplicates to a list

def remove_duplicates_from_json(file_name, duplicates_list):
    """Removes the duplicated URLs from the JSON file and saves the unique URLs back."""
    with open(file_name, 'r') as file:
        urls = json.load(file)  # Load the list of URLs from the JSON file

    seen = set()  # To track seen URLs
    unique_urls = []  # To store unique URLs

    for url in urls:
        if url not in seen:
            seen.add(url)  # Add to seen set
            unique_urls.append(url)  # Keep the first occurrence

    # Save the unique URLs back to the JSON file
    with open(file_name, 'w') as file:
        json.dump(unique_urls, file, indent=4)

    print(f"Removed {len(urls) - len(unique_urls)} duplicate URLs. Unique URLs saved to {file_name}.")
