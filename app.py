import argparse
from taichi.examples.patterns import taichi_logo

import taichi as ti

def compile_graph_aot(arch):
    ti.init(arch=arch)

    if ti.lang.impl.current_cfg().arch != arch:
        return

    res = (512, 512)

    @ti.kernel
    def make_texture(tex: ti.types.rw_texture(num_dimensions=2,
                                              num_channels=4,
                                              channel_format=ti.u8,
                                              lod=0)):
        for i, j in ti.ndrange(128, 128):
            ret = ti.cast(taichi_logo(ti.Vector([i, j]) / 128), ti.f32)
            tex.store(ti.Vector([i, j]), ti.Vector([ret, 0., 0., 0.]))


    @ti.kernel
    def paint(t: ti.f32, pixels: ti.types.ndarray(field_dim=2),
              tex: ti.types.texture(num_dimensions=2)):
        for i, j in pixels:
            uv = ti.Vector([i / res[0], j / res[1]])
            warp_uv = uv + ti.Vector(
                [ti.cos(t + uv.x * 5.0),
                 ti.sin(t + uv.y * 5.0)]) * 0.1
            c = ti.math.vec4(0.0)
            if uv.x > 0.5:
                c = tex.sample_lod(warp_uv, 0.0)
            else:
                c = tex.fetch(ti.cast(warp_uv * 128, ti.i32), 0)
            pixels[i, j] = [c.r, c.r, c.r, 1.0]

    _t = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 't', ti.f32)
    _pixels_arr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY,
                               'pixels_arr',
                               ti.f32,
                               field_dim=2,
                               element_shape=(4, ))

    _rw_tex = ti.graph.Arg(ti.graph.ArgKind.RWTEXTURE,
                           'rw_tex',
                           channel_format=ti.u8,
                           shape=(128, 128),
                           num_channels=4)

    g_init_builder = ti.graph.GraphBuilder()
    g_init_builder.dispatch(make_texture, _rw_tex)
    g_init = g_init_builder.compile()

    _tex = ti.graph.Arg(ti.graph.ArgKind.TEXTURE,
                        'tex',
                        channel_format=ti.u8,
                        shape=(128, 128),
                        num_channels=4)

    g_builder = ti.graph.GraphBuilder()
    g_builder.dispatch(paint, _t, _pixels_arr, _tex)
    g = g_builder.compile()

    # test run in python
    pixels_arr = ti.Vector.ndarray(4, dtype=float, shape=res)
    texture = ti.Texture(ti.u8, 4, (128, 128))
    g_init.run({'rw_tex': texture})
    g.run({'t': 0.03, 'pixels_arr': pixels_arr, 'tex': texture})
    print(pixels_arr.to_numpy().sum())

    tmpdir = 'module'
    mod = ti.aot.Module(ti.vulkan)
    mod.add_graph('g', g)
    mod.add_graph('g_init', g_init)
    mod.save(tmpdir, '')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", type=str)
    args = parser.parse_args()

    if args.arch == "vulkan":
        compile_graph_aot(arch=ti.vulkan)
    else:
        assert False
