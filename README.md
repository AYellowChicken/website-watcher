# Website Watcher Script

Basic Python tool designed for monitoring multiple websites to check for the presence or absence of specific patterns on their web pages. Useful if you're too lazy to F5 yourself and want to get a Powershell Notification when an event happened.

## Notifications (Optional)

The script can notify you using the BurntToast PowerShell module which allows you to send Windows toast notifications with customized messages.

### Installation of BurntToast

To use BurntToast, you'll need to install it on your system. You can install it using PowerShell with the following command:

```powershell
Install-Module -Name BurntToast -Force
```

## Installation

```bash
pip install -r requirements.txt
```

## Features

- Monitors multiple websites specified in a 'urls.txt' file.
- Supports two primary options:
  1. Watch (--watch): Checks if a specific string pattern is present on the web page.
  2. Unwatch (--unwatch): Checks if a specific string pattern is absent on the web page.
  3. Sanity check
- Can load cookies and headers from files in `cre` folder

### Watch and Unwatch File

The `watch` file contains patterns that you want the script to watch for on each website. Each line in the file corresponds to a website and specifies a pattern to look for. For websites where you want to ignore patterns, use "IGNORE_ME_PLEASE" as the line content.

Example `watch.txt` file:

```
New Stock
ImportantKeyword
IGNORE_ME_PLEASE
```

In this example, the script will watch for "New Stock" on the first website and "ImportantKeyword" on the second website. It will ignore patterns on the third.

The `unwatch` file contains patterns that you want the script to unwatch for on each website. Similar to the `watch` file, each line in the `unwatch` file corresponds to a website and specifies a pattern to avoid. To ignore patterns for specific websites, use "IGNORE_ME_PLEASE" in the file.

## Sanity check

You might get logged out or rate limited or blocked for some reason. 
The script already checks for error HTTP status code to detect that, but on top of that, the `checker.txt` file contains sanity checks. If these patterns aren't detected in the website response, the application notifies you and exits.

## Usage

```bash
python website_watcher.py urls.txt -c cookies.txt -w watch.txt -u unwatch.txt -b headers.txt
```