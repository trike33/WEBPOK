# 🌐 WEBPOK

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/main.png)

## ⚙️  Inner workings
Most the results(except for the crawling ones) are saved in memory inside a set, but with mode 4 you can save them to the `master.json` file and work later with them.

If you do want to test it out before using it, I've included a sample website(under `/webtest`) and a sample wordlist(`wd`) which are the ones that I used for testing and development of WEBPOK. Please note that you will get better results if you run the website with: `sudo python3 -m http.server 80`, the port does not matter, but the directory listing for example, will help you get better intial results.

All of the async features currently include an `await` statement of 2 seconds used for throttling but you can simply comment it out ;)

## 🧩 Modules

### Module 1: Snorlax Snooze

It is a module designed to search for sensitive information. This search is structured in 2 priority levels, ranging from 1(less important) to 2(most important). It is important to keep in mind that priority 1 can take a while to complete if it has a lot of URLs to check, its search is performed through regular expressions.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/snorlax.png)

### Module 2: Pidgey Wind

The purpouse of this module is to help you discover all the pages that the developers intended to be public, such as the ones referenced on the sitemaps files or the ones found via crawling.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/pidgey.png)

*Robots/sitemap check:*

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/robots%20check.png)

*Crawling:*

What is most interesting about this module is that it lets you <ins>crawl</ins> with asynchronous requests and <ins>without a web browser</ins>, which makes it ideal for systems with very low hardware resources and to <ins>crawl static websites</ins>. In order to accomplish this task it uses regular expresions to get full and relative URLs patterns. However, the main counter part of this feature is that can be quite slow on large websites even though you use many paralel requests.

Once a full URL set has been constructed via crawling, it lets you check if the URLs found are valid or not.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/crawler.png)

### Mode 3: Gengar Shadows

The main objective of this module is to find all the URLs that are not intended to be public(but yet the website has). This module uses a variety of techniques to gather them, such as:

- Directory brute-forcing with recursion
- Checking the Wayback machine(http://web.archive.org/)
- Find hidden input fields on HTML code
- Brute force GET/POST parameters

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/gengar.png)

**Recursive directory bruteforcing with or without extensions, with wordlist split**

Ex. Consider a wordlist with 10 words:

We don't start one captain that covers the whole wordlist(1 to 10)
Instead we create various asynchronous tasks(called captains, say 2 or more) that divides the workload, such as:

- Captain 1: Goes from 1 to 5
- Captain 2: Goes from 6 to 10

By doing this splitting we can cover more wordlist contents more faster, meaning it is great for fastly find weird or hidden URLs. Although you can still find all the website URLs(but it will be slower) due to its recursion strategy.

In addition to this splitting strategy some optimization has been done so that each captain can run more than 1 paralel request, and they share a common results pool that they are constantly checking and updating with findings.

Also, there are some simple matching and filtering patterns that will help streamline the results.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/dirbrute.png)

### Mode 4: Treecko Roots

This module organizes all the URLs stored inside the `master.json` file and it prints them to a window from which you can expand and collapse directories to get a quick overview of the target. Another interesing functionality about this module is that it displays the full URL on the left-side, so you easily know its full route. Additionally all the boxes are clickable, meaning that if you double click one, it will automatically that URL in a web browser.

Some icons have been placed strategically in order to facilitate the visual organization, their meanings are the following:

- Flower: Domain
- Leaf: Directory
- Treecko: Endpoint

Please note that this processing can take a while if the `master.json` contains a large amount of URLs. 

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/treecko.png)

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/treecko%20tree.png)

### Mode 5: Pikachu Vault

With this module you can save your results stored in memory into the `master.json` file(please note that it can take a while if the master.json file is very large).

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/pikachu.png)

### Mode 6: Ditto Twins Check

This helper module will check for duplicates into the `master.json` file(please note that it can take a while if the master.json file is very large).

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/ditto.png)

### Mode 7: Hawlucha Sight

The aim of this last mode is to smartly view the results files contents. It includes a variety of functionalities such as; finding sensitve extensions and/or keywords on URLs, find guessable parameters in the URLS and parse a Burp-compatible JSON scope file.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/hawlucha.png)

## ⚠️ Disclaimer

This tool is intended solely for research and educational purposes. The author does not assume any responsibility for improper or illegal use of this software.

Users are fully responsible for ensuring that they have the necessary authorization before conducting any tests on a system. Unauthorized use of this tool may violate applicable laws and regulations.

By using this software, you agree that the author shall not be held liable for any misuse, damages, or legal consequences resulting from its use.This tool is intended solely for research and educational purposes. The author does not assume any responsibility for improper or illegal use of this software.

Users are fully responsible for ensuring that they have the necessary authorization before conducting any tests on a system. Unauthorized use of this tool may violate applicable laws and regulations.

By using this software, you agree that the author shall not be held liable for any misuse, damages, or legal consequences resulting from its use.

## 🤝 Support

This project is maintained as a personal research and development effort. While I welcome and review pull requests, I do not provide official support for issues or troubleshooting.

If you would like to contribute improvements, feel free to submit a pull request and I will review it happily.

If you find this project useful, consider starring the repository ⭐ to show your support and help others discover it!

I appreciate any contributions that help improve WEBPOK! 🚀
