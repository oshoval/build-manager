#!/usr/bin/env python3

import os
import sys
import glob
import pprint
import requests

rules = "rules/rules.txt"
rules_db = {}

all_targets = [os.path.basename(dir) for dir in glob.glob("cluster-provision/k8s/*", recursive=False) if os.path.isdir(dir)]
all_targets = sorted(all_targets)
# print(all_targets)


def main():
    build_db()
    # pprint.pprint(rules_db)
    diff_finder()


def build_db():
    with open(rules) as f:
        content = f.read().splitlines()

    for rule in content:
        if rule == "" or rule.startswith("#"):
            continue
        process_rule(rule)


def process_rule(rule):
    arr = rule.split()
    if len(arr) != 3 or arr[1] != "-":
        print("ERROR: rule format must be 'directory - value', rule:", rule)
        sys.exit(1)

    dir = arr[0]
    value = arr[2]

    if value == "all":
        rules_db[dir] = all_targets
    elif value == "none":
        rules_db[dir] = "none"
    elif value.startswith("!"):
        value = value[1:]
        rules_db[dir] = [target for target in all_targets if target != value]
    elif value == "regex":
        regex_targets = [os.path.basename(dir) for dir in glob.glob(dir, recursive=False) if os.path.isdir(dir)]
        dir = os.path.dirname(dir)
        for target in regex_targets:
            rules_db[dir + "/" + target + "/*"] = target.replace("k8s-", "")
    elif value == "regex_none":
        regex_targets = [dir for dir in glob.glob(dir, recursive=False) if os.path.isdir(dir)]
        for target in regex_targets:
            rules_db[target + "/*"] = "none"
    else:
        if value not in all_targets:
            print("ERROR: value must be a valid target, rule:", rule)
            sys.exit(1) 
        rules_db[dir] = value


def diff_finder():
    url = "https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirtci/latest?ignoreCache=1"
    try:
        r = requests.get(url)
    except Exception as e:
        print("ERROR: exception occured while fetching latest kubevirtci tag", e)
        sys.exit(1)

    if r.status_code != 200:
        print("ERROR: error fetching latest kubevirtci tag, status code", r.status_code)
        sys.exit(1)

    tag = r.text.rstrip('\n')


def process():
    pass


if __name__ == "__main__":
    main()
