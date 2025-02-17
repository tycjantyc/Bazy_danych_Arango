import argparse
import os
import time

# List of Python scripts to execute (mapped by number)
SCRIPTS = {
    1: "query_1.py",
    2: "query_2.py",
    3: "query_3.py",
    4: "query_4.py",
    5: "query_5.py",
    6: "query_6.py",
    7: "query_7.py",
    8: "query_8.py",
    9: "query_9.py",
    10:"query_10.py"
}

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run a Python script based on input number.")
    parser.add_argument(
        "number", type=int, choices=SCRIPTS.keys(),
        help="Input a number corresponding to the script to run (1-10)"
    )
    args = parser.parse_args()

    # Get the script to execute
    script_to_run = SCRIPTS.get(args.number)

    if not script_to_run:
        print(f"No script found for number {args.number}")
        return

    # Check if the script file exists
    if not os.path.exists(script_to_run):
        print(f"Error: {script_to_run} does not exist.")
        return

    # Measure execution time
    start_time = time.time()
    try:
        # Execute the script using `exec`
        with open(script_to_run, 'r') as file:
            script_code = file.read()
            exec(script_code)
    except Exception as e:
        print(f"An error occurred while running {script_to_run}: {e}")
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time for {script_to_run}: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
