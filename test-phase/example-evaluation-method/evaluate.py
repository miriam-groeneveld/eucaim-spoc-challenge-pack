"""
The following is a simple example evaluation method.

It is meant to run within a container. Its steps are as follows:

  1. Read the algorithm output
  2. Associate original algorithm inputs with a ground truths via predictions.json
  3. Calculate metrics by comparing the algorithm output to the ground truth
  4. Repeat for all algorithm jobs that ran for this submission
  5. Aggregate the calculated metrics
  6. Save the metrics to metrics.json

To run it locally, you can call the following bash script:

  ./do_test_run.sh

This will start the evaluation and reads from ./test/input and writes to ./test/output

To save the container and prep it for upload to Grand-Challenge.org you can call:

  ./do_save.sh

Any container that shows the same behaviour will do, this is purely an example of how one COULD do it.

Reference the documentation to get details on the runtime environment on the platform:
https://grand-challenge.org/documentation/runtime-environment/

Happy programming!
"""

import json
from glob import glob
import SimpleITK
import re
import random
from statistics import mean
from pathlib import Path
from pprint import pformat, pprint
from helpers import run_prediction_processing, tree

INPUT_DIRECTORY = Path("/input")
OUTPUT_DIRECTORY = Path("/output")



def process(job):
    """Processes a single algorithm job, looking at the outputs"""
    report = "Processing:\n"
    report += pformat(job)
    report += "\n"

    # For now, we will just report back some bogus metric
    return {
        "my_metric": random.choice([1, 0]),
    }


def main():
    print_inputs()

    metrics = {
      "iou": {
        "mean": {
          "1": 0.5649914628630184
        },
        "median": {
          "1": 0.6231253281263195
        },
        "std": {
          "1": 0.2350942928527168
        },
        "min": {
          "1": 0.02226143613411158
        },
        "max": {
          "1": 0.8721490778519141
        },
        "ci_95": {
          "1": [
            0.040736543931159094,
            0.8609207021957904
          ]
        }
      },
      "dice": {
        "mean": {
          "1": 0.6875749182655478
        },
        "median": {
          "1": 0.7676957931145107
        },
        "std": {
          "1": 0.23272392341627107
        },
        "min": {
          "1": 0.043553312973044746
        },
        "max": {
          "1": 0.9317090056232162
        },
        "ci_95": {
          "1": [
            0.07801625170687917,
            0.9252616948660578
          ]
        }
      }
    }
    # Make sure to save the metrics
    write_metrics(metrics=metrics)

    return 0


def print_inputs():
    # Just for convenience, in the logs you can then see what files you have to work with
    print("Input Files:")
    for line in tree(INPUT_DIRECTORY):
        print(line)
    print("")



def write_metrics(*, metrics):
    # Write a json document used for ranking results on the leaderboard
    with open(OUTPUT_DIRECTORY / "metrics.json", "w") as f:
        f.write(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    raise SystemExit(main())
