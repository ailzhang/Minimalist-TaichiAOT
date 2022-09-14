#include <iostream>
#include <taichi/cpp/taichi.hpp>

const uint32_t WIDTH = 320;
const uint32_t HEIGHT = 320;
const uint32_t D = 4;

int main(int argc, const char** argv) {
  ti::Runtime runtime(TI_ARCH_VULKAN);

  ti::AotModule aot_module = runtime.load_aot_module("module");
  ti::ComputeGraph g_run = aot_module.get_compute_graph("taichi_add");

  std::vector<float> input_data(WIDTH * HEIGHT * D, 1);
  ti::NdArray<float> in_ten =
    runtime.allocate_ndarray<float>({ WIDTH, HEIGHT, D }, {}, true);
  in_ten.write(input_data.data(), input_data.size() * sizeof(float));
  ti::NdArray<float> out_ten =
    runtime.allocate_ndarray<float>({ WIDTH, HEIGHT, D }, {}, true);
  runtime.wait();


  g_run["in_ten"] = in_ten;
  g_run["out_ten"] = out_ten;
  g_run["addend"] = 3;
  g_run.launch();
  runtime.wait();

  auto arr_data = (const float*)out_ten.map();
  for (uint32_t i = 0; i < 16; ++i) {
    std::cout << arr_data[i] << std::endl;
  }
  out_ten.unmap();

  return 0;
}
