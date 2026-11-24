"""Greedy Qwen3-8B direct and validated symbolic inference; never execute model code."""
import argparse, hashlib, json, re, time
from pathlib import Path
import pyarrow.parquet as pq
import z3


def domains(row):
    groups = [re.findall(r'`([^`]+)`', line) for line in row['puzzle'].splitlines() if line.lstrip().startswith('- ')]
    header = row['solution']['header'][1:]
    n = int(row['size'].split('*')[0])
    if len(groups) != len(header) or any(len(g) != n for g in groups):
        raise ValueError('Cannot extract complete attribute domains')
    return dict(zip(header, groups))


class OutputError(ValueError):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category


def parse_json(text):
    if '<think>' in text and '</think>' not in text:
        raise OutputError('unfinished_thinking', 'Thinking block did not finish')
    text = text.split('</think>')[-1].strip()
    if text.startswith('```'):
        match = re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if not match:
            raise OutputError('malformed_json', 'Incomplete JSON fence or trailing content')
        text = match.group(1)
    def unique_keys(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise OutputError('malformed_json', f'Duplicate JSON key: {k}')
            result[k] = v
        return result
    try:
        obj = json.loads(text, object_pairs_hook=unique_keys)
    except (json.JSONDecodeError, RecursionError) as e:
        raise OutputError('malformed_json', str(e)) from e
    if not isinstance(obj, dict):
        raise OutputError('invalid_schema', 'Expected a complete JSON object')
    return obj


def integer(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r'[0-9]+', value.strip()):
        return int(value.strip())
    raise OutputError('invalid_schema', 'Expected an integer or decimal integer string')


def solve(row, obj, timeout=10000, enumerate_all=False):
    start = time.perf_counter()
    ds = domains(row)
    n = int(row['size'].split('*')[0])
    variables = {(c,v): z3.Int(f'v_{i}_{j}') for i,(c,vs) in enumerate(ds.items()) for j,v in enumerate(vs)}
    solver = z3.Solver(); solver.set(timeout=timeout)
    for c,vs in ds.items():
        xs = [variables[c,v] for v in vs]
        solver.add(z3.Distinct(xs), *[z3.And(x>=1,x<=n) for x in xs])
    def term(x):
        if type(x) is int or isinstance(x, str):
            x = integer(x)
            if 1 <= x <= n: return z3.IntVal(x)
        if isinstance(x,list) and len(x)==2 and tuple(x) in variables: return variables[tuple(x)]
        raise ValueError(f'Invalid position term: {x}')
    def expr(x, depth=0):
        if depth > 12 or not isinstance(x,dict): raise ValueError('Invalid constraint')
        op=x.get('op'); args=x.get('args',[])
        if not isinstance(args,list): raise ValueError('args must be a list')
        if op in ('and','or') and args:
            return (z3.And if op=='and' else z3.Or)(*[expr(a,depth+1) for a in args])
        if op=='not' and len(args)==1: return z3.Not(expr(args[0],depth+1))
        if len(args)!=2: raise ValueError('Binary relation needs two arguments')
        a,b=map(term,args)
        if op=='eq': return a==b
        if op=='ne': return a!=b
        if op=='lt': return a<b
        if op=='adjacent': return z3.Abs(a-b)==1
        if op=='immediately_left': return a+1==b
        if op=='distance':
            k=integer(x.get('distance'))
            if type(k) is not int or not 1<=k<n: raise ValueError('Invalid distance')
            return z3.Abs(a-b)==k
        raise ValueError(f'Unknown relation: {op}')
    clues=re.findall(r'^\d+\.\s+.+',row['puzzle'],re.M)
    rules=obj.get('constraints')
    if not isinstance(rules, list):
        raise OutputError('invalid_schema', 'constraints must be an array')
    if any(not isinstance(r, dict) or 'clue' not in r or 'rule' not in r for r in rules):
        raise OutputError('invalid_schema', 'Every constraint needs clue and rule')
    ids=[integer(r['clue']) for r in rules]
    expected=set(range(1,len(clues)+1))
    if len(ids)!=len(set(ids)):
        raise OutputError('duplicate_clues', 'Duplicate clue numbers')
    if set(ids)-expected:
        raise OutputError('unexpected_clues', f'Unexpected clue numbers: {sorted(set(ids)-expected)}')
    if expected-set(ids):
        raise OutputError('missing_clues', f'Missing clue numbers: {sorted(expected-set(ids))}')
    solver.add(*[expr(r['rule']) for r in rules])
    status=solver.check()
    result={'status':str(status),'unique':None,'rows':None}
    if status==z3.sat:
        m=solver.model()
        result['rows']=[[str(h)]+[next(v for v in vs if m.eval(variables[c,v]).as_long()==h) for c,vs in ds.items()] for h in range(1,n+1)]
        solver.add(z3.Or(*[v!=m.eval(v) for v in variables.values()]))
        second=solver.check()
        result['unique']=True if second==z3.unsat else False if second==z3.sat else None
        result['uniqueness_status']=str(second)
        if enumerate_all:
            count=1
            while second==z3.sat and count<10000:
                other=solver.model(); count+=1
                solver.add(z3.Or(*[v!=other.eval(v) for v in variables.values()]))
                second=solver.check()
            result['solution_count']=count
            result['enumeration_complete']=second==z3.unsat
    result['solver_seconds']=time.perf_counter()-start
    return result


def score(pred, gold):
    # Structural house numbers are excluded from cell accuracy.
    if any(v=='___' for row in gold['rows'] for v in row): return None
    truth=gold['rows']; total=sum(len(r)-1 for r in truth)
    if not isinstance(pred,list) or len(pred)!=len(truth) or any(not isinstance(r,list) or len(r)!=len(truth[0]) for r in pred):
        return {'exact':False,'correct_cells':0,'total_cells':total}
    try:
        mapped={str(r[0]):r for r in pred}
        if len(mapped)!=len(truth) or set(mapped)!={str(r[0]) for r in truth}: raise ValueError()
        correct=sum(str(a).strip().casefold()==str(b).strip().casefold() for r in truth for a,b in zip(mapped[str(r[0])][1:],r[1:]))
    except (TypeError,ValueError): correct=0
    return {'exact':correct==total,'correct_cells':correct,'total_cells':total}


def prompt(row, method):
    base=row['puzzle']+'\n\n'
    if method=='direct':
        return base+'Solve the puzzle. Return only JSON with keys header and rows. Header: '+json.dumps(row['solution']['header'])+'. Rows must list houses in order, with house number first and one value for every category.'
    clues = re.findall(r'^(\d+)\.\s+(.+)', row['puzzle'], re.M)
    instructions = """Translate ALL numbered clues into position constraints. Return one JSON object with a constraints array.
Each array entry has two keys: clue (the original integer clue number), and rule (a relation object).
Each relation object has op and args. A position term is a house number (1-based) or a two-string array [category, value].
Allowed binary relations:
- eq: both positions are equal.
- ne: positions differ (including 'not in house').
- lt: first position is somewhere left of the second.
- adjacent: positions differ by exactly 1.
- immediately_left: first position plus 1 equals the second.
- distance: absolute position difference; also include an integer distance field. One house BETWEEN means distance 2.
Composite relations: and/or take a list of relation objects as args; not takes one relation object as its only argument.
Do not infer a final answer. Translate each clue independently. Domain and all-different constraints are already supplied.
Do not merge or omit clues even if redundant. Do not add clues. Use exact category and value strings below.
"""
    return base + instructions + "\nDomains: " + json.dumps(domains(row)) + "\nClues to translate: " + json.dumps(clues) + "\nYour constraints array MUST contain exactly " + str(len(clues)) + " entries, with clue numbers " + json.dumps([int(n) for n, _ in clues]) + ". Fill every entry with the translation of its corresponding clue. Return JSON only."



def summarize(path):
    records=[json.loads(s) for s in Path(path).read_text().splitlines()]
    report={}
    for method in ('direct','symbolic'):
        rs=[r for r in records if r['method']==method]; scored=[r['score'] for r in rs if r['score'] is not None]
        report[method]={'completed':len(rs),'errors':sum('error' in r for r in rs),'scored':len(scored),'puzzle_accuracy':sum(s['exact'] for s in scored)/len(scored) if scored else None,'cell_accuracy':sum(s['correct_cells'] for s in scored)/sum(s['total_cells'] for s in scored) if scored else None,'unique_sat':sum(r.get('unique') is True for r in rs)}
    Path(path).with_name('summary.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))


