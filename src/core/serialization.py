"""GDShare-compatible compact XML/plist, with gzip+URL-safe base64 k4.
See docs/format_sources.md. No savefile injection or verification flags.
"""
import base64
import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
from .objects import Object

def number(v):
    return format(v,'.9g') if isinstance(v,float) else str(v)

def pairs(d):
    return ','.join(v for k,value in d.items() for v in (str(k),number(value)))

def encode_raw(level):
    colors='|'.join('_'.join(map(str,(1,r,2,g,3,b,5,int(blend),6,ch,7,1)))
                    for ch,(r,g,b,blend) in sorted(level.colors.items()))
    header={'kA2':0,'kA3':0,'kA4':4,'kA6':1,'kA7':1,'kA13':0,'kS38':colors}
    return pairs(header)+';'+''.join(pairs(o.fields())+';' for o in level.objects)

def parse_pairs(text):
    tokens=text.split(',')
    if len(tokens)%2: raise ValueError('Odd number of tokens')
    d={}
    for k,v in zip(tokens[::2],tokens[1::2]):
        if k in d: raise ValueError('Duplicate property')
        d[k]=v
    return d

def decode_raw(raw):
    if not raw.endswith(';'): raise ValueError('Missing terminator')
    header,*parts=raw.split(';')[:-1]
    head=parse_pairs(header)
    if 'kA4' not in head: raise ValueError('Missing header')
    objects=[]
    for part in parts:
        d=parse_pairs(part)
        try:
            obj=Object(int(d.pop('1')),float(d.pop('2')),float(d.pop('3')),
                float(d.pop('6','0')),float(d.pop('32','1')),
                tuple(map(int,d.pop('57','').split('.'))) if d.get('57') else (),
                int(d.pop('21','1')),
                {int(k):float(v) for k,v in d.items()})
            obj.validate()
        except (KeyError,ValueError) as e:
            raise ValueError(f'Invalid object: {e}') from e
        objects.append(obj)
    return head,objects

def export_gmd(level, path):
    raw=encode_raw(level)
    payload=base64.urlsafe_b64encode(gzip.compress(raw.encode(),mtime=0)).decode()
    plist=ET.Element('plist',version='1.0',gjver='2.0')
    outer=ET.SubElement(plist,'dict')
    ET.SubElement(outer,'k').text='root'
    data=ET.SubElement(outer,'dict')
    fields={'kCEK':( 'i',4),'k2':('s',level.name),'k4':('s',payload),
            'k5':('s','GD Challenge Engine'),'k14':('f',None),
            'k21':('i',2),'k48':('i',len(level.objects))}
    for key,(tag,value) in fields.items():
        ET.SubElement(data,'k').text=key
        el=ET.SubElement(data,tag)
        if value is not None: el.text=str(value)
    Path(path).write_bytes(b'<?xml version="1.0"?>\n'+ET.tostring(plist,encoding='utf-8'))

def read_gmd(path):
    tree=ET.parse(path)
    outer=tree.getroot().find('dict')
    if outer is None or outer.findtext('k') != 'root': raise ValueError('Missing root')
    data=outer.find('dict')
    if data is None: raise ValueError('Missing dictionary')
    children=list(data)
    fields={children[i].text:children[i+1].text for i in range(0,len(children),2)}
    raw=gzip.decompress(base64.b64decode(fields['k4'],altchars=b'-_',validate=True)).decode()
    decode_raw(raw)
    return fields,raw

def convert(raw_path,gmd_path,name='ABSOLUTE COLLAPSE'):
    from .level import Level
    raw=Path(raw_path).read_text()
    _,objects=decode_raw(raw)
    # Preserve the exact source header, including its channels/speed.
    level=Level(name=name,objects=objects)
    export_gmd(level,gmd_path)
    tree=ET.parse(gmd_path)
    for key,value in zip(list(tree.getroot().find('dict/dict'))[::2],list(tree.getroot().find('dict/dict'))[1::2]):
        if key.text == 'k4': value.text=base64.urlsafe_b64encode(gzip.compress(raw.encode(),mtime=0)).decode()
    Path(gmd_path).write_bytes(b'<?xml version="1.0"?>\n'+ET.tostring(tree.getroot()))
