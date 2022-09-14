import argparse

import taichi as ti
import numpy as np

WIDTH = 16
HEIGHT = 16

def compile_graph_aot(arch):
    ti.init(arch=arch)

    if ti.lang.impl.current_cfg().arch != arch:
        return

    @ti.kernel
    def taichi_add(in_ten: ti.types.ndarray(), out_ten: ti.types.ndarray(), addend: ti.i32):
        for i, j, k in in_ten:
            out_ten[i, j, k] = ti.cast(ti.cast(in_ten[i, j, k], ti.i32) + addend, ti.f32)

    in_ten = ti.ndarray(dtype=ti.f32, shape=(320, 320, 4))
    out_ten = ti.ndarray(dtype=ti.f32, shape=(320, 320, 4))
    in_ten.from_numpy(np.ones((320, 320, 4), dtype=np.uint8))
    out_ten.from_numpy(np.ones((320, 320, 4), dtype=np.uint8))
    addend = 3

    arg_0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "in_ten", dtype=ti.f32, field_dim=3)
    arg_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_ten", dtype=ti.f32, field_dim=3)
    arg_2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "addend", ti.i32)
    g = ti.graph.GraphBuilder()
    g.dispatch(taichi_add, arg_0, arg_1, arg_2)
    g = g.compile()

    g.run({"in_ten": in_ten, "out_ten": out_ten, "addend": addend})
    print(out_ten.to_numpy())

    m = ti.aot.Module(arch)
    m.add_graph("taichi_add", g)
    m.save("module", "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", type=str)
    args = parser.parse_args()

    if args.arch == "vulkan":
        compile_graph_aot(arch=ti.vulkan)
    else:
        assert False
