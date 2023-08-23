# Этот скрипт умеет отслеживать определенные текстовые комментарии к футбольной трансляции на сайте williamhill.com
# и воспроизводить соответствующие аудио сообщения: "dangerous attack", "attack", "goal", "half time" и "end game".
# 
# До запуска необходимо:
#   - в папке proxy в файл "backgrounf.js" внести правки (указать свой прокси) 
#   - далее папку proxy архивируем в zip-архив
#   - открываем файл config.py прописываем ссылку на трансляцию и название клуба за которым будем следить
#
# Необходимо использовать библиотеку playsound 1.2.2

from config import LINK, TEAM
from time import sleep
from playsound import playsound
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

# Список в котором будут храниться комментарии
comment_list = []
temp_list = []

# Флаг для остановки цикла
flag = True

# Переменные для сверки времени
last_min = 0
last_sec = 0

# Создаём объект опций
chrome_options = Options()
# Добавляем расшиерение в опции (прокси с авторизацией)
chrome_options.add_extension('wh_event_alert\proxy.zip')

# Создаем объект вэбдрайвер
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

# Откраваем страницу в браузере
driver.get(LINK)

# Находим фрейм содержащий необходимый плеер
iframe = driver.find_element(By.CSS_SELECTOR, 'div #scoreboard_frame > iframe')
# Переключаемся на фрейм
driver.switch_to.frame(iframe)
# Находим кнопку "комментарии" и кликаем по ней
btn_commentary = driver.find_element(By.CSS_SELECTOR, '._commentary').click()

while flag:
    # Забираем время последнего события
    try:
        min = driver.find_element(By.XPATH, '//*[@id="box_commentaries"]/ul/li[1]/span[1]/span[1]').text
        sec = driver.find_element(By.XPATH, '//*[@id="box_commentaries"]/ul/li[1]/span[1]/span[2]').text
    except StaleElementReferenceException:
        pass

    # Сравниваем время последнего события с временем предидущего. Если время совпадает то пропускаем итерацию и проверяем заного.
    if min != last_min or sec != last_sec:
        try:
            # Находим последний комментарий в чате
            last_ul_li = driver.find_element(By.XPATH, '//*[@id="box_commentaries"]/ul/li[1]/span[3]').text
            temp_list.append(last_ul_li)
            last_min = min
            last_sec = sec
        except StaleElementReferenceException:
            pass
    else:
        continue 

    # Проверка события
    if len(comment_list) < len(temp_list): # По идее эту проверку можно убрать т.к. теперь мы проверяем по времени события. Но пока что оставлю.
        
        if f'Dangerous Attack by {TEAM}' in temp_list[-1]:
            print(f'{min+sec} Dangerous Attack by {TEAM}!')
            playsound('wh_event_alert\\audio\\dangerous_attack.mp3')
       
        elif f'Attack by {TEAM}' in temp_list[-1]:
            print(f'{min+sec} Attack by {TEAM}!')
            playsound('wh_event_alert\\audio\\attack.mp3')

        elif f'Goal for {TEAM}' in temp_list[-1]:
            print(f'{min+sec} Goal for {TEAM}')
            playsound('wh_event_alert\\audio\\goal.mp3') 

        elif 'Half Time' in temp_list[-1]:
            print('HALF TIME !') 
            playsound('wh_event_alert\\audio\\half_time.mp3')
            # Задаём ожидание начала нового тайма в секундах (15 мин)
            sleep(900)

        elif 'Full Time' in temp_list[-1]:
            print('END GAME !')
            playsound('wh_event_alert\\audio\\end_game.mp3')
            flag = False

        comment_list.append(last_ul_li)

# Ждем 10 секунд и закрываем браузер
sleep(10)
driver.quit()