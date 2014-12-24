#!/usr/bin/env python3
"""Notmuch spam classification interface

Notspam is a spam classification system for the Notmuch mail handling
system.  It includes classifiers based on a couple of spam
classification systems.

To start, import a classifier:

>>> import notspam
>>> classifier = notspam.import_classifier('sylfilter')

To train the classifier, initialize the trainer with the given meat,
and add notmuch message objects for messages of the specified type:

>>> trainer = classifier.Trainer('spam')
>>> with notmuch.Database() as db:
...     query = db.create_query(spam_query_string)
...     for msg in query.search_messages():
...         trainer.add(msg)
>>> trainer.sync()

To classify a message as spam or ham (or unknown), pass the notmuch
message object to the spam classifier:

>>> classify = classifier.Classifier()
>>> with notmuch.Database() as db:
...     query = db.create_query(query_string)
...     for msg in query.search_messages():
...         isspam, score = classify(msg)

The train() and classify() functions are convenience wrappers to train
the classifier and classify messages.

"""

import os
import sys
import time
import signal
import notmuch
import importlib
import traceback

import notspam_classifiers
from notspam_classifiers import *

_PROG = 'notspam'
_VERSION = '0.0'
DEFAULT_CLASSIFIER = 'sylfilter'
CLASSIFIERS = notspam_classifiers.classifiers_list()

############################################################

def _usage():
    clist = '%s (default)' % DEFAULT_CLASSIFIER
    for c in CLASSIFIERS:
        if c in [DEFAULT_CLASSIFIER, 'null']:
            continue
        clist += ', %s' % c
    clist += ', null'

    print("Usage:", _PROG, "<command> [args...]")
    print("""
Notmuch spam classification interface.

Commands:

  train <meat> <search-terms>       train classifier with spam/ham
    --dry                             dry run
  classify [options] <search-terms> tag messages as spam or ham
    --spam=<tag>[,...]                tags to apply to spam
    --ham=<tag>[,...]                 tags to apply to ham
    --unk=<tag>[,...]                 tags to apply to unknown
    --dry                             dry run (no tags applied)
  check <search-terms>              synonym for 'classify --dry'
  help                              this help

Description:

  Train: Messages returned from the specified notmuch search (see
    notmuch-search-terms(7)) are handed to the classifier as training
    for the specified meat ('ham' or 'spam').  If NOTSPAM_LOG is
    non-nil, the following will be logged on stdout:

    <msg #>/<# msgs> id:<msg-id>

  Classify: Messages returned from the specified notmuch search will
    be classified as 'spam', 'ham', or '?' by the classifier.  If
    NOTSPAM_LOG is non-nil, classifications will be logged to stdout:

    <msg #>/<# msgs> <meat> (<score>) [<applied tags>] id:<msg-id>

    The (<score>) field will be left out if none is returnd by the
    classifier, and the [<applied tags>] field will be left out with
    --dry.

Classifiers:

  The following classification systems are available (can be specified
  with the NOTSPAM_CLASSIFIER environment variable):

    %s
""" % clist)
    
############################################################

def _logproc(msg):
    if not os.getenv('NOTSPAM_LOG'):
        return
    end = '\n'
    output = sys.stdout
    print(msg, end=end, file=output)

############################################################

def import_classifier(name):
    """Import named spam classifcation system.

    Returns a classification system module object.

    """
    return importlib.import_module('.'+name, package='notspam_classifiers')

def _import_classifier(name):
    print("classifier: %s" % name, file=sys.stderr)
    return import_classifier(name)
    
############################################################

def train(classifier, meat, query_string):
    """Train classifier with specified messages as ham or spam.

    'classifier' is classifier module imported with import_classifier.
    'query_string' is a notmuch query string.

    returns nmsgs

    """
    trainer = classifier.Trainer(meat)

    # open the database READ.WRITE, as this seems to be the only way
    # to lock the database, which we want during this potentially long
    # operation.
    with notmuch.Database(mode=1) as db:
        query = db.create_query(query_string)
        nmsgs = query.count_messages()
        nmsg = 0
        for msg in query.search_messages():
            nmsg += 1
            logmsg = '%d/%d' % (nmsg, nmsgs)
            try:
                cmsg = trainer.add(msg)
            except NotspamTrainingError as e:
                print("Training error: id:%s" % (msg.get_message_id()), file=sys.stderr)
                print("  %s" % e, file=sys.stderr)
                continue
            except:
                print("Fatal error: id:%s" % (msg.get_message_id()), file=sys.stderr)
                raise
            if cmsg:
                logmsg += ' %s'
            logmsg += ' id:%s     ' % (msg.get_message_id())
            _logproc(logmsg)

    trainer.sync()

    return nmsgs

def _train(*args, **kwargs):
    t = time.time()
    nmsgs = train(*args, **kwargs)
    t = time.time() - t
    print("trained %d '%s' messages in %.2fs (%.2f msgs/s)" % (
        nmsgs,
        args[1],
        t,
        nmsgs/t),
          file=sys.stderr)

############################################################

def _tag_msg(msg, tag):
    if tag[0] == '+':
        msg.add_tag(tag[1:])
    elif tag[0] == '-':
        msg.remove_tag(tag[1:])
    else:
        msg.add_tag(tag)

def classify(classifier, query_string, spam_tags=[], ham_tags=[], unk_tags=[], dry=True):
    """Classify specified messages and apply tags appropriately.

    'classifier' is classifier module imported with
    import_classifier().  'query_string' is a notmuch query string.

    Returns the tuple (nmsgs, nham, nspam, nunk) where:
      nmsgs   total number of messages in search
      nham    number of ham messages
      hspam   number of spam messages
      nunk    number of unknown messages

    """
    classify = classifier.Classifier()

    if dry:
        mode = 0
    else:
        mode = 1

    # open the database READ.WRITE
    with notmuch.Database(mode=mode) as db:
        query = db.create_query(query_string)
        nmsgs = query.count_messages()
        nmsg = 0
        nham = 0
        nspam = 0
        nunk = 0

        for msg in query.search_messages():
            nmsg += 1

            try:
                isspam, cmsg = classify(msg)
            except NotspamClassificationError as e:
                print("Classification error: id:%s" % (msg.get_message_id()), file=sys.stderr)
                print("  %s" % e, file=sys.stderr)
                continue
                continue
            except:
                print("Fatal error: id:%s" % (msg.get_message_id()), file=sys.stderr)
                raise

            if isspam is None:
                flag = '?'
                tags = unk_tags
                nunk += 1
            elif isspam:
                flag = 'SPAM'
                tags = spam_tags
                nspam += 1
            else:
                flag = 'HAM'
                tags = ham_tags
                nham += 1

            logmsg = '%d/%d %s' % (nmsg, nmsgs, flag)
            if cmsg:
                logmsg += ' (%s)' % cmsg
            if not dry:
                logmsg += ' %s' % (tags)
                if tags:
                    msg.freeze
                    for tag in tags:
                        _tag_msg(msg, tag)
                    msg.thaw
            logmsg += ' id:%s     ' % (msg.get_message_id())

            _logproc(logmsg)

        return nmsgs, nham, nspam, nunk

def _classify(*args, **kwargs):
    t = time.time()
    nmsgs, nham, nspam, nunk = classify(*args, **kwargs)
    t = time.time() - t
    pham = pspam = punk = 0.0
    if nmsgs:
        pham = nham*100/nmsgs
        pspam = nspam*100/nmsgs
        punk = nunk*100/nmsgs
    print('classified %d messages is %.2fs (%.2f msgs/s): %d ham (%.2f%%), %d spam (%.2f%%), %d unknown (%.2f%%)' % (
        nmsgs,
        t,
        nmsgs/t,
        nham, pham,
        nspam, pspam,
        nunk, punk),
          file=sys.stderr)

############################################################

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        cmd = 'help'

    ########################################

    cname = os.getenv('NOTSPAM_CLASSIFIER', DEFAULT_CLASSIFIER).lower()

    ########################################

    if cmd in ['train']:
        if len(sys.argv) < 4:
            print("Must specify meat and search terms.", file=sys.stderr)
            sys.exit(1)

        argc = 2
        while True:
            if argc >= len(sys.argv):
                break
            elif '--dry' in sys.argv[argc]:
                mname = 'null'
            else:
                break
            argc += 1

        meat = sys.argv[argc]
        if meat not in ['ham', 'spam']:
            print("Meat must be either 'ham' or 'spam'.", file=sys.stderr)
            sys.exit(2)

        query_string = ' '.join(sys.argv[argc+1:])

        module = _import_classifier(cname)
        try:
            msgs = _train(module, meat, query_string)
        except KeyboardInterrupt:
            sys.exit(-1)

    ########################################
    elif cmd in ['classify']:
        spam_tags = []
        ham_tags = []
        dry = False
        argc = 2
        while True:
            if argc >= len(sys.argv):
                break
            elif '--spam=' in sys.argv[argc]:
                spam_tags = sys.argv[argc].split('=',1)[1].split(',')
            elif '--ham=' in sys.argv[argc]:
                ham_tags = sys.argv[argc].split('=',1)[1].split(',')
            elif '--unk=' in sys.argv[argc]:
                unk_tags = sys.argv[argc].split('=',1)[1].split(',')
            elif '--dry' in sys.argv[argc]:
                dry = True
            else:
                break
            argc += 1

        query_string = ' '.join(sys.argv[argc:])
        module = _import_classifier(cname)
        _classify(module, query_string,
                  spam_tags=spam_tags,
                  ham_tags=ham_tags,
                  unk_tags=unk_tags,
                  dry=dry
              )

    ########################################
    elif cmd in ['check']:
        query_string = ' '.join(sys.argv[2:])
        module = _import_classifier(cname)
        _classify(module, query_string, dry=True)

    ########################################
    elif cmd in ['help','h','-h','--help']:
        _usage()
        sys.exit(0)

    ########################################
    else:
        print("Unknown command '%s'." % cmd, sys.stderr)
        _usage()
        sys.exit(1)
