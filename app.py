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


def get_all_values(symbol, driver, index, cp):
    delta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[" + str(cp) + "]")
    strike = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[4]")
    iv = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[5]")
    theta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[9]")
    premium = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(index) + "]/div/div[" + (str(cp+1) if (cp == 2) else str(cp-1)) + "]")
    today = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open('sensibull_data.csv', mode='a') as sensibull_data:
        sensibull_writer = csv.writer(sensibull_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensibull_writer.writerow([symbol, "CE" if cp == 2 else "PE", strike.text, premium.text.split("\n")[0], delta.text, iv.text, theta.text, today, current_time])
    return

def start_driver(symbol, threshold):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get("https://web.sensibull.com/option-chain?expiry=2020-07-16&tradingsymbol=" + symbol)

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
    find_threshold(symbol, threshold, driver, 2)
    find_threshold(symbol, -threshold, driver, 7)
    driver.close()

def find_threshold(symbol, threshold, driver, cp):
    delta_list = []
    threshold_found = False
    for i in range(1, 100):
        try:
            delta = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div/div/div[3]/div[1]/div/div[1]/div[3]/div[" + str(i) + "]/div/div[" + str(cp) + "]")
            delta_value = float(delta.text)
            delta_list.append(delta_value)
            if (delta_value == threshold):
                threshold_found = True
                index = i
                get_all_values(symbol, driver, index, cp)
        except ValueError:
            print("Not a float -> No Delta Value:", delta.text) 
        except NoSuchElementException as e:
            print("Reached the end of the List")
            break
    
    if not threshold_found:
        if cp == 2:
            largest = float('-inf')
            index = -1
            for idx, val in enumerate(delta_list):
                if val < threshold and val > largest:
                    largest = val
                    index = idx
            get_all_values(symbol, driver, index + 1, cp)
        else:
            smallest = float('inf')
            index = -1
            for idx, val in enumerate(delta_list):
                if val > threshold and val < smallest:
                    smallest = val
                    index = idx
            get_all_values(symbol, driver, index + 1, cp)

def main(threshold):
    start_driver("NIFTY", threshold)
    start_driver("BANKNIFTY", threshold)

threshold = float(input("Enter cutt-off delta: "))
# main(threshold)
schedule.every().day.at("09:20").do(main, threshold)
schedule.every().day.at("15:20").do(main, threshold)

while True:
    schedule.run_pending()
    time.sleep(1)