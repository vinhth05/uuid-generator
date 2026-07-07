import csv
import json
from pathlib import Path
from typing import List
from utils.logger import logger
import xml.etree.ElementTree as ET

class Exporter:
    @staticmethod
    def export_to_txt(filepath: Path, uuids: List[str]):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(uuids))
            logger.info(f"Exported {len(uuids)} UUIDs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export TXT: {e}")
            return False

    @staticmethod
    def export_to_csv(filepath: Path, uuids: List[str]):
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["UUID"])
                for u in uuids:
                    writer.writerow([u])
            logger.info(f"Exported {len(uuids)} UUIDs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return False

    @staticmethod
    def export_to_json(filepath: Path, uuids: List[str]):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"uuids": uuids}, f, indent=4)
            logger.info(f"Exported {len(uuids)} UUIDs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return False

    @staticmethod
    def export_to_xml(filepath: Path, uuids: List[str]):
        try:
            root = ET.Element("UUIDs")
            for u in uuids:
                item = ET.SubElement(root, "UUID")
                item.text = u
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            logger.info(f"Exported {len(uuids)} UUIDs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export XML: {e}")
            return False
