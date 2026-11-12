"""Interface locale : python3 Scripts/pipeline_et_validation/validation_web/serveur.py."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import threading
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
FILES = ('reference_annotations.csv', 'reference_annotations_validees.csv',
         'annotations_consolidees_a_valider.csv', 'suivi_annotations.csv',
         'validations_documents.json')


class Store:
    def __init__(self, root, folder=None, lot_file='lot_pilote_12_documents.csv'):
        self.root = Path(root)
        self.folder = Path(folder) if folder else self.root / 'archives' / 'evaluations_historiques'
        self.lot_file = lot_file
        self.lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)

    def read(self, name):
        with (self.folder / name).open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            return reader.fieldnames, list(reader)

    def version(self):
        h = hashlib.sha256()
        for name in FILES:
            path = self.folder / name
            h.update(name.encode())
            h.update(path.read_bytes() if path.exists() else b'')
        return h.hexdigest()

    def documents(self):
        return self.read(self.lot_file)[1]

    def document(self, ident):
        return next((x for x in self.documents() if x['document_id'] == ident), None)

    def source(self, document, field):
        if field == 'pdf':
            return self.root.parent / 'donnees' / 'comptes_rendus' / 'total' / Path(document[field]).name
        source = Path(document[field])
        if source.parts and source.parts[0] in {'evaluation_extraction', 'evaluation'}:
            source = Path(*source.parts[1:])
            if source.parts and source.parts[0] == self.folder.name:
                source = Path(*source.parts[1:])
            path = (self.folder / source).resolve()
        else:
            path = (self.root / source).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError('Chemin source hors du dossier de travail.')
        return path

    def states(self):
        path = self.folder / 'validations_documents.json'
        return json.loads(path.read_text()) if path.exists() else {}

    def pages(self, document):
        """Texte par page, ou pages vides lorsque seul le PDF est lisible."""
        chemin = self.source(document, 'texte_pour_annotation')
        pages = chemin.read_text(encoding='utf-8').split('\f') if chemin.exists() else []
        if pages and not pages[-1].strip():
            pages.pop()
        if not pages:
            pages = [''] * max(1, int(document.get('nombre_pages') or 1))
        return pages

    def load(self, ident):
        with self.lock:
            doc = self.document(ident)
            if not doc:
                raise ValueError('Document hors du lot de validation.')
            fields, rows = self.read('reference_annotations.csv')
            pages = self.pages(doc)
            status = next(x for x in self.read('suivi_annotations.csv')[1] if x['document_id'] == ident)
            return dict(document=doc, fields=fields, rows=[x for x in rows if x['document_id'] == ident],
                        pages=pages, version=self.version(), status=status['statut'])

    @staticmethod
    def csv_bytes(fields, rows):
        text = io.StringIO(newline='')
        writer = csv.DictWriter(text, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
        return text.getvalue().encode('utf-8-sig')

    @staticmethod
    def atomic(path, data):
        temp = path.with_name(path.name + '.tmp-' + secrets.token_hex(6))
        try:
            temp.write_bytes(data)
            os.replace(temp, path)
        finally:
            if temp.exists():
                temp.unlink()

    def save(self, payload):
        with self.lock:
            if not isinstance(payload, dict):
                raise ValueError('Objet JSON attendu.')
            if payload.get('version') != self.version():
                raise RuntimeError('Les fichiers ont changé depuis leur ouverture. Recharge le document avant de sauvegarder.')
            ident = payload.get('document_id')
            doc = self.document(ident)
            if not doc:
                raise ValueError('Document hors du lot de validation.')
            validate = payload.get('validate') is True
            if validate and (payload.get('reviewed_all') is not True or not str(payload.get('reviewer', '')).strip()):
                raise ValueError('Indique le nom du relecteur et confirme la lecture intégrale du document.')
            incoming = payload.get('rows')
            if not isinstance(incoming, list) or len(incoming) > 2000:
                raise ValueError('Liste d’annotations invalide.')
            fields, all_rows = self.read('reference_annotations.csv')
            page_count = len(self.pages(doc))
            new = []
            for i, row in enumerate(incoming, 1):
                if not isinstance(row, dict) or any(not isinstance(v, str) for v in row.values()):
                    raise ValueError(f'Ligne {i} : valeurs textuelles attendues.')
                item = {k: row.get(k, '').strip() for k in fields}
                for key in ('nom', 'page', 'extrait_exact', 'date_conseil'):
                    if not item[key]:
                        raise ValueError(f'Ligne {i} : champ {key} obligatoire.')
                if not item['page'].isdigit() or not 1 <= int(item['page']) <= page_count:
                    raise ValueError(f'Ligne {i} : page invalide (1 à {page_count}).')
                date.fromisoformat(item['date_conseil'])
                if item['type_nomination'] not in ('fonction_individuelle', 'conseil_administration', 'autre'):
                    raise ValueError(f'Ligne {i} : type de nomination invalide.')
                if validate and (not item['fonction'] or not item['ministere']) and not item['commentaire']:
                    raise ValueError(f'Ligne {i} : explique les champs absents dans le commentaire.')
                item.update(document_id=ident, statut_verification='verifie_sur_pdf' if validate else 'a_verifier')
                if validate:
                    item['mode_proposition'] = 'relecture_interface'
                else:
                    item['mode_proposition'] = item.get('mode_proposition') or 'saisie_interface'
                new.append(item)
            merged = [x for x in all_rows if x['document_id'] != ident] + new
            gold_fields, _ = self.read('reference_annotations_validees.csv')
            gold = [x for x in merged if x['statut_verification'] == 'verifie_sur_pdf']
            status_fields, statuses = self.read('suivi_annotations.csv')
            now = datetime.now(timezone.utc).isoformat()
            states = self.states()
            states[ident] = dict(valide=validate, nombre_lignes=len(new), relecteur=str(payload.get('reviewer', '')).strip(), date_utc=now)
            for status in statuses:
                if status['document_id'] == ident:
                    status.update(statut=('annote_et_verifie' if new else 'aucune_nomination_verifiee') if validate else 'propositions_a_valider',
                                  nombre_propositions='0' if validate else str(len(new)),
                                  note='Lecture intégrale confirmée dans l’interface.' if validate else 'Brouillon enregistré ; document à relire intégralement.')
            outputs = {
                FILES[0]: self.csv_bytes(fields, merged),
                FILES[1]: self.csv_bytes(gold_fields, gold),
                FILES[2]: self.csv_bytes(fields, merged),
                FILES[3]: self.csv_bytes(status_fields, statuses),
                FILES[4]: json.dumps(states, ensure_ascii=False, indent=2).encode(),
            }
            backup = self.folder / 'sauvegardes_validation' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + secrets.token_hex(4))
            backup.mkdir(parents=True)
            previous = {}
            for name in FILES:
                path = self.folder / name
                previous[name] = path.read_bytes() if path.exists() else None
                if previous[name] is not None:
                    (backup / name).write_bytes(previous[name])
            written = []
            try:
                for name, data in outputs.items():
                    self.atomic(self.folder / name, data)
                    written.append(name)
            except OSError:
                for name in reversed(written):
                    if previous[name] is None:
                        (self.folder / name).unlink(missing_ok=True)
                    else:
                        self.atomic(self.folder / name, previous[name])
                raise
            return dict(version=self.version(), backup=str(backup.relative_to(self.root)))


class Store30(Store):
    """Édite les fichiers du protocole courant, sans toucher aux archives."""
    fields = ['document_id', 'date_conseil', 'nom', 'fonction', 'ministere',
              'statut_verification', 'page', 'extrait_exact', 'type_nomination',
              'civilite', 'matricule', 'commentaire']
    files = ('reference_30.csv', 'validation_30.csv', 'validations_30.json')

    def __init__(self, root, folder=None, lot_file='evaluation_30.csv'):
        super().__init__(root, folder or Path(root) / 'lots', lot_file)

    def version(self):
        h = hashlib.sha256()
        for name in (*self.files, self.lot_file):
            p = self.folder / name
            h.update(name.encode())
            h.update(p.read_bytes() if p.exists() else b'')
        return h.hexdigest()

    def documents(self):
        docs = self.read(self.lot_file)[1]
        if len(docs) != 30 or len({d['document_id'] for d in docs}) != 30:
            raise ValueError('Le protocole exige exactement 30 documents distincts.')
        for i, doc in enumerate(docs, 1):
            match = __import__('re').search(r'(20\d{2})[_-](\d{2})[_-](\d{2})', doc['document_id'])
            doc.update(ordre_relecture=i, motif_selection='Lot d’évaluation de 30 PDF — relecture intégrale.',
                       date_nom_fichier='-'.join(match.groups()) if match else '')
        return docs

    def source(self, document, field):
        if field != 'pdf':
            raise ValueError('Source inconnue.')
        path = (self.root.parent / document['pdf_source']).resolve()
        corpus = (self.root.parent / 'donnees/comptes_rendus/total').resolve()
        if not path.is_relative_to(corpus):
            raise ValueError('PDF hors du corpus.')
        return path

    def pages(self, document):
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        pdf = self.source(document, 'pdf')
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != document['sha256']:
            raise ValueError('Le PDF a changé depuis la constitution du lot (SHA-256 différent).')
        with fitz.open(pdf) as doc:
            return [page.get_text() for page in doc]

    def load(self, ident):
        with self.lock:
            doc = self.document(ident)
            if not doc:
                raise ValueError('Document hors du lot des 30 PDF.')
            refs = self.read('reference_30.csv')[1]
            status = next(x['statut'] for x in self.read('validation_30.csv')[1] if x['document_id'] == ident)
            states_path = self.folder / 'validations_30.json'
            states = json.loads(states_path.read_text()) if states_path.exists() else {}
            rows = [x for x in refs if x['document_id'] == ident]
            # Propositions uniquement à la première ouverture ; jamais après une suppression enregistrée.
            if not rows and ident not in states and status != 'valide':
                predictions = self.root / 'evaluation/extractions_pipeline_evaluation_30.csv'
                if predictions.exists():
                    with predictions.open(encoding='utf-8-sig', newline='') as f:
                        rows = [{k: x.get(k, '') for k in self.fields} for x in csv.DictReader(f) if x['document_id'] == ident]
            return dict(document=doc, fields=self.fields, rows=rows, pages=self.pages(doc),
                        version=self.version(), status=status)

    def save(self, payload):
        with self.lock:
            if not isinstance(payload, dict):
                raise ValueError('Objet JSON attendu.')
            if payload.get('version') != self.version():
                raise RuntimeError('Les fichiers ont changé. Rechargez le document.')
            ident = payload.get('document_id')
            doc = self.document(ident)
            if not doc:
                raise ValueError('Document hors du lot des 30 PDF.')
            validate = payload.get('validate') is True
            reviewer = str(payload.get('reviewer', '')).strip()
            if validate and (payload.get('reviewed_all') is not True or not reviewer):
                raise ValueError('Confirmez la lecture intégrale et indiquez le relecteur.')
            incoming = payload.get('rows')
            if not isinstance(incoming, list) or len(incoming) > 2000:
                raise ValueError('Liste d’annotations invalide.')
            page_count = len(self.pages(doc))
            new = []
            for row in incoming:
                if not isinstance(row, dict) or any(not isinstance(v, str) for v in row.values()):
                    raise ValueError('Valeurs textuelles attendues.')
                item = {k: row.get(k, '').strip() for k in self.fields}
                if not all(item[k] for k in ('nom', 'page', 'date_conseil', 'extrait_exact')):
                    raise ValueError('Nom, page, date et extrait source obligatoires.')
                if not item['page'].isdigit() or not 1 <= int(item['page']) <= page_count:
                    raise ValueError('Page invalide.')
                date.fromisoformat(item['date_conseil'])
                if item['type_nomination'] and item['type_nomination'] not in ('fonction_individuelle', 'conseil_administration', 'autre'):
                    raise ValueError('Type de nomination invalide.')
                if validate and (not item['fonction'] or not item['ministere']) and not item['commentaire']:
                    raise ValueError('Expliquez les champs absents dans le commentaire.')
                item.update(document_id=ident, statut_verification='valide' if validate else 'a_verifier')
                new.append(item)
            refs = self.read('reference_30.csv')[1]
            merged = [x for x in refs if x['document_id'] != ident] + new
            fields, statuses = self.read('validation_30.csv')
            for x in statuses:
                if x['document_id'] == ident:
                    x['statut'] = 'valide' if validate else 'a_relire'
            state_path = self.folder / 'validations_30.json'
            states = json.loads(state_path.read_text()) if state_path.exists() else {}
            states[ident] = dict(valide=validate, relecteur=reviewer, nombre_lignes=len(new),
                                 date_utc=datetime.now(timezone.utc).isoformat())
            outputs = {'reference_30.csv': self.csv_bytes(self.fields, merged),
                       'validation_30.csv': self.csv_bytes(fields, statuses),
                       'validations_30.json': json.dumps(states, ensure_ascii=False, indent=2).encode()}
            backup = self.folder / 'sauvegardes_validation' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + secrets.token_hex(4))
            backup.mkdir(parents=True)
            previous = {}
            for name in outputs:
                p = self.folder / name
                previous[name] = p.read_bytes() if p.exists() else None
                if previous[name] is not None:
                    (backup / name).write_bytes(previous[name])
            written = []
            try:
                for name, data in outputs.items():
                    self.atomic(self.folder / name, data)
                    written.append(name)
            except OSError:
                for name in reversed(written):
                    if previous[name] is None:
                        (self.folder / name).unlink(missing_ok=True)
                    else:
                        self.atomic(self.folder / name, previous[name])
                raise
            return dict(version=self.version(), backup=str(backup.relative_to(self.root)))


def handler_for(store):
    class Handler(BaseHTTPRequestHandler):
        def local_host(self):
            return self.headers.get('Host', '').split(':')[0] in ('localhost', '127.0.0.1')

        def send(self, body, kind='application/json; charset=utf-8', code=200):
            data = json.dumps(body, ensure_ascii=False).encode() if isinstance(body, (dict, list)) else body
            self.send_response(code)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if not self.local_host():
                self.send(dict(error='Accès local uniquement.'), code=403)
                return
            url = urlparse(self.path)
            ident = parse_qs(url.query).get('id', [''])[0]
            try:
                if url.path == '/':
                    self.send(Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
                elif url.path == '/api/documents':
                    self.send(dict(documents=store.documents(), token=store.token, campagne="evaluation_30" if isinstance(store, Store30) else "historique", lot=str(store.folder / store.lot_file)))
                elif url.path == '/api/document':
                    self.send(store.load(ident))
                elif url.path == '/pdf':
                    doc = store.document(ident)
                    if not doc:
                        raise ValueError('Document inconnu.')
                    self.send(store.source(doc, 'pdf').read_bytes(), 'application/pdf')
                else:
                    self.send(dict(error='Adresse inconnue.'), code=404)
            except (ValueError, OSError, StopIteration) as error:
                self.send(dict(error=str(error)), code=400)

        def do_POST(self):
            if not self.local_host() or self.path != '/api/save' or self.headers.get('X-Validation-Token') != store.token:
                self.send(dict(error='Requête non autorisée.'), code=403)
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 10_000_000:
                    raise ValueError('Taille de requête invalide.')
                result = store.save(json.loads(self.rfile.read(size)))
                self.send(result)
            except RuntimeError as error:
                self.send(dict(error=str(error)), code=409)
            except (ValueError, OSError, TypeError) as error:
                self.send(dict(error=str(error)), code=400)
    return Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--ouvrir', action='store_true')
    parser.add_argument('--dossier-validation', default=str(ROOT / 'lots'),
                        help='Dossier contenant les CSV de la campagne de validation.')
    parser.add_argument('--lot', default='evaluation_30.csv',
                        help='Nom du manifeste CSV du lot dans ce dossier.')
    args = parser.parse_args()
    dossier = Path(args.dossier_validation)
    if not dossier.is_absolute():
        dossier = ROOT / dossier
    # Le serveur courant utilise exclusivement le protocole des 30 PDF.
    # Accepter les anciennes cellules Jupyter sans rouvrir une campagne archivée.
    dossier = ROOT / 'lots'
    args.lot = 'evaluation_30.csv'
    store = Store30(ROOT, dossier, args.lot)
    store.documents()  # Vérifie les 30 identifiants avant de démarrer.
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(store))
    port_effectif = server.server_address[1]
    print(f'Validation locale : http://localhost:{port_effectif} — arrêt : Ctrl+C', flush=True)
    if args.ouvrir:
        webbrowser.open(f'http://localhost:{port_effectif}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
