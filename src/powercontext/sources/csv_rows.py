import csv
import io
import json
import urllib.parse
from typing import Any, Dict, List, Tuple

class CSVRowInput:
    def __init__(self, document_id: str, primary_key: str, primary_key_value: str, columns: Tuple[str, ...], values: Tuple[str, ...]):
        self.document_id = document_id
        self.primary_key = primary_key
        self.primary_key_value = primary_key_value
        self.columns = columns
        self.values = values

class CSVRowSource:
    def __init__(self, identity: str, document_id: str, primary_key: str, primary_key_value: str, columns: Tuple[str, ...], values: Tuple[str, ...]):
        self.identity = identity
        self.document_id = document_id
        self.primary_key = primary_key
        self.primary_key_value = primary_key_value
        self.columns = columns
        self.values = values

def parse_csv_document(content: bytes, document_id: str, primary_key: str) -> List[CSVRowInput]:
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise ValueError("Invalid UTF-8 encoding")
    
    reader = csv.reader(io.StringIO(text), strict=True)
    
    try:
        rows = list(reader)
    except csv.Error as e:
        raise ValueError(f"Malformed CSV: {e}")
        
    if not rows:
        raise ValueError("Empty document")
        
    headers = rows[0]
    if not headers or any(not h.strip() for h in headers):
        raise ValueError("Invalid headers")
        
    if primary_key not in headers:
        raise ValueError("Primary key not in headers")
        
    pk_index = headers.index(primary_key)
    
    result = []
    for row in rows[1:]:
        if not row:
            continue
        if len(row) != len(headers):
            raise ValueError("Column count mismatch")
            
        pk_value = row[pk_index]
        if not pk_value.strip():
            raise ValueError("Empty primary key value")
            
        row_input = CSVRowInput(
            document_id=document_id,
            primary_key=primary_key,
            primary_key_value=pk_value,
            columns=tuple(headers),
            values=tuple(row)
        )
        result.append(row_input)
        
    return result

def generate_identity(document_id: str, primary_key_value: str) -> str:
    doc_id_encoded = urllib.parse.quote(document_id, safe="")
    pk_val_encoded = urllib.parse.quote(primary_key_value, safe="")
    return f"csv-row:{doc_id_encoded}:{pk_val_encoded}"

def generate_text_evidence(row: CSVRowSource) -> Dict[str, Any]:
    row_dict = dict(zip(row.columns, row.values))
    return {
        "source_type": "csv-row",
        "source_id": row.identity,
        "content": json.dumps(row_dict, ensure_ascii=False, separators=(',', ':')),
        "metadata": {
            "document_id": row.document_id,
            "primary_key": row.primary_key,
            "primary_key_value": row.primary_key_value,
            "columns": row.columns,
            "row": row_dict
        }
    }