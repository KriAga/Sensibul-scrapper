
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import sys
import csv
import schedule
from datetime import date
from datetime import datetime


def get_all_values(index, symbol, driver):
    delta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[2]")
    strike = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[4]")
    iv = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[5]")
    theta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[9]")
    premium = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[6]")
    today = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open('sensible_data.csv', mode='a') as sensible_data:
        sensible_writer = csv.writer(sensible_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensible_writer.writerow([symbol, strike.text, premium.text.split("\n")[0], delta.text, iv.text, theta.text, today, current_time])
    driver.close()

def main(threshold):
    delta_list = []
    threshold_found = False
    symbol = "Nifty" 
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get("https://web.sensibull.com/option-chain?expiry=2020-07-16&tradingsymbol=NIFTY")

    popup_close = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "/html/body/div[13]/div[3]/div/div/button")),
                            message="Close Popup"
                        )

    popup_close.click()
    print("Popup closed")

    greek = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[2]/div[2]/label[2]/span[1]/span[1]/span[1]/input')

    if not greek.is_selected():
        greek.click()
    print("Geek mode selected")

    for i in range(1, 100):
        try:
            delta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(i) + "]/div/div[2]")
            delta_value = float(delta.text)
            delta_list.append(delta_value)
            if (delta_value == threshold):
                threshold_found = True
                index = i
                get_all_values(index, symbol, driver)
        except ValueError:
            print("Not a float -> No Delta Value:", delta.text) 
        except NoSuchElementException as e:
            print("Reached the end of the List")
            break
        
    if not threshold_found:
        min_diff = float('-inf')
        index = -1
        for i in range(len(delta_list)):
            diff = delta_list[i] - threshold
            if min_diff < diff and diff < 0:
                min_diff = diff;
                index = i
        delta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index + 1) + "]/div/div[2]")
        get_all_values(index + 1, symbol, driver)


threshold = float(input("Enter cutt-off delta: "))
schedule.every().day.at("18:55").do(main, threshold)
schedule.every().day.at("18:56").do(main, threshold)

while True:
    schedule.run_pending()
    time.sleep(1)