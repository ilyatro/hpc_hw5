import random

from mpi4py import MPI
import math

rule_no = 110
rule = dict()
for i in range(8):
    rule[i] = rule_no & 1
    rule_no = rule_no >> 1


comm = MPI.COMM_WORLD
n_receivers = comm.Get_size()
rank = comm.Get_rank()
cycle = False

length = 35
epoch = 40

batch_size = math.ceil(length / n_receivers)
left = batch_size * rank


batch = [0] * (min(batch_size, length - rank * batch_size) + 2)
if rank == 0:
    batch[1] = 1

for i in range(1, len(batch) - 1):
    batch[i] = random.randint(0, 1)


# print(len(batch))


for i in range(epoch):

    # print(f'rank = {rank} epoch = {i}')
    prev_ = rank - 1
    next_ = rank + 1

    prev_ %= n_receivers
    next_ %= n_receivers

    if n_receivers == 1:
        if cycle:
            batch[0], batch[-1] = batch[-2], batch[1]
    else:
        if prev_ != n_receivers - 1 or cycle:
            comm.send(batch[1], prev_, tag=0)
        if next_ != 0 or cycle:
            comm.send(batch[-2], next_, tag=0)
        # if i > 0:
        if prev_ != n_receivers - 1 or cycle:
            batch[0] = comm.recv(source=prev_, tag=0)
        if next_ != 0 or cycle:
            batch[-1] = comm.recv(source=next_, tag=0)


    data = []
    if rank == 0:
        data.append((0, batch[-2:0:-1], i))
        for i in range(n_receivers - 1):
            r_d = comm.recv(source=MPI.ANY_SOURCE, tag=1)
            data.append(r_d)

        data.sort(reverse=True)
        # print(data)
        for _, d, _ in data:
            print(*d, sep='', end='')
        print()
        for i in range(n_receivers - 1):
            comm.send('rank', i + 1, tag=1)
    else:
        comm.send((rank, batch[-2:0:-1], i), 0, tag=1)
        comm.recv(source=0, tag=1)

    old = batch[0]
    for j in range(1, len(batch) - 1):
        old, batch[j] = batch[j], rule[old + 2 * batch[j] + 4 * batch[j + 1]]