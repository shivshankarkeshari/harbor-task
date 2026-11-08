#!/usr/bin/env python3
"""Original local work-order fixture application. Python standard library only."""
import argparse
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent


def connect():
    db = sqlite3.connect(DATABASE, timeout=15)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    with connect() as db:
        db.executescript('''
          CREATE TABLE IF NOT EXISTS preferences (operator TEXT PRIMARY KEY,locale TEXT NOT NULL,notifications INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY,title TEXT NOT NULL,customer TEXT NOT NULL,status TEXT NOT NULL,budget_minor INTEGER NOT NULL,crew_id INTEGER);
          CREATE TABLE IF NOT EXISTS crews (id INTEGER PRIMARY KEY,name TEXT NOT NULL,available INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY,name TEXT NOT NULL,stock INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY,kind TEXT NOT NULL,actor TEXT NOT NULL,payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS charges (id INTEGER PRIMARY KEY,order_id INTEGER NOT NULL,amount_minor INTEGER NOT NULL,memo TEXT NOT NULL);
        ''')
        if not db.execute('SELECT count(*) FROM preferences').fetchone()[0]:
            db.executemany('INSERT INTO preferences VALUES (?,?,?)',[('robin','en',1),('amal','de',0)])
            db.executemany('INSERT INTO crews VALUES (?,?,?)',[(1,'North crew',1),(2,'West crew',0)])
            db.executemany('INSERT INTO parts VALUES (?,?,?)',[(1,'Adapter A',4),(2,'Valve B',0),(3,'Cable C',1),(4,'Seal D',2),(5,'Bolt E',11),(6,'Clip F',102)])
            db.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)',[
                (i,'Ready for pickup' if i==1 else f'Workshop job {i}','Open House Ltd' if i==1 else f'Customer {i}',
                 'OPEN' if i % 3 else 'ASSIGNED',125000+i*100,None if i % 3 else 1) for i in range(1,13)])
            db.execute('INSERT INTO activity(kind,actor,payload) VALUES (?,?,?)',('opened','robin',json.dumps({'title':'Ready for pickup'})))


class App(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, status, data, content_type='application/json'):
        raw = json.dumps(data,ensure_ascii=False).encode() if content_type=='application/json' else data
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        try: self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError): pass

    def failure(self, code, message, **details):
        self.send(400,{'ok':False,'error':{'code':code,'message':message,**details}})

    def do_GET(self):
        url=urlparse(self.path)
        if url.path=='/healthz':
            return self.send(200,{'ok':True})
        if url.path=='/api/bootstrap':
            operator=parse_qs(url.query).get('operator',['robin'])[0]
            with connect() as db:
                pref=db.execute('SELECT * FROM preferences WHERE operator=?',(operator,)).fetchone()
                if pref is None: return self.send(404,{'error':'unknown operator'})
                data={name:[dict(row) for row in db.execute('SELECT * FROM '+name+' ORDER BY id')]
                      for name in ['orders','crews','parts','activity','charges']}
                data['preferences']=dict(pref)
                data['operators']=[{'id':'robin','name':'Robin'},{'id':'amal','name':'Amal'}]
            return self.send(200,data)
        if url.path=='/api/export':
            with connect() as db:
                stream=io.StringIO();writer=csv.writer(stream)
                writer.writerow(['order_id','title','status','budget_minor','crew_id'])
                writer.writerows(db.execute('SELECT id,title,status,budget_minor,crew_id FROM orders ORDER BY id'))
            return self.send(200,stream.getvalue().encode(),'text/csv; charset=utf-8')
        if url.path.startswith('/api/'):
            return self.send(404,{'error':'unknown endpoint'})
        relative='index.html' if url.path=='/' else url.path.lstrip('/')
        path=(ROOT/'static'/relative).resolve()
        if not path.is_relative_to((ROOT/'static').resolve()) or not path.is_file():
            return self.send(404,b'Not found','text/plain')
        types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8'}
        self.send(200,path.read_bytes(),types.get(path.suffix,'application/octet-stream'))

    def do_POST(self):
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length>1024*1024: return self.send(413,{'error':'request too large'})
            body=json.loads(self.rfile.read(length))
        except (ValueError,TypeError): return self.failure('BAD_REQUEST','Expected a JSON object.')
        if not isinstance(body,dict): return self.failure('BAD_REQUEST','Expected a JSON object.')
        operator=self.headers.get('X-Operator','robin')
        with connect() as db:
            if not db.execute('SELECT 1 FROM preferences WHERE operator=?',(operator,)).fetchone():
                return self.send(403,{'error':'unknown operator'})
            route=urlparse(self.path).path
            if route=='/api/preferences':
                if body.get('locale') not in ['en','de','ar']: return self.failure('LOCALE_INVALID','Unsupported locale.')
                db.execute('UPDATE preferences SET locale=?,notifications=? WHERE operator=?',
                    (body['locale'],int(bool(body.get('notifications',True))),operator))
            elif route=='/api/order':
                title=body.get('title','')
                if not isinstance(title,str) or not title.strip(): return self.failure('TITLE_REQUIRED','A work-order title is required.')
                amount=body.get('budget_minor')
                if type(amount) is not int or not 0<=amount<=99999999: return self.failure('AMOUNT_INVALID','Enter a valid amount with at most two decimal places.')
                if body.get('id'):
                    db.execute('UPDATE orders SET title=?,customer=?,budget_minor=? WHERE id=?',
                        (title,body.get('customer',''),amount,body['id']))
                    order_id=body['id']
                else:
                    cursor=db.execute('INSERT INTO orders(title,customer,status,budget_minor) VALUES (?,?,?,?)',
                        (title,body.get('customer',''),'OPEN',amount));order_id=cursor.lastrowid
                db.execute('INSERT INTO activity(kind,actor,payload) VALUES (?,?,?)',('saved',operator,json.dumps({'title':title})))
                result={'ok':True,'order_id':order_id}
            elif route=='/api/assign':
                crew=db.execute('SELECT * FROM crews WHERE id=?',(body.get('crew_id'),)).fetchone()
                if crew is None or not crew['available']: return self.failure('CREW_UNAVAILABLE','The selected crew is unavailable.')
                db.execute('UPDATE orders SET crew_id=?,status=? WHERE id=?',(crew['id'],'ASSIGNED',body.get('order_id')))
            elif route=='/api/reserve':
                part=db.execute('SELECT * FROM parts WHERE id=?',(body.get('part_id'),)).fetchone()
                units=body.get('units')
                if part is None or type(units) is not int or units<=0: return self.failure('QUANTITY_INVALID','Enter a positive whole quantity.')
                if units>part['stock']: return self.failure('PARTS_SHORT','Not enough parts are available.',available=part['stock'])
                db.execute('UPDATE parts SET stock=stock-? WHERE id=?',(units,part['id']))
                db.execute('INSERT INTO activity(kind,actor,payload) VALUES (?,?,?)',('reserved',operator,json.dumps({'count':units,'name':part['name']})))
            elif route=='/api/charge':
                amount=body.get('amount_minor')
                if type(amount) is not int or not 0<=amount<=99999999: return self.failure('AMOUNT_INVALID','Enter a valid amount with at most two decimal places.')
                db.execute('INSERT INTO charges(order_id,amount_minor,memo) VALUES (?,?,?)',(body.get('order_id'),amount,body.get('memo','')))
            elif route=='/api/complete':
                ids=body.get('ids',[])
                if not ids or not all(type(i) is int for i in ids): return self.failure('SELECTION_REQUIRED','Select at least one work order.')
                db.execute('UPDATE orders SET status=? WHERE id IN ('+','.join('?' for _ in ids)+')',['DONE',*ids])
                db.execute('INSERT INTO activity(kind,actor,payload) VALUES (?,?,?)',('completed',operator,json.dumps({'count':len(ids)})))
            else: return self.send(404,{'error':'unknown endpoint'})
        self.send(200,result if route=='/api/order' else {'ok':True})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8000);parser.add_argument('--data',type=Path,default=Path('/tmp/field-desk'))
    args=parser.parse_args();args.data.mkdir(parents=True,exist_ok=True);DATABASE=args.data/'desk.sqlite'
    initialize();ThreadingHTTPServer(('127.0.0.1',args.port),App).serve_forever()
