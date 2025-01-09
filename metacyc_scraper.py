from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

n = 0


def get_node_text(node):
    """Get text content from a node"""
    try:
        return node.text.strip()
    except:
        return ""


def traverse_tree(driver, current_path, results):
    """Recursively traverse the tree and collect paths"""
    # Try to find child nodes (both leaf nodes and branches)
    global n
    # wait 0.5s
    time.sleep(1)
    # Wait for and find direct children ul/li elements
    children = driver.find_elements(By.XPATH, f"{current_path}/ul/li")

    if not children:  # This is a leaf node
        node = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"{current_path}/a/a"))
        )
        path_text = get_node_text(node)
        if path_text:
            results.append(path_text)
            print(path_text)
            n += 1
            print(n)
    else:
        # This is a branch node
        # Wait for and get the text of current node
        node = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"{current_path}/a/a"))
        )
        current_text = get_node_text(node)
        for i, child in enumerate(children, 1):
            # Create new path for child
            new_path = f"{current_path}/ul/li[{i}]"

            # Recursively traverse child nodes
            child_results = []
            # Wait for expand button to be clickable and click it
            expand_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"{new_path}/i"))
            )
            expand_button.click()

            # Traverse the expanded tree
            traverse_tree(driver, new_path, child_results)

            # Wait for collapse button to be clickable and click it
            collapse_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"{new_path}/i"))
            )
            collapse_button.click()
            # Add current node text to the beginning of each child result
            if current_text:
                for result in child_results:
                    results.append(f"{current_text}, {result}")


def scrape_metacyc_pathways():
    driver = webdriver.Chrome()
    # Navigate to the MetaCyc pathways page
    driver.get("https://metacyc.org/META/class-tree?object=Pathways")

    # Wait for root element to be present
    root_path = "/html/body/div[3]/div/div/ul/li"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, root_path))
    )
    results = []

    # Start traversal
    traverse_tree(driver, root_path, results)

    # Convert results to DataFrame
    # Split the comma-separated paths into columns
    df = pd.DataFrame([path.split(", ") for path in results])
    df.columns = [f"Level_{i+1}" for i in range(df.shape[1])]

    # Save to CSV
    df.to_csv("metacyc_pathways.csv", index=False)

    input("Press Enter to close the driver...")
    driver.quit()

    return df


if __name__ == "__main__":
    pathways_df = scrape_metacyc_pathways()
    print(f"Successfully scraped {len(pathways_df)} pathways")
