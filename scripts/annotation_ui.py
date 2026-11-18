"""Local browser annotation tool. Run with Python; no external services required."""
import hashlib
import json
import shutil
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/annotations/eval_gold.jsonl'
PAGE = ROOT / 'scripts/annotation_ui.html'
URL = 'http://127.0.0.1:8765'


class Handler(BaseHTTPRequestHandler):
    def reply(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/records':
            raw = DATA.read_bytes()
            self.reply({'records': [json.loads(x) for x in raw.decode('utf-8').splitlines()],
                        'version': hashlib.sha256(raw).hexdigest()})
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(PAGE.read_bytes())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != '/api/save' or self.headers.get('Origin') != URL:
            return self.reply({'error': 'İstek reddedildi.'}, 403)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 100000:
                raise ValueError('Geçersiz istek boyutu.')
            change = json.loads(self.rfile.read(length))
            raw = DATA.read_bytes()
            if change.get('version') != hashlib.sha256(raw).hexdigest():
                return self.reply({'error': 'Dosya başka bir yerde değişti. Sayfayı yenileyin.'}, 409)
            records = [json.loads(x) for x in raw.decode('utf-8').splitlines()]
            record = next(r for r in records if r['id'] == change['id'])
            entities = change['entities']
            if not isinstance(entities, list) or type(change['complete']) is not bool:
                raise ValueError('Geçersiz kayıt.')
            seen = set()
            for e in entities:
                if not isinstance(e, dict) or set(e) != {'text', 'type'}:
                    raise ValueError('Geçersiz varlık.')
                if e['type'] not in ('PERSON', 'ORGANIZATION', 'LOCATION') or not isinstance(e['text'], str) or not e['text'].strip() or e['text'] not in record['text']:
                    raise ValueError('Varlık metindeki ifadeyle aynı olmalı.')
                key = (e['text'], e['type'])
                if key in seen:
                    raise ValueError('Tekrarlanan varlık.')
                seen.add(key)
            backup = DATA.parent / 'backups'
            backup.mkdir(exist_ok=True)
            shutil.copy2(DATA, backup / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.jsonl'))
            record['gold_entities'] = entities
            record['annotation_complete'] = change['complete']
            result = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records).encode('utf-8')
            temp = DATA.with_suffix('.tmp')
            temp.write_bytes(result)
            temp.replace(DATA)
            self.reply({'version': hashlib.sha256(result).hexdigest()})
        except (ValueError, KeyError, StopIteration, TypeError) as error:
            self.reply({'error': str(error) or 'Kayıt bulunamadı.'}, 400)
        except OSError:
            self.reply({'error': 'Dosya kaydedilemedi. Seçimleriniz ekranda korunuyor.'}, 500)


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8765), Handler)
    threading.Timer(0.5, lambda: webbrowser.open(URL)).start()
    print('Anotasyon arayüzü: ' + URL, flush=True)
    server.serve_forever()
