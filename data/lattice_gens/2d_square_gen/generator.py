import numpy as np
import sys
import configparser

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

    np.savetxt(f'2d_square_N{lattice.shape[0]}.mfsys', lattice, header=head, comments='', fmt='%d %05.5f %05.5f %05.5f %05.5f %05.5f %05.5f %d')
    return lattice

def make_ini(n: int, temperatures=np.logspace(-1, 1, 20), name='2d_square.ini', steps=10000, r=5.1):
    config = configparser.ConfigParser()
    syssize_x = 2*n
    syssize_y = 2*n

    config['main'] = {
        'file': f'2d_square_N{n*n*2}.mfsys',
        'heatup': f'{steps}',
        'calculate': f'{steps}',
        'range': f'{r}',
        'seed': '123',
        'temperature': ', '.join(map(str, temperatures)),
        'field': '0|0',
        'boundaries': 'periodic',
        'size': f'{syssize_x}|{syssize_y}',
        'restart': '1',
        'restartThreshold': '1e-6',
        'saveGS': '2d_square_gs.mfsys'
    }
    with open(name, 'w') as f:
        config.write(f)
    print("\n ############# ini file created successfully #############\n")


if __name__ == '__main__':
    n = int(sys.argv[1])
    system = make_lattice(n)
    make_ini(n, temperatures=np.logspace(-2, 2, 50), name=f'2d_square_N{len(system)}.ini')
    print(f'sbatch -p amd -N 1 -o "2d_square/2d_square_N{len(system)}.out" --exclusive -J "n0" start.sh 2d_square/2d_square_N{len(system)}.ini -f 2d_square/2d_square_N{len(system)}.mfsys --save 10')