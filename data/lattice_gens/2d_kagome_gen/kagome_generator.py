import numpy as np
import matplotlib.pyplot as plt

# Создаем систему и пишем в файл
# выводим в терминал размеры системы для ini
# и код для запуска в sbatch (ДАННЫЕ В ПАПКЕ kagome/)

def make_system(n: int, m: int, dilute: float = 0, mute=False) -> np.ndarray:
    """
    Generates a 3D spin ice lattice system.

    Parameters
    ----------
    n : int
        number of cells in the x direction
    m : int
        number of cells in the y direction
    k : int
        number of layers in the z direction
    offset : float
        layer offset
    dilute : float
        dilution parameter
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

if __name__ == "__main__":
    system = make_system(5, 5)
    save_to_mfsys(f"kagome_N{len(system)}.mfsys", system)

    print(f'sbatch -p amd -N 1 -o "kagome/kagome_N{len(system)}.out" --exclusive -J "n0" start.sh kagome/kagome_N{len(system)}.ini -f kagome/kagome_N{len(system)}.mfsys')