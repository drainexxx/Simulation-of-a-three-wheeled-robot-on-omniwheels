# Ручное управление роботом с моделькой и динамикой
import random

import pygame
import sys
import numpy as np

# Инициализация Pygame
pygame.init()

# Установка размеров экрана
WIDTH, HEIGHT = 900, 660
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Движение точки")

background_image = pygame.image.load("sr.png")

# Часть кода которая отвечает за робота
player_image = pygame.image.load("rob.png")
player_center = player_image.get_rect().center


# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Список для хранения координат предыдущего положения точки
trail = []
# Создание объекта шрифта
font = pygame.font.Font(None, 24)

# Начальное положение точки
x, y = WIDTH // 7.6, HEIGHT // 1.3

# Объявляем переменные
#.............................................................................
w_1 = 0
w_2 = 0
w_3 = 0
w_imax = 50

wc = 0
L = 1
R = 0.3

vx = 0
vy = 0

angle = 0

transmission = 0

multic = R/3
M_R = np.array([[0, np.sqrt(3)/2, -np.sqrt(3)/2],
                    [-1, 1/2, 1/2],
                    [-1/L, -1/L, -1/L]])

M_R = np.dot(multic, M_R)

#...............................................................

# Решение прямой задачи кинематики
def forward_task(w_1, w_2, w_3):
    global R, L
    M_W = np.array([[w_1], [w_2], [w_3]])

    result = np.dot(M_R, M_W)

    vx = result[0][0]
    vy = result[1][0]
    wc = result[2][0]

    print(vx, vy, wc)
    return (vx, vy, wc)

# Решение обратной задачи кинематики
def reverse_task(vx, vy, wc):
    global L, R
    
    W_R = np.linalg.inv(M_R)

    V_R = np.array([[vx], [vy], [wc]])

    result = np.dot(W_R, V_R)

    w1 = result[0][0]
    w2 = result[1][0]
    w3 = result[2][0]

    return (w1, w2, w3)

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
    w_1_bad = random.uniform(0.9, 1) * w_1_ideal
    w_2_bad = random.uniform(0.9, 1) * w_2_ideal
    w_3_bad = random.uniform(0.9, 1) * w_3_ideal

    return (w_1_bad, w_2_bad, w_3_bad)

# Основной цикл программы
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Получение состояния клавиш
    keys = pygame.key.get_pressed()


    # M_R - матрица для расчета обратной задачи кинематики
    # W_R = np.array([[0, 1/R, -L/R],
    #                 [np.sqrt(3)/(2*R), -1/(2*R), -L/R],
    #                 [-np.sqrt(3)/(2*R), -1/(2*R), -L/R]])
    #
    # V_R = np.array([[vx], [vy], [wc]])
    #
    # # M_R - матрица для расчета прямой задачи кинематики
    # M_R = np.array([[0, R / np.sqrt(3), R / np.sqrt(3)],
    #                 [(2 * R)/3, -R / 3, -R / 3],
    #                 [-R / (3 * L), -R / (3 * L), -R / (3 * L)]])
    #
    # # M_W - матрица скоростей независимых двигателей
    # M_W = np.array([[w_1], [w_2], [w_3]])

    # Изменение передаточного числа
    if keys[pygame.K_z]:
        transmission = 0.02
    if keys[pygame.K_x]:
        transmission = 0.05
    if keys[pygame.K_c]:
        transmission = 0.2

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
            wc -= 0.03
    if keys[pygame.K_w]==False:
        if wc < 0:
            wc += 0.03

    w_actual = reverse_task(vx, vy, wc)
    w_actual = recalc_velocity(w_actual[0], w_actual[1], w_actual[2])
    w_actual = change_velocity_randomly(w_actual[0], w_actual[1], w_actual[2])

    # Реальные значения скоростей
    speed_real = forward_task(w_actual[0], w_actual[1], w_actual[2])
    # Сохранение текущих координат точки в следе
    trail.append((x, y))

    # Обновление координат точки
    x += speed_real[0]
    y += speed_real[1]

    angle += speed_real[2]

    # result = np.dot(W_R, V_R)

    player_center = (x, y)
    # Поворот изображения объекта
    rotated_player = pygame.transform.rotate(player_image, angle)
    rotated_rect = rotated_player.get_rect(center=player_center)

    # Очистка экрана
    screen.blit(background_image, (0, 0))

    # Отрисовка точки
    pygame.draw.circle(screen, BLUE, (WIDTH // 7.6, HEIGHT // 1.3), 5)

    # Отображение вращающегося объекта
    screen.blit(rotated_player, rotated_rect)

    for i in range(1, len(trail)):
        pygame.draw.line(screen, BLUE, trail[i - 1], trail[i], 2)

    # Отображение значений скоростей по осям

    v_text = font.render(f"vx: {speed_real[0]}, vy: {speed_real[1]}, wc: {speed_real[2]}", True, BLUE)
    w_text = font.render(f"W_1: {w_actual[0]}, W_2: {w_actual[1]}, W_3: {w_actual[2]}, ", True, BLUE)

    screen.blit(v_text, (10, 50))
    screen.blit(w_text, (10, 100))
    # Перерисовка экрана
    pygame.display.flip()

    # Задержка для плавного движения
    pygame.time.delay(20)
