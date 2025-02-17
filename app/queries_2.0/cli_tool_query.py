import argparse
import os
import time

SCRIPTS = {
    1: "query1.py",
    2: "query2.py",
    3: "query3.py",
    4: "query4.py",
    5: "query5.py",
    6: "query6.py",
    7: "query7.py",
    8: "query8.py",
    9: "query9.py",
    10:"query10.py"
}

def main():
    
    parser = argparse.ArgumentParser(description="Run a Python script based on input number.")
    parser.add_argument(
        "number", type=int, choices=SCRIPTS.keys(),
        help="Input a number corresponding to the script to run (1-10)"
    )
    args = parser.parse_args()

    script_to_run = SCRIPTS.get(args.number)

    if not script_to_run:
        print(f"No script found for number {args.number}")
        return

    if not os.path.exists(script_to_run):
        print(f"Error: {script_to_run} does not exist.")
        return

    start_time = time.time()
    try:
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
