#include <iostream>
#include <taichi/cpp/taichi.hpp>

const uint32_t width = 128;
const uint32_t height = 128;

int main(int argc, const char** argv) {
  ti::Runtime runtime(TI_ARCH_VULKAN);

  ti::AotModule aot_module = runtime.load_aot_module("module");
  ti::ComputeGraph g_run = aot_module.get_compute_graph("g");
  ti::ComputeGraph g_init = aot_module.get_compute_graph("g_init");

  ti::NdArray<float> arr =
    runtime.allocate_ndarray<float>({ 512, 512 }, {4}, true);
  ti::Texture tex0 = runtime.allocate_texture2d(width, height, TI_FORMAT_RGBA8, TI_NULL_HANDLE);

  g_init["rw_tex"] = tex0;
  g_init.launch();

  g_run["tex"] = tex0;
  g_run["t"] = (float)0.03;
  g_run["pixels_arr"] = arr;
  g_run.launch();

  runtime.wait();

  std::vector<float> arr_data(512 * 512 * 4);
  arr.read(arr_data);
  float sum = 0.;
  for (auto x: arr_data) {
      sum += x;
    //std::cout << x << std::endl;
  }
  std::cout << sum << std::endl;
  return 0;
}
