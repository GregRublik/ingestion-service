from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from pathlib import Path

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True  # Включить OCR для извлечения текста из изображений
pipeline_options.do_table_structure = True
pipeline_options.table_mode = TableFormerMode.FAST

# Создаем конвертер с настройками
converter = DocumentConverter(
)

document = Path(__file__).parent / "resume.pdf"


doc = converter.convert(document).document

print(doc.export_to_markdown())

