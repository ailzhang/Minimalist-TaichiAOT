#!/bin/bash
set -ex

if [[ -z "${TAICHI_REPO_DIR}" ]]; then
  echo "env TAICHI_REPO_DIR not set!"
  exit
else
  echo "Rebuilding libtaichi_c_api.so in ${TAICHI_REPO_DIR}"
fi

pushd ${TAICHI_REPO_DIR}
python setup.py clean
TAICHI_CMAKE_ARGS="-DTI_WITH_VULKAN:BOOL=ON -DTI_WITH_OPENGL:BOOL=ON -DTI_WITH_C_API:BOOL=ON -DTI_WITH_GRAPHVIZ:BOOL=ON -DCMAKE_TOOLCHAIN_FILE=${ANDROID_NDK_ROOT}/build/cmake/android.toolchain.cmake -DANDROID_NATIVE_API_LEVEL=29 -DANDROID_ABI=arm64-v8a" DEBUG=1 python setup.py build_ext
popd

rm -rf build-android-aarch64
mkdir build-android-aarch64
pushd build-android-aarch64
cmake .. \
    -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake" \
    -DANDROID_PLATFORM=android-26 \
    -DANDROID_ABI="arm64-v8a"
cmake --build .
popd

adb shell rm -rf /data/local/tmp/taichi-aot/
adb shell mkdir /data/local/tmp/taichi-aot/
adb push ./build-android-aarch64/TaichiAot /data/local/tmp/taichi-aot/
adb push ./build-android-aarch64/libtaichi_c_api.so /data/local/tmp/taichi-aot/
adb push ./module /data/local/tmp/taichi-aot/
adb push ./scripts/__android_main.sh /data/local/tmp/taichi-aot/
adb shell sh /data/local/tmp/taichi-aot/__android_main.sh
