import pytest
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import os


class TestCalculator:
    @pytest.fixture(scope="class")
    def driver(self):
        chrome_options = Options()

        if os.getenv("CI"):
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)

        yield driver
        driver.quit()

    def open_page(self, driver):
        file_path = os.path.abspath("../src/index.html")
        driver.get(f"file://{file_path}")

    def wait_result_text(self, driver, timeout=10):
        """Attend que #result contienne du texte non vide."""
        locator = (By.ID, "result")
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(*locator).text.strip() != ""
        )
        return driver.find_element(*locator).text.strip()

    def set_inputs_and_calculate(self, driver, num1, num2, op_value):
        # Nettoyer / saisir les valeurs
        n1 = driver.find_element(By.ID, "num1")
        n2 = driver.find_element(By.ID, "num2")
        n1.clear()
        n2.clear()
        n1.send_keys(str(num1))
        n2.send_keys(str(num2))

        # Sélectionner l'opération
        select = Select(driver.find_element(By.ID, "operation"))
        select.select_by_value(op_value)

        # Calculer
        driver.find_element(By.ID, "calculate").click()

    def test_page_loads(self, driver):
        """Test 1: Vérifier que la page se charge correctement"""
        self.open_page(driver)

        assert "Calculatrice Simple" in driver.title

        assert driver.find_element(By.ID, "num1").is_displayed()
        assert driver.find_element(By.ID, "num2").is_displayed()
        assert driver.find_element(By.ID, "operation").is_displayed()
        assert driver.find_element(By.ID, "calculate").is_displayed()

    def test_addition(self, driver):
        """Test 2: Tester l'addition"""
        self.open_page(driver)

        self.set_inputs_and_calculate(driver, "10", "5", "add")

        result_text = self.wait_result_text(driver)
        assert "Résultat: 15" in result_text

    def test_division_by_zero(self, driver):
        """Test 3: Tester la division par zéro"""
        self.open_page(driver)

        self.set_inputs_and_calculate(driver, "10", "0", "divide")

        result_text = self.wait_result_text(driver)
        assert "Erreur: Division par zéro" in result_text

    def test_all_operations(self, driver):
        """Test 4: Tester toutes les opérations"""
        self.open_page(driver)

        operations = [
            ("add", "8", "2", "10"),
            ("subtract", "8", "2", "6"),
            ("multiply", "8", "2", "16"),
            ("divide", "8", "2", "4"),
        ]

        for op, num1, num2, expected in operations:
            self.set_inputs_and_calculate(driver, num1, num2, op)

            result_text = self.wait_result_text(driver)
            assert f"Résultat: {expected}" in result_text

            time.sleep(0.2)

    def test_page_load_time(self, driver):
        """Test 5: Mesurer le temps de chargement de la page"""
        start_time = time.time()
        self.open_page(driver)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "calculator"))
        )

        load_time = time.time() - start_time
        print(f"Temps de chargement: {load_time:.2f} secondes")

        assert load_time < 3.0, f"Page trop lente à charger: {load_time:.2f}s"

    def test_negatifs(self, driver):
        """Test 7: Tester avec des nombres négatifs"""
        self.open_page(driver)

        # -10 + 3 = -7
        self.set_inputs_and_calculate(driver, "-10", "3", "add")
        result_text = self.wait_result_text(driver)
        assert "Résultat:" in result_text
        assert "-7" in result_text

        # -10 * -2 = 20
        self.set_inputs_and_calculate(driver, "-10", "-2", "multiply")
        result_text = self.wait_result_text(driver)
        assert "20" in result_text

    def test_ui_styles(self, driver):
        """Test 8: Test de l'interface utilisateur (couleurs, tailles)"""
        self.open_page(driver)

        button = driver.find_element(By.ID, "calculate")
        num1 = driver.find_element(By.ID, "num1")

        btn_size = button.size
        assert btn_size["width"] >= 80, f"Bouton trop étroit: {btn_size}"
        assert btn_size["height"] >= 25, f"Bouton trop petit: {btn_size}"

        btn_bg = button.value_of_css_property("background-color")
        btn_color = button.value_of_css_property("color")

        assert btn_bg is not None and btn_bg != "rgba(0, 0, 0, 0)", f"Background suspect: {btn_bg}"
        assert btn_color is not None and btn_color != "rgba(0, 0, 0, 0)", f"Couleur texte suspecte: {btn_color}"

        font_size = num1.value_of_css_property("font-size")
        assert font_size.endswith("px"), f"Font-size inattendu: {font_size}"


if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html", "--self-contained-html"])
