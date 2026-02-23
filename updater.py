import csv
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

CSV_FILE = "psw_change.csv"


def get_today_password():
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Checking password change for date: {today}")

    if not os.path.exists(CSV_FILE):
        logger.error(f"CSV file '{CSV_FILE}' not found.")
        sys.exit(1)

    try:
        with open(CSV_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            # Normalize headers (remove BOM and spaces)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]

            required_fields = {"Fecha", "Contrasenia"}
            if not required_fields.issubset(set(reader.fieldnames)):
                logger.error(
                    f"CSV must contain headers: {required_fields}. Found: {reader.fieldnames}"
                )
                sys.exit(1)

            for row in reader:
                fecha = row["Fecha"].strip()
                if fecha == today:
                    logger.info("Password entry found for today.")
                    return row["Contrasenia"].strip()

    except Exception:
        logger.exception("Error reading CSV file.")
        sys.exit(1)

    logger.info("No password change scheduled for today.")
    return None


def update_files(new_password):
    updated_files = []

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".html") or file.endswith(".js"):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Replace whatever password logic you currently use
                    # Example: replace placeholder PASSWORD_HERE
                    if "PASSWORD_PLACEHOLDER" in content:
                        logger.info(f"Updating password in {filepath}")
                        updated_content = content.replace(
                            "PASSWORD_PLACEHOLDER",
                            new_password
                        )

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


def main():
    logger.info("Starting password update process...")

    new_password = get_today_password()

    if not new_password:
        logger.info("No updates needed today. Exiting.")
        return

    update_files(new_password)

    logger.info("Process completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unexpected error occurred!")
        sys.exit(1)
