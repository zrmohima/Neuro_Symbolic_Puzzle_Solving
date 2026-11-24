"""Per-clue translation, durable call checkpoints and explicit reasoning budgets."""
import argparse, hashlib, json, re, time
from pathlib import Path
import pyarrow.parquet as pq
from answer_validation import normalize_answer
from solver import domains, parse_json, solve, score, OutputError, integer, summarize

EXAMPLES = '''Examples from unrelated, invented puzzles (not benchmark solutions):
Clue: Mira is in house 3.
{"relation":"eq","left":["Name","Mira"],"right":3}
Clue: The violin player is not in house 1.
{"relation":"ne","left":["Instrument","violin"],"right":1}
Clue: The owner of the rabbit lives somewhere left of the tea drinker.
{"relation":"lt","left":["Pet","rabbit"],"right":["Drink","tea"]}
Clue: Mira lives directly left of the orange house.
{"relation":"immediately_left","left":["Name","Mira"],"right":["Color","orange"]}
Clue: The kite owner lives next to the baker.
{"relation":"adjacent","left":["Toy","kite"],"right":["Job","baker"]}
Clue: One house lies between the harp player and the cocoa drinker.
{"relation":"distance","left":["Instrument","harp"],"right":["Drink","cocoa"],"distance":2}
'''


def clue_prompt(row, clue):
    return ('Translate only the following clue into one flat JSON relation. Think through the meaning, then return the JSON. '
            'Position terms are [category,value] pairs or 1-based house numbers. '
            'Allowed relations: eq, ne, lt, immediately_left, adjacent, distance. '
            'Do not nest relation objects. Distance counts position difference, not intervening houses. '
            'Use only actual domain values; examples below illustrate syntax only.\n'+EXAMPLES+
            '\nActual domains: '+json.dumps(domains(row))+'\nNumber of houses: '+row['size'].split('*')[0]+
            '\nActual clue: '+clue)


def flat_rule(obj):
    op=obj.get('relation')
    if op not in ('eq','ne','lt','immediately_left','adjacent','distance'):
        raise OutputError('invalid_schema','Unsupported relation')
    required={'relation','left','right'} | ({'distance'} if op=='distance' else set())
    if set(obj)!=required: raise OutputError('invalid_schema','Unexpected or missing relation fields')
    def term(x):
        if isinstance(x,list) and len(x)==2 and all(isinstance(v,str) for v in x): return x
        return integer(x)
    rule={'op':op,'args':[term(obj['left']),term(obj['right'])]}
    if op=='distance': rule['distance']=integer(obj['distance'])
    return rule


def direct_prompt(row):
    return (row['puzzle']+'\nSolve the puzzle. Before answering, check every clue against your proposed table, '
            'and check that each category uses every listed value exactly once. '
            'After reasoning, return one JSON object with header and rows, without commentary. '
            'Use this exact header: '+json.dumps(row['solution']['header'])+
            '. List houses in order with the house number first.')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='runs/new-experiment')
    p.add_argument('--gold',default='datasets/private/grid_mode.parquet')
    p.add_argument('--model',default='models/Qwen3-8B-4bit')
    p.add_argument('--size',default='2*2')
    p.add_argument('--limit',type=int,default=20)
    p.add_argument('--max-tokens',type=int,default=8192)
    p.add_argument('--thinking',action=argparse.BooleanOptionalAction,default=True)
    p.add_argument('--prepare-only',action='store_true')
    a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    rows=[r for r in pq.read_table('datasets/public/grid_mode.parquet').to_pylist() if r['size']==a.size][:a.limit]
    if not rows or a.max_tokens<1: raise ValueError('Invalid limit or budget')
    gold={r['id']:r for r in pq.read_table(a.gold).to_pylist()}
    for r in rows:
        g=gold[r['id']]
        assert g['puzzle']==r['puzzle'] and g['solution']['header']==r['solution']['header']
        assert score(None,g['solution']) is not None
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest={k:v for k,v in vars(a).items() if k!='prepare_only'}|{'ids':[r['id'] for r in rows], 'version':'selected-thinking-size-transfer','reference_run':'results/4x4','validator_sha256':sha(Path(__file__).with_name('answer_validation.py')),'source_sha256':sha(__file__),'solver_sha256':sha(Path(__file__).with_name('solver.py')),'gold_sha256':sha(a.gold),'data_sha256':sha('datasets/public/grid_mode.parquet'),'quantization':json.loads((Path(a.model)/'config.json').read_text()).get('quantization'),'decoding':'greedy','seed':0}
    dest=out/'manifest.json'
    if dest.exists() and json.loads(dest.read_text())!=manifest: raise ValueError('Use a new output directory for changed settings/code')
    dest.write_text(json.dumps(manifest,indent=2))
    if a.prepare_only: print('Prepared',len(rows),'puzzles; answers verified.'); return
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler
    import mlx.core as mx
    mx.random.seed(0); model,tokenizer=load(a.model)
    callsfile=out/'calls.jsonl'; records=out/'predictions.jsonl'
    read=lambda f:[json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []
    calls={r['key']:r for r in read(callsfile)}
    done={(r['id'],r['method']) for r in read(records)}
    def generate(key,prompt):
        if key in calls: return calls[key]
        rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True,enable_thinking=a.thinking)
        start=time.perf_counter(); chunks=[]; last=None
        for event in stream_generate(model,tokenizer,prompt=rendered,max_tokens=a.max_tokens,sampler=make_sampler(temp=0)):
            chunks.append(event.text);last=event
        if last is None: raise RuntimeError('No generation events')
        call={'key':key,'prompt':rendered,'raw':''.join(chunks),'generation_seconds':time.perf_counter()-start,'generation_tokens':last.generation_tokens,'prompt_tokens':last.prompt_tokens,'finish_reason':last.finish_reason,'hit_token_limit':last.finish_reason=='length'}
        with callsfile.open('a') as f:f.write(json.dumps(call)+'\n')
        calls[key]=call
        print(key,last.finish_reason,last.generation_tokens,'tokens',flush=True)
        return call
    for row in rows:
        for method in ('direct','symbolic'):
            if (row['id'],method) in done: continue
            rec={'id':row['id'],'method':method}; used=[]; errors=[]; rules=[]
            if method=='direct':
                call=generate(row['id']+'/direct',direct_prompt(row));used.append(call)
                try:
                    rec['rows']=normalize_answer(call['raw'],row['solution']['header'],int(row['size'].split('*')[0]))
                except (ValueError,TypeError,KeyError) as e: errors.append({'category':getattr(e,'category','invalid_schema'),'message':str(e)})
            else:
                for num,clue in re.findall(r'^(\d+)\.\s+(.+)',row['puzzle'],re.M):
                    call=generate(row['id']+'/clue/'+num,clue_prompt(row,clue));used.append(call)
                    try:rules.append({'clue':int(num),'rule':flat_rule(parse_json(call['raw']))})
                    except (ValueError,TypeError,KeyError) as e: errors.append({'clue':int(num),'category':getattr(e,'category','invalid_schema'),'message':str(e)})
                rec['constraints']=rules
                if not errors:
                    try:rec.update(solve(row,{'constraints':rules}))
                    except (ValueError,TypeError,KeyError,AttributeError) as e:errors.append({'category':getattr(e,'category','invalid_constraint'),'message':str(e)})
            if errors:rec['error']=errors
            rec.update({'call_keys':[c['key'] for c in used],'model_calls':len(used),'generation_seconds':sum(c['generation_seconds'] for c in used),'generation_tokens':sum(c['generation_tokens'] for c in used),'token_limit_hits':sum(c['hit_token_limit'] for c in used),'score':score(rec.get('rows'),gold[row['id']]['solution'])})
            with records.open('a') as f:f.write(json.dumps(rec)+'\n')
            summarize(records)
            print(row['id'],method,'correct:',rec['score']['exact'],flush=True)
    rs=read(records)
    metrics={method:{'model_calls':sum(r['model_calls'] for r in rs if r['method']==method),'generation_seconds':sum(r['generation_seconds'] for r in rs if r['method']==method),'generation_tokens':sum(r['generation_tokens'] for r in rs if r['method']==method),'token_limit_hits':sum(r['token_limit_hits'] for r in rs if r['method']==method)} for method in ('direct','symbolic')}
    (out/'runtime.json').write_text(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
