-- =====================================================
-- SUPABASE MIGRATION: Additional Substances Database Schema
-- =====================================================
-- Створення 5 таблиць для додаткових речовин у дієтичних добавках
-- Автор: LabelCheck UA Team
-- Дата: 2025-01-22
-- Версія: 1.0

-- =====================================================
-- ТАБЛИЦЯ 1: allowed_plants
-- =====================================================
-- Дозволені рослини (Додаток 3, Розділ I)

CREATE TABLE allowed_plants (
    id SERIAL PRIMARY KEY,
    botanical_name_lat VARCHAR(300) NOT NULL UNIQUE,
    botanical_family_ua VARCHAR(200),
    botanical_family_lat VARCHAR(200),
    common_name_ua VARCHAR(300),
    plant_part_ua VARCHAR(200), -- частина рослини (корінь, листя, плід)
    plant_part_lat VARCHAR(200),
    regulatory_source VARCHAR(100) DEFAULT 'Проєкт Змін до Наказу №1114, Додаток 3, Розділ I',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Індекси
CREATE INDEX idx_plants_botanical_name ON allowed_plants(botanical_name_lat);
CREATE INDEX idx_plants_common_name ON allowed_plants(common_name_ua);
CREATE INDEX idx_plants_family ON allowed_plants(botanical_family_lat);

-- =====================================================
-- ТАБЛИЦЯ 2: amino_acids
-- =====================================================
-- Амінокислоти (Додаток 3, Розділ III)

CREATE TABLE amino_acids (
    id SERIAL PRIMARY KEY,
    amino_acid_name_ua VARCHAR(200) NOT NULL UNIQUE,
    amino_acid_name_en VARCHAR(200) NOT NULL,
    max_daily_dose DECIMAL(10, 2), -- г/день
    unit VARCHAR(20) DEFAULT 'г/день',
    is_essential BOOLEAN DEFAULT FALSE, -- незамінна амінокислота
    regulatory_source VARCHAR(100) DEFAULT 'Проєкт Змін до Наказу №1114, Додаток 3, Розділ III',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Індекс
CREATE INDEX idx_amino_acids_name ON amino_acids(amino_acid_name_en);

-- =====================================================
-- ТАБЛИЦЯ 3: other_substances
-- =====================================================
-- Інші речовини (Додаток 3, Розділ IV)

CREATE TABLE other_substances (
    id SERIAL PRIMARY KEY,
    substance_name_ua VARCHAR(300) NOT NULL,
    substance_name_en VARCHAR(300) NOT NULL,
    category VARCHAR(100), -- 'fatty_acid', 'coenzyme', 'antioxidant', 'fiber', 'other'
    max_daily_dose DECIMAL(10, 2),
    unit VARCHAR(20),
    regulatory_source VARCHAR(100) DEFAULT 'Проєкт Змін до Наказу №1114, Додаток 3, Розділ IV',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(substance_name_en, category)
);

-- Індекс
CREATE INDEX idx_other_substances_category ON other_substances(category);
CREATE INDEX idx_other_substances_name ON other_substances(substance_name_en);

-- =====================================================
-- ТАБЛИЦЯ 4: microorganisms
-- =====================================================
-- Мікроорганізми / Пробіотики (Додаток 3, Розділ V)

CREATE TABLE microorganisms (
    id SERIAL PRIMARY KEY,
    genus VARCHAR(100) NOT NULL, -- рід (Lactobacillus, Bifidobacterium)
    species VARCHAR(200) NOT NULL, -- вид
    strain VARCHAR(200), -- штам (необов'язково)
    category VARCHAR(50) DEFAULT 'probiotic',
    regulatory_source VARCHAR(100) DEFAULT 'Проєкт Змін до Наказу №1114, Додаток 3, Розділ V',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(genus, species, strain)
);

-- Індекс
CREATE INDEX idx_microorganisms_genus ON microorganisms(genus);

-- =====================================================
-- ТАБЛИЦЯ 5: banned_substances
-- =====================================================
-- Заборонені речовини

CREATE TABLE banned_substances (
    id SERIAL PRIMARY KEY,
    substance_name_ua VARCHAR(300) NOT NULL UNIQUE,
    substance_name_en VARCHAR(300) NOT NULL,
    reason TEXT, -- причина заборони
    regulatory_source VARCHAR(100) DEFAULT 'Проєкт Змін до Наказу №1114, Додаток 3',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Індекс
CREATE INDEX idx_banned_substances_name ON banned_substances(substance_name_en);

-- =====================================================
-- ДАНІ ДЛЯ ЗАВАНТАЖЕННЯ
-- =====================================================

-- ВАЖЛИВО: allowed_plants створюється порожньою
-- Дані будуть завантажені через CSV імпорт (626 рослин)
-- CSV файл буде надано окремо

-- Амінокислоти (29 записів)
INSERT INTO amino_acids (amino_acid_name_ua, amino_acid_name_en, max_daily_dose, is_essential, notes) VALUES
-- НЕЗАМІННІ АМІНОКИСЛОТИ
('L-валін', 'L-Valine', 5.00, TRUE, 'BCAA'),
('L-ізолейцин', 'L-Isoleucine', 5.00, TRUE, 'BCAA'),
('L-лейцин', 'L-Leucine', 5.00, TRUE, 'BCAA'),
('L-лізин', 'L-Lysine', 6.00, TRUE, NULL),
('L-метіонін', 'L-Methionine', 3.00, TRUE, NULL),
('L-фенілаланін', 'L-Phenylalanine', 5.00, TRUE, NULL),
('L-треонін', 'L-Threonine', 4.00, TRUE, NULL),
('L-триптофан', 'L-Tryptophan', 2.00, TRUE, 'Попередник серотоніну'),

-- УМОВНО-НЕЗАМІННІ
('L-аргінін', 'L-Arginine', 6.00, FALSE, 'Попередник NO'),
('L-гістидин', 'L-Histidine', 4.00, FALSE, NULL),
('L-тирозин', 'L-Tyrosine', 5.00, FALSE, 'Попередник дофаміну'),
('L-цистеїн', 'L-Cysteine', 1.50, FALSE, 'Антиоксидант'),

-- ЗАМІННІ АМІНОКИСЛОТИ
('L-аланін', 'L-Alanine', NULL, FALSE, 'Немає обмежень від EFSA'),
('L-аспарагін', 'L-Asparagine', NULL, FALSE, NULL),
('L-аспарагінова кислота', 'L-Aspartic acid', NULL, FALSE, NULL),
('Гліцин', 'Glycine', NULL, FALSE, 'Найпростіша амінокислота'),
('L-глутамін', 'L-Glutamine', NULL, FALSE, 'Найпоширеніша в організмі'),
('L-глутамінова кислота', 'L-Glutamic acid', NULL, FALSE, NULL),
('L-пролін', 'L-Proline', NULL, FALSE, NULL),
('L-серин', 'L-Serine', NULL, FALSE, NULL),

-- СПЕЦІАЛЬНІ АМІНОКИСЛОТИ ТА ПОХІДНІ
('L-карнітин', 'L-Carnitine', 2.00, FALSE, 'EFSA Safe Level'),
('Ацетил-L-карнітин', 'Acetyl-L-Carnitine', 2.00, FALSE, 'Форма L-карнітину'),
('Таурин', 'Taurine', 3.00, FALSE, 'Сульфоамінокислота'),
('Креатин', 'Creatine', 3.00, FALSE, 'Креатин моногідрат'),
('Бета-аланін', 'Beta-Alanine', 3.20, FALSE, 'Попередник карнозину'),
('N-ацетил-L-цистеїн', 'N-Acetyl-L-Cysteine (NAC)', 1.80, FALSE, 'Форма цистеїну'),
('L-орнітин', 'L-Ornithine', 6.00, FALSE, NULL),
('L-цитрулін', 'L-Citrulline', 6.00, FALSE, 'Попередник аргініну'),
('Гідроксипролін', 'Hydroxyproline', NULL, FALSE, 'Компонент колагену');

-- Інші речовини (30 записів)
INSERT INTO other_substances (substance_name_ua, substance_name_en, category, max_daily_dose, unit, notes) VALUES
-- ЖИРНІ КИСЛОТИ
('Омега-3 (EPA+DHA)', 'Omega-3 (EPA+DHA)', 'fatty_acid', 5.00, 'г', 'EFSA UL'),
('EPA (ейкозапентаєнова кислота)', 'EPA (Eicosapentaenoic acid)', 'fatty_acid', 5.00, 'г', 'Сумарно з DHA'),
('DHA (докозагексаєнова кислота)', 'DHA (Docosahexaenoic acid)', 'fatty_acid', 5.00, 'г', 'Сумарно з EPA'),
('ALA (альфа-ліноленова кислота)', 'ALA (Alpha-linolenic acid)', 'fatty_acid', NULL, 'г', 'Рослинна омега-3'),
('Омега-6 (лінолева кислота)', 'Omega-6 (Linoleic acid)', 'fatty_acid', NULL, 'г', NULL),
('GLA (гамма-ліноленова кислота)', 'GLA (Gamma-linolenic acid)', 'fatty_acid', NULL, 'мг', 'З олії огірочника'),
('Олеїнова кислота (омега-9)', 'Oleic acid (Omega-9)', 'fatty_acid', NULL, 'г', NULL),
('CLA (кон''югована лінолева кислота)', 'CLA (Conjugated linoleic acid)', 'fatty_acid', 3.00, 'г', NULL),

-- КОЕНЗИМИ
('Коензим Q10', 'Coenzyme Q10 (Ubiquinone)', 'coenzyme', 200.00, 'мг', 'Популярний антиоксидант'),
('Альфа-ліпоєва кислота', 'Alpha-lipoic acid', 'coenzyme', 600.00, 'мг', 'Універсальний антиоксидант'),
('PQQ (пірролохінолінхінон)', 'PQQ (Pyrroloquinoline quinone)', 'coenzyme', 20.00, 'мг', NULL),

-- КАРОТИНОЇДИ
('Бета-каротин', 'Beta-carotene', 'antioxidant', 15.00, 'мг', 'Провітамін А'),
('Лютеїн', 'Lutein', 'antioxidant', 20.00, 'мг', 'Для зору'),
('Зеаксантин', 'Zeaxanthin', 'antioxidant', 2.00, 'мг', 'Для зору'),
('Лікопін', 'Lycopene', 'antioxidant', 15.00, 'мг', 'З томатів'),
('Астаксантин', 'Astaxanthin', 'antioxidant', 12.00, 'мг', 'З мікроводоростей'),

-- ФОСФОЛІПІДИ
('Фосфатидилсерин', 'Phosphatidylserine', 'other', 300.00, 'мг', 'Для когнітивних функцій'),
('Фосфатидилхолін', 'Phosphatidylcholine', 'other', NULL, 'мг', NULL),
('Холін', 'Choline', 'other', 3500.00, 'мг', 'EFSA UL'),
('Інозитол', 'Inositol', 'other', NULL, 'мг', 'Немає UL від EFSA'),

-- ПОЛІСАХАРИДИ
('Бета-глюкани', 'Beta-glucans', 'fiber', NULL, 'г', 'З грибів або вівса'),
('Інулін', 'Inulin', 'fiber', NULL, 'г', 'Пребіотик'),

-- ІНШЕ
('Глюкозамін', 'Glucosamine', 'other', 1500.00, 'мг', 'Для суглобів'),
('Хондроїтин', 'Chondroitin', 'other', 1200.00, 'мг', 'Для суглобів'),
('MSM (метилсульфонілметан)', 'MSM (Methylsulfonylmethane)', 'other', 3000.00, 'мг', NULL),
('Гіалуронова кислота', 'Hyaluronic acid', 'other', 200.00, 'мг', NULL),
('Ресвератрол', 'Resveratrol', 'antioxidant', 150.00, 'мг', 'З винограду'),
('Кверцетин', 'Quercetin', 'antioxidant', 500.00, 'мг', 'Флавоноїд');

-- Мікроорганізми (20 записів)
INSERT INTO microorganisms (genus, species, strain, notes) VALUES
-- LACTOBACILLUS
('Lactobacillus', 'acidophilus', NULL, 'Найпопулярніший пробіотик'),
('Lactobacillus', 'casei', NULL, NULL),
('Lactobacillus', 'plantarum', NULL, NULL),
('Lactobacillus', 'rhamnosus', 'GG', 'Відомий штам LGG'),
('Lactobacillus', 'reuteri', NULL, NULL),
('Lactobacillus', 'fermentum', NULL, NULL),
('Lactobacillus', 'gasseri', NULL, NULL),
('Lactobacillus', 'salivarius', NULL, NULL),
('Lactobacillus', 'paracasei', NULL, NULL),
('Lactobacillus', 'helveticus', NULL, NULL),

-- BIFIDOBACTERIUM
('Bifidobacterium', 'bifidum', NULL, NULL),
('Bifidobacterium', 'longum', NULL, NULL),
('Bifidobacterium', 'breve', NULL, NULL),
('Bifidobacterium', 'infantis', NULL, 'Для немовлят'),
('Bifidobacterium', 'lactis', 'BB-12', 'Популярний штам'),
('Bifidobacterium', 'animalis', NULL, NULL),

-- ІНШІ КОРИСНІ БАКТЕРІЇ
('Streptococcus', 'thermophilus', NULL, 'Використовується в йогуртах'),
('Bacillus', 'coagulans', NULL, 'Спороутворюючий пробіотик'),
('Saccharomyces', 'boulardii', NULL, 'Дріжджі-пробіотик'),

-- КОМБІНАЦІЇ
('Lactococcus', 'lactis', NULL, NULL);

-- Заборонені речовини (6 записів)
INSERT INTO banned_substances (substance_name_ua, substance_name_en, reason, notes) VALUES
('Алое-емодин', 'Aloe-emodin', 'Токсичність, канцерогенність', 'І всі препарати, в яких присутня ця речовина'),
('Дантрон', 'Danthron', 'Токсичність', 'І всі препарати, в яких присутня ця речовина'),
('Емодин', 'Emodin', 'Токсичність', 'І всі препарати, в яких присутня ця речовина'),
('Епіблема', 'Epiblema', 'Небезпечна речовина', NULL),
('Стрихнін', 'Strychnine', 'Високотоксична речовина', 'Отруйна алкалоїдна речовина'),
('Йохімбін', 'Yohimbine', 'Побічні ефекти на серцево-судинну систему', 'Алкалоїд з кори йохімбе');

-- =====================================================
-- КІНЕЦЬ МІГРАЦІЇ
-- =====================================================
-- Створено: 5 таблиць
-- allowed_plants: порожня (CSV імпорт 626 рослин)
-- amino_acids: 29 записів
-- other_substances: 30 записів  
-- microorganisms: 20 записів
-- banned_substances: 6 записів
-- Готово до використання в LabelCheck UA системі
