from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat):
        cmd = ['sa-learn',
               '--local',
               '--progress',
               '--no-sync',
               '--' + meat,
               '-f', '-',
               ]
        self.__proc = subprocess.Popen(cmd,
                                       stdin=subprocess.PIPE
                                   )

    def add(self, msg):
        # write the message file paths to process stdin
        path = msg.get_filename()
        self.__proc.stdin.write(bytes(path + '\n', 'UTF-8'))

    def sync(self):
        # run the learner
        self.__proc.communicate()
        ret = self.__proc.wait()

        # sync the result
        cmd = ['sa-learn',
               '--sync',
               ]
        subprocess.check_call(cmd)

    ########################################################

class Classifier(NotspamClassifier):

    def classify1(self, msg):
        cmd = ["spamc",
               "--socket=/home/jrollins/.spamassassin/spamd",
               "--log-to-stderr",
               "--max-size=5000000",
               "--check",
               ]
        with open(msg.get_filename(), 'r') as f:
            proc = subprocess.Popen(cmd,
                                    stdin=f,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            (stdout, stderr) = proc.communicate()
            ret = proc.wait()
        score = stdout.decode().strip()
        # process the return code.
        # 1 == spam
        # 0 == ham or error
        #score, threshold = output.split('/')
        if ret == 1:
            isspam = True
        else:
            if score == '0/0':
                isspam = None
            else:
                isspam = False
        return isspam, score #'%s/%s' % (float(score), float(threshold))

    def classify2(self, msg):
        cmd = ['spamassassin',
               '-L',
               msg.get_filename(),
               ]
        ret = subprocess.call(cmd, stdout=subprocess.DEVNULL)
        if ret != 0:
            isspam = True
        else:
            isspam = False
        return isspam, None

    classify = classify1
