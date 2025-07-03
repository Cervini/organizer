import time
import utils

def main():
    # Run the scheduler in a loop
    while True:
        print("\nSorting")
        utils.file_sorter()
        time.sleep(10)
        # be aware that this solution doesn't make so that the sorting happens every 5 minutes but that there
        # are 5 minutes between every sorting

if __name__ == "__main__":
    main()