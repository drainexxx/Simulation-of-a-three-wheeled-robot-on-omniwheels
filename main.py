# Ручное управление роботом с моделькой и динамикой
import random

import pygame
import sys
import numpy as np
import math
import colors
from timeit import default_timer as timer
import statistics
import matplotlib.pyplot as plt
import precision_settings

# Инициализация Pygame
pygame.init()

# Установка размеров экрана
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Движение точки")

background_image = pygame.image.load("pole2.png")

# Часть кода которая отвечает за робота
player_image = pygame.image.load("rob.png")
player_center = player_image.get_rect().center

start_pos = (185, 640)

# Список для хранения координат предыдущего положения точки
trail = []
# Создание объекта шрифта
font = pygame.font.Font(None, 24)

# Начальное положение точки
x, y = start_pos[0], start_pos[1]
x_prev, y_prev = start_pos[0], start_pos[1]
x_imag, y_imag = start_pos[0], start_pos[1]
x_imag_prev, y_imag_prev = start_pos[0], start_pos[1]

# Объявляем переменные
#.............................................................................
variant = 9
w_1 = 0
w_2 = 0
w_3 = 0
w_imax = 10 * variant * 2 * math.pi

#настройка скорости
speed_koef = 1
current_gear = 'neutral'

wc = 0
L = 0.1 * variant
R = 0.03 * variant

vx = 0
vy = 0

angle = 0

transmission = 0

multic = R/3
M_R = np.array([[0, np.sqrt(3)/2, -np.sqrt(3)/2],
                    [-1, 1/2, 1/2],
                    [-1/L, -1/L, -1/L]])

M_R = np.dot(multic, M_R)

#Список для хранения контрольных точек
control_points_coords = []

#массив времени прохождение контрольных точек
auto_start_time = 0
control_points_coords_achieve_time_raw = []
control_points_coords_achieve_time_real = []

#массив для отслеживания точности
closest_distances_to_control_points = []
distances_to_control_point = []
#для автоматического режима
is_auto = 0
time_to_display = 0
current_destination_control_point = 0
after_auto_break_state = 0

#настройки движения
is_dynamic = True
is_bad_wheels = True
use_imag_laser = True
#...............................................................

# Решение прямой задачи кинематики
def forward_task(w_1, w_2, w_3):
    global R, L
    M_W = np.array([[w_1], [w_2], [w_3]])

    result = np.dot(M_R, M_W)

    vx = result[0][0]
    vy = result[1][0]
    wc = result[2][0]

    #print(vx, vy, wc)
    return [vx, vy, wc]

# Решение обратной задачи кинематики
def reverse_task(vx, vy, wc):
    global L, R
    
    W_R = np.linalg.inv(M_R)

    V_R = np.array([[vx], [vy], [wc]])

    result = np.dot(W_R, V_R)

    w1 = result[0][0]
    w2 = result[1][0]
    w3 = result[2][0]

    return [w1, w2, w3]

# Пересчет, чтобы не выходило за диапазон
def recalc_velocity(w1, w2, w3):
    global w_imax

    w_list = [w1, w2, w3]
    w_res_list = []
    for i in w_list:
        if (i < w_imax * (-1)):
            w_res_list.append(w_imax * (-1))
        elif (i > w_imax):
            w_res_list.append(w_imax)
        else:
            w_res_list.append(i)
    return w_res_list

# Неравномерное вращение колес
def change_velocity_randomly(w_1_ideal, w_2_ideal, w_3_ideal):
    random.seed(a=None)
    w_1_bad = random.uniform(precision_settings.wheel_under, precision_settings.wheel_over) * w_1_ideal
    w_2_bad = random.uniform(precision_settings.wheel_under, precision_settings.wheel_over) * w_2_ideal
    w_3_bad = random.uniform(precision_settings.wheel_under, precision_settings.wheel_over) * w_3_ideal

    return [w_1_bad, w_2_bad, w_3_bad]

def draw_control_points_path():
    global control_points_coords, current_destination_control_point
    #отрисовка пути движения робота по контрольным точкам
    for i in range(1, len(control_points_coords)):
        pygame.draw.line(screen, colors.RED, control_points_coords[i - 1], control_points_coords[i], 2)
        pygame.draw.circle(screen,
                            colors.PALEGOLDENROD if i >= current_destination_control_point else colors.GREEN,
                            control_points_coords[i], 5)
    #перекрасить старт и финиш
    if (len(control_points_coords)):
        pygame.draw.circle(screen, colors.BLUEVIOLET,
                            control_points_coords[0], 5)
        pygame.draw.circle(screen, colors.MEDIUMTURQUOISE,
                           control_points_coords[len(control_points_coords)-1], 5)

def normalize_vector(vect):
    x,y = vect[0],vect[1]
    length = math.sqrt(x*x+y*y)
    inv_length = 1/length
    x *= inv_length
    y *= inv_length
    
    return (x,y)

# Основной цикл программы
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN: #На нажатие лкм будет ставить контрольная точка
            control_points_coords.append(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: 
                is_dynamic = not is_dynamic
            if event.key == pygame.K_2:
                is_bad_wheels = not is_bad_wheels
            if event.key == pygame.K_3:
                use_imag_laser = not use_imag_laser
            if event.key == pygame.K_o: #графики движения
                fig, axs = plt.subplots(2)
                axs[0].plot(closest_distances_to_control_points)
                axs[0].set_title("Ошибка при прохождении точек")
                axs[1].plot(control_points_coords_achieve_time_real)
                axs[1].set_title("Время прохождения точек")
                plt.show()



    # Получение состояния клавиш
    keys = pygame.key.get_pressed()


    if keys[pygame.K_t]:
        is_auto = 0
        after_auto_break_state = 0
    if keys[pygame.K_y]:
        is_auto = 1
        auto_start_time = timer()
        control_points_coords_achieve_time_raw = [auto_start_time]
        current_destination_control_point = 0
        after_auto_break_state = 0
        distances_to_control_point = []
        closest_distances_to_control_points = []
    if keys[pygame.K_r]: #reset button
        x, y = start_pos[0], start_pos[1]
        vx, vy, wc, angle = 0, 0, 0, 0
        distances_to_control_point = []
        closest_distances_to_control_points = []
        control_points_coords = []
        trail = []
        after_auto_break_state = 0
        x_imag, y_imag = x, y
        x_imag_prev, y_imag_prev = x, y
        current_gear = 'neutral'

    #езда по контрольным точкам в авто режиме
    if (is_auto):
        if (use_imag_laser):
            diff_x = control_points_coords[current_destination_control_point][0]-x_imag
            diff_y = control_points_coords[current_destination_control_point][1]-y_imag
        else:
            diff_x = control_points_coords[current_destination_control_point][0]-x
            diff_y = control_points_coords[current_destination_control_point][1]-y
        destination_vector = (diff_x, diff_y)
        destination_vector_normalized = normalize_vector(destination_vector)
        
        vx_desired = destination_vector_normalized[0] * speed_koef
        vy_desired = destination_vector_normalized[1] * speed_koef

        if (vx_desired < vx):
            vx -= transmission
        if (vx_desired > vx):
            vx += transmission

        if (vy_desired < vy):
            vy -= transmission
        if (vy_desired > vy):
            vy += transmission
        
        time_to_display = timer() - control_points_coords_achieve_time_raw[len(control_points_coords_achieve_time_raw)-1]

        distances_to_control_point.append(math.sqrt(diff_x * diff_x + diff_y * diff_y))

        if (math.sqrt(diff_x * diff_x + diff_y * diff_y) < precision_settings.desired_movement_precision):
            closest_distances_to_control_points.append(min(distances_to_control_point))
            distances_to_control_point = []
            control_points_coords_achieve_time_raw.append(timer())
            current_destination_control_point+=1
            if (current_destination_control_point >= len(control_points_coords)):
                is_auto = 0
                after_auto_break_state = 1
                
                
                

                


    # Изменение передаточного числа
    if keys[pygame.K_z]:
        transmission = 0.02
        current_gear = 1
        speed_koef = 1
    if keys[pygame.K_x]:
        transmission = 0.05
        current_gear = 2
        speed_koef = 2
    if keys[pygame.K_c]:
        transmission = 0.2
        current_gear = 3
        speed_koef = 3
    if keys[pygame.K_a]:
        current_gear = 'neutral'
        transmission = 0


    # Изменение скорости по осям x и y при нажатии соответствующих клавиш
    if keys[pygame.K_LEFT]:
        vx -= transmission
    if keys[pygame.K_RIGHT]:
        vx += transmission
    if keys[pygame.K_UP]:
        vy -= transmission
    if keys[pygame.K_DOWN]:
        vy += transmission
    if keys[pygame.K_q]:
        wc -= transmission
    if keys[pygame.K_w]:
        wc += transmission
    if keys[pygame.K_SPACE]:
        vx -= vx/10
        vy -= vy/10
        wc -= wc/10

    # Затухание скорости по осям x и y при свободном движении
    if (is_auto==0 and is_dynamic):
        if keys[pygame.K_LEFT]==False:
            if vx > 0:
                vx -= 0.01
        if keys[pygame.K_RIGHT]==False:
            if vx < 0:
                vx += 0.01
        if keys[pygame.K_UP]==False:
            if vy > 0:
                vy -= 0.01
        if keys[pygame.K_DOWN]==False:
            if vy < 0:
                vy += 0.01
        if keys[pygame.K_q]==False:
            if wc > 0:
                wc -= 0.01
        if keys[pygame.K_w]==False:
            if wc < 0:
                wc += 0.01

    

    w_actual = reverse_task(vx, vy, wc)

    if (after_auto_break_state):
        for i in range(len(w_actual)):
            if w_actual[i] > 0.02:
                w_actual[i] /= 10
            else:
                w_actual[i] = 0
        
        if (not is_dynamic):
            vx, vy = 0, 0

        if (sum(w_actual) < 0.004 or (vx < 0.06 and vy < 0.06)):
            vx, vy, wc = 0, 0, 0
            w_actual = [0, 0, 0]
            after_auto_break_state = 0
            for i in range(1, len(control_points_coords_achieve_time_raw)-1):
                    control_points_coords_achieve_time_real.append(control_points_coords_achieve_time_raw[i]-control_points_coords_achieve_time_raw[i-1])

            res_time = timer()-auto_start_time
            print("Общее время движения: ", res_time)
            print("Время движения до каждой контрольной точки")    
            print(control_points_coords_achieve_time_real)
            print("Расстояния до контрольных точек при их прохождении")
            print(closest_distances_to_control_points)

            print("Минимальное расстояние до точки: ", min(closest_distances_to_control_points))
            print("Максимальное расстояние до точки: ", max(closest_distances_to_control_points))
            print("Среднее расстояние до точки", statistics.mean(closest_distances_to_control_points))


            diff_x = control_points_coords[len(control_points_coords)-1][0]-x
            diff_y = control_points_coords[len(control_points_coords)-1][1]-y
            distance_to_end = math.sqrt(diff_x * diff_x + diff_y * diff_y)
            print("Точность позиционирования на финише: ", distance_to_end)

    w_actual = recalc_velocity(w_actual[0], w_actual[1], w_actual[2])

    if (is_bad_wheels):
        w_actual = change_velocity_randomly(w_actual[0], w_actual[1], w_actual[2])

    

    # Реальные значения скоростей
    speed_real = forward_task(w_actual[0], w_actual[1], w_actual[2])
    # Сохранение текущих координат точки в следе
    trail.append((x, y))

    # Обновление координат точки
    x_prev = x
    x += speed_real[0]
    y_prev = y
    y += speed_real[1]
    
    #Обновление координат на лазере
    x_change = x - x_prev
    y_change = y - y_prev
    x_imag_prev = x_imag
    y_imag_prev = y_imag
    if abs(x_change) > 0:
        x_imag += x_change + random.uniform(-precision_settings.laser_accuracy, precision_settings.laser_accuracy)
    if abs(y_change) > 0:
        y_imag += y_change + random.uniform(-precision_settings.laser_accuracy, precision_settings.laser_accuracy)

    angle += speed_real[2]

    # result = np.dot(W_R, V_R)

    player_center = (x, y)

    # Поворот изображения объекта
    rotated_player = pygame.transform.rotate(player_image, angle)
    rotated_rect = rotated_player.get_rect(center=player_center)

    # Очистка экрана
    screen.blit(background_image, (0, 0))

    # Отрисовка точки
    pygame.draw.circle(screen, colors.BLUE, start_pos, 5)

    # Отображение вращающегося объекта
    screen.blit(rotated_player, rotated_rect)

    #отрисовка трейла для движения робота
    for i in range(1, len(trail)):
        pygame.draw.line(screen, colors.BLUE, trail[i - 1], trail[i], 2)
    
    #отрисовка трейла контрольных точек
    draw_control_points_path()

    # Вывод текстовой информации

    line1_text = font.render(f" break_state: {after_auto_break_state}, x: {x:.4f}, y: {y:.4f}, x_imag: {x_imag:.4f}, y_imag: {y_imag:.4f}", True, colors.BLUE)
    line2_text = font.render(f"vx: {speed_real[0]:.4f}, vy: {speed_real[1]:.4f}, wc: {speed_real[2]:.4f}, W_1: {w_actual[0]:.4f}, W_2: {w_actual[1]:.4f}, W_3: {w_actual[2]:.4f}, current_gear {current_gear}", True, colors.BLUE)
    settings_text = font.render(f"is_dynamic: {is_dynamic}, is_bad_wheels: {is_bad_wheels}, use_imag_laser: {use_imag_laser}", True, colors.BLUE)
    screen.blit(line1_text, (10, 50))
    screen.blit(line2_text, (10, 100))
    screen.blit(settings_text, (10, 150))
    if (len(control_points_coords) and current_destination_control_point < len(control_points_coords)):
        point_info_text = font.render(f"Current: point x: {control_points_coords[current_destination_control_point][0]:.1f}, point y: {control_points_coords[current_destination_control_point][1]:.1f}, time between point: {time_to_display:.2f}, movement time {timer()-auto_start_time if is_auto else 0:.2f}", True, colors.BLUE)
        screen.blit(point_info_text, (10, 200))
    # Перерисовка экрана
    pygame.display.flip()

    # Задержка для плавного движения
    pygame.time.delay(20)


    

    pygame.display.update()

