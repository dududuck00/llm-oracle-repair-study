"""Standalone standard-library verification of the dual-source IST table package."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,zipfile
BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def body(text):return text.split('\\midrule\n',1)[1].split('\\bottomrule',1)[0]
def groups(rows,block):
    bad={(r['case_id'],r['seed']) for r in rows if r['technical_failure'] or r['dependent_not_started']}
    predicates=dict(conflicts=lambda r:r['any_conflict'] and r['reference_adjudicable'],guards=lambda r:r['subgroup']=='guard' and r['reference_adjudicable'],
        formed_originals=lambda r:r['original_wellformed'] and r['reference_adjudicable'],all_fixed_slots=lambda r:True,
        available_guards=lambda r:r['subgroup']=='guard' and r['reference_adjudicable'] and (r['case_id'],r['seed']) not in bad)
    return {name:block([r for r in rows if pred(r)]) for name,pred in predicates.items()}
def main():
    manifest=read(BASE/'SHA256SUMS.json')
    for n,h in manifest.items():assert hashlib.sha256((BASE/n).read_bytes()).hexdigest()==h,n
    with tempfile.TemporaryDirectory(prefix='dual-source-') as tmp:
        with zipfile.ZipFile(BASE/'replay-inputs.zip') as z:
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(tmp)
        old=Path(tmp)/'oracle-conflict-table-reproduction'
        subprocess.run([sys.executable,str(old/'verify_and_reproduce.py')],cwd=old,check=True)
        project=old/'oracle-conflict-research'
        block=module('portable_blocks',project/'ccfa-workfiles/manuscript/icse-oracle/source/judge_repair_analysis.py').block
        qwen_data=read(project/'a8_humaneval_full_final_gpu0_v3/publication/data.json')
        gemma_data=read(BASE/'gemma-data.json')
        qwen=read(BASE/'qwen-summary.json');gemma=read(BASE/'gemma-summary.json');checks=0
        for data,summary in [(qwen_data,qwen),(gemma_data,gemma)]:
            oldtasks=set(data['reused_tasks']);tasks=set(data['tasks'])
            assert len(tasks)==164 and len(oldtasks)==40 and len(tasks-oldtasks)==124
            for model,rows in data['evaluations'].items():
                assert len(rows)==7872
                for scope,ids in [('full164',tasks),('reused40',oldtasks),('new124',tasks-oldtasks)]:
                    for name,actual in groups([r for r in rows if r['task_id'] in ids],block).items():
                        assert actual==summary['models'][model][scope][name],(model,scope,name)
                        checks+=1
        rendered=module('table_renderer',BASE/'render_dual_source_tables.py').render(qwen,gemma)
        out=BASE/'reproduced';out.mkdir(exist_ok=True)
        for name,rows in rendered.items():
            expected=(BASE/'expected'/ (name+'.tex')).read_text()
            assert rows==body(expected),name
            (out/(name+'.rows.tex')).write_text(rows)
        assert checks==105
        print(json.dumps(dict(passed=True,verified_files=len(manifest),reaggregated_groups=checks,dual_source_tables=6,
            source_judge_cells=7,all_source_frames=1312,model_calls=0,generated_code_executions=0)))
if __name__=='__main__':main()
