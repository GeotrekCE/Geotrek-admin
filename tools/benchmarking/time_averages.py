from statistics import mean
from pathlib import Path


def get_time_averages(measure_filepath):
    file = Path(measure_filepath)
    if file.is_file():
        # Generating the times matrix:
        # Each row contains the time mesures of all executions for one session
        # e.g. all time mesures of the request execution from 0 to 100 via-steps
        with open(measure_filepath, 'r') as f:
            times = [[time for time in line.split()] for line in f]

        # Computing the average of all sessions time mesures for each execution
        # e.g. if time = [[1, 20, 300], [7, 80, 900]] then averages = [4, 50, 600]
        averages = [mean(map(float, x)) for x in zip(*times)]
        return averages

    else:
        return "No data"


if __name__ == '__main__':
    averages = get_time_averages('time_measures/time_measures_py.txt')
    print('Python:', averages)
    averages = get_time_averages('time_measures/time_measures_js.txt')
    print('JavaScript:', averages)
