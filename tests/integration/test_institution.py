#!/usr/bin/python3
"""
Frontend tests using Selenium WebDriver.
"""

import pytest
import time
import os
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lib.selenium_helpers import (
    get_firefox_driver,
    get_application_url,
    get_realm,
    SeleniumTestSuite
)
from lib.db_helpers import delete_institution_from_db
from lib.auth import TEST_USERS

# Screenshot directory
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


class TestFrontendInstitution(SeleniumTestSuite):
    """Test suite for frontend functionality and integration tests"""

    @pytest.mark.flaky(reruns=2)  # can be flaky in CI
    def test_institution_duplicate_address_warning(self, authenticated_driver_factory):
        """
        Test that creating a new institution with a duplicate address triggers the warning dialog.
        Login as chefredakteur, navigate to Institutionen tab, create new institution, and trigger duplicate address warning.
        """
        # Login as chefredakteur
        driver = authenticated_driver_factory("chefredakteur")
        wait = WebDriverWait(driver, 10)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_1_logged_in.png")

        # Switch to "Institutionen" tab
        institutions_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='tab' and contains(., 'Institutionen')]"))
        )
        institutions_tab.click()
        print("Switched to Institutionen tab")
        time.sleep(1)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_2_institutions_tab.png")

        # Click "Institution hinzufügen" button to create a new institution
        # The button has the icon mdi-office-building-plus
        add_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//i[contains(@class, 'mdi-office-building-plus')]]"))
        )
        add_button.click()
        print("Clicked 'Institution hinzufügen' button")
        time.sleep(1)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_3_create_dialog.png")

        # Fill in the name first
        name_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Name')]/following-sibling::input"))
        )
        unique_name = f"TestInstitution_{int(time.time())}"
        name_field.click()
        name_field.send_keys(unique_name)
        print(f"Entered institution name: {unique_name}")

        # Fill in the address with duplicate values (Institution 1's address)
        # Find the input fields by their labels
        ort_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Ort des Dienstgebäudes')]/following-sibling::input"))
        )
        ort_field.click()
        ort_field.send_keys("ExampleLocation-1")
        plz_field = driver.find_element(By.XPATH, "//label[contains(., 'PLZ des Dienstgebäudes')]/following-sibling::input")
        plz_field.click()
        plz_field.send_keys("12345")
        strasse_field = driver.find_element(By.XPATH, "//label[contains(., 'Straße/Hausnummer des Dienstgebäudes')]/following-sibling::input")
        strasse_field.click()
        strasse_field.send_keys("Examplestreet 1")

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_4_changed_data.png")

        # click somewhere else to trigger duplicate check
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)  # Wait for duplicate check
        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_5_duplicate_warning.png")

        # Verify that the "Institution existiert bereits" popup appears
        duplicate_dialog_title = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'v-card-title') and contains(., 'Institution existiert bereits')]"))
        )
        assert duplicate_dialog_title.is_displayed()
        print("Duplicate institution warning dialog appeared")

        # Click "Ja, fortfahren" to confirm and continue despite duplicate warning
        confirm_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='v-btn__content'][contains(., 'Ja, fortfahren')]"))
        )
        confirm_button.click()
        print("Dismisses duplicate warning")
        time.sleep(0.5)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_6_before_category.png")

        # Click on the input category field
        category_input = driver.find_element(By.NAME, "tags")
        print(f'category_input {category_input}')
        category_input.click()
        time.sleep(0.3)
        print("Opened category dropdown")

        # Select a category option - use the 7th child as detected by Selenium IDE
        category_option = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".v-list-item:nth-child(7)"))
        )
        print(f'category_option {category_option}')
        driver.execute_script("arguments[0].click();", category_option)
        print("Selected category")
        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_6a_category_selected.png")
        time.sleep(0.5)

        # Submit the form by clicking the submit button
        save_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(., 'Erstellen')]]"))
        )
        save_button.click()
        print("Clicked save button to submit the form")
        time.sleep(1)  # Wait for save operation

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_7_after_save.png")

        # Wait for the create dialog to disappear
        wait.until(
            EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'v-card-title')]//span[contains(@class, 'text-h5')]"))
        )
        print("Create dialog closed, form submitted successfully")

        # Reopen the newly created institution to verify the values
        edit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[contains(., '{unique_name}')]//button[contains(@aria-label, 'edit') or .//i[contains(@class, 'mdi-pencil')]]"))
        )
        edit_button.click()
        print(f"Reopened {unique_name} for verification")
        time.sleep(1)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_duplicate_8_reopened.png")

        # Verify the name
        name_verify = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Name')]/following-sibling::input"))
        )
        actual_name = name_verify.get_attribute("value")
        assert actual_name == unique_name
        print(f"Verified name: {actual_name}")

        # Get the address values
        ort_field = driver.find_element(By.XPATH, "//label[contains(., 'Ort des Dienstgebäudes')]/following-sibling::input")
        plz_field = driver.find_element(By.XPATH, "//label[contains(., 'PLZ des Dienstgebäudes')]/following-sibling::input")
        strasse_field = driver.find_element(By.XPATH, "//label[contains(., 'Straße/Hausnummer des Dienstgebäudes')]/following-sibling::input")
        actual_ort = ort_field.get_attribute("value")
        actual_plz = plz_field.get_attribute("value")
        actual_strasse = strasse_field.get_attribute("value")

        # Verify the address values
        assert actual_ort == "ExampleLocation-1"
        assert actual_plz == "12345"
        assert actual_strasse == "Examplestreet 1"
        print(f"Verified address values: Ort={actual_ort}, PLZ={actual_plz}, Straße={actual_strasse}")

        delete_institution_from_db(institution_name=unique_name)

    def test_institution_no_duplicate_check_for_existing(self, authenticated_driver_factory):
        """
        Test that the duplicate address check does NOT trigger when viewing an existing institution
        """
        # Login as exampleuser
        driver = authenticated_driver_factory("exampleuser")
        wait = WebDriverWait(driver, 10)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_no_duplicate_check_for_exampleuser_1_logged_in.png")

        # Switch to "Institutionen" tab
        institutions_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='tab' and contains(., 'Institutionen')]"))
        )
        institutions_tab.click()
        print("Switched to Institutionen tab")
        time.sleep(1)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_no_duplicate_check_for_exampleuser_2_institutions_tab.png")

        # Click the view button
        view_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//tr[contains(., 'inst_2')]//button[contains(@aria-label, 'edit') or .//i[contains(@class, 'mdi-information-outline')]]"))
        )
        institution_name = "inst_2"

        view_button.click()
        print(f"Clicked edit button for {institution_name}")
        time.sleep(1)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_no_duplicate_check_for_exampleuser_3_edit_dialog.png")

        # Click in the PLZ field
        plz_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'PLZ des Dienstgebäudes')]/following-sibling::input"))
        )
        plz_field.click()
        print("Clicked PLZ field")
        time.sleep(0.5)

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_no_duplicate_check_for_exampleuser_4_plz_clicked.png")

        # click somewhere else
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)  # Wait for duplicate check

        driver.save_screenshot(f"{SCREENSHOT_DIR}/test_institution_no_duplicate_check_for_exampleuser_5_after_blur.png")

        # Verify that the duplicate warning dialog does NOT appear
        duplicate_dialogs = driver.find_elements(By.XPATH, "//div[contains(@class, 'v-card-title') and contains(., 'Institution existiert bereits')]")

        assert len(duplicate_dialogs) == 0
