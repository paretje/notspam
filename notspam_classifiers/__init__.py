import pkgutil

def classifiers_list():
    clist = []
    for finder, name, ispkg in pkgutil.iter_modules(__path__):
        if ispkg:
            continue
        name = name.split('.')[-1]
        if name[0] == '_':
            continue
        clist.append(name)
    return clist

##################################################

class NotspamTrainingError(Exception): pass
class NotspamClassificationError(Exception): pass

class NotspamTrainer(object):
    """Spam classification trainer

    """
    def __init__(self, meat):
        """Initialized with meat to train on, e.g. 'ham' or 'spam'.

        """
        pass

    def add(self, message):
        """Add message to train as specified meat.

        Passed a notmuch.message object.

        """
        pass

    def sync(self):
        """Called after all messages have been added.

        """
        pass

class NotspamClassifier(object):
    """Spam message classifier

    """
    def classify(self, message):
        """Classify a single message as spam or ham.

        Passed a notmuch.message object.

        Should return a tuple (isspam, score).  'isspam' should be
        either True, False, or None.  'score' should be a string
        representation of the score, in whatever format is relevant to
        the underlying classifier.

        """
        return False, ''

    def __call__(self, message):
        return self.classify(message)
