"""Normalize complete JSON tables without filling, correcting or inferring answers."""
import json,re

class TableFormatError(ValueError):
    pass


def normalize_answer(text, expected_header, house_count):
    if '<think>' in text and '</think>' not in text:
        raise TableFormatError('Unfinished thinking block')
    text=text.split('</think>')[-1].strip()
    if text.startswith('```'):
        match=re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```',text)
        if not match: raise TableFormatError('Incomplete fence or trailing content')
        text=match.group(1)
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj: raise TableFormatError('Duplicate JSON key')
            obj[k]=v
        return obj
    try: obj=json.loads(text,object_pairs_hook=unique)
    except (json.JSONDecodeError,RecursionError) as e: raise TableFormatError('Malformed complete JSON') from e
    if isinstance(obj,list):
        if not all(isinstance(r,dict) and set(r)==set(expected_header) for r in obj):
            raise TableFormatError('Each record must contain exactly the expected attributes')
        rows=[[r[h] for h in expected_header] for r in obj]
    elif isinstance(obj,dict) and set(obj)=={'header','rows'}:
        header=obj['header']; rows=obj['rows']
        if not isinstance(header,list) or not all(isinstance(h,str) for h in header) or len(header)!=len(expected_header) or set(header)!=set(expected_header):
            raise TableFormatError('Missing, duplicate or unexpected columns')
        if not isinstance(rows,list) or any(not isinstance(r,list) or len(r)!=len(header) for r in rows):
            raise TableFormatError('Invalid row shape')
        rows=[[r[header.index(h)] for h in expected_header] for r in rows]
    else: raise TableFormatError('Expected header/rows object or array of records')
    if len(rows)!=house_count: raise TableFormatError('Incorrect number of houses')
    normalized=[]
    for row in rows:
        house=row[0]
        if isinstance(house,str) and re.fullmatch(r'[0-9]+',house.strip()): house=int(house.strip())
        if type(house) is not int or not 1<=house<=house_count: raise TableFormatError('Invalid house number')
        if any(not isinstance(v,str) or not v.strip() for v in row[1:]): raise TableFormatError('Attribute values must be nonempty strings')
        normalized.append([str(house)]+row[1:])
    if len({r[0] for r in normalized})!=house_count: raise TableFormatError('Duplicate house number')
    return sorted(normalized,key=lambda r:int(r[0]))
