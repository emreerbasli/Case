import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding="utf-8")

z = zipfile.ZipFile("Zolvo_Case_Study.docx")
xml_content = z.read("word/document.xml")
root = ET.fromstring(xml_content)
ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

paragraphs = list(root.iter(f"{{{ns}}}p"))
for para in paragraphs:
    texts = [t.text for t in para.iter(f"{{{ns}}}t") if t.text]
    line = "".join(texts)
    if line.strip():
        print(line)
