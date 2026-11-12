"""Render the six full-task HumanEval tables from verified frozen summaries."""
from pathlib import Path
import json

ORDER=['qwen9','qwen27','qwen35','gemma','deepseek']
NAMES=dict(qwen9='Qwen9B',qwen27='Qwen27B',qwen35='Qwen35B',gemma='Gemma',deepseek='DeepSeek')
def signed(x):return f'{x:+.2f}'
def pair(g,field='correct_retained'):
    return '/'.join(f"{g['means'][a][field]:.2f}" for a in ['visible','hidden'])
def line(items):return ' & '.join(str(x) for x in items)+r' \\'
def render(qwen,gemma):
    cells=[('Qwen9B',m,qwen['models'][m]) for m in ORDER]+[('Gemma',m,gemma['models'][m]) for m in ['qwen9','gemma']]
    rows={name:[] for name in ['visibility','guard_accounting','visibility_availability','visibility_decomposition','visibility_formation','visibility_task_splits']}
    for source,model,parts in cells:
        c=parts['full164']['conflicts'];g=parts['full164']['guards'];a=parts['full164']['available_guards'];f=parts['full164']['formed_originals'];full=parts['full164']['all_fixed_slots'];judge=NAMES[model]
        rows['visibility'].append(line([source,judge,int(c['n']),pair(c),signed(c['delta_pp']),int(g['n']),pair(g),signed(g['delta_pp']),signed(a['delta_pp'])]))
        rows['guard_accounting'].append(line([source,judge,*[signed(g['delta'][k]) for k in ['recovered','regressed','correct_removed_technical','correct_removed_defer','correct_retained']]]))
        rows['visibility_availability'].append(line([source,judge,round(3*a['n']),round(3*a['means']['visible']['correct_retained']),round(3*a['means']['hidden']['correct_retained']),signed(a['delta_pp'])]))
        for name,block in [('Conflict',c),('Guard',g)]:
            td=block['task_direction']
            rows['visibility_decomposition'].append(line([source,judge,name,*[signed(block['delta'][k]) for k in ['recovered','regressed','correct_removed_technical','correct_removed_defer']],'/'.join(str(x) for x in block['seed_delta_u']),'/'.join(str(td[k]) for k in ['improved','worsened','tied'])]))
        failure='/'.join(str(round(3*full['means'][arm]['technical_failure'])) for arm in ['visible','hidden'])
        rows['visibility_formation'].append(line([source,judge,int(f['n']),pair(f),pair(full),failure,pair(full,'new_correct_from_unformed_original')]))
        values=[parts[p][group]['delta_pp'] for group in ['conflicts','guards'] for p in ['reused40','new124','full164']]
        rows['visibility_task_splits'].append(line([source,judge,*[signed(v) for v in values]]))
    return {name:'\n'.join(value)+'\n' for name,value in rows.items()}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('qwen',type=Path);ap.add_argument('gemma',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for name,body in render(json.loads(args.qwen.read_text()),json.loads(args.gemma.read_text())).items():(args.output/(name+'.rows.tex')).write_text(body)
