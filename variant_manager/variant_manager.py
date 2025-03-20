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

from pxr import Usd


class UsdVariantManager(object):

    def __init__(self, source_layer_filepath, prim_path):
        self.source_layer_filepath = Path(source_layer_filepath)
        self.prim_path = prim_path

        if self.source_exists():
            self.stage = Usd.Stage.Open(self.source_layer_filepath.as_posix())
            self.prim = self.stage.GetPrimAtPath(self.prim_path)
            self.variant_sets = self.prim.GetVariantSets()
        else:
            self.stage = Usd.Stage.CreateNew(
                                    self.source_layer_filepath.as_posix())
            self.prim = self.stage.DefinePrim(self.prim_path)
            self.variant_sets = self.prim.GetVariantSets()
        
    def source_exists(self) -> bool:
        return self.source_layer_filepath.exists()

    def get_stage(self) -> Usd.Stage:
        return self.stage

    def get_prim(self) -> Usd.Prim:
        return self.prim

    def get_vset_names(self) -> list[str]:
        return self.variant_sets.GetNames()

    def get_var_selections_map(self) -> dict:
        return self.variant_sets.GetAllVariantSelections()

    def get_vset_variant_names(self, vset_name: str) -> list[str]:
        return self.get_vset(vset_name).GetVariantNames()

    def get_vset(self, vset_name: str) -> Usd.VariantSet:
        return self.variant_sets.GetVariantSet(vset_name)

    def get_vset_selected_var(self, vset_name: str) -> str:
        return self.variant_sets.GetVariantSelection(vset_name)

    def set_vset_sel_variant(self, vset_name: str, variant_name: str):
        if not self.has_vset(vset_name):
            raise Exception('Prim does not have VariantSet named '
                            f'"{vset_name}"')
        vset = self.get_vset(vset_name)
        if variant_name not in vset.GetVariantNames():
            raise Exception(f'VariantSet "{vset_name}" does not have a '
                            f'variant named "{variant_name}"')
        vset.SetVariantSelection(variant_name)

    def has_vset(self, vset_name: str) -> bool:
        return self.variant_sets.HasVariantSet(vset_name)

    def add_vset(self, new_vset_name: str) -> Usd.VariantSet:
        '''Not supporting nested variants - just "geo" and "look" variants
        '''
        if self.has_vset(new_vset_name):
            return self.get_vset(new_vset_name)

        new_vset = self.variant_sets.AddVariantSet(new_vset_name)
        return new_vset

    def add_variant(self, vset_name: str, variant_name: str):
        if not self.has_vset(vset_name):
            self.add_vset(vset_name)

        vset = self.get_vset(vset_name)
        if not vset.HasAuthoredVariant(variant_name):
            vset.AddVariant(variant_name)

    def apply_variant_operations(self, vset_name: str, variant_name: str,
                                 op_fn: callable, data: dict):
        vset = self.get_vset(vset_name)
        saved_var_sel = vset.GetVariantSelection()

        vset.SetVariantSelection(variant_name)
        with vset.GetVariantEditContext():
            op_fn(self.stage, self.prim, data)

        # return to saved variant selection
        vset.SetVariantSelection(saved_var_sel)

    def write_to_usda_file(self, usda_output_filepath: str|Path):

        usda_output_text = self.stage.GetRootLayer().ExportToString()

        with open(usda_output_filepath, 'w') as out_fp:
            out_fp.write(f'{usda_output_text}\n')

