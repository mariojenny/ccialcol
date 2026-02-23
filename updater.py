import csv
import logging
import os
import sys
from datetime import datetime

# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

CSV_FILE = "psw_change.csv"


# -----------------------------
# Open CSV with safe encoding detection
# -----------------------------
def open_csv_file(filename):
    encodings = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            logger.info(f"Trying to open CSV with encoding: {enc}")
            return open(filename, newline="", encoding=enc)
        except UnicodeDecodeError:
            continue

    logger.error("Could not decode CSV file with supported encodings.")
    sys.exit(1)


# -----------------------------
# Get today's password change
# -----------------------------
def get_today_password():
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Checking password change for date: {today}")

    if not os.path.exists(CSV_FILE):
        logger.error(f"CSV file '{CSV_FILE}' not found.")
        sys.exit(1)

    try:
        with open_csv_file(CSV_FILE) as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                logger.error("CSV file has no headers.")
                sys.exit(1)

            required_fields = {"date", "old_password", "new_password"}
            if not required_fields.issubset(set(reader.fieldnames)):
                logger.error(
                    f"CSV must contain headers: {required_fields}. Found: {reader.fieldnames}"
                )
                sys.exit(1)

            for row in reader:
                if row["date"] == today:
                    logger.info("Password entry found for today.")
                    return row["old_password"], row["new_password"]

    except Exception:
        logger.exception("Error reading CSV file.")
        sys.exit(1)

    logger.info("No password change scheduled for today.")
    return None, None


# -----------------------------
# Update HTML and JS files
# -----------------------------
def update_files(old_password, new_password):
    updated_files = []

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".html") or file.endswith(".js"):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if old_password in content:
                        logger.info(f"Updating password in {filepath}")
                        updated_content = content.replace(old_password, new_password)

                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(updated_content)

                        updated_files.append(filepath)

                except Exception:
                    logger.exception(f"Error processing file {filepath}")
                    sys.exit(1)

    if updated_files:
        logger.info(f"Updated {len(updated_files)} file(s).")
    else:
        logger.info("No files required updating.")

    return updated_files


# -----------------------------
# Main process
# -----------------------------
def main():
    logger.info("Starting password update process...")

    old_password, new_password = get_today_password()

    if not old_password:
        logger.info("No updates needed today. Exiting.")
        return

    update_files(old_password, new_password)

    logger.info("Process completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unexpected error occurred!")
        sys.exit(1)
