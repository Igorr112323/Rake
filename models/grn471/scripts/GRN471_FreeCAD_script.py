#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания 3D-модели граблей ГРН-471 "Kolibri" в FreeCAD
ЗАПУСКАТЬ ВНУТРИ FREECAD (Макросы → Выполнить макрос)
"""

import FreeCAD as App
import Part
import PartDesign
import Sketcher
import Assembly
import math

# Создаем новый документ
doc = App.newDocument("GRN471_Kolibri")

# Создаем таблицу параметров
spreadsheet = doc.addObject("Spreadsheet::Sheet", "Параметры")
spreadsheet.set("A1", "Параметр")
spreadsheet.set("B1", "Значение")
spreadsheet.set("C1", "Единица")
spreadsheet.set("D1", "Источник")

# Заполняем параметры из Таблицы 2.1 (стр. 6)
spreadsheet.set("A2", "габарит_длина")
spreadsheet.set("B2", "4650")
spreadsheet.set("C2", "мм")
spreadsheet.set("D2", "Таблица 2.1, стр.6")

spreadsheet.set("A3", "габарит_ширина")
spreadsheet.set("B3", "4050")
spreadsheet.set("C3", "мм")
spreadsheet.set("D3", "Таблица 2.1, стр.6")

spreadsheet.set("A4", "габарит_высота")
spreadsheet.set("B4", "1350")
spreadsheet.set("C4", "мм")
spreadsheet.set("D4", "Таблица 2.1, стр.6")

spreadsheet.set("A5", "количество_штанг")
spreadsheet.set("B5", "11")
spreadsheet.set("C5", "шт")
spreadsheet.set("D5", "Таблица 2.1, стр.6")

spreadsheet.set("A6", "наклон_вала_ротора")
spreadsheet.set("B6", "3")
spreadsheet.set("C6", "градус")
spreadsheet.set("D6", "Раздел 2.3.2, стр.10")

spreadsheet.recompute()

print("="*80)
print("СОЗДАНИЕ МОДЕЛИ ГРАБЛЕЙ ГРН-471 'Kolibri'")
print("="*80)

# ============================================================================
# СОЗДАНИЕ ОСНОВНЫХ УЗЛОВ
# ============================================================================

print("\n[1/10] Создание рамы...")
# Рама ГРН-471.03.000А
frame_body = doc.addObject("PartDesign::Body", "ГРН_471_03_000А_Рама")
frame_sketch = frame_body.newObjectAt("Sketcher::SketchObject", "Sketch", frame_body.Origin.OriginFeatures[2])
# XY плоскость
frame_sketch.MapMode = "FlatFace"
frame_sketch.addGeometry(Part.LineSegment(App.Vector(-2000, -1500, 0), App.Vector(2000, -1500, 0)))
frame_sketch.addGeometry(Part.LineSegment(App.Vector(2000, -1500, 0), App.Vector(2000, 1500, 0)))
frame_sketch.addGeometry(Part.LineSegment(App.Vector(2000, 1500, 0), App.Vector(-2000, 1500, 0)))
frame_sketch.addGeometry(Part.LineSegment(App.Vector(-2000, 1500, 0), App.Vector(-2000, -1500, 0)))
frame_pad = frame_body.newObjectAt("PartDesign::Pad", "Pad", frame_sketch)
frame_pad.Length = 150
frame_pad.Reversed = True
doc.recompute()

print("[2/10] Создание навески...")
# Навеска ГРН-471.04.000
hitch_body = doc.addObject("PartDesign::Body", "ГРН_471_04_000_Навеска")
hitch_sketch = hitch_body.newObjectAt("Sketcher::SketchObject", "Sketch", hitch_body.Origin.OriginFeatures[2])
hitch_sketch.MapMode = "FlatFace"
# Рамка навески (трехточечная)
hitch_sketch.addGeometry(Part.LineSegment(App.Vector(-400, 0, 0), App.Vector(400, 0, 0)))
hitch_sketch.addGeometry(Part.LineSegment(App.Vector(400, 0, 0), App.Vector(400, 600, 0)))
hitch_sketch.addGeometry(Part.LineSegment(App.Vector(400, 600, 0), App.Vector(-400, 600, 0)))
hitch_sketch.addGeometry(Part.LineSegment(App.Vector(-400, 600, 0), App.Vector(-400, 0, 0)))
hitch_pad = hitch_body.newObjectAt("PartDesign::Pad", "Pad", hitch_sketch)
hitch_pad.Length = 80
hitch_body.Placement.Base = App.Vector(-2200, 0, 200)
doc.recompute()

print("[3/10] Создание ротора с редуктором...")
# Ротор (сборка)
rotor_assembly = doc.addObject("App::DocumentObjectGroup", "Ротор_с_редуктором")

# Редуктор Staroselski 170-01.110.ACT
gearbox_body = doc.addObject("PartDesign::Body", "Редуктор_170_01_110_ACT")
gearbox_sketch = gearbox_body.newObjectAt("Sketcher::SketchObject", "Sketch", gearbox_body.Origin.OriginFeatures[2])
gearbox_sketch.MapMode = "FlatFace"
gearbox_sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 400))
gearbox_pad = gearbox_body.newObjectAt("PartDesign::Pad", "Pad", gearbox_sketch)
gearbox_pad.Length = 500
rotor_assembly.addObject(gearbox_body)

# Штанги (11 штук по кругу)
print("  - Создание 11 штанг...")
for i in range(11):
    angle = i * (360.0 / 11)
    rod_name = f"Штанга_{i+1:02d}"
    rod_body = doc.addObject("PartDesign::Body", rod_name)
    rod_sketch = rod_body.newObjectAt("Sketcher::SketchObject", "Sketch", rod_body.Origin.OriginFeatures[2])
    rod_sketch.MapMode = "FlatFace"
    rod_sketch.addGeometry(Part.LineSegment(App.Vector(0, -50, 0), App.Vector(2200, -50, 0)))
    rod_sketch.addGeometry(Part.LineSegment(App.Vector(2200, -50, 0), App.Vector(2200, 50, 0)))
    rod_sketch.addGeometry(Part.LineSegment(App.Vector(2200, 50, 0), App.Vector(0, 50, 0)))
    rod_sketch.addGeometry(Part.LineSegment(App.Vector(0, 50, 0), App.Vector(0, -50, 0)))
    rod_pad = rod_body.newObjectAt("PartDesign::Pad", "Pad", rod_sketch)
    rod_pad.Length = 80
    
    # Поворот штанги
    rod_body.Placement = App.Placement(
        App.Vector(0, 0, 0),
        App.Rotation(App.Vector(0, 0, 1), angle)
    )
    rotor_assembly.addObject(rod_body)

# Граблины (по 4 на каждую штангу = 44 граблины)
print("  - Создание 44 граблин...")
for i in range(11):
    angle = i * (360.0 / 11)
    for j in range(4):
        rake_name = f"Граблина_{i+1:02d}_{j+1}"
        rake_body = doc.addObject("PartDesign::Body", rake_name)
        rake_sketch = rake_body.newObjectAt("Sketcher::SketchObject", "Sketch", rake_body.Origin.OriginFeatures[2])
        rake_sketch.MapMode = "FlatFace"
        # Пружинный зуб
        rake_sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(0, -400, 0)))
        rake_pad = rake_body.newObjectAt("PartDesign::Pad", "Pad", rake_sketch)
        rake_pad.Length = 20
        
        # Позиционирование на штанге
        offset_x = 400 + j * 500
        rad_angle = math.radians(angle)
        x = offset_x * math.cos(rad_angle)
        y = offset_x * math.sin(rad_angle)
        
        rake_body.Placement = App.Placement(
            App.Vector(x, y, -200),
            App.Rotation(App.Vector(0, 0, 1), angle)
        )
        rotor_assembly.addObject(rake_body)

doc.recompute()

print("[4/10] Создание каретки...")
# Каретка ГРН-471.02.000
carriage_assembly = doc.addObject("App::DocumentObjectGroup", "ГРН_471_02_000_Каретка")

# Балка
carriage_beam = doc.addObject("PartDesign::Body", "ГРН_471_02_010Г_Балка")
beam_sketch = carriage_beam.newObjectAt("Sketcher::SketchObject", "Sketch", carriage_beam.Origin.OriginFeatures[2])
beam_sketch.MapMode = "FlatFace"
beam_sketch.addGeometry(Part.LineSegment(App.Vector(-1500, -200, 0), App.Vector(1500, -200, 0)))
beam_sketch.addGeometry(Part.LineSegment(App.Vector(1500, -200, 0), App.Vector(1500, 200, 0)))
beam_sketch.addGeometry(Part.LineSegment(App.Vector(1500, 200, 0), App.Vector(-1500, 200, 0)))
beam_sketch.addGeometry(Part.LineSegment(App.Vector(-1500, 200, 0), App.Vector(-1500, -200, 0)))
beam_pad = carriage_beam.newObjectAt("PartDesign::Pad", "Pad", beam_sketch)
beam_pad.Length = 150
carriage_beam.Placement.Base = App.Vector(0, 0, -500)
carriage_assembly.addObject(carriage_beam)

# Колеса (4 штуки)
print("  - Создание 4 колес...")
for i in range(4):
    wheel_name = f"ГРН_471_02_060_Колесо_{i+1}"
    wheel_body = doc.addObject("PartDesign::Body", wheel_name)
    wheel_sketch = wheel_body.newObjectAt("Sketcher::SketchObject", "Sketch", wheel_body.Origin.OriginFeatures[2])
    wheel_sketch.MapMode = "FlatFace"
    wheel_sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 250))
    wheel_pad = wheel_body.newObjectAt("PartDesign::Pad", "Pad", wheel_sketch)
    wheel_pad.Length = 150
    
    # Позиционирование колес
    positions = [
        App.Vector(-1200, -800, -750),
        App.Vector(1200, -800, -750),
        App.Vector(-1200, 800, -750),
        App.Vector(1200, 800, -750),
    ]
    wheel_body.Placement.Base = positions[i]
    wheel_body.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
    carriage_assembly.addObject(wheel_body)

doc.recompute()

print("[5/10] Создание ограждений...")
# Ограждение правое ГРН-471.05.000
guard_right = doc.addObject("PartDesign::Body", "ГРН_471_05_000_Ограждение_правое")
guard_r_sketch = guard_right.newObjectAt("Sketcher::SketchObject", "Sketch", guard_right.Origin.OriginFeatures[2])
guard_r_sketch.MapMode = "FlatFace"
guard_r_sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(2000, 0, 0)))
guard_r_sketch.addGeometry(Part.LineSegment(App.Vector(2000, 0, 0), App.Vector(2000, 100, 0)))
guard_r_sketch.addGeometry(Part.LineSegment(App.Vector(2000, 100, 0), App.Vector(0, 100, 0)))
guard_r_sketch.addGeometry(Part.LineSegment(App.Vector(0, 100, 0), App.Vector(0, 0, 0)))
guard_r_pad = guard_right.newObjectAt("PartDesign::Pad", "Pad", guard_r_sketch)
guard_r_pad.Length = 50
guard_right.Placement.Base = App.Vector(0, 2000, 300)
doc.recompute()

# Ограждение левое ГРН-471.06.000А с отражателем
guard_left = doc.addObject("PartDesign::Body", "ГРН_471_06_000А_Ограждение_левое")
guard_l_sketch = guard_left.newObjectAt("Sketcher::SketchObject", "Sketch", guard_left.Origin.OriginFeatures[2])
guard_l_sketch.MapMode = "FlatFace"
guard_l_sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(2000, 0, 0)))
guard_l_sketch.addGeometry(Part.LineSegment(App.Vector(2000, 0, 0), App.Vector(2000, 100, 0)))
guard_l_sketch.addGeometry(Part.LineSegment(App.Vector(2000, 100, 0), App.Vector(0, 100, 0)))
guard_l_sketch.addGeometry(Part.LineSegment(App.Vector(0, 100, 0), App.Vector(0, 0, 0)))
guard_l_pad = guard_left.newObjectAt("PartDesign::Pad", "Pad", guard_l_sketch)
guard_l_pad.Length = 50
guard_left.Placement.Base = App.Vector(0, -2000, 300)

# Отражатель
reflector = doc.addObject("PartDesign::Body", "ГРН_471_06_070_Отражатель")
reflector_sketch = reflector.newObjectAt("Sketcher::SketchObject", "Sketch", reflector.Origin.OriginFeatures[2])
reflector_sketch.MapMode = "FlatFace"
reflector_sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(1400, 0, 0)))
reflector_sketch.addGeometry(Part.LineSegment(App.Vector(1400, 0, 0), App.Vector(1400, 800, 0)))
reflector_sketch.addGeometry(Part.LineSegment(App.Vector(1400, 800, 0), App.Vector(0, 800, 0)))
reflector_sketch.addGeometry(Part.LineSegment(App.Vector(0, 800, 0), App.Vector(0, 0, 0)))
reflector_pad = reflector.newObjectAt("PartDesign::Pad", "Pad", reflector_sketch)
reflector_pad.Length = 20
reflector.Placement.Base = App.Vector(500, -2200, -200)
doc.recompute()

print("[6/10] Создание контрпривода...")
# Контрпривод ГРН-471.00.060
counterdrive = doc.addObject("PartDesign::Body", "ГРН_471_00_060_Контрпривод")
counter_sketch = counterdrive.newObjectAt("Sketcher::SketchObject", "Sketch", counterdrive.Origin.OriginFeatures[2])
counter_sketch.MapMode = "FlatFace"
counter_sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 150))
counter_pad = counterdrive.newObjectAt("PartDesign::Pad", "Pad", counter_sketch)
counter_pad.Length = 300
counterdrive.Placement.Base = App.Vector(-1800, 0, 400)
doc.recompute()

print("[7/10] Создание карданных валов...")
# Вал карданный 2005/1200/KH/37.1-37.1
cardan1 = doc.addObject("PartDesign::Body", "Вал_карданный_2005_1200_KH")
cardan1_sketch = cardan1.newObjectAt("Sketcher::SketchObject", "Sketch", cardan1.Origin.OriginFeatures[2])
cardan1_sketch.MapMode = "FlatFace"
cardan1_sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 80))
cardan1_pad = cardan1.newObjectAt("PartDesign::Pad", "Pad", cardan1_sketch)
cardan1_pad.Length = 1200
cardan1.Placement.Base = App.Vector(-2500, 0, 400)
cardan1.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)
doc.recompute()

# Вал карданный с обгонной муфтой 2005/950/KH/37.28-93.8
cardan2 = doc.addObject("PartDesign::Body", "Вал_карданный_2005_950_KH")
cardan2_sketch = cardan2.newObjectAt("Sketcher::SketchObject", "Sketch", cardan2.Origin.OriginFeatures[2])
cardan2_sketch.MapMode = "FlatFace"
cardan2_sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 80))
cardan2_pad = cardan2.newObjectAt("PartDesign::Pad", "Pad", cardan2_sketch)
cardan2_pad.Length = 950
cardan2.Placement.Base = App.Vector(-1500, 0, 400)
cardan2.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)
doc.recompute()

print("[8/10] Создание крепежа...")
# Создаем группу крепежа
fasteners_group = doc.addObject("App::DocumentObjectGroup", "Крепеж")

# Болты М12-6g*45 (4 шт на общем виде)
for i in range(4):
    bolt = doc.addObject("Part::Cylinder", f"Болт_М12х45_{i+1}")
    bolt.Radius = 6
    bolt.Height = 45
    fasteners_group.addObject(bolt)

# Гайки М12-6Н (8 шт)
for i in range(8):
    nut = doc.addObject("Part::Cylinder", f"Гайка_М12_{i+1}")
    nut.Radius = 10
    nut.Height = 12
    fasteners_group.addObject(nut)

# Шплинты
for i in range(12):
    cotter = doc.addObject("Part::Cylinder", f"Шплинт_3_2х25_{i+1}")
    cotter.Radius = 1.6
    cotter.Height = 25
    fasteners_group.addObject(cotter)

doc.recompute()

print("[9/10] Сохранение модели...")
# Сохраняем документ
fcstd_path = "GRN471_Kolibri.FCStd"
doc.saveAs(fcstd_path)

print("[10/10] Экспорт в STEP...")
# Экспорт в STEP
step_path = "GRN471_Kolibri.step"
Part.export([obj for obj in doc.Objects if hasattr(obj, "Shape")], step_path)

print("\n" + "="*80)
print("✓ МОДЕЛЬ СОЗДАНА УСПЕШНО")
print("="*80)
print(f"\nФайлы:")
print(f"  FCStd: {fcstd_path}")
print(f"  STEP:  {step_path}")
print(f"\nСтатистика:")
print(f"  Узлов: {len([o for o in doc.Objects if o.TypeId == 'PartDesign::Body'])}")
print(f"  Деталей: {len(doc.Objects)}")

