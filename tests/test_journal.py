"""Original static/publication checks; invented fixtures only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import subprocess
import tempfile
import unittest
import zlib

import pc
sys.path.insert(0,str(pc.ROOT/'scripts'))
import journal
from check_public_tree import validate_blob, validate_paths


class JournalTests(unittest.TestCase):
    def png(self):
        def chunk(tag,payload):
            return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload))
        return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+
                chunk(b'IDAT',zlib.compress(b'\0\x12\x34\x56'))+chunk(b'IEND',b''))

    def test_invented_png_header_crc_and_trailing_data(self):
        data=self.png();self.assertEqual(journal.png_size(data),(1,1))
        for bad in [data[:-2], data+b'extra',data[:35]+b'x'+data[36:]]:
            with self.assertRaises(ValueError):journal.png_size(bad)

    def test_game_and_generated_paths_refused_even_if_allowlisted(self):
        for p in ['docs/game.iso','docs/data.dat','generated/f.cpp','.local/private.md','../x.md']:
            with self.assertRaises(ValueError):validate_paths([p],{p})

    def test_unregistered_images_and_secrets_rejected(self):
        with self.assertRaises(ValueError):validate_blob('docs/media/invented.png',self.png(),{})
        with self.assertRaises(ValueError):validate_blob('docs/x.html',('github_pat_'+'a'*50).encode(),{})
        with self.assertRaises(UnicodeDecodeError):validate_blob('docs/x.txt',b'\xff',{})
        with self.assertRaises(ValueError):validate_blob('docs/x.txt',b'\0',{})
        validate_blob('docs/.nojekyll',b'',{})

    def test_escaped_report_markdown_and_unsafe_scheme(self):
        meta={'reports':{},'source_revision':'a'*40}
        self.assertIn('&lt;script&gt;',journal.markdown('<script>bad</script>',meta))
        with self.assertRaises(ValueError):journal.linked_text('[x](javascript:bad)',meta)
        self.assertIn('<code>&lt;x&gt;</code>',journal.markdown('`<x>`',meta))

    def test_report_links_route_to_selected_html(self):
        meta={'reports':{'prior.md':{}},'source_revision':'a'*40}
        self.assertIn('href="prior.html"',journal.linked_text('[prior](prior.md)',meta))
        self.assertIn('/blob/'+('a'*40)+'/docs/',journal.linked_text('[old](unmigrated.md)',meta))

    def test_new_shell_keeps_utf8_punctuation(self):
        text=journal.shell('Invented page','<p>Invented</p>')
        self.assertIn(' · God Hand PC',text)
        self.assertNotIn('\u00c2',text)
        self.assertNotIn('\u00e2\u20ac',text)

    def test_new_report_links_do_not_replace_historical_report_index(self):
        url='https://github.com/YYoudi/god-hand-pc/blob/main/INVENTED.md'
        entry={'date':'2026-11-09','title':'Invented current result','summary':'Invented',
               'changes':['Invented change'],'validation':'Invented check','limits':'Invented limit',
               'link':{'url':url,'label':'Invented current report'}}
        data={'repo':'https://github.com/YYoudi/god-hand-pc','migration_date':'2026-11-09',
              'known_limits':[],'next':'Invented next step','updates':[entry],
              'milestones':[],'comparisons':[],'captures':[]}
        result=journal.render(data,{'reports':{},'entries':{}},lambda p:b'')
        self.assertIn(url,result['docs/reports/index.html'])
        self.assertIn('Migrated historical reports',result['docs/reports/index.html'])
        self.assertIn('new experiments and preserved historical records',result['docs/comparisons.html'])
        self.assertNotIn('Previously reviewed original screenshots, migrated byte-for-byte.',result['docs/comparisons.html'])

    def test_fresh_autocrlf_checkout_preserves_original_report_bytes(self):
        with tempfile.TemporaryDirectory(prefix='godhand-journal-eol-synthetic-') as name:
            root=Path(name);source=root/'source';source.mkdir()
            def git(*args,cwd=source):
                return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.STDOUT)
            git('init','-b','main');git('config','core.autocrlf','true')
            (source/'.gitattributes').write_bytes((pc.ROOT/'.gitattributes').read_bytes())
            invented=b'# Invented historical text\n\nNo game data.\n'
            path=source/'docs/reports/invented.md';path.parent.mkdir(parents=True);path.write_bytes(invented)
            git('add','--','.gitattributes','docs/reports/invented.md')
            git('-c','user.name=Synthetic Journal Test','-c','user.email=test@example.invalid',
                'commit','-m','Invented immutable report')
            target=root/'clone'
            git('-c','core.autocrlf=true','clone',str(source),str(target))
            self.assertEqual((target/'docs/reports/invented.md').read_bytes(),invented)

    def test_broken_navigation_and_traversal_refused(self):
        for url in ['missing.html','../../outside.html']:
            with self.assertRaises(ValueError):journal.check_links({'docs/index.html':'<a href="'+url+'">x</a>'},set())
        journal.check_links({'docs/index.html':'<a href="reports/ok.html">x</a>'},{'docs/reports/ok.html'})

    def historical_fixture(self):
        old={'date':'2001-01-02','title':'Invented historical finding'}
        digest=hashlib.sha256(json.dumps(old,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        migration={'schema':1,'entries':{'0':{'sha256':digest}},'reports':{},'comparisons':{},'media':{}}
        data={'schema':1,'updated':'2026-11-09','repo':'https://github.com/YYoudi/god-hand-pc',
              'updates':[{'title':'New entry'},old],'comparisons':[],'captures':[]}
        return data,migration

    def test_entry_build_evidence_requires_reviewed_comparison_ids(self):
        data, migration = self.historical_fixture()
        for selected in ['not-a-list', None, ['missing'], ['missing','missing'], ['unsafe#id']]:
            data['updates'][0]['evidence_comparisons'] = selected
            with self.assertRaises(ValueError):
                journal.validate(data, migration, lambda p: b'')
        data['updates'][0]['evidence_comparisons'] = []
        self.assertEqual(journal.validate(data, migration, lambda p: b''), {})

    def test_entry_embeds_only_registered_originals_and_provenance_link(self):
        item = {'path':'media/' + 'a'*64 + '.png', 'width':1, 'height':1,
                'caption':'Invented native build <A>'}
        pair = {'id':'invented-native-build', 'reference':item, 'bevy':item,
                'labels':{'reference':'Invented before','bevy':'Invented after'}}
        entry = {'evidence_comparisons':['invented-native-build']}
        html = journal.entry_evidence(entry, [pair])
        self.assertEqual(html.count('<img '), 2)
        self.assertIn('download><img', html)
        self.assertIn('comparisons.html#invented-native-build', html)
        self.assertIn('Invented native build &lt;A&gt;', html)
        self.assertEqual(journal.entry_evidence({}, [pair]), '')

    def test_future_posts_do_not_break_historical_identity(self):
        data,migration=self.historical_fixture()
        data['updates'].insert(0,{'title':'Later feature, not a migration'})
        self.assertEqual(journal.validate(data,migration,lambda p:b''),{})

    def test_changed_or_duplicated_historical_entry_refused(self):
        data,migration=self.historical_fixture()
        data['updates'][-1]['title']='Not the original finding'
        with self.assertRaises(ValueError):journal.validate(data,migration,lambda p:b'')
        data,migration=self.historical_fixture();data['updates'].append(data['updates'][-1])
        with self.assertRaises(ValueError):journal.validate(data,migration,lambda p:b'')


if __name__=='__main__':unittest.main()
