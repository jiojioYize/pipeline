-- ============================================================
-- english_reading 数据库种子数据
-- 基于 TED / TED-Ed 演讲资源
-- 生成日期: 2026-03-21
-- ============================================================
-- 使用说明：
--   1. audio_url 字段使用占位符，需替换为实际存储地址
--   2. total_duration 为预估值（秒），需根据实际音频校准
--   3. word_count 为预估值，需根据实际文本用工具校准
--   4. article_segments 由 pipeline.py 脚本自动生成
-- ============================================================

USE `english_reading`;

-- ============================================================
-- 1. TAGS 标签表（先插入，后续关联需要 tag_id）
-- ============================================================

INSERT INTO `tags` (`tag_id`, `name`, `slug`) VALUES
(1,  'Bridge Engineering',     'bridge-engineering'),
(2,  'Structural Design',      'structural-design'),
(3,  'Urban Planning',         'urban-planning'),
(4,  'Construction',           'construction'),
(5,  'Algorithm',              'algorithm'),
(6,  'Artificial Intelligence','artificial-intelligence'),
(7,  'Cybersecurity',          'cybersecurity'),
(8,  'Quantum Computing',      'quantum-computing'),
(9,  'Data Science',           'data-science'),
(10, 'Calculus',               'calculus'),
(11, 'Probability',            'probability'),
(12, 'Geometry',               'geometry'),
(13, 'Applied Mathematics',    'applied-mathematics'),
(14, 'Robotics',               'robotics'),
(15, 'Materials Science',      'materials-science'),
(16, 'Thermodynamics',         'thermodynamics'),
(17, '3D Printing',            '3d-printing'),
(18, 'Autonomous Vehicles',    'autonomous-vehicles'),
(19, 'Transportation Systems', 'transportation-systems'),
(20, 'Aerodynamics',           'aerodynamics'),
(21, 'Sustainability',         'sustainability'),
(22, 'History of Engineering', 'history-of-engineering'),
(23, 'Innovation',             'innovation'),
(24, 'Ethics in Technology',   'ethics-in-technology'),
(25, 'Machine Learning',       'machine-learning');

-- ============================================================
-- 2. ARTICLES 文章表
-- ============================================================
-- 命名规则：
--   来源标注: [TED-Ed] = TED-Ed 动画短片, [TED] = TED 主舞台/TEDx 演讲
--   难度说明: Easy = TED-Ed 动画 (4-6min)
--            Intermediate = 通俗 TED Talk (8-15min)
--            Advanced = 技术深度较高的 TED Talk (10-18min)
-- ============================================================

-- -----------------------------------------------------------
-- 2.1 Civil Engineering（7 篇）
-- -----------------------------------------------------------

INSERT INTO `articles` (`article_id`, `subject`, `title`, `slug`, `audio_url`, `author`, `source`, `level`, `accent`, `total_duration`, `resource_type`, `word_count`) VALUES

-- Easy × 2
(1, 'Civil Engineering',
 'Building the Impossible: Golden Gate Bridge',
 'building-the-impossible-golden-gate-bridge',
 'https://your-storage.com/audio/ce/golden-gate-bridge.mp3',
 'Alex Gendler', 'TED-Ed', 'Easy', 'US', 305, 'audio', 820),

(2, 'Civil Engineering',
 'One of the Most Epic Engineering Feats in History',
 'epic-engineering-building-the-brooklyn-bridge',
 'https://your-storage.com/audio/ce/brooklyn-bridge.mp3',
 'Alex Gendler', 'TED-Ed', 'Easy', 'US', 290, 'audio', 780),

-- Intermediate × 2
(3, 'Civil Engineering',
 'How the World\'s Longest Underwater Tunnel Was Built',
 'worlds-longest-underwater-tunnel',
 'https://your-storage.com/audio/ce/underwater-tunnel.mp3',
 'Alex Gendler', 'TED-Ed', 'Intermediate', 'US', 310, 'audio', 850),

(4, 'Civil Engineering',
 'Bridges Should Be Beautiful',
 'bridges-should-be-beautiful',
 'https://your-storage.com/audio/ce/bridges-beautiful.mp3',
 'Ian Firth', 'TED', 'Intermediate', 'UK', 720, 'audio', 2200),

-- Advanced × 3
(5, 'Civil Engineering',
 'Architecture That\'s Built to Heal',
 'architecture-built-to-heal',
 'https://your-storage.com/audio/ce/architecture-heal.mp3',
 'Michael Murphy', 'TED', 'Advanced', 'US', 780, 'audio', 2400),

(6, 'Civil Engineering',
 '4 Ways to Make a City More Walkable',
 'four-ways-to-make-city-more-walkable',
 'https://your-storage.com/audio/ce/walkable-city.mp3',
 'Jeff Speck', 'TED', 'Advanced', 'US', 1080, 'audio', 3200),

(7, 'Civil Engineering',
 'How Megacities Are Changing the Map of the World',
 'megacities-changing-map-of-world',
 'https://your-storage.com/audio/ce/megacities.mp3',
 'Parag Khanna', 'TED', 'Advanced', 'US', 1140, 'audio', 3400),

-- -----------------------------------------------------------
-- 2.2 Mathematics（6 篇）
-- -----------------------------------------------------------

-- Easy × 2
(8, 'Mathematics',
 'Where Do Math Symbols Come From?',
 'where-do-math-symbols-come-from',
 'https://your-storage.com/audio/math/math-symbols.mp3',
 'John David Walters', 'TED-Ed', 'Easy', 'US', 280, 'audio', 750),

(9, 'Mathematics',
 'The Magic of Fibonacci Numbers',
 'the-magic-of-fibonacci-numbers',
 'https://your-storage.com/audio/math/fibonacci-numbers.mp3',
 'Arthur Benjamin', 'TED', 'Easy', 'US', 370, 'audio', 1000),

-- Intermediate × 2
(10, 'Mathematics',
 'The Math and Magic of Origami',
 'the-math-and-magic-of-origami',
 'https://your-storage.com/audio/math/origami-math.mp3',
 'Robert Lang', 'TED', 'Intermediate', 'US', 960, 'audio', 2800),

(11, 'Mathematics',
 'How Math Is Our Real Sixth Sense',
 'how-math-is-our-real-sixth-sense',
 'https://your-storage.com/audio/math/math-sixth-sense.mp3',
 'Eddie Woo', 'TED', 'Intermediate', 'UK', 810, 'audio', 2400),

-- Advanced × 3
(12, 'Mathematics',
 'The Beautiful Math Behind the World\'s Ugliest Music',
 'beautiful-math-ugliest-music',
 'https://your-storage.com/audio/math/ugliest-music.mp3',
 'Scott Rickard', 'TED', 'Advanced', 'US', 420, 'audio', 1200),

(13, 'Mathematics',
 'Does Math Have a Major Flaw?',
 'does-math-have-a-major-flaw',
 'https://your-storage.com/audio/math/math-major-flaw.mp3',
 'Jacqueline Doan and Alex Kazachek', 'TED-Ed', 'Advanced', 'US', 310, 'audio', 860),

-- -----------------------------------------------------------
-- 2.3 Computer Science（7 篇）
-- -----------------------------------------------------------

-- Easy × 2
(14, 'Computer Science',
 'The Birth of the Computer',
 'the-birth-of-the-computer',
 'https://your-storage.com/audio/cs/birth-of-computer.mp3',
 'George Dyson', 'TED', 'Easy', 'US', 360, 'audio', 980),

(15, 'Computer Science',
 'The Greatest Machine That Never Was',
 'greatest-machine-that-never-was',
 'https://your-storage.com/audio/cs/greatest-machine.mp3',
 'John Graham-Cumming', 'TED', 'Easy', 'UK', 420, 'audio', 1100),

-- Intermediate × 2
(16, 'Computer Science',
 'The Promise of Quantum Computers',
 'the-promise-of-quantum-computers',
 'https://your-storage.com/audio/cs/quantum-computers.mp3',
 'Matt Langione', 'TED', 'Intermediate', 'US', 600, 'audio', 1800),

(17, 'Computer Science',
 'The Era of Blind Faith in Big Data Must End',
 'blind-faith-big-data-must-end',
 'https://your-storage.com/audio/cs/big-data-blind-faith.mp3',
 'Cathy O\'Neil', 'TED', 'Intermediate', 'US', 780, 'audio', 2300),

-- Advanced × 3
(18, 'Computer Science',
 'What a Driverless World Could Look Like',
 'what-a-driverless-world-could-look-like',
 'https://your-storage.com/audio/cs/driverless-world.mp3',
 'Wanis Kabbaj', 'TED', 'Advanced', 'US', 720, 'audio', 2100),

(19, 'Computer Science',
 'How We Can Protect Truth in the Age of Misinformation',
 'protect-truth-age-misinformation',
 'https://your-storage.com/audio/cs/protect-truth.mp3',
 'Sinan Aral', 'TED', 'Advanced', 'US', 840, 'audio', 2500),

(20, 'Computer Science',
 'How AI Could Empower Any Business',
 'how-ai-could-empower-any-business',
 'https://your-storage.com/audio/cs/ai-empower-business.mp3',
 'Andrew Ng', 'TED', 'Advanced', 'US', 660, 'audio', 1900),

-- -----------------------------------------------------------
-- 2.4 Mechanical Engineering（6 篇）
-- -----------------------------------------------------------

-- Easy × 2
(21, 'Mechanical Engineering',
 'Why Don\'t Perpetual Motion Machines Ever Work?',
 'why-dont-perpetual-motion-machines-work',
 'https://your-storage.com/audio/me/perpetual-motion.mp3',
 'Netta Schramm', 'TED-Ed', 'Easy', 'US', 280, 'audio', 750),

(22, 'Mechanical Engineering',
 'Metal That Breathes',
 'metal-that-breathes',
 'https://your-storage.com/audio/me/metal-breathes.mp3',
 'Doris Kim Sung', 'TED', 'Easy', 'US', 360, 'audio', 980),

-- Intermediate × 2
(23, 'Mechanical Engineering',
 'Play with Smart Materials',
 'play-with-smart-materials',
 'https://your-storage.com/audio/me/smart-materials.mp3',
 'Catarina Mota', 'TED', 'Intermediate', 'US', 570, 'audio', 1700),

(24, 'Mechanical Engineering',
 'The Unexpected Beauty of Everyday Sounds',
 'unexpected-beauty-everyday-sounds',
 'https://your-storage.com/audio/me/everyday-sounds.mp3',
 'Meklit Hadero', 'TED', 'Intermediate', 'US', 480, 'audio', 1400),

-- Advanced × 2
(25, 'Mechanical Engineering',
 'Can We Make Things That Make Themselves?',
 'can-we-make-things-that-make-themselves',
 'https://your-storage.com/audio/me/4d-printing.mp3',
 'Skylar Tibbits', 'TED', 'Advanced', 'US', 480, 'audio', 1400),

(26, 'Mechanical Engineering',
 'How to Discover the Materials of the Future',
 'discover-materials-of-the-future',
 'https://your-storage.com/audio/me/materials-future.mp3',
 'Taylor Sparks', 'TED', 'Advanced', 'US', 660, 'audio', 1900),

-- -----------------------------------------------------------
-- 2.5 Mechanical Engineering with Transportation（6 篇）
-- -----------------------------------------------------------

-- Easy × 2
(27, 'Mechanical Engineering with Transportation',
 'How Do Self-Driving Cars "See"?',
 'how-do-self-driving-cars-see',
 'https://your-storage.com/audio/met/self-driving-see.mp3',
 'Sajan Saini', 'TED-Ed', 'Easy', 'US', 280, 'audio', 750),

(28, 'Mechanical Engineering with Transportation',
 'The Ethical Dilemma of Self-Driving Cars',
 'ethical-dilemma-self-driving-cars',
 'https://your-storage.com/audio/met/self-driving-ethics.mp3',
 'Patrick Lin', 'TED-Ed', 'Easy', 'US', 260, 'audio', 700),

-- Intermediate × 2
(29, 'Mechanical Engineering with Transportation',
 'What a Driverless World Could Look Like',
 'driverless-world-transportation',
 'https://your-storage.com/audio/met/driverless-world-transport.mp3',
 'Wanis Kabbaj', 'TED', 'Intermediate', 'US', 720, 'audio', 2100),

(30, 'Mechanical Engineering with Transportation',
 'Your Self-Driving Robotaxi Is Almost Here',
 'self-driving-robotaxi-almost-here',
 'https://your-storage.com/audio/met/robotaxi.mp3',
 'Aicha Evans', 'TED', 'Intermediate', 'US', 600, 'audio', 1800),

-- Advanced × 2
(31, 'Mechanical Engineering with Transportation',
 'How Autonomous Vehicles Will Transform Our Cities',
 'autonomous-vehicles-transform-cities',
 'https://your-storage.com/audio/met/av-transform-cities.mp3',
 'Nico Larco', 'TED', 'Advanced', 'US', 780, 'audio', 2300),

(32, 'Mechanical Engineering with Transportation',
 'How Self-Driving Cars Work',
 'how-self-driving-cars-work',
 'https://your-storage.com/audio/met/self-driving-how.mp3',
 'David Silver', 'TED', 'Advanced', 'US', 540, 'audio', 1600);


-- ============================================================
-- 3. ARTICLE_TAGS 关联表（每篇 3-5 个标签）
-- ============================================================

INSERT INTO `article_tags` (`article_id`, `tag_id`) VALUES
-- Civil Engineering
(1, 1), (1, 2), (1, 4), (1, 22),           -- Golden Gate Bridge
(2, 1), (2, 2), (2, 4), (2, 22),           -- Brooklyn Bridge
(3, 4), (3, 22), (3, 2),                    -- Underwater Tunnel
(4, 1), (4, 2), (4, 23),                    -- Bridges Beautiful
(5, 3), (5, 4), (5, 21), (5, 23),          -- Architecture Heal
(6, 3), (6, 21), (6, 19),                   -- Walkable City
(7, 3), (7, 19), (7, 23),                   -- Megacities

-- Mathematics
(8, 13), (8, 22), (8, 12),                  -- Math Symbols
(9, 13), (9, 12), (9, 23),                  -- Fibonacci
(10, 12), (10, 13), (10, 23),               -- Origami Math
(11, 13), (11, 12), (11, 23),               -- Math Sixth Sense
(12, 13), (12, 23), (12, 5),                -- Ugliest Music
(13, 13), (13, 11), (13, 23),               -- Math Flaw

-- Computer Science
(14, 5), (14, 22), (14, 23),                -- Birth of Computer
(15, 5), (15, 22), (15, 23),                -- Greatest Machine
(16, 8), (16, 5), (16, 23),                 -- Quantum Computers
(17, 9), (17, 5), (17, 24), (17, 25),      -- Big Data
(18, 18), (18, 6), (18, 19), (18, 23),     -- Driverless World
(19, 6), (19, 9), (19, 24),                 -- Misinformation
(20, 6), (20, 25), (20, 23),                -- AI Empower

-- Mechanical Engineering
(21, 16), (21, 23), (21, 22),               -- Perpetual Motion
(22, 15), (22, 23), (22, 21),               -- Metal Breathes
(23, 15), (23, 23), (23, 14),               -- Smart Materials
(24, 15), (24, 16), (24, 23),               -- Everyday Sounds
(25, 17), (25, 14), (25, 23), (25, 15),    -- 4D Printing
(26, 15), (26, 23), (26, 6),                -- Materials Future

-- Mechanical Engineering with Transportation
(27, 18), (27, 6), (27, 19),                -- Self-Driving See
(28, 18), (28, 24), (28, 19),               -- Self-Driving Ethics
(29, 18), (29, 19), (29, 6), (29, 23),     -- Driverless World Transport
(30, 18), (30, 19), (30, 14), (30, 23),    -- Robotaxi
(31, 18), (31, 3), (31, 19), (31, 23),     -- AV Transform Cities
(32, 18), (32, 6), (32, 5), (32, 19);      -- Self-Driving How


-- ============================================================
-- 4. USERS 用户表（测试数据）
-- ============================================================

INSERT INTO `users` (`user_id`, `name`, `email`, `password`) VALUES
(1, 'Alice Zhang',   'alice.zhang@example.com',   '$2b$12$LJ3m4ys2Kq9XjYZ1a2b3cOeDfGhIjKlMnOpQrStUvWxYz012345'),
(2, 'Bob Chen',      'bob.chen@example.com',      '$2b$12$AB3m4ys2Kq9XjYZ1a2b3cOeDfGhIjKlMnOpQrStUvWxYz054321'),
(3, 'Carol Liu',     'carol.liu@example.com',     '$2b$12$CD3m4ys2Kq9XjYZ1a2b3cOeDfGhIjKlMnOpQrStUvWxYz067890'),
(4, 'David Wang',    'david.wang@example.com',    '$2b$12$EF3m4ys2Kq9XjYZ1a2b3cOeDfGhIjKlMnOpQrStUvWxYz098765'),
(5, 'Eva Li',        'eva.li@example.com',        '$2b$12$GH3m4ys2Kq9XjYZ1a2b3cOeDfGhIjKlMnOpQrStUvWxYz011223');


-- ============================================================
-- 5. TED 演讲 URL 参考表（非数据库表，仅供团队操作参考）
-- ============================================================
-- 以下信息用于 pipeline.py 下载音频和字幕
-- 格式: article_id | TED URL | YouTube 搜索关键词
-- ============================================================

/*
REFERENCE - TED Talk URLs for pipeline.py:

-- Civil Engineering
1  | https://www.ted.com/talks/alex_gendler_building_the_impossible_golden_gate_bridge
2  | https://www.ted.com/talks/alex_gendler_epic_engineering_building_the_brooklyn_bridge
3  | https://www.ted.com/talks/alex_gendler_how_the_world_s_longest_underwater_tunnel_was_built
4  | https://www.ted.com/talks/ian_firth_bridges_should_be_beautiful
5  | https://www.ted.com/talks/michael_murphy_architecture_that_s_built_to_heal
6  | https://www.ted.com/talks/jeff_speck_4_ways_to_make_a_city_more_walkable
7  | https://www.ted.com/talks/parag_khanna_how_megacities_are_changing_the_map_of_the_world

-- Mathematics
8  | https://www.ted.com/talks/john_david_walters_where_do_math_symbols_come_from
9  | https://www.ted.com/talks/arthur_benjamin_the_magic_of_fibonacci_numbers
10 | https://www.ted.com/talks/robert_lang_the_math_and_magic_of_origami
11 | https://www.ted.com/talks/eddie_woo_how_math_is_our_real_sixth_sense
12 | https://www.ted.com/talks/scott_rickard_the_beautiful_math_behind_the_world_s_ugliest_music
13 | https://www.ted.com/talks/jacqueline_doan_and_alex_kazachek_does_math_have_a_major_flaw

-- Computer Science
14 | https://www.ted.com/talks/george_dyson_the_birth_of_the_computer
15 | https://www.ted.com/talks/john_graham_cumming_the_greatest_machine_that_never_was
16 | https://www.ted.com/talks/matt_langione_the_promise_of_quantum_computers
17 | https://www.ted.com/talks/cathy_o_neil_the_era_of_blind_faith_in_big_data_must_end
18 | https://www.ted.com/talks/wanis_kabbaj_what_a_driverless_world_could_look_like
19 | https://www.ted.com/talks/sinan_aral_how_we_can_protect_truth_in_the_age_of_misinformation
20 | https://www.ted.com/talks/andrew_ng_how_ai_could_empower_any_business

-- Mechanical Engineering
21 | https://www.ted.com/talks/netta_schramm_why_don_t_perpetual_motion_machines_ever_work
22 | https://www.ted.com/talks/doris_kim_sung_metal_that_breathes
23 | https://www.ted.com/talks/catarina_mota_play_with_smart_materials
24 | https://www.ted.com/talks/meklit_hadero_the_unexpected_beauty_of_everyday_sounds
25 | https://www.ted.com/talks/skylar_tibbits_can_we_make_things_that_make_themselves
26 | https://www.ted.com/talks/dr_taylor_sparks_how_to_discover_the_materials_of_the_future_in_30_seconds_or_less

-- Mechanical Engineering with Transportation
27 | https://www.ted.com/talks/sajan_saini_how_do_self_driving_cars_see
28 | https://www.ted.com/talks/patrick_lin_the_ethical_dilemma_of_self_driving_cars
29 | https://www.ted.com/talks/wanis_kabbaj_what_a_driverless_world_could_look_like
30 | https://www.ted.com/talks/aicha_evans_your_self_driving_robotaxi_is_almost_here
31 | https://www.ted.com/talks/nico_larco_how_will_autonomous_vehicles_transform_our_cities
32 | https://www.ted.com/talks/david_silver_how_self_driving_cars_work
*/
