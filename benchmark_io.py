import time
import sys
import os

# Add 'onkohelper' subdirectory to path
sys.path.append(os.path.join(os.getcwd(), 'onkohelper'))

from oncology_helper.data import Tietokanta

def benchmark_loading(iterations=1000):
    # Ensure file exists
    Tietokanta.lataa()

    start_time = time.time()
    for _ in range(iterations):
        Tietokanta.lataa()
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / iterations
    print(f"Total time for {iterations} loads: {total_time:.4f}s")
    print(f"Average loading time: {avg_time*1000:.4f} ms")

if __name__ == "__main__":
    benchmark_loading()
