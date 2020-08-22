import pandas as pd
from time import sleep
from datetime import date, datetime

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    JavascriptException, ElementClickInterceptedException


def update_from_investing_com(data: pd.DataFrame,
                              investing_address: str,
                              end_date: date = date.today()):
    """
    Takes a dataframe with parsed format (after reformat_investing_data()) and updates its data.
    Assumes the last row is the latest data for the dataframe.

    Args:
        data: Pandas dataframe. The data to be updated.
        investing_address: String of url. The url of the product on investing.com.
        end_date: Date. Default today. The last day of data to update for the dataframe.

    Returns:
        An updated pandas dataframe.

    TODO: Complete the function.
    """

    r = Request(investing_address,
                headers={"User-Agent": "Mozilla/5.0"})
    c = urlopen(r).read()
    soup = bs(c, 'html.parser')

    td = soup.findAll("td", attrs={"data-real-value": True})
    values = []
    for children in td:
        values.append(children.get_text())

    values = [values[x:x + 6] for x in range(0, len(values), 6)]
    pd.DataFrame(values).set_index(0)

    last_date = data.iloc[-1]


def download_from_investing_com(
        account_email: str,
        account_password: str,
        investing_address: str,
        start_date: date = date(2000, 1, 1),
        end_date: date = date.today(),
        return_download_name: bool = False,
        download_directory: str = 'default',
        **kwargs):

    """
    Getting price and volume data from investing.com. This should only be used when alternative, easier solutions are
    not available, e.g. for Hong Kong Hang Seng Futures in yahoo or google apis.

    Args:
        investing_address: String of url. The url of the product on investing.com.
        start_date: Date of datetime. The starting date of data query, default to be 2000/01/01.
        end_date: Date of datetime. The ending date of data query, default to today and will be automatically converted to the last trading date.
        return_download_name: Boolean. If the function returns the name of the downloaded file. Default to be false to save processing time.
        account_email: String. The investing.com account's email address.
        account_password: String. The investing.com account's password.
        download_directory: String of the directory to insert the downloaded file, or 'default' to download to the default directory. Should be a raw string to accommodate backslash.

    Returns:
        An empty string if return_download_name is set to false. Returns the downloaded file name if true.

    Examples:
        download_from_investing_com(investing_address='https://www.investing.com/indices/hong-kong-40-futures-historical-data',
                                    account_email='example@gmail.com', account_password='passw0rd',
                                    download_directory=r'C:\Users\my_user\Desktop\New_Folder\\')

    TODO: Convert the investing_address variable into stock tickers or stock numbers.
          Check the validity of parameters.
    """

    download_name = ''
    start_date = date.strftime(start_date, '%d/%m/%Y')

    is_end_date_changed = False
    if end_date != date.today():
        end_date = date.strftime(end_date, '%d/%m/%Y')
        is_end_date_changed = True

    options = ChromeOptions()

    if download_directory == 'default':
        options.add_experimental_option('prefs', {
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
        })
    else:
        options.add_experimental_option('prefs', {
            'download.default_directory': download_directory,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
        })

    # Initialize the chromium session and direct to the html provided
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
    driver.get(investing_address)

    # Wait for the possible popup
    sleep(5)

    # Investing.com would sometimes pop up advertisements. Turns the popup off if it appears.
    try:
        close_popup_btn = driver.find_element_by_css_selector('.largeBannerCloser')
        close_popup_btn.click()
        print('Closing pop up...')
        sleep(1)
    except (NoSuchElementException, ElementNotInteractableException):
        pass

    # Log in processes
    sign_in_popup_btn = driver.find_element_by_css_selector('.topBarUserAvatar .login')
    sign_in_popup_btn.click()
    print('Clicking on sign in button...')
    print('Logging in...')
    sleep(1)

    email_box = driver.find_element_by_id('loginFormUser_email')
    email_box.send_keys(account_email)
    sleep(1)

    password_box = driver.find_element_by_id('loginForm_password')
    password_box.send_keys(account_password)
    sleep(1)

    sign_in_btn = driver.find_element_by_css_selector('.newButton.orange')
    driver.execute_script("loginFunctions.submitLogin()", sign_in_btn)

    sleep(3)

    # Select the date range to download
    while True:
        try:
            date_picker = driver.find_element_by_id('widgetField')
            date_picker.click()
            print('Setting date ranges...')
            break
        except (NoSuchElementException, ElementClickInterceptedException):
            sleep(1)
            continue

    sleep(1)

    start_date_box = driver.find_element_by_id('startDate')
    start_date_box.send_keys(Keys.BACK_SPACE)
    start_date_box.send_keys(Keys.CONTROL + 'a')
    start_date_box.send_keys(Keys.DELETE)
    start_date_box.send_keys(start_date)

    if is_end_date_changed:
        end_date_box = driver.find_element_by_id('endDate')
        end_date_box.send_keys(Keys.BACK_SPACE)
        end_date_box.send_keys(Keys.CONTROL + 'a')
        end_date_box.send_keys(Keys.DELETE)
        end_date_box.send_keys(end_date)

    apply_btn = driver.find_element_by_id('applyBtn')
    apply_btn.click()

    sleep(2)

    # Download the file
    download_btn = driver.find_element_by_css_selector('.newBtn.LightGray.downloadBlueIcon.js-download-data')
    download_btn.click()
    print('Downloading data...')

    sleep(5)  # Wait for download to finish

    if return_download_name:
        try:
            driver.get('chrome://downloads')
            sleep(1)

            download_name = driver.execute_script("return document.querySelector("
                                                  "'downloads-manager').shadowRoot.querySelector('#downloadsList "
                                                  "downloads-item').shadowRoot.querySelector('div#content  "
                                                  "#file-link').text")
        except JavascriptException:
            print('Exception while file download.')

    driver.quit()
    print('Chrome session finished.')
    return download_name


def reformat_investing_com_data(data: pd.DataFrame,
                                drop_volume=True,
                                save_csv: bool = False,
                                save_name: str = 'investing_' + datetime.today().strftime('%Y%m%d_%H%M') + '.csv',
                                **kwargs):
    """
    This function reformat data from investing.com and makes it suitable for analysis.

    Args:
        data: Pandas dataframe. The data to feed into the project.
        drop_volume: Boolean. Default True. If the column "Vol." should be dropped.
        save_csv: Boolean. If the data is to be saved as csv.
        save_name: String. The file name of data to save as. Only used when save_csv is set to True.

    Returns:
        The reformatted dataframe.

    """
    data = data[data['High'] != data['Low']]

    data.drop('Change %', axis=1, inplace=True)

    if drop_volume:
        data.drop('Vol.', axis=1, inplace=True)

    data.rename(columns={'Price': 'Close'}, inplace=True)
    data = data[::-1]

    data.index = data.index.map(lambda x: datetime.strptime(x, '%b %d, %Y').strftime('%Y-%m-%d'))
    data[['Close', 'Open', 'High', 'Low']] = \
        data[['Close', 'Open', 'High', 'Low']].applymap(lambda num: int(float(num.replace(',', ''))))

    if save_csv:
        data.to_csv(save_name)

    return data