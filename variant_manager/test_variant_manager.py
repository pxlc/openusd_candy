# -----------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2023 pxlc@github
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

from pathlib import Path

from pxr import Usd, UsdGeom, Sdf

from variant_manager import UsdVariantManager


def apply_custom_attr_fn(stage: Usd.Stage, prim: Usd.Prim, data: dict):
    attr_name = data.get('attr_name')
    attr_value = data.get('attr_value')

    if not prim.HasAttribute(attr_name):
        prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.String)

    prim_attr = prim.GetAttribute(attr_name)
    prim_attr.Set(attr_value)


apply_data_list = [
    {'variant': 'Blue',
        'data': {'attr_name': 'hex_color', 'attr_value': '#6699FF'}},
    {'variant': 'Green',
        'data': {'attr_name': 'hex_color', 'attr_value': '#99CC66'}},
    {'variant': 'Red',
        'data': {'attr_name': 'hex_color', 'attr_value': '#CC0000'}},
    {'variant': 'Yellow',
        'data': {'attr_name': 'hex_color', 'attr_value': '#FFFF66'}},
]


if __name__ == '__main__':

    uvm = UsdVariantManager('./prim_color_variants_layer.usda', '/color_prim')

    uvm.add_variant('Color', 'Yellow')

    for apply_d in apply_data_list:
        color_variant = apply_d['variant']
        color_value = apply_d['data']['attr_value']
        color_attr_name = apply_d['data']['attr_name']

        uvm.apply_variant_operations('Color', color_variant,
                                     apply_custom_attr_fn,
                                    {'attr_name': color_attr_name,
                                    'attr_value': color_value})

    uvm.set_vset_sel_variant('Color', 'Yellow')

    stage = uvm.get_stage()
    stage.SetDefaultPrim(uvm.get_prim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    print('')
    print(stage.GetRootLayer().ExportToString())
    print('')
    print('')

    uvm.write_to_usda_file(Path('./variant_manager_OUTPUT.usda'))

