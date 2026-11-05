import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def label_lists():
    training=ast.parse((ROOT/'src/run_ncbi_rel_exp.py').read_text())
    evaluation=ast.parse((ROOT/'src/utils/run_pubtator_eval.py').read_text())
    train=[ast.literal_eval(n.value) for n in ast.walk(training) if isinstance(n,ast.Return) and isinstance(n.value,ast.List) and any(isinstance(e,ast.Constant) and e.value=='Association' for e in n.value.elts)]
    evaluate=[ast.literal_eval(n.value) for n in ast.walk(evaluation) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='labels' for t in n.targets) and isinstance(n.value,ast.List)]
    return train[0],evaluate[0]

class PredictionLabelsTests(unittest.TestCase):
    def test_processor_and_writer_match_published_checkpoint_label_order(self):
        train,evaluate=label_lists()
        self.assertEqual(train,evaluate)
        self.assertEqual(len(train),47)
        self.assertEqual(train[0:2],['None','Association'])
        self.assertEqual(train[46],'None-Conversion')

    def test_last_negative_class_writes_mentions_without_relations(self):
        labels=label_lists()[1]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'input.pubtator';tsv=root/'input.tsv';scores=root/'scores.tsv';output=root/'output.pubtator'
            source.write_text('paper_1|t|T\npaper_1|a|V600E melanoma\npaper_1\t2\t7\tV600E\tSequenceVariant\tHGVS:p.V600E;CorrespondingGene:673\npaper_1\t8\t16\tmelanoma\tDiseaseOrPhenotypicFeature\tMESH:D008545\n\n')
            tsv.write_text('paper_1\tGeneOrGeneProduct\tDiseaseOrPhenotypicFeature\tHGVS:p.V600E;CorrespondingGene:673\tMESH:D008545\tTrue\t0\ttext\t\tNone\n')
            row=['0']*len(labels);row[-1]='10';scores.write_text('\t'.join(row)+'\n')
            result=subprocess.run([sys.executable,str(ROOT/'src/utils/run_pubtator_eval.py'),'--exp_option','to_pubtator','--in_test_pubtator_file',str(source),'--in_test_tsv_file',str(tsv),'--in_pred_tsv_file',str(scores),'--out_pred_pubtator_file',str(output)],text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(output.read_text(),source.read_text())

if __name__=='__main__':unittest.main()
