import numpy as np
import matplotlib.pyplot as plt
import configparser

# Создаем систему и пишем в файл
# выводим в терминал размеры системы для ini
# и код для запуска в sbatch (ДАННЫЕ В ПАПКЕ kagome/)

def make_system(n: int, m: int, dilute: float = 0, mute=False) -> np.ndarray:
    """
    Generates a 2D Kagome lattice system.

    Parameters
    ----------
    n : int
        number of cells in the x direction
    m : int
        number of cells in the y direction
    dilute : float
        dilution parameter
    mute : bool
        whether to mute the output

    Returns
    -------
    system : 2D numpy array
        array with the positions and directions of the spins
    """

    # 30 degree angle in radians
    cos30 = np.cos(np.pi / 6)
    sin30 = np.sin(np.pi / 6)

    # Positions of the atoms in the unit cell
    x = np.array([1, 0.5, 1.5])
    y = np.array([4*np.sqrt(3)/6, np.sqrt(3)/6, np.sqrt(3)/6])
    z = np.array([0, 0, 0])

    # Directions of the spin in the unit cell
    mx = np.array([0, -cos30, cos30])
    my = np.array([1, -sin30, -sin30])
    mz = np.array([0, 0, 0])

    # Create the unit cell
    cell = np.array([x, y, z, mx, my, mz]).T

    if not mute:
        syssize_x = 2*n
        syssize_y = 2*m*np.sqrt(3)/2
        syssize_z = 0
        print(f"size = {syssize_x}|{syssize_y}|{syssize_z}")

    # Create the first line of cells
    line = np.empty((0, 6))
    for i in range(n):
        line = np.vstack((line, cell + [2*i, 0, 0, 0, 0, 0]))

    # Create the first layer of cells
    surf = np.empty((0, 6))
    for i in range(m):
        if i%2 == 0:
            surf = np.vstack((surf, line + [1, 2*np.sqrt(3)/2*i, 0, 0, 0, 0]))
        else:
            surf = np.vstack((surf, line + [0, 2*np.sqrt(3)/2*i, 0, 0, 0, 0]))
    
    system = surf

    # Dilute the system
    if dilute > 0:
        N = len(system)
        n_dilute = int(N * dilute)
        idx = [i for i in range(N)] 
        np.random.shuffle(idx)
        idx = idx[n_dilute:]
        system = system[list(idx)]

    return system

def save_to_mfsys(filename, system):
    N = len(system)
    head = f'[header]\nversion=2\ndimensions=3\ntype=standart\nsize={N}\nemin=0.000000\nemax=0.000000\nstate={"0"*N}\nminstate=\nmaxstate=\ninteractionrange=0\nsizescale=1\nmagnetizationscale=1\n[parts]'

    np.savetxt(filename, np.vstack((np.arange(N), system.T, np.array(N*[0]))).T, fmt="%i\t%.15f\t%.15f\t%.15f\t%.15f\t%.15f\t%.15f\t%i", comments="", header=head)

def make_ini(n: int, m: int, temperatures=np.logspace(-1, 1, 20), name='kagome_N1280.ini', steps=10000, r=5.1):
    '''
    [main] 
    file = kagome_N1280.mfsys
    heatup = 10000
    calculate = 10000
    range = 5.1
    seed = 123
    temperature = 5e-2, 1e-1, 5e-1, 4.1, 40
    field = 0|0 ; add external field
    boundaries = periodic ; open or periodic boundary conditions
    ; For periodic you have to set size along x and y
    size = 27.661016949152543|27.661016949152543 ; set rectangle of the lattice to translate it over the space
    restart = 1 ; restart the program if found lower energy. Default is 1.
    restartThreshold = 1e-6 ; minimal difference between the initial and lower energy, in relative to initial energy units. Default is 1e-6.
    saveGS = kagome_gs.mfsys ; if defined, the resulting GS will be saved to this file
    '''
    config = configparser.ConfigParser()
    syssize_x = 2*n
    syssize_y = 2*m*np.sqrt(3)/2

    config['main'] = {
        'file': f'kagome_N{n*m*3}.mfsys',
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
        'saveGS': 'kagome_gs.mfsys'
    }
    with open(name, 'w') as f:
        config.write(f)
    print("\n ############# ini file created successfully #############\n")


if __name__ == "__main__":
    system = make_system(20, 20)
    save_to_mfsys(f"kagome_N{len(system)}.mfsys", system)
    make_ini(10, 10, temperatures=np.logspace(-1, 1, 50), name=f"kagome_N{len(system)}.ini")

    print(f'sbatch -p amd -N 1 -o "kagome/kagome_N{len(system)}.out" --exclusive -J "n0" start.sh kagome/kagome_N{len(system)}.ini -f kagome/kagome_N{len(system)}.mfsys --save 10')