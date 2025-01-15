# WEBPOK

Inner workings: Most the results(except for the crawling ones) are saved in memory inside a set, but with mode 4 you can save them to the master.json file and work later with them.

If you do not want to test it out before using it, I've included a sample website which is the one that I used for testing and developing of WEBPOK. Please note that you will get better results if you run the website with: `sudo python3 -m http.server 80`, the port does not matter, but the directory listing for example, will help you get better intial results.

all of the async features currently include an await statement used for throttling but you can simply comment it out ;)

## Modules

### Module 1: Snorlax Snooze

It is a module designed to search for sensitive information. This search is structured in 2 priority levels, ranging from 1(less important) to 2(most important). It is important to keep in mind that priority 1 can take a while to complete if it has a lot of URLs to check, its search if performed through regular expressions.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/snorlax.png)

### Module 2: Pidgey Wind

The purpouse of this module is to help you discover all the pages that the developers intended to be public, such as the ones referenced on the sitemaps files or the ones found via crawling.

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/pidgey.png)

*Robots/sitemap check:*

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/robots%20check.png)

*Crawling:*

What is most interesting about this module is that it lets you <ins>crawl</ins> with asynchronous requests and <ins>without a web browser</ins>, which makes it ideal for systems with very low hardware resources and to <ins>crawl static websites</ins>. In order to accomplish this task it uses regular expresions to get full and relative URLs patterns. However, the main counter part of this feature is that can be quite slow on large websites even though you use many paralel requests.

Once a full URL set has been constructed via crawling, it lets you check if the URLs found are valid or not.

__implement a check avoid writting duplicate urls to pidgey results file or to remove duplicates once the crawler has ended__

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/crawler.png)

### Mode 3: Gengar Shadows

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/gengar.png)

### Mode 4: Treecko Roots

This module organizes all the URLs stored inside the `master.json` file and it prints them to a window from which you can expand and collapse directories to get a quick overview of the target. Another interesing functionality about this module is that it displays the full URL at the bottom, so you can copy-paste it easily. Additionally all the boxes are clickable, meaning that if you double click one, it will automatically that URL in a web browser.

Please note that this processing can take a while if the master.json contains a huge amount of URLs. 

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/treecko.png)

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/treecko%20tree.png)

### Mode 5: Pikachu Vault

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/pikachu.png)

### Mode 6: Ditto Twins Check

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/ditto.png)

### Mode 7: Hawlucha Sight

![](https://github.com/trike33/WEBPOK/blob/main/repo_images/hawlucha.png)
