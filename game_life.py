import time
import copy

from mpi4py import MPI
import math

comm = MPI.COMM_WORLD
n_receivers = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    start = time.time()

width = 10
height = 10

epoch = 20

batch_size = math.ceil(height / n_receivers)
left = batch_size * rank


batch = [[0 for _ in range(width + 2)] for i in range(min(batch_size, width - rank * batch_size) + 2)]

if rank == 0:
    batch[1][2] = 1
    batch[2][3] = 1
    batch[3][1] = 1
    batch[3][2] = 1
    batch[3][3] = 1

for i in range(epoch):
    prev_ = rank - 1
    next_ = rank + 1

    prev_ %= n_receivers
    next_ %= n_receivers

    if n_receivers > 1:
        if prev_ != n_receivers - 1:
            comm.send(batch[1].copy(), prev_, tag=0)
        if next_ != 0:
            comm.send(batch[-2].copy(), next_, tag=0)
        if prev_ != n_receivers - 1:
            batch[0] = comm.recv(source=prev_, tag=0)
        if next_ != 0:
            batch[-1] = comm.recv(source=next_, tag=0)


    data = []
    if rank == 0:
        data.append((0, batch[-2:0:-1].copy(), i))
        for i in range(n_receivers - 1):
            r_d = comm.recv(source=MPI.ANY_SOURCE, tag=1)
            data.append(r_d)

        data.sort(reverse=True)
        # print(data)
        for _, d, _ in data:
            for line in d:
                print(*line, sep='')
        print()
        for i in range(n_receivers - 1):
            comm.send('rank', i + 1, tag=1)
    else:
        comm.send((rank, batch[-2:0:-1].copy(), i), 0, tag=1)
        comm.recv(source=0, tag=1)

    old = copy.deepcopy(batch)
    for row in range(1, len(batch) - 1):
        for col in range(1, width + 1):
            nb = old[row - 1][col - 1] + old[row - 1][col] + old[row - 1][col + 1] + \
                 old[row][col - 1] + old[row][col + 1] + \
                 old[row + 1][col - 1] + old[row + 1][col] + old[row + 1][col + 1]
            if row == 4 and col == 2:
                q=0
            if old[row][col] == 0 and nb == 3:
                batch[row][col] = 1
            if old[row][col] == 1 and (nb < 2 or nb > 3):
                batch[row][col] = 0

if rank == 0:
    print('time = ', time.time() - start)