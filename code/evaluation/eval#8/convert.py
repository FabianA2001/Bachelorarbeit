import os

from algbench import Benchmark

DEFAULT_BENCHMARK_PATH = lokal_benchmark_path = os.path.join(
    os.path.dirname(__file__), "lokal_benchmark"
)
new_benchmark = Benchmark(DEFAULT_BENCHMARK_PATH)

OLD_BENCHMARK_PATH = lokal_benchmark_path = os.path.join(
    os.path.dirname(__file__), "lokal_benchmark_old"
)
old_benchmark = Benchmark(OLD_BENCHMARK_PATH)


for result in old_benchmark:
    result["parameters"]["args"]["host"] = result["env"]["hostname"]
    new_benchmark.insert(result)

# for result in new_benchmark:
#     print(format_dictionary(result))

print(len(list(old_benchmark)))
print(len(list(new_benchmark)))

new_benchmark.compress()
