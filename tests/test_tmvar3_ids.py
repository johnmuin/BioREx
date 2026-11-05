from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/dataset_format_converter'))
from convert_pubtator_2_tsv import load_pubtator_into_documents

class VariantIdsTests(unittest.TestCase):
    def read(self, kind, identifier):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'input.pubtator'
            p.write_text(f'paper_2|t|T\npaper_2|a|V600E\npaper_2\t2\t7\tV600E\t{kind}\t{identifier}\n\n')
            return load_pubtator_into_documents(p, normalized_type_dict={'SequenceVariant':'GeneOrGeneProduct'}, re_id_spliter_str=r'[,;]')[0].text_instances[1].annotations[0]

    def test_hgvs_gene_is_one_identity(self):
        value='HGVS:p.V600E;CorrespondingGene:673'
        ann=self.read('SequenceVariant',value)
        self.assertEqual(ann.ids,{value})
        self.assertEqual(ann.ne_type,'GeneOrGeneProduct')
        self.assertEqual(ann.orig_ne_type,'SequenceVariant')

    def test_nonvariant_semicolon_ids_unchanged(self):
        self.assertEqual(self.read('ChemicalEntity','MESH:D1;MESH:D2').ids,{'MESH:D1','MESH:D2'})

    def test_dbsnp_and_legacy_variant_lists_unchanged(self):
        self.assertEqual(self.read('SequenceVariant','rs1').ids,{'rs1'})
        self.assertEqual(self.read('SequenceVariant','rs1;rs2').ids,{'rs1','rs2'})

if __name__=='__main__':unittest.main()
