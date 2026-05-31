import numpy as np
import cv2

def simple_clean_outliers(data, accuracy):
    """ Исключение выбросов """
    cleaned = data.copy()

    median_val = np.median(data)
    std_val = np.std(data)

    lower = median_val - accuracy * std_val
    upper = median_val + accuracy * std_val
    
    for i in range(len(data)):
        if data[i] < lower or data[i] > upper:
            # Ближайшие нормальные значения
            neighbors = []
            # Поиск слева
            for j in range(i-1, -1, -1):
                if lower <= data[j] <= upper:
                    neighbors.append(data[j])
                    break
            # Поиск справа
            for j in range(i+1, len(data)):
                if lower <= data[j] <= upper:
                    neighbors.append(data[j])
                    break
            # Замена выброса
            if neighbors:
                cleaned[i] = int(np.mean(neighbors))
            else:
                cleaned[i] = int(median_val)

    return cleaned


def get_brightness_matrix(img: np.ndarray):
    """ 
    Возвращение матрицы яркости
    """
    b, g, r = cv2.split(img)
    r_float = r.astype(np.float32) / 255.0
    g_float = g.astype(np.float32) / 255.0
    b_float = b.astype(np.float32) / 255.0
    # Вычисление яркости
    brightness = 0.299 * r_float + 0.587 * g_float + 0.114 * b_float
    
    return brightness


def draw_point(point_x, point_y, color, radius, img):
    """
    Отрисовка точки
    """
    if color == "red": color = (0, 0, 120)
    elif color == "blue": color = (120, 0, 0)
    thickness = -1  # Залитая точка
    cv2.circle(img, (point_x, point_y), radius, color, thickness)

