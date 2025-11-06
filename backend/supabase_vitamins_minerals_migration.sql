-- =====================================================
-- SUPABASE MIGRATION: Vitamins & Minerals Database Schema
-- =====================================================
-- Створення 4 таблиць для системи перевірки дозувань вітамінів та мінералів
-- Автор: LabelCheck UA Team
-- Дата: 2025-01-22
-- Версія: 1.0

-- =====================================================
-- ТАБЛИЦЯ 1: allowed_vitamins_minerals
-- =====================================================
-- Дозволені вітаміни та мінеральні речовини згідно Додатку 1 Наказу МОЗ №1114

CREATE TABLE allowed_vitamins_minerals (
    id SERIAL PRIMARY KEY,
    substance_name_ua VARCHAR(200) NOT NULL,
    substance_name_en VARCHAR(200) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('vitamin', 'mineral')),
    alternative_names TEXT[], -- альтернативні назви
    regulatory_source VARCHAR(100) DEFAULT 'Наказ МОЗ №1114, Додаток 1',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(substance_name_ua, category)
);

-- Індекси
CREATE INDEX idx_vitamins_minerals_category ON allowed_vitamins_minerals(category);
CREATE INDEX idx_vitamins_minerals_name ON allowed_vitamins_minerals(substance_name_ua);

-- =====================================================
-- ТАБЛИЦЯ 2: vitamin_mineral_forms
-- =====================================================
-- Дозволені форми вітамінів та мінеральних речовин згідно Додатку 2 Наказу МОЗ №1114

CREATE TABLE vitamin_mineral_forms (
    id SERIAL PRIMARY KEY,
    substance_id INTEGER REFERENCES allowed_vitamins_minerals(id) ON DELETE CASCADE,
    form_name_ua VARCHAR(300) NOT NULL,
    form_name_en VARCHAR(300) NOT NULL,
    chemical_formula VARCHAR(100),
    regulatory_source VARCHAR(100) DEFAULT 'Наказ МОЗ №1114, Додаток 2',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(substance_id, form_name_ua)
);

-- Індекси
CREATE INDEX idx_forms_substance ON vitamin_mineral_forms(substance_id);
CREATE INDEX idx_forms_name ON vitamin_mineral_forms(form_name_ua);

-- =====================================================
-- ТАБЛИЦЯ 3: max_doses_table1
-- =====================================================
-- Максимально допустимі добові дози з Таблиці 1 Проєкту Змін до Наказу МОЗ №1114

CREATE TABLE max_doses_table1 (
    id SERIAL PRIMARY KEY,
    substance_name_ua VARCHAR(200) NOT NULL UNIQUE,
    substance_name_en VARCHAR(200) NOT NULL,
    max_dose_value DECIMAL(10, 2) NOT NULL,
    max_dose_unit VARCHAR(20) NOT NULL,
    regulatory_source VARCHAR(200) DEFAULT 'Проєкт Змін до Наказу №1114, Таблиця 1',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Індекс
CREATE INDEX idx_max_doses_substance ON max_doses_table1(substance_name_ua);

-- =====================================================
-- ТАБЛИЦЯ 4: efsa_limits
-- =====================================================
-- EFSA ліміти (UL та Safe Levels)

CREATE TABLE efsa_limits (
    id SERIAL PRIMARY KEY,
    substance_name_ua VARCHAR(200) NOT NULL,
    substance_name_en VARCHAR(200) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('vitamin', 'mineral', 'amino_acid', 'fatty_acid', 'other')),
    
    -- UL (Tolerable Upper Intake Level)
    ul_value DECIMAL(10, 2),
    ul_unit VARCHAR(20),
    ul_age_group VARCHAR(50) DEFAULT 'adults',
    ul_source_url TEXT,
    ul_publication_year INTEGER,
    
    -- Safe Level (якщо UL не встановлено)
    safe_level_value DECIMAL(10, 2),
    safe_level_unit VARCHAR(20),
    safe_level_source_url TEXT,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(substance_name_en, category)
);

-- Індекси
CREATE INDEX idx_efsa_category ON efsa_limits(category);
CREATE INDEX idx_efsa_substance ON efsa_limits(substance_name_en);

-- =====================================================
-- ДАНІ ДЛЯ ЗАВАНТАЖЕННЯ
-- =====================================================

-- Дозволені вітаміни та мінерали (28 записів)
INSERT INTO allowed_vitamins_minerals (substance_name_ua, substance_name_en, category, alternative_names, notes) VALUES
-- ВІТАМІНИ
('Вітамін A', 'Vitamin A', 'vitamin', ARRAY['ретинол', 'бета-каротин'], 'Включає ретинол та провітамін А каротиноїди'),
('Вітамін B1', 'Vitamin B1', 'vitamin', ARRAY['тіамін', 'thiamin'], NULL),
('Вітамін B2', 'Vitamin B2', 'vitamin', ARRAY['рибофлавін', 'riboflavin'], NULL),
('Вітамін B3', 'Vitamin B3', 'vitamin', ARRAY['ніацин', 'нікотинамід', 'нікотинова кислота', 'niacin'], 'Включає нікотинову кислоту та нікотинамід'),
('Вітамін B5', 'Vitamin B5', 'vitamin', ARRAY['пантотенова кислота', 'pantothenic acid'], NULL),
('Вітамін B6', 'Vitamin B6', 'vitamin', ARRAY['піридоксин', 'pyridoxine'], NULL),
('Вітамін B9', 'Vitamin B9', 'vitamin', ARRAY['фолат', 'фолієва кислота', 'folate', 'folic acid'], 'Включає фолат та фолієву кислоту'),
('Вітамін B12', 'Vitamin B12', 'vitamin', ARRAY['кобаламін', 'cobalamin'], NULL),
('Біотин', 'Biotin', 'vitamin', ARRAY['вітамін B7', 'вітамін H'], NULL),
('Вітамін C', 'Vitamin C', 'vitamin', ARRAY['аскорбінова кислота', 'ascorbic acid'], NULL),
('Вітамін D', 'Vitamin D', 'vitamin', ARRAY['кальциферол', 'D2', 'D3', 'cholecalciferol'], 'Включає D2 (ергокальциферол) та D3 (холекальциферол)'),
('Вітамін E', 'Vitamin E', 'vitamin', ARRAY['токоферол', 'tocopherol'], 'Включає альфа-токоферол та змішані токофероли'),
('Вітамін K', 'Vitamin K', 'vitamin', ARRAY['K1', 'K2', 'філохінон', 'менахінон'], 'Включає K1 (філохінон) та K2 (менахінон)'),

-- МІНЕРАЛИ
('Кальцій', 'Calcium', 'mineral', ARRAY['Ca'], NULL),
('Магній', 'Magnesium', 'mineral', ARRAY['Mg'], NULL),
('Залізо', 'Iron', 'mineral', ARRAY['Fe'], NULL),
('Цинк', 'Zinc', 'mineral', ARRAY['Zn'], NULL),
('Мідь', 'Copper', 'mineral', ARRAY['Cu'], NULL),
('Марганець', 'Manganese', 'mineral', ARRAY['Mn'], NULL),
('Селен', 'Selenium', 'mineral', ARRAY['Se'], NULL),
('Йод', 'Iodine', 'mineral', ARRAY['I'], NULL),
('Хром', 'Chromium', 'mineral', ARRAY['Cr'], NULL),
('Молібден', 'Molybdenum', 'mineral', ARRAY['Mo'], NULL),
('Фосфор', 'Phosphorus', 'mineral', ARRAY['P'], NULL),
('Калій', 'Potassium', 'mineral', ARRAY['K'], NULL),
('Бор', 'Boron', 'mineral', ARRAY['B'], NULL),
('Кремній', 'Silicon', 'mineral', ARRAY['Si'], NULL),
('Ванадій', 'Vanadium', 'mineral', ARRAY['V'], NULL);

-- Дозволені форми вітамінів та мінералів (приклади для основних речовин)
-- Вітамін A (ID=1)
INSERT INTO vitamin_mineral_forms (substance_id, form_name_ua, form_name_en, chemical_formula, notes) VALUES
(1, 'ретинілу ацетат', 'retinyl acetate', 'C22H32O2', NULL),
(1, 'ретинілу пальмітат', 'retinyl palmitate', 'C36H60O2', NULL),
(1, 'бета-каротин', 'beta-carotene', 'C40H56', 'Провітамін А'),
(1, 'змішані каротиноїди', 'mixed carotenoids', NULL, 'Природні каротиноїди'),

-- Вітамін B1 (ID=2)
(2, 'тіаміну гідрохлорид', 'thiamin hydrochloride', 'C12H17ClN4OS·HCl', NULL),
(2, 'тіаміну мононітрат', 'thiamin mononitrate', 'C12H17N5O4S', NULL),

-- Вітамін B2 (ID=3)
(3, 'рибофлавін', 'riboflavin', 'C17H20N4O6', NULL),
(3, 'рибофлавін-5-фосфат натрію', 'riboflavin-5-phosphate sodium', NULL, NULL),

-- Вітамін B3 (ID=4)
(4, 'нікотинова кислота', 'nicotinic acid', 'C6H5NO2', NULL),
(4, 'нікотинамід', 'nicotinamide', 'C6H6N2O', NULL),

-- Вітамін B5 (ID=5)
(5, 'D-пантотенат кальцію', 'calcium D-pantothenate', 'C18H32CaN2O10', NULL),
(5, 'D-пантотенова кислота', 'D-pantothenic acid', 'C9H17NO5', NULL),

-- Вітамін B6 (ID=6)
(6, 'піридоксину гідрохлорид', 'pyridoxine hydrochloride', 'C8H11NO3·HCl', NULL),
(6, 'піридоксаль-5-фосфат', 'pyridoxal-5-phosphate', NULL, 'Активна форма'),

-- Вітамін B9 (ID=7)
(7, 'птероїлмоноглутамінова кислота', 'pteroylmonoglutamic acid', 'C19H19N7O6', 'Фолієва кислота'),
(7, 'кальцію L-метилфолат', 'calcium L-methylfolate', NULL, 'Метилфолат'),
(7, '5-метилтетрагідрофолат', '5-methyltetrahydrofolate', NULL, 'Активна форма фолату'),

-- Вітамін B12 (ID=8)
(8, 'ціанокобаламін', 'cyanocobalamin', 'C63H88CoN14O14P', NULL),
(8, 'метилкобаламін', 'methylcobalamin', NULL, 'Активна форма'),
(8, 'аденозилкобаламін', 'adenosylcobalamin', NULL, 'Активна форма'),

-- Біотин (ID=9)
(9, 'D-біотин', 'D-biotin', 'C10H16N2O3S', NULL),

-- Вітамін C (ID=10)
(10, 'L-аскорбінова кислота', 'L-ascorbic acid', 'C6H8O6', NULL),
(10, 'натрію L-аскорбат', 'sodium L-ascorbate', 'C6H7NaO6', NULL),
(10, 'кальцію L-аскорбат', 'calcium L-ascorbate', NULL, NULL),
(10, 'калію L-аскорбат', 'potassium L-ascorbate', NULL, NULL),

-- Вітамін D (ID=11)
(11, 'ергокальциферол', 'ergocalciferol', 'C28H44O', 'Вітамін D2'),
(11, 'холекальциферол', 'cholecalciferol', 'C27H44O', 'Вітамін D3'),

-- Вітамін E (ID=12)
(12, 'D-альфа-токоферол', 'D-alpha-tocopherol', 'C29H50O2', NULL),
(12, 'DL-альфа-токоферол', 'DL-alpha-tocopherol', NULL, 'Синтетичний'),
(12, 'D-альфа-токоферилу ацетат', 'D-alpha-tocopheryl acetate', 'C31H52O3', NULL),
(12, 'змішані токофероли', 'mixed tocopherols', NULL, 'Природні'),

-- Вітамін K (ID=13)
(13, 'філохінон', 'phylloquinone', 'C31H46O2', 'Вітамін K1'),
(13, 'менахінон', 'menaquinone', NULL, 'Вітамін K2'),

-- МІНЕРАЛИ

-- Кальцій (ID=14)
(14, 'кальцію карбонат', 'calcium carbonate', 'CaCO3', NULL),
(14, 'кальцію цитрат', 'calcium citrate', 'Ca3(C6H5O7)2', NULL),
(14, 'кальцію лактат', 'calcium lactate', 'C6H10CaO6', NULL),
(14, 'кальцію глюконат', 'calcium gluconate', 'C12H22CaO14', NULL),
(14, 'кальцію фосфат', 'calcium phosphate', 'Ca3(PO4)2', NULL),
(14, 'кальцію бісглицинат', 'calcium bisglycinate', NULL, 'Хелатна форма'),

-- Магній (ID=15)
(15, 'магнію оксид', 'magnesium oxide', 'MgO', NULL),
(15, 'магнію цитрат', 'magnesium citrate', 'Mg3(C6H5O7)2', NULL),
(15, 'магнію бісглицинат', 'magnesium bisglycinate', NULL, 'Хелатна форма'),
(15, 'магнію малат', 'magnesium malate', NULL, NULL),
(15, 'магнію L-треонат', 'magnesium L-threonate', NULL, NULL),
(15, 'магнію хлорид', 'magnesium chloride', 'MgCl2', NULL),
(15, 'магнію лактат', 'magnesium lactate', NULL, NULL),

-- Залізо (ID=16)
(16, 'заліза сульфат', 'ferrous sulfate', 'FeSO4', NULL),
(16, 'заліза фумарат', 'ferrous fumarate', 'C4H2FeO4', NULL),
(16, 'заліза глюконат', 'ferrous gluconate', 'C12H22FeO14', NULL),
(16, 'заліза бісглицинат', 'ferrous bisglycinate', NULL, 'Хелатна форма'),
(16, 'заліза цитрат', 'ferrous citrate', NULL, NULL),

-- Цинк (ID=17)
(17, 'цинку оксид', 'zinc oxide', 'ZnO', NULL),
(17, 'цинку цитрат', 'zinc citrate', 'Zn3(C6H5O7)2', NULL),
(17, 'цинку глюконат', 'zinc gluconate', 'C12H22O14Zn', NULL),
(17, 'цинку піколінат', 'zinc picolinate', NULL, NULL),
(17, 'цинку бісглицинат', 'zinc bisglycinate', NULL, 'Хелатна форма'),
(17, 'цинку сульфат', 'zinc sulfate', 'ZnSO4', NULL),

-- Мідь (ID=18)
(18, 'міді глюконат', 'copper gluconate', 'C12H22CuO14', NULL),
(18, 'міді сульфат', 'copper sulfate', 'CuSO4', NULL),
(18, 'міді цитрат', 'copper citrate', NULL, NULL),
(18, 'міді бісглицинат', 'copper bisglycinate', NULL, 'Хелатна форма'),

-- Марганець (ID=19)
(19, 'марганцю глюконат', 'manganese gluconate', 'C12H22MnO14', NULL),
(19, 'марганцю сульфат', 'manganese sulfate', 'MnSO4', NULL),
(19, 'марганцю цитрат', 'manganese citrate', NULL, NULL),

-- Селен (ID=20)
(20, 'селенометіонін', 'selenomethionine', 'C5H11NO2Se', 'Органічна форма'),
(20, 'натрію селеніт', 'sodium selenite', 'Na2SeO3', NULL),
(20, 'натрію селенат', 'sodium selenate', 'Na2SeO4', NULL),
(20, 'селен-збагачені дріжджі', 'selenium-enriched yeast', NULL, NULL),

-- Йод (ID=21)
(21, 'калію йодид', 'potassium iodide', 'KI', NULL),
(21, 'калію йодат', 'potassium iodate', 'KIO3', NULL),
(21, 'натрію йодид', 'sodium iodide', 'NaI', NULL),

-- Хром (ID=22)
(22, 'хрому піколінат', 'chromium picolinate', NULL, NULL),
(22, 'хрому хлорид', 'chromium chloride', 'CrCl3', NULL),

-- Молібден (ID=23)
(23, 'молібдену натрію', 'sodium molybdate', 'Na2MoO4', NULL),

-- Фосфор (ID=24)
(24, 'кальцію фосфат', 'calcium phosphate', 'Ca3(PO4)2', NULL),
(24, 'натрію фосфат', 'sodium phosphate', NULL, NULL),

-- Калій (ID=25)
(25, 'калію хлорид', 'potassium chloride', 'KCl', NULL),
(25, 'калію цитрат', 'potassium citrate', NULL, NULL),
(25, 'калію глюконат', 'potassium gluconate', NULL, NULL),

-- Бор (ID=26)
(26, 'борна кислота', 'boric acid', 'H3BO3', NULL),
(26, 'натрію борат', 'sodium borate', 'Na2B4O7', NULL),

-- Кремній (ID=27)
(27, 'діоксид кремнію', 'silicon dioxide', 'SiO2', NULL),

-- Ванадій (ID=28)
(28, 'ванадилсульфат', 'vanadyl sulfate', 'VOSO4', NULL);

-- Максимальні дози з українського законодавства (7 записів)
INSERT INTO max_doses_table1 (substance_name_ua, substance_name_en, max_dose_value, max_dose_unit, notes) VALUES
('Вітамін А', 'Vitamin A', 800.00, 'мкг RE', 'Максимум для готової форми ретинолу (не застосовується до каротиноїдів)'),
('Вітамін D', 'Vitamin D', 50.00, 'мкг', 'Максимум для дорослих'),
('Вітамін E', 'Vitamin E', 300.00, 'мг α-TE', 'Максимум для синтетичного альфа-токоферолу'),
('Фолієва кислота', 'Folic acid', 1000.00, 'мкг', 'Максимум для синтетичної фолієвої кислоти'),
('Магній', 'Magnesium', 250.00, 'мг', 'Максимум з добавок (легкозасвоювані солі магнію)'),
('Цинк', 'Zinc', 25.00, 'мг', 'Максимум для дорослих'),
('Селен', 'Selenium', 300.00, 'мкг', 'Максимум для дорослих');

-- =====================================================
-- КІНЕЦЬ МІГРАЦІЇ
-- =====================================================
-- Створено: 4 таблиці, 28 речовин, 80+ форм, 7 максимальних доз
-- Готово до використання в LabelCheck UA системі
-- EFSA ліміти будуть додані після дослідження
