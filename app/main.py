#!/usr/bin/env python
import os
import sys

path = os.path.join(os.path.dirname(__file__), "../utils")
sys.path.insert(0, path)

import argparse
from spider import Spider


def run_task(task, overide=False, skip=-1):
    spider = Spider(task)
    spider.workflow(overide=overide, skip=skip)


def main():
    parser = argparse.ArgumentParser(description="Define task arguments.")
    parser.add_argument(
        "-t", "--task", type=str, default="app/task.json", help="Task file path"
    )
    parser.add_argument(
        "-o",
        "--overide",
        type=bool,
        default=False,
        help="If True, db table will be overided. ",
    )
    args = parser.parse_args()
    run_task(args.task, args.overide)


if __name__ == "__main__":
    main()
