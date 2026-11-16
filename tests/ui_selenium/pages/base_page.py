from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = "/") -> None:
        self.driver.get(f"{self.base_url}{path}")

    def wait_visible(self, locator: tuple[str, str]):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator: tuple[str, str]):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def save_failure_screenshot(self, test_name: str, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{test_name}.png"
        self.driver.save_screenshot(str(path))
        return path
