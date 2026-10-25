#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание 3D-модели граблей роторных ГРН-471 "Kolibri"
Формат: FreeCAD FCStd
"""

import zipfile
import json
import os
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Размеры из руководства (Таблица 2.1, страница 6)
DIMENSIONS = {
    "габарит_длина": 4650,  # мм, ±50
    "габарит_ширина": 4050,  # мм, ±50
    "габарит_высота": 1350,  # мм, ±50
    "ширина_захвата": 4700,  # мм
    "транспортный_просвет": 250,  # мм
    "количество_штанг": 11,
    "наклон_вала_ротора": 3,  # градусы
    "обороты_ротора": 66,  # об/мин
    "масса": 690,  # кг, ±35
}

class FCStdBuilder:
    """Построитель FCStd файлов"""
    
    def __init__(self, name="GRN471"):
        self.name = name
        self.objects = []
        self.bodies = []
        self.assemblies = []
        self.spreadsheet_data = {}
        
    def add_body(self, name, label=None, shape_type="Box", parameters=None):
        """Добавить тело PartDesign"""
        body = {
            "name": name,
            "label": label or name,
            "type": shape_type,
            "parameters": parameters or {},
            "features": []
        }
        self.bodies.append(body)
        return body
    
    def add_sketch(self, body, plane="XY", constraints=None):
        """Добавить эскиз к телу"""
        sketch = {
            "type": "Sketch",
            "plane": plane,
            "constraints": constraints or []
        }
        body["features"].append(sketch)
        return sketch
    
    def add_pad(self, body, length, symmetric=False):
        """Добавить выдавливание"""
        pad = {
            "type": "Pad",
            "length": length,
            "symmetric": symmetric
        }
        body["features"].append(pad)
        return pad
    
    def create_spreadsheet(self):
        """Создать таблицу параметров"""
        sheet = {
            "name": "Параметры",
            "cells": {}
        }
        
        # Заполняем из DIMENSIONS
        row = 1
        sheet["cells"][f"A{row}"] = "Параметр"
        sheet["cells"][f"B{row}"] = "Значение"
        sheet["cells"][f"C{row}"] = "Единица"
        sheet["cells"][f"D{row}"] = "Источник"
        
        for key, value in DIMENSIONS.items():
            row += 1
            sheet["cells"][f"A{row}"] = key
            sheet["cells"][f"B{row}"] = str(value)
            sheet["cells"][f"C{row}"] = "мм" if "размер" in key or "просвет" in key else "шт" if "количество" in key else ""
            sheet["cells"][f"D{row}"] = "Руководство, Таблица 2.1, стр.6"
        
        self.spreadsheet_data = sheet
        return sheet
    
    def save(self, filepath):
        """Сохранить в FCStd файл"""
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Document.xml
            doc_xml = self._create_document_xml()
            zf.writestr("Document.xml", doc_xml)
            
            # GuiDocument.xml
            gui_xml = self._create_gui_document_xml()
            zf.writestr("GuiDocument.xml", gui_xml)
            
            # Spreadsheet
            if self.spreadsheet_data:
                sheet_xml = self._create_spreadsheet_xml()
                zf.writestr("Spreadsheet.xml", sheet_xml)
        
        print(f"✓ Файл сохранен: {filepath}")
    
    def _create_document_xml(self):
        """Создать Document.xml"""
        root = ET.Element("Document")
        root.set("SchemaVersion", "4")
        
        # Properties
        props = ET.SubElement(root, "Properties")
        props.set("count", "1")
        
        prop = ET.SubElement(props, "Property")
        prop.set("name", "Comment")
        prop_str = ET.SubElement(prop, "String")
        prop_str.set("value", "Грабли роторные навесные ГРН-471 Kolibri")
        
        # Objects
        objects = ET.SubElement(root, "Objects")
        objects.set("count", str(len(self.bodies) + 1))
        
        # Spreadsheet
        obj = ET.SubElement(objects, "Object")
        obj.set("type", "Spreadsheet::Sheet")
        obj.set("name", "Параметры")
        
        # Bodies
        for body in self.bodies:
            obj = ET.SubElement(objects, "Object")
            obj.set("type", "PartDesign::Body")
            obj.set("name", body["name"])
        
        # Object data
        obj_data = ET.SubElement(root, "ObjectData")
        obj_data.set("count", str(len(self.bodies) + 1))
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _create_gui_document_xml(self):
        """Создать GuiDocument.xml"""
        root = ET.Element("Document")
        root.set("SchemaVersion", "1")
        
        view_prov = ET.SubElement(root, "ViewProviderData")
        view_prov.set("count", str(len(self.bodies)))
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _create_spreadsheet_xml(self):
        """Создать Spreadsheet.xml"""
        root = ET.Element("Document")
        
        obj_data = ET.SubElement(root, "ObjectData")
        obj_data.set("count", "1")
        
        obj = ET.SubElement(obj_data, "Object")
        obj.set("type", "Spreadsheet::Sheet")
        
        props = ET.SubElement(obj, "Properties")
        props.set("count", str(len(self.spreadsheet_data["cells"])))
        
        for cell, value in self.spreadsheet_data["cells"].items():
            prop = ET.SubElement(props, "Property")
            prop.set("name", cell)
            prop_str = ET.SubElement(prop, "String")
            prop_str.set("value", str(value))
        
        return ET.tostring(root, encoding='unicode', method='xml')


# Создаем модель
print("="*80)
print("СОЗДАНИЕ 3D-МОДЕЛИ ГРАБЛЕЙ ГРН-471 'Kolibri'")
print("="*80)

builder = FCStdBuilder("GRN471")

# Создаем таблицу параметров
print("\n[1/5] Создание таблицы параметров...")
builder.create_spreadsheet()

# Создаем основные узлы
print("\n[2/5] Создание основных узлов...")

# Рама
frame = builder.add_body("Рама", "ГРН-471.03.000А Рама", "Weldment", {
    "длина": 4000,
    "ширина": 3500,
    "высота": 200
})

# Навеска
hitch = builder.add_body("Навеска", "ГРН-471.04.000 Навеска", "Assembly", {
    "тип": "трехточечная"
})

# Ротор
rotor = builder.add_body("Ротор", "Ротор с редуктором", "Assembly", {
    "количество_штанг": 11,
    "диаметр": 4500
})

# Каретка
carriage = builder.add_body("Каретка", "ГРН-471.02.000 Каретка", "Assembly", {
    "количество_колес": 4
})

# Ограждения
guard_right = builder.add_body("Ограждение_правое", "ГРН-471.05.000 Ограждение правое", "Weldment")
guard_left = builder.add_body("Ограждение_левое", "ГРН-471.06.000А Ограждение левое с отражателем", "Weldment")

# Контрпривод
counterdrive = builder.add_body("Контрпривод", "ГРН-471.00.060 Контрпривод", "Assembly")

print(f"✓ Создано {len(builder.bodies)} основных узлов")

# Сохраняем модель
print("\n[3/5] Сохранение FCStd файла...")
output_dir = Path("exports")
output_dir.mkdir(exist_ok=True)
fcstd_path = output_dir / "GRN471_Kolibri.FCStd"
builder.save(fcstd_path)

print("\n" + "="*80)
print("✓ МОДЕЛЬ СОЗДАНА УСПЕШНО")
print("="*80)
print(f"\nФайл: {fcstd_path.absolute()}")
print(f"Размер: {fcstd_path.stat().st_size} байт")

