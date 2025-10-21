import numpy as np
import sys

def make_lattice(n):
    arr = np.array([[0, 2, 0, 1, 0, 0], [1, 1, 0, 0, 1, 0]])
    lattice = arr.copy()

    for i in range(n):
        for j in range(n):
            if j==0 and i==0:
                continue
            lattice = np.append(lattice, arr+np.array([i*2, j*2, 0, 0, 0, 0]), axis=0)

    head = f'''[header]\nversion=2\ndimensions=3\ntype=standart\nsize={lattice.shape[0]}\nemin=0.000000\nemax=0.000000\nstate={'0'*(lattice.shape[0])}\nminstate=\nmaxstate=\ninteractionrange=0\nsizescale=1\nmagnetizationscale=1\n[parts]'''

    lattice = np.array([[i for i in range(lattice.shape[0])], *lattice.T, [0 for i in range(lattice.shape[0])]]).T

    np.savetxt(f'apamea_N{lattice.shape[0]}.mfsys', lattice, header=head, comments='', fmt='%d %05.5f %05.5f %05.5f %05.5f %05.5f %05.5f %d')


if __name__ == '__main__':
    n = int(sys.argv[1])
    make_lattice(n)