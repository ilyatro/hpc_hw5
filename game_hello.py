from mpi4py import MPI
import random

comm = MPI.COMM_WORLD
n_receivers = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    print(f'I am {rank}.')
    data = []
    name = 'name_' + str(rank)
    data.append((name, rank))
    dest = random.randint(1, n_receivers - 1)
    comm.send(data, dest, tag=0)
    print(f'Send from {rank} to {dest} data: {data} ')
elif rank > 0:
    data = comm.recv(source=MPI.ANY_SOURCE, tag=0)
    print(f'I am {rank}.')
    print(f'Received data {data}')
    name = 'name_' + str(rank)
    data.append((name, rank))
    next_receivers = list(range(n_receivers))
    for _, receiver in data:
        next_receivers.remove(receiver)
    if next_receivers:
        dest = random.choice(next_receivers)
        comm.send(data, dest, tag=0)
        print(f'Send from {rank} to {dest} data: {data} ')

