#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Script for downloading the latest release JAR file from a list of GitHub
# repositories. The list of GitHub repositories should be given in the first
# parameter when calling this script.
#
# GitHub repositories should be in the following format (no .git):
# https://github.com/<organization>/<repository>
# Example: https://github.com/actions/checkout
#
# Note: This script assumes that the "jars" directory already exists, and all
# downloaded JAR files will be saved into that directory in this format:
# <organization>-<repository>.jar

import json
import os
import sys
import urllib.request

urlsFilePath = sys.argv[1]
urls = []
count = 0

with open(urlsFilePath) as urlsFile:
    urls = urlsFile.readlines()
    print("Found {0} URLs".format(len(urls)))

os.chdir("jars")

for url in urls:
    parts = url.rstrip().split("/")
    org = parts[3]
    repo = parts[4]

    apiUrl = "https://api.github.com/repos/{0}/{1}/releases/latest".format(org, repo)
    data = {}

    try:
        with urllib.request.urlopen(apiUrl) as apiRequest:
            data = json.loads(apiRequest.read().decode())
    except urllib.error.HTTPError:
        # Usually 404, but may be others
        continue

    if "assets" in data:
        toDownload = data["assets"][0]["browser_download_url"]
    else:
        continue

    if not toDownload.endswith('.jar'):
        continue

    fileName = "{0}-{1}.jar".format(org, repo)
    urllib.request.urlretrieve(toDownload, fileName)
    count += 1

print("{0} files downloaded".format(count))
