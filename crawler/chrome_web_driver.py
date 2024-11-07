from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


class ChromeWebDriver:
    __slots__ = (
        "driver_path",
        "sleep_time",
    )

    def __init__(self, driver_path: str, sleep_time: int = 5):
        self.driver_path = driver_path
        self.sleep_time = sleep_time

    def get_html_content(self, target_url: str) -> str:
        """
        用来获取一个动态网页的表层HTML内容，但是不包括类似shadow-root这种内容潜藏的结构

        :param target_url: 访问的页面链接
        :return: 渲染后的HTML内容
        """
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service)
        driver.get(target_url)
        time.sleep(self.sleep_time)
        html_content = driver.page_source
        driver.quit()
        return html_content

    def get_shadow_root_content(self, target_url: str, selectors: list[str]) -> str:
        """
        用来递归访问嵌套的 shadow-root 并获取目标内容

        :param target_url: 访问的页面链接
        :param selectors: 选择器列表，每个选择器对应一层 shadow-root
        :return: 最终目标内容的文本
        """
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service)
        driver.get(target_url)
        time.sleep(self.sleep_time)

        element = None
        try:
            # 遍历选择器列表，逐层进入 shadow-root
            for selector in selectors:
                if element is None:
                    # 初始层的元素
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                else:
                    # 进入下一个 shadow-root 层
                    element = driver.execute_script("return arguments[0].shadowRoot", element)
                    element = element.find_element(By.CSS_SELECTOR, selector)

            content = element.text
        except Exception as e:
            print(f"An error occurred: {e}")
            content = ""
        finally:
            driver.quit()

        return content
