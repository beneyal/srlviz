import copy
import json
import os

from collections import OrderedDict
from itertools import groupby
from operator import itemgetter

from conllu.parser import parse as conllu_parse
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'balls'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

DATA_ROOT = os.path.join(app.root_path, 'static', 'dataset')


class AnnotationForm(FlaskForm):
    annotation = RadioField('Annotation', choices=[
        ('err_sent', 'Error in Sentence Alignment'),
        ('err_word', 'Error in Word Alignment'),
        ('poor_trans', 'Poor Translation'),
        ('poor_syn', 'Poor Syntactic Parsing'),
        ('poor_frame', 'Poor Frame Parsing'),
        ('ok', 'OK')
    ])
    submit = SubmitField('Annotate')


class Annotation(db.Model):
    __tablename__ = 'annotations'
    file = db.Column(db.String(40), primary_key=True)
    sentence = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(20))

    def __repr__(self):
        return f'<Annotation for {self.file}/{self.sentence}>'


def english_sents(filename):
    with open(os.path.join(DATA_ROOT, 'english_parsed', filename), encoding='utf-8') as f:
        english = conllu_parse(f.read())
    return [' '.join([row['form'] for row in sent]) for sent in english]


def get_head_of_span(tokens, start, end):
    return [token for token in tokens[start:end] if token['head'] not in range(start, end)]


def get_subtree_from_head(tokens, head):
    visited, stack = [], [head]
    while stack:
        token = stack.pop()
        if token not in visited:
            visited.append(token)
            stack.extend([t for t in tokens if t['head'] == token['id']])
    return sorted(visited, key=lambda t: t['id'])


def en_token1():
    return [OrderedDict(
        [('id', 1), ('form', "'Tonight"), ('lemma', '_'), ('upostag', 'NNP'), ('xpostag', 'NNP'), ('feats', None),
         ('head', 4), ('deprel', 'nsubj'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 2), ('form', ','), ('lemma', '_'), ('upostag', ','), ('xpostag', ','), ('feats', None), ('head', 4),
         ('deprel', 'punct'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 3), ('form', 'James'), ('lemma', '_'), ('upostag', 'NNP'), ('xpostag', 'NNP'), ('feats', None),
         ('head', 4), ('deprel', 'nsubj'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 4), ('form', 'falls'), ('lemma', '_'), ('upostag', 'VBZ'), ('xpostag', 'VBZ'), ('feats', None),
         ('head', 0), ('deprel', 'null'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 5), ('form', 'out'), ('lemma', '_'), ('upostag', 'IN'), ('xpostag', 'IN'), ('feats', None), ('head', 4),
         ('deprel', 'prep'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 6), ('form', 'of'), ('lemma', '_'), ('upostag', 'IN'), ('xpostag', 'IN'), ('feats', None), ('head', 5),
         ('deprel', 'dep'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 7), ('form', 'a'), ('lemma', '_'), ('upostag', 'DT'), ('xpostag', 'DT'), ('feats', None), ('head', 8),
         ('deprel', 'det'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 8), ('form', 'boat'), ('lemma', '_'), ('upostag', 'NN'), ('xpostag', 'NN'), ('feats', None),
         ('head', 6), ('deprel', 'pobj'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 9), ('form', '.'), ('lemma', '_'), ('upostag', '.'), ('xpostag', '.'), ('feats', None), ('head', 4),
         ('deprel', 'punct'), ('deps', None), ('misc', None)])]


def he_tokens1():
    return [OrderedDict(
        [('id', 1), ('form', '�����'), ('lemma', '_'), ('upostag', 'RB'), ('xpostag', 'RB'), ('feats', None),
         ('head', 5), ('deprel', 'parataxis'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 2), ('form', "'"), ('lemma', '_'), ('upostag', 'NNP'), ('xpostag', 'NNP'),
         ('feats', OrderedDict([('gen', 'F,M'), ('num', 'S')])), ('head', 5), ('deprel', 'parataxis'), ('deps', None),
         ('misc', None)]), OrderedDict(
        [('id', 3), ('form', ','), ('lemma', '_'), ('upostag', 'yyCM'), ('xpostag', 'yyCM'), ('feats', None),
         ('head', 5), ('deprel', 'punct'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 4), ('form', "�'����"), ('lemma', '_'), ('upostag', 'NNP'), ('xpostag', 'NNP'), ('feats', None),
         ('head', 5), ('deprel', 'subj'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 5), ('form', '����'), ('lemma', '_'), ('upostag', 'VB'), ('xpostag', 'VB'),
         ('feats', OrderedDict([('gen', 'F,M'), ('num', 'P'), ('per', '1'), ('tense', 'FUTURE')])), ('head', 0),
         ('deprel', 'ROOT'), ('deps', None), ('misc', None)]), OrderedDict(
        [('id', 6), ('form', '�����'), ('lemma', '_'), ('upostag', 'NN'), ('xpostag', 'NN'),
         ('feats', OrderedDict([('gen', 'F'), ('num', 'S')])), ('head', 5), ('deprel', 'obj'), ('deps', None),
         ('misc', None)]), OrderedDict(
        [('id', 7), ('form', '.'), ('lemma', '_'), ('upostag', 'yyDOT'), ('xpostag', 'yyDOT'), ('feats', None),
         ('head', 5), ('deprel', 'punct'), ('deps', None), ('misc', None)])]


def english_srl1():
    return [{'target': {'name': 'Partitive', 'spans': [{'start': 4, 'end': 6, 'text': 'out of'}]}, 'annotationSets': [
        {'rank': 0, 'score': 9.101323875751197,
         'frameElements': [{'name': 'Subset', 'spans': [{'start': 2, 'end': 3, 'text': 'James'}]},
                           {'name': 'Group', 'spans': [{'start': 6, 'end': 8, 'text': 'a boat'}]}]}]},
            {'target': {'name': 'Change_position_on_a_scale', 'spans': [{'start': 3, 'end': 4, 'text': 'falls'}]},
             'annotationSets': [{'rank': 0, 'score': 84.85292008150958,
                                 'frameElements': [{'name': 'Item', 'spans': [{'start': 2, 'end': 3, 'text': 'James'}]},
                                                   {'name': 'Attribute',
                                                    'spans': [{'start': 4, 'end': 8, 'text': 'out of a boat'}]}]}]},
            {'target': {'name': 'Vehicle', 'spans': [{'start': 7, 'end': 8, 'text': 'boat'}]}, 'annotationSets': [
                {'rank': 0, 'score': 26.65792845712213,
                 'frameElements': [{'name': 'Vehicle', 'spans': [{'start': 7, 'end': 8, 'text': 'boat'}]}]}]}]


def project_srl(english_srl, alignment, en_tokens, he_tokens):
    print(' '.join([t['form'] for t in en_tokens]))
    hebrew_srl = copy.deepcopy(english_srl)
    print(english_srl)

    en2he_alignment = {}
    for key, group in groupby(sorted(alignment), key=itemgetter(0)):
        en2he_alignment[key] = list(map(itemgetter(1), group))
    try:
        print(en2he_alignment)
        for obj in hebrew_srl:
            span = obj['target']['spans'][0]
            head_of_span = get_head_of_span(en_tokens, span['start'], span['end'])
            if len(head_of_span) != 1:
                continue
            head_of_span, = head_of_span
            aligned_head = en2he_alignment[head_of_span['id'] - 1]
            if len(aligned_head) != 1:
                continue
            aligned_head, = aligned_head
            subtree = get_subtree_from_head(he_tokens, he_tokens[aligned_head])
            obj['target']['spans'][0]['start'] = subtree[0]['id'] - 1
            obj['target']['spans'][0]['end'] = subtree[-1]['id'] - 1
            for fe in obj['annotationSets'][0]['frameElements']:
                span = fe['spans'][0]
                head_of_span = get_head_of_span(en_tokens, span['start'], span['end'])
                if len(head_of_span) != 1:
                    continue
                head_of_span, = head_of_span
                aligned_head = en2he_alignment[head_of_span['id'] - 1]
                if len(aligned_head) != 1:
                    continue
                aligned_head, = aligned_head
                subtree = get_subtree_from_head(he_tokens, he_tokens[aligned_head])
                span['start'] = subtree[0]['id'] - 1
                span['end'] = subtree[-1]['id'] - 1
    except KeyError:
        return []
    return hebrew_srl


def create(filename):
    with open(os.path.join(DATA_ROOT, 'english_parsed', filename), encoding='utf-8') as f:
        english = conllu_parse(f.read())
    with open(os.path.join(DATA_ROOT, 'hebrew_parsed', filename), encoding='utf-8') as f:
        hebrew = conllu_parse(f.read())
    with open(os.path.join(DATA_ROOT, 'english_srl', filename), encoding='utf-8') as f:
        english_srl = [json.loads(line.strip()) for line in f]
    with open(os.path.join(DATA_ROOT, 'fastalign_outputs', filename + '.forward'), encoding='utf-8') as f:
        alignment = []
        for line in f:
            dashed_pairs = line.strip().split(' ')
            pairs = [(int(i), int(j)) for i, j in [p.split('-') for p in dashed_pairs]]
            alignment.append(pairs)
    sents = []
    for en, he, srl, alignment_ in zip(english, hebrew, english_srl, alignment):
        obj = {
            'imdbid': filename.split('_')[2],
            'english': {
                'frames': srl['frames'],
                'words': en
            },
            'hebrew': {
                'frames': project_srl(srl['frames'], alignment_, en, he),
                'words': he
            },
            'alignment': alignment_,
        }
        sents.append(obj)
    return sents


@app.route('/')
def index():
    files = os.listdir(os.path.join(DATA_ROOT, 'english_parsed'))
    total_annotations = len(Annotation.query.all())
    annotations_by_file = {file: len([*Annotation.query.filter_by(file=file)]) for file in files}
    files.sort(key=lambda f: annotations_by_file[f], reverse=True)
    return render_template('index.html',
                           files=files,
                           total_annotations=total_annotations,
                           annotations_by_file=annotations_by_file,
                           page='File Selection')


@app.route('/<filename>')
def sentence_select(filename):
    sents = english_sents(filename)
    sent2annotation = {a.sentence: a for a in Annotation.query.filter_by(file=filename)}
    total_annotations = len(sent2annotation)
    annotated_sents = []
    for sent_id, sent in enumerate(sents):
        annotation = sent2annotation.get(sent_id)
        if annotation:
            annotated_sents.append((sent, annotation.message))
        else:
            annotated_sents.append((sent, 'none'))
    return render_template('sentenceselect.html',
                           filename=filename,
                           sents=annotated_sents,
                           total_annotations=total_annotations,
                           page='Sentence Selection')


@app.route('/<filename>/<sent_id>', methods=['GET', 'POST'])
def tree_view(filename, sent_id):
    annotation = Annotation.query.filter_by(file=filename, sentence=sent_id).first()
    if request.method == 'POST':
        form = AnnotationForm()
        if annotation:
            annotation.message = form.annotation.data
        else:
            db.session.add(Annotation(file=filename, sentence=sent_id, message=form.annotation.data))
        db.session.commit()
        return redirect(url_for('sentence_select', filename=filename))
    form = AnnotationForm(annotation=annotation.message) if annotation else AnnotationForm()
    data = create(filename)
    return render_template('treeview.html', data=data[int(sent_id)], page='Graphic', form=form)


if __name__ == '__main__':
    app.run()
