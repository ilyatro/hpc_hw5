# поскольку mpiexec пока не поддерживает юникод, то взял английский перевод
# предварительно убрав все лишние знаки
import time
from collections import defaultdict
from itertools import islice

from mpi4py import MPI

comm = MPI.COMM_WORLD
n_receivers = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    start = time.time()

word_count = defaultdict(int)
with open('war_and_peace_NEW.txt', 'r', encoding='utf-8') as file:
    lines = islice(file, rank, None, n_receivers)
    for line in lines:
        for word in line.strip().lower().split():
            word_count[word] += 1


if rank == 0:
    for i in range(1, n_receivers):

        rd = comm.recv(source=i, tag=0)
        for key, value in rd.items():
            word_count[key] += value

    word_count = list(word_count.items())
    word_count.sort(key=lambda item: item[1], reverse=True)
    for word, count in word_count[:10]:
        print(word)
    print(time.time() - start)
else:
    comm.send(word_count, 0, tag=0)
