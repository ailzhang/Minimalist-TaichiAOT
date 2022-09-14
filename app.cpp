#include <iostream>
#include <taichi/cpp/taichi.hpp>

const uint32_t WIDTH = 320;
const uint32_t HEIGHT = 320;
const uint32_t D = 4;

int main(int argc, const char** argv) {
  ti::Runtime runtime(TI_ARCH_VULKAN);

  ti::AotModule aot_module = runtime.load_aot_module("module");
  ti::ComputeGraph g_run = aot_module.get_compute_graph("taichi_add");

  std::vector<int8_t> input_data(WIDTH * HEIGHT * D, 1);
  ti::NdArray<int8_t> in_ten =
    runtime.allocate_ndarray<int8_t>({ WIDTH, HEIGHT, D }, {}, true);
  in_ten.write(input_data.data(), input_data.size() * sizeof(int8_t));
  runtime.wait();
  ti::NdArray<int8_t> out_ten =
    runtime.allocate_ndarray<int8_t>({ WIDTH, HEIGHT, D }, {}, true);


  g_run["in_ten"] = in_ten;
  g_run["out_ten"] = out_ten;
  g_run["addend"] = 3;
  g_run.launch();
  runtime.wait();

  auto arr_data = (const int8_t*)out_ten.map();
  for (uint32_t i = 0; i < 16; ++i) {
    std::cout << static_cast<int16_t>(arr_data[i]) << std::endl;
  }
  out_ten.unmap();

  return 0;
}
