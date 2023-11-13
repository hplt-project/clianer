from collections import deque
import gzip
import random


N_HEAD = 5
N_SAMPLE = 5
N_TAIL = 5


class ParallelDataset:

    def __init__(self, src_path, tgt_path):
        self.src_path = src_path
        self.tgt_path = tgt_path


        src_name = src_path.split('/')[-1].split('.')[0]
        tgt_name = tgt_path.split('/')[-1].split('.')[0]
        if src_name == tgt_name:
            self.name = src_name
        else:
            self.name = src_path.split('/')[-1] + '_' + tgt_path.split('/')[-1]

        self.sample = None

    def generate_sample(self, sort_reservoir=True):
        head = []
        reservoir = []
        tail = deque(maxlen=N_TAIL)

        with gzip.open(self.src_path, 'rt') as src_file, \
             gzip.open(self.tgt_path, 'rt') as tgt_file:
            for i, (src_line, tgt_line) in enumerate(zip(src_file, tgt_file)):
                if i < N_HEAD:
                    head.append((src_line, tgt_line))

                elif i < N_HEAD + N_TAIL:
                    tail.append((src_line, tgt_line))

                else:
                    tail.append((src_line, tgt_line))

                    j = i - N_HEAD - N_TAIL
                    if j < N_SAMPLE:
                        reservoir.append((j, src_line, tgt_line))
                    else:
                        k = random.randint(0, j)
                        if k < N_SAMPLE:
                            reservoir[k] = (j, src_line, tgt_line)

        if sort_reservoir:
            reservoir.sort(key=lambda x: x[0])

        sample = []
        for src_line, tgt_line in head:
            sample.append((src_line.rstrip("\r\n"), tgt_line.rstrip("\r\n")))
        for _, src_line, tgt_line in reservoir:
            sample.append((src_line.rstrip("\r\n"), tgt_line.rstrip("\r\n")))
        for src_line, tgt_line in tail:
            sample.append((src_line.rstrip("\r\n"), tgt_line.rstrip("\r\n")))

        return sample

    def __iter__(self):
        if self.sample is None:
            self.sample = self.generate_sample()
        return iter(self.sample)
