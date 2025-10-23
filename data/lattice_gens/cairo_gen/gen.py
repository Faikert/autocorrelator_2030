import math
import numpy as np
import configparser


def make_ini(n: int, m: int, delta: float, temperatures=np.logspace(-1, 1, 20), name='cairo.ini', steps=10000, r=5.1):
    config = configparser.ConfigParser()
    syssize_x = n*delta
    syssize_y = m*delta

    config['main'] = {
        'file': f'cairo_N{n*n*5}.mfsys',
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
        'saveGS': 'cairo_gs.mfsys'
    }
    with open(name, 'w') as f:
        config.write(f)
    print("\n ############# ini file created successfully #############\n")



def main():
    sin60 = math.sin(math.pi / 3)
    
    a = 472
    b = 344
    l = 300
    c = 0.996*a


    delta = 816
    
    l /= l
    delta /= a
    b /= a
    c /= a
    a /= a


    yd = (2 * a - c) / 2
    xd = yd / 2
    
    # Первая конфигурация точек
    x1 = [0, xd + b/2, xd + b/2, -xd - b/2, -xd - b/2]
    y1 = [0, yd * sin60, -yd * sin60, -yd * sin60, yd * sin60]
    mx1 = [l * 1, l * 0.5, l * 0.5, l * (-0.5), l * (-0.5)]
    my1 = [0, l * sin60, l * (-sin60), l * (-sin60), l * sin60]
    
    # Вторая конфигурация (поворот на 90 градусов)
    x2 = y1
    y2 = x1
    mx2 = my1
    my2 = mx1
    
    # Генерация сетки точек
    n, m = 16, 16
    vx, vy, vmx, vmy = [], [], [], []
    
    for i in range(n):
        for j in range(m):
            if ((i % 2) ^ (j % 2)) == 0:
                points_config = (x1, y1, mx1, my1)
            else:
                points_config = (x1_config, y1_config, mx1_config, my1_config) = (x2, y2, mx2, my2)
            
            x_config, y_config, mx_config, my_config = points_config
            for k in range(len(x_config)):
                vx.append(x_config[k] + i * delta)
                vy.append(y_config[k] + j * delta)
                vmx.append(mx_config[k])
                vmy.append(my_config[k])
    
    # Корректировка направлений магнитизации
    for i in range(len(vx)):
        if vmy[i] < 0:
            vmx[i] *= -1
            vmy[i] *= -1
        elif vmy[i] == 0 and vmx[i] < 0:
            vmx[i] *= -1
    
    # Запись в файл
    with open(f"cairo_N{len(vx)}.mfsys", "w") as f:
        f.write("[header]\n")
        f.write("version=2\n")
        f.write("dimensions=2\n")
        f.write("type=standart\n")
        f.write(f"size={len(vx)}\n")
        f.write("state=" + "0" * len(vx) + "\n")
        f.write("minstate=" + "0" * len(vx) + "\n")
        f.write("minscale=" + "0" * len(vx) + "\n")
        f.write("interactionrange=0\n")
        f.write("sizescale=1\n")
        f.write("magnetizationscale=1\n")
        f.write("[parts]\n")
        
        for i in range(len(vx)):
            f.write(f"{i}\t{vx[i]:.16e}\t{vy[i]:.16e}\t0\t{vmx[i]:.16e}\t{vmy[i]:.16e}\t0\t0")
            if i != len(vx) - 1:
                f.write("\n")
    
    # Конвертация в numpy массивы для дальнейших вычислений
    x = np.array(vx, dtype=np.float32)
    y = np.array(vy, dtype=np.float32)
    mx = np.array(vmx, dtype=np.float32)
    my = np.array(vmy, dtype=np.float32)
    make_ini(n, m, delta, temperatures=np.logspace(-2, 2, 50), name=f'cairo_N{n*n*5}.ini', steps=10000, r=5.1)
    
    # TODO: Complete E and M computing
    # Матрица e будет размером N x N
    # e = np.zeros((len(x), len(x)))
    
    print(m*delta, n*delta)
    
    

    return 0

if __name__ == "__main__":
    main()