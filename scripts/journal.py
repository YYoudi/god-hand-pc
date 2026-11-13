"""Original GPL-3.0-only, buildless English journal. No external dependencies."""
import argparse
import datetime
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import struct
from urllib.parse import unquote, urlsplit
import zlib

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
LABELS = {"done": "Verified for stated scope", "in_progress": "In progress",
          "planned": "Planned", "blocked": "Blocked", "paused": "Paused"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def png_size(blob):
    require(blob.startswith(b"\x89PNG\r\n\x1a\n") and len(blob) <= 20*1024*1024,
            "Invalid/oversized screenshot PNG")
    at, dimensions, image = 8, None, False
    while at + 12 <= len(blob):
        length = struct.unpack_from(">I", blob, at)[0]
        end = at + 12 + length
        require(end <= len(blob), "Truncated PNG")
        tag, payload = blob[at+4:at+8], blob[at+8:end-4]
        require(zlib.crc32(tag+payload) == struct.unpack_from(">I", blob, end-4)[0], "PNG CRC")
        if dimensions is None:
            require(tag == b"IHDR" and length == 13, "PNG IHDR required")
            w,h,depth,color,c,f,i = struct.unpack(">IIBBBBB", payload)
            require(0 < w <= 8192 and 0 < h <= 8192 and w*h <= 16777216 and
                    depth == 8 and color in (2,6) and c == f == 0 and i in (0,1), "PNG profile")
            dimensions = (w,h)
        else:
            require(tag != b"IHDR", "Duplicate IHDR")
        image |= tag == b"IDAT"
        if tag == b"IEND":
            require(length == 0 and image and end == len(blob), "PNG end")
            return dimensions
        at = end
    raise ValueError("Missing PNG end")


def host_jpeg_size(blob):
    """Bounded baseline JFIF envelope, not a JPEG decoder or pixel-fidelity test.

    A separate publication profile for unchanged owned-app captures. Reject EXIF,
    comments, trailing data and unreviewed marker types; keep old PNG rules intact.
    """
    require(blob.startswith(b'\xff\xd8') and len(blob)<=20*1024*1024,
            'Invalid/oversized native host JPEG')
    at,dimensions,quant,huffman,jfif=2,None,False,False,False
    while at+4<=len(blob):
        require(blob[at]==255,'JPEG marker required')
        tag=blob[at+1];length=struct.unpack_from('>H',blob,at+2)[0]
        end=at+2+length
        require(length>=2 and end<=len(blob),'JPEG segment bounds')
        payload=blob[at+4:end];at=end
        if tag==0xe0:
            require(not jfif and dimensions is None and len(payload)==14 and
                    payload[:5]==b'JFIF\0' and payload[-2:]==b'\0\0','JPEG JFIF profile')
            jfif=True
        elif tag==0xdb:
            require(len(payload)>0,'Empty JPEG quantization table');quant=True
        elif tag==0xc4:
            require(len(payload)>0,'Empty JPEG Huffman table');huffman=True
        elif tag==0xc0:
            require(dimensions is None and len(payload)==15 and payload[0]==8 and payload[5]==3,
                    'Baseline 8-bit three-component JPEG required')
            h,w=struct.unpack_from('>HH',payload,1)
            require(0<w<=8192 and 0<h<=8192 and w*h<=16777216,'JPEG dimensions')
            dimensions=(w,h)
        elif tag==0xda:
            require(jfif and dimensions and quant and huffman and len(payload)==10 and
                    payload[0]==3 and payload[-3:]==b'\0\x3f\0','JPEG scan profile')
            # Baseline single scan: stuffed FF00 and restart markers are allowed;
            # a second scan, metadata, incomplete escape or appended file is not.
            entropy_start=at
            while at<len(blob):
                if blob[at]!=255:at+=1;continue
                require(at+1<len(blob),'Truncated JPEG entropy marker')
                marker=blob[at+1]
                if marker==0 or 0xd0<=marker<=0xd7:at+=2;continue
                require(marker==0xd9 and at>entropy_start and at+2==len(blob),'JPEG end/scan profile')
                return dimensions
            raise ValueError('Missing JPEG end')
        else:
            raise ValueError('Unapproved native host JPEG marker')
    raise ValueError('Missing JPEG scan')


def screenshot_time(item):
    """Distinguish a known artifact-save time from an unknown capture time.

    Existing captured_at records/rendering remain unchanged. A later save must
    not silently become a capture-completion or guest-frame timestamp.
    """
    if 'recorded_at' in item:
        require('captured_at' not in item and
                item.get('timestamp_basis')=='artifact-save-after-observation' and
                item.get('publication_profile')=='native-host-jpeg-v1',
                'Recorded-only native time must not claim capture completion')
        return item['recorded_at'],'Recorded after observation (not capture time): '+item['recorded_at']
    require('captured_at' in item and 'timestamp_basis' not in item,
            'Explicit capture time or separately qualified recording time required')
    return item['captured_at'],item['captured_at']


def validate(data, migration, read):
    """Validate reviewed metadata and bytes, not pixels as game/test fixtures."""
    require(data["schema"] == migration["schema"] == 1, "Unknown journal schema")
    datetime.date.fromisoformat(data["updated"])
    require(data["repo"] == "https://github.com/YYoudi/god-hand-pc", "Wrong canonical repository")
    media, ids = {}, set()
    stable_hash=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    entry_hashes=[stable_hash(e) for e in data['updates']]
    for meta in migration['entries'].values():
        require(entry_hashes.count(meta['sha256']) == 1, 'Historical entry changed/missing/duplicated')
    for pair in data["comparisons"]:
        require(pair["id"] not in ids and pair["reviewed"] is True, "Duplicate/unreviewed comparison")
        ids.add(pair["id"])
        if pair['id'] in migration['comparisons']:
            require(stable_hash(pair) == migration['comparisons'][pair['id']]['sha256'], 'Historical comparison metadata changed')
        require(pair["alignment"] in {"same-frame","same-landmark","unmatched"}, "Invalid alignment")
        require(pair["observations"] and pair["limits"] and set(pair["labels"]) == {"reference","bevy"},
                "Explicit findings, limitations and implementation labels required")
        for side in ("reference","bevy"):
            item = pair[side]
            require("original" not in item, "Raw PPM requires a separately reviewed publication profile")
            digest = item["sha256"]
            profile=item.get('publication_profile','native-png-v1')
            require(profile in {'native-png-v1','native-host-jpeg-v1'},'Unknown screenshot publication profile')
            jpeg=profile=='native-host-jpeg-v1'
            if jpeg:
                require(item.get('capture_source')=='computer-use-owned-window' and
                        item.get('unchanged_original') is True and item.get('lossy') is True,
                        'Native host JPEG source/original/lossy declaration required')
            extension='jpg' if jpeg else 'png'
            require(re.fullmatch("[a-f0-9]{64}",digest) and item["path"] == f"media/{digest}.{extension}", "Image path/hash")
            path = "docs/" + item["path"]
            blob = read(path)
            require(hashlib.sha256(blob).hexdigest() == digest, "Screenshot bytes differ")
            size=host_jpeg_size(blob) if jpeg else png_size(blob)
            require(size == (item["width"], item["height"]), "Screenshot dimensions differ")
            require(item["revision"] in {"unknown","uncommitted"} or
                    re.fullmatch("[0-9a-f]{40}",item["revision"]), "Exact revision required")
            timestamp = datetime.datetime.fromisoformat(screenshot_time(item)[0].replace("Z","+00:00"))
            require(timestamp.tzinfo is not None, "Capture timezone required")
            require(item["runtime"] and item["caption"], "Runtime/caption required")
            require(item["profile"] in {"retail-usa","prototype-june-2006"}, "Disc profile")
            media[path] = digest
        require(pair["reference"]["profile"] == pair["bevy"]["profile"], "Mixed retail/prototype pair")
    require(set(migration['comparisons']).issubset(ids), 'Missing historical comparison')
    for entry in data['updates']:
        selected = entry.get('evidence_comparisons', [])
        require(isinstance(selected, list) and all(isinstance(x, str) for x in selected),
                'Entry evidence must be a comparison ID list')
        require(len(selected) == len(set(selected)) and all(
            re.fullmatch('[a-z0-9-]+', x) and x in ids for x in selected),
            'Unknown, duplicate or unsafe entry comparison')
    for p,meta in migration['media'].items():
        require(media.get('docs/'+p) == meta['sha256'], 'Missing/changed selected migrated original')
    for name, meta in migration["reports"].items():
        require(re.fullmatch("[a-z0-9-]+[.]md",name), "Report basename")
        require(hashlib.sha256(read("docs/reports/"+name)).hexdigest() == meta["sha256"], "Migrated report changed")
    for item in data.get("captures",[]):
        digest = item["sha256"]
        require(re.fullmatch("[a-f0-9]{64}",digest) and item["path"] == f"captures/{digest}.jpg" and
                item["kind"] == "journal" and item["reviewed"] is True, "Unreviewed journal capture")
        blob = read("docs/"+item["path"])
        require(blob.startswith(b"\xff\xd8\xff") and blob.endswith(b"\xff\xd9") and len(blob) <= 1024*1024 and
                hashlib.sha256(blob).hexdigest() == digest, "Journal JPEG bytes/profile")
        media["docs/"+item["path"]] = digest
    return media


def shell(title, body, prefix=""):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · God Hand PC</title><link rel="stylesheet" href="{prefix}style.css"></head>
<body><header><a class="name" href="{prefix}index.html">God Hand PC</a><nav aria-label="Main navigation">
<a href="{prefix}index.html#journal">Journal</a><a href="{prefix}roadmap.html">Roadmap</a>
<a href="{prefix}comparisons.html">Comparisons</a><a href="{prefix}reports/index.html">Reports</a>
<a href="https://github.com/YYoudi/god-hand-pc">Source</a></nav></header><main>{body}</main>
<footer>Unofficial LasVola continuation. Personal ISO required; no game distributed.<br>
Original continuation code: GPL-3.0-only. Migrated text retains its MIT notice. Game imagery is neither MIT nor GPL.<br>
<a href="https://yyoudi.github.io/god-hand-rs/dashboard/">Historical independent Rust/Bevy lab — paused, not achieved</a> · Free GitHub Pages</footer></body></html>
'''


def linked_text(text, migration):
    """Small escaped Markdown subset, not arbitrary HTML execution."""
    pattern = re.compile(r'\[([^\]]+)\]\(([^\s)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*')
    out, at = [], 0
    for match in pattern.finditer(text):
        out.append(escape(text[at:match.start()]))
        label,url,code,bold = match.groups()
        if url:
            info=urlsplit(url)
            name=PurePosixPath(info.path).name
            if name in migration["reports"]:
                url=name[:-3]+".html"+("#"+info.fragment if info.fragment else "")
            elif not info.scheme and not url.startswith("#"):
                url="https://github.com/YYoudi/god-hand-rs/blob/"+migration["source_revision"]+"/docs/"+url
            require(urlsplit(url).scheme in {"", "https", "http"}, "Unsafe report link scheme")
            out.append(f'<a href="{escape(url,quote=True)}">{escape(label)}</a>')
        elif code is not None: out.append("<code>"+escape(code)+"</code>")
        else: out.append("<strong>"+escape(bold)+"</strong>")
        at=match.end()
    return "".join(out)+escape(text[at:])


def markdown(text, migration):
    out, paragraph, code, fence, list_open = [], [], [], False, False
    def flush():
        if paragraph: out.append("<p>"+linked_text(" ".join(paragraph),migration)+"</p>"); paragraph.clear()
    for line in text.splitlines():
        if line.startswith("```"):
            flush()
            if list_open: out.append("</ul>");list_open=False
            if fence: out.append("<pre><code>"+escape("\n".join(code))+"</code></pre>");code=[]
            fence=not fence;continue
        if fence: code.append(line);continue
        if not line.strip(): flush();continue
        heading=re.match(r'^(#{1,6})\s+(.+)',line)
        bullet=re.match(r'^\s*(?:[-*]|\d+[.])\s+(.+)',line)
        if heading or (not bullet and list_open):
            flush()
            if list_open:out.append("</ul>");list_open=False
        if heading:
            level=min(len(heading[1])+1,6); slug=re.sub('[^a-z0-9]+','-',heading[2].lower()).strip('-')
            out.append(f'<h{level} id="{slug}">{linked_text(heading[2],migration)}</h{level}>')
        elif bullet:
            flush()
            if not list_open:out.append("<ul>");list_open=True
            out.append("<li>"+linked_text(bullet[1],migration)+"</li>")
        else:paragraph.append(line)
    flush()
    if list_open:out.append("</ul>")
    require(not fence,"Unclosed report code fence")
    return "\n".join(out)


def entry_evidence(entry, comparisons):
    """Embed reviewed original build images, never arbitrary media or site captures."""
    selected = entry.get('evidence_comparisons', [])
    out = ''
    for identity in selected:
        pair = next(p for p in comparisons if p['id'] == identity)
        out += '<div class="pair">'
        for side in ('reference', 'bevy'):
            item, label = pair[side], pair['labels'][side]
            out += (f'<figure><figcaption>{escape(label)}</figcaption>'
                    f'<a href="{item["path"]}" download><img src="{item["path"]}" '
                    f'width="{item["width"]}" height="{item["height"]}" loading="lazy" '
                    f'alt="{escape(label, quote=True)}"></a>'
                    f'<p>{escape(item["caption"])}</p></figure>')
        out += ('</div><p><a href="comparisons.html#' + identity +
                '">Unchanged originals, build provenance, alignment and limits</a></p>')
    return out


def render(data, migration, read):
    outputs={}
    current_reports={e['link']['url']:e['link']['label'] for e in data['updates'] if
                     e.get('link',{}).get('url','').startswith(data['repo']+'/blob/main/') and
                     e['link']['url'].endswith('.md')}
    current_section=('<h2>Current development reports</h2><ul>'+''.join(
        '<li><a href="'+escape(url,quote=True)+'">'+escape(label)+'</a></li>'
        for url,label in current_reports.items())+'</ul>') if current_reports else ''
    report_links="".join(f'<li><a href="{name[:-3]}.html">{escape(name[:-3].replace("-"," "))}</a> · <a href="{name}" download>Unchanged Markdown</a></li>' for name in migration["reports"])
    outputs['docs/reports/index.html']=shell("Reports",'<h1>Reports</h1>'+current_section+'<h2>Migrated historical reports</h2><p>Editorial migration on '+data['migration_date']+'. These dated reports are unchanged historical evidence, not rerun experiments. Later journal entries may supersede their pending statuses.</p><ul>'+report_links+'</ul>',"../")
    for name,meta in migration["reports"].items():
        body=f'<p class="notice">Historical report, migrated unchanged on {data["migration_date"]}. Not a new technical result. Original <a href="{escape(meta["source_url"])}">source at the recorded revision</a>; <a href="{name}" download>download unchanged Markdown</a>. Current direction and limitations live in the journal/roadmap. Text retains its <a href="../IMPORTED_MIT_LICENSE.txt">MIT notice</a>.</p>'
        body+=markdown(read('docs/reports/'+name).decode('utf-8-sig'),migration)
        outputs['docs/reports/'+name[:-3]+'.html']=shell(name[:-3].replace('-',' '),body,'../')
    intro='''<h1>Development notes</h1>
<p>This project continues <a href="https://github.com/LasVola/godhand-recomp">LasVola’s God Hand PC base</a>. It is not a new Rust engine or a mirror of generated game code.</p>
<p>A supported personal USA retail ISO is required. No game, extracted assets or executable is distributed. A local opening/first-fight build and a same-size external texture test have been reproduced; a complete accurate port and remaster are <strong>not yet validated</strong>.</p>
<p><a href="https://github.com/YYoudi/god-hand-pc/blob/main/SETUP.md">ISO-required setup</a> · <a href="roadmap.html">Work ahead</a> · <a href="comparisons.html">Reviewed original comparisons</a></p>'''
    intro+='<section><details><summary>Known limits and next checks</summary><ul>'+''.join('<li>'+escape(s)+'</li>' for s in data['known_limits'])+'</ul><p>Next: '+escape(data['next'])+'</p></details></section>'
    posts=[]
    for e in data['updates']:
        digest=hashlib.sha256(json.dumps(e,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        historical=next((m for m in migration['entries'].values() if m['sha256']==digest),None)
        provenance=('<p class="meta">Historical entry, migrated unchanged. <a href="'+historical['source_url']+'">Original dated record</a>; not a new experiment.</p>' if historical else
                    '<p class="meta">Editorial transition — not a gameplay milestone.</p>' if e.get('kind')=='editorial-migration' else '')
        link=e.get('link')
        report=PurePosixPath(urlsplit(link['url']).path).name if link else ''
        href='reports/'+report[:-3]+'.html' if report in migration['reports'] else (link['url'] if link else '')
        posts.append('<article><time datetime="'+e['date']+'">'+e['date']+'</time><h2>'+escape(e['title'])+'</h2>'+provenance+'<p>'+escape(e['summary'])+'</p><ul>'+''.join('<li>'+escape(c)+'</li>' for c in e['changes'])+'</ul>'+entry_evidence(e,data['comparisons'])+'<details><summary>Evidence and limits</summary><p>'+escape(e['validation'])+'</p><p>'+escape(e['limits'])+'</p></details>'+(f'<p><a href="{escape(href,quote=True)}">{escape(link["label"])}</a></p>' if link else '')+'</article>')
    capture_links=''
    if data.get('captures'):capture_links='<h2>Journal capture</h2><ul>'+''.join('<li><a href="'+c['path']+'">'+escape(c['caption'])+'</a></li>' for c in data['captures'])+'</ul>'
    outputs['docs/index.html']=shell('Development journal',intro+'<section id="journal"><h2>Journal</h2>'+''.join(posts)+'</section>'+capture_links)
    roadmap=['# God Hand PC roadmap','','<!-- Generated from docs/journal.json; edit the canonical data. -->','','Done applies only to the stated evidence, not full-game coverage.','',data['next'],'']
    roadmap_html='<h1>Roadmap</h1><p>Evidence gates, not percentages or release promises. Historical independent-engine work remains in the old lab.</p>'
    for m in data['milestones']:
        roadmap += ['## '+m['id']+' — '+m['title'],'',m['goal'],'']
        roadmap_html+='<section><h2>'+escape(m['title'])+'</h2><p>'+escape(m['goal'])+'</p>'
        for t in m['tasks']:
            require(t['status'] in LABELS,'Invalid task status')
            status=LABELS[t['status']]
            roadmap+=['- **'+t['id']+' '+t['title']+' — '+status+':** '+t['acceptance']]
            roadmap_html+='<article id="'+t['id']+'"><h3>'+escape(t['id']+' · '+t['title'])+'</h3><p class="meta">'+status+'</p><p>'+escape(t['acceptance'])+'</p></article>'
        roadmap_html+='</section>';roadmap.append('')
    outputs['ROADMAP.md']='\n'.join(roadmap).rstrip()+'\n'
    outputs['docs/roadmap.html']=shell('Roadmap',roadmap_html)
    gallery='<h1>Selected comparisons</h1><p>Reviewed native PC outputs, emulator references and explicitly labeled GS-only replays: new experiments and preserved historical records. Each entry distinguishes its runtime, date, alignment and limitations. Historical migration is not a new result. Full-resolution original files are unretouched and individually downloadable. Emulator references are not native-port output or PS2 hardware captures. GS-only replays are not new native-port gameplay or PS2 hardware captures; historical Bevy work stays in the separate paused lab. Game imagery belongs to its rights holders; publication is the owner’s selected-screenshot request, not rights-holder permission.</p>'
    for pair in data['comparisons']:
        gallery+='<article id="'+pair['id']+'"><time>'+pair['date']+'</time><h2>'+escape(pair['title'])+'</h2><p>'+escape(pair['scenario'])+'</p><p>Alignment: <strong>'+pair['alignment']+'</strong>.</p><div class="pair">'
        for side in ('reference','bevy'):
            item=pair[side];label=pair['labels'][side]
            gallery+=f'<figure><figcaption>{escape(label)}</figcaption><a href="{item["path"]}"><img src="{item["path"]}" width="{item["width"]}" height="{item["height"]}" loading="lazy" alt="{escape(label,quote=True)}"></a><p>{escape(item["caption"])}</p><a href="{item["path"]}" download>Download unchanged original ({item["width"]} × {item["height"]})</a><details><summary>Capture provenance</summary><p>{escape(item["runtime"])}</p><p>{escape(item["profile"])} · {escape(screenshot_time(item)[1])}<br>Revision: <code>{escape(item["revision"])}</code><br>SHA-256: <code>{item["sha256"]}</code></p></details></figure>'
        gallery+='</div><ul>'+''.join('<li>'+escape(s)+'</li>' for s in pair['observations'])+'</ul><details><summary>Limits (unchanged)</summary><ul>'+''.join('<li>'+escape(s)+'</li>' for s in pair['limits'])+'</ul></details></article>'
    outputs['docs/comparisons.html']=shell('Selected comparisons',gallery)
    return outputs


class Links(HTMLParser):
    def __init__(self):super().__init__();self.targets=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in {'href','src'} and v:self.targets.append(v)


def check_links(outputs, available):
    for path,html in outputs.items():
        if not path.endswith('.html'):continue
        parser=Links();parser.feed(html)
        for url in parser.targets:
            info=urlsplit(url)
            if info.scheme or info.netloc or not info.path:continue
            target=(ROOT/PurePosixPath(path).parent/unquote(info.path)).resolve()
            require(target.is_relative_to(SITE.resolve()),'Link outside site')
            relative=target.relative_to(ROOT).as_posix()
            require(relative in available,'Broken static link: '+path+' -> '+url)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.loads((SITE/'journal.json').read_text(encoding='utf-8'))
    migration=json.loads((SITE/'migration.json').read_text(encoding='utf-8'))
    read=lambda path:(ROOT/path).read_bytes()
    validate(data,migration,read)
    outputs=render(data,migration,read)
    available={p.relative_to(ROOT).as_posix() for p in SITE.rglob('*') if p.is_file()}|set(outputs)
    check_links(outputs,available)
    for path,text in outputs.items():
        p=ROOT/path
        if args.check: require(p.read_text(encoding='utf-8')==text,'Stale generated file: '+path)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
    print('Journal, roadmap, historical reports, reviewed image hashes and local navigation: valid')


if __name__=='__main__':main()
