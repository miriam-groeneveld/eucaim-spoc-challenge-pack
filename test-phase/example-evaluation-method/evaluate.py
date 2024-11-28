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
GROUND_TRUTH_DIRECTORY = Path("ground_truth")


def process(job):
    """Processes a single algorithm job, looking at the outputs"""
    report = "Processing:\n"
    report += pformat(job)
    report += "\n"

    # Firstly, find the location of the results
    location_binary_vessel_segmentation = get_file_location(
        job_pk=job["pk"],
        values=job["outputs"],
        slug="binary-vessel-segmentation",
    )

    # Secondly, read the results
    result_binary_vessel_segmentation = load_image_file(
        location=location_binary_vessel_segmentation,
    )

    # Thirdly, retrieve the input file name to match it with your ground truth
    image_name_color_fundus_image = get_image_name(
        values=job["inputs"],
        slug="color-fundus-image",
    )

    # Fourthly, load your ground truth
    # Include it in your evaluation container by placing it in ground_truth/
    with open(GROUND_TRUTH_DIRECTORY / "some_resource.txt", "r") as f:
        report += f.read()
    print(report)

    # TODO: compare the results to your ground truth and compute some metrics

    # For now, we will just report back some bogus metric
    return {
        "my_metric": random.choice([1, 0]),
    }


def main():
    print_inputs()

    metrics = {}
    predictions = read_predictions()

    # We now process each algorithm job for this submission
    # Note that the jobs are not in any order!
    # We work that out from predictions.json

    # Use concurrent workers to process the predictions more efficiently
    metrics["results"] = run_prediction_processing(fn=process, predictions=predictions)

    # We have the results per prediction, we can aggregate the results and
    # generate an overall score(s) for this submission
    metrics["aggregates"] = {
        "my_metric": mean(result["my_metric"] for result in metrics["results"])
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


def read_predictions():
    # The prediction file tells us the location of the users' predictions
    with open(INPUT_DIRECTORY / "predictions.json") as f:
        return json.loads(f.read())


def get_image_name(*, values, slug):
    # This tells us the user-provided name of the input or output image
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["image"]["name"]

    raise RuntimeError(f"Image with interface {slug} not found!")


def get_interface_relative_path(*, values, slug):
    # Gets the location of the interface relative to the input or output
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["interface"]["relative_path"]

    raise RuntimeError(f"Value with interface {slug} not found!")


def get_file_location(*, job_pk, values, slug):
    # Where a job's output file will be located in the evaluation container
    relative_path = get_interface_relative_path(values=values, slug=slug)
    return INPUT_DIRECTORY / job_pk / "output" / relative_path


def load_image_file(*, location):
    # Use SimpleITK to read a file
    input_files = glob(str(location / "*.tiff")) + glob(str(location / "*.mha"))
    result = SimpleITK.ReadImage(input_files[0])

    # Convert it to a Numpy array
    return SimpleITK.GetArrayFromImage(result)


def write_metrics(*, metrics):
    # Write a json document used for ranking results on the leaderboard
    with open(OUTPUT_DIRECTORY / "metrics.json", "w") as f:
        f.write(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    raise SystemExit(main())
