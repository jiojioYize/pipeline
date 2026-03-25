#!/usr/bin/env python3
"""
TED 演讲数据处理流水线（SRT 字幕方案，无需 GPU）
==================================================
用法:
  python pipeline.py --mode download   # 下载音频和字幕
  python pipeline.py --mode parse      # 解析 SRT 字幕，合并为段落
  python pipeline.py --mode sql        # 补全 seed_data.sql
  python pipeline.py --mode all        # 一键执行全部步骤

前置依赖:
  pip install yt-dlp pysrt
"""

import argparse, json, os, re, subprocess, sys
from pathlib import Path

OUTPUT_DIR = Path("./ted_data")
AUDIO_DIR = OUTPUT_DIR / "audio"
SUBS_DIR = OUTPUT_DIR / "subtitles"
PARSED_DIR = OUTPUT_DIR / "parsed"
SEED_SQL_PATH = Path(__file__).parent / "seed_data.sql"

TALKS = {
    1:{"search":"TED-Ed Building the impossible Golden Gate Bridge Alex Gendler","slug":"golden-gate-bridge"},
    2:{"search":"TED-Ed epic engineering building the Brooklyn Bridge Alex Gendler","slug":"brooklyn-bridge"},
    3:{"search":"TED-Ed How the world's longest underwater tunnel was built","slug":"underwater-tunnel"},
    4:{"search":"TED Ian Firth Bridges should be beautiful","slug":"bridges-beautiful"},
    5:{"search":"TED Michael Murphy Architecture that's built to heal","slug":"architecture-heal"},
    6:{"search":"TED Jeff Speck 4 ways to make a city more walkable","slug":"walkable-city"},
    7:{"search":"TED Parag Khanna How megacities are changing the map of the world","slug":"megacities"},
    8:{"search":"https://www.youtube.com/watch?v=X_xR5Kes4Rs","slug":"math-discovered-or-invented"},
    9:{"search":"TED Arthur Benjamin the magic of Fibonacci numbers","slug":"fibonacci-numbers"},
    10:{"search":"TED Robert Lang the math and magic of origami","slug":"origami-math"},
    11:{"search":"TED Eddie Woo How math is our real sixth sense","slug":"math-sixth-sense"},
    12:{"search":"TED Scott Rickard beautiful math ugliest music","slug":"ugliest-music"},
    13:{"search":"TED-Ed Does math have a major flaw Banach-Tarski","slug":"math-major-flaw"},
    14:{"search":"TED George Dyson the birth of the computer","slug":"birth-of-computer"},
    15:{"search":"TED John Graham-Cumming the greatest machine that never was","slug":"greatest-machine"},
    16:{"search":"TED Matt Langione the promise of quantum computers","slug":"quantum-computers"},
    17:{"search":"TED Cathy O'Neil the era of blind faith in big data must end","slug":"big-data-blind-faith"},
    18:{"search":"TED Wanis Kabbaj what a driverless world could look like","slug":"driverless-world"},
    19:{"search":"TED Sinan Aral how we can protect truth in the age of misinformation","slug":"protect-truth"},
    20:{"search":"TED Andrew Ng how AI could empower any business","slug":"ai-empower-business"},
    21:{"search":"TED-Ed Why don't perpetual motion machines ever work Netta Schramm","slug":"perpetual-motion"},
    22:{"search":"TED Doris Kim Sung metal that breathes","slug":"metal-breathes"},
    23:{"search":"TED Catarina Mota play with smart materials","slug":"smart-materials"},
    24:{"search":"TED Meklit Hadero the unexpected beauty of everyday sounds","slug":"everyday-sounds"},
    25:{"search":"TED Skylar Tibbits can we make things that make themselves","slug":"4d-printing"},
    26:{"search":"https://www.youtube.com/watch?v=KAiWdme6EEM","slug":"sustainable-architecture-building-blocks"},
    27:{"search":"TED-Ed How do self-driving cars see Sajan Saini","slug":"self-driving-see"},
    28:{"search":"TED-Ed ethical dilemma of self-driving cars Patrick Lin","slug":"self-driving-ethics"},
    29:{"search":"TED Wanis Kabbaj driverless world","slug":"driverless-world-transport"},
    30:{"search":"TED Aicha Evans your self-driving robotaxi is almost here","slug":"robotaxi"},
    31:{"search":"https://www.youtube.com/watch?v=tiwVMrTLUWg","slug":"driverless-car-sees-road"},
    32:{"search":"https://www.youtube.com/watch?v=apPWr-jkTeQ","slug":"why-driverless-cars-still-bad-driving"},
}

# ====================== 步骤 1: 下载 ======================

def download_all():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SUBS_DIR.mkdir(parents=True, exist_ok=True)

    for aid, info in TALKS.items():
        slug = info["slug"]
        sq = info["search"]
        audio_path = AUDIO_DIR / f"{aid:02d}_{slug}.mp3"
        existing_srt = list(SUBS_DIR.glob(f"{aid:02d}_{slug}*.srt"))

        if audio_path.exists() and existing_srt:
            print(f"[跳过] id={aid} 已存在")
            continue

        print(f"\n{'='*60}\n[下载] id={aid} | {slug}\n{'='*60}")
        source = sq if sq.startswith("http") else f"ytsearch1:{sq}"

        if not audio_path.exists():
            try:
                subprocess.run(["yt-dlp", source, "-x", "--audio-format", "mp3",
                    "--audio-quality", "0", "-o", str(audio_path), "--no-playlist"],
                    check=True, capture_output=True, text=True)
                print(f"  ✅ 音频: {audio_path}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ 音频失败: {e.stderr[:200]}")
                continue

        if not existing_srt:
            try:
                subprocess.run(["yt-dlp", source, "--write-subs", "--write-auto-subs",
                    "--sub-lang", "en", "--sub-format", "srt", "--convert-subs", "srt",
                    "--skip-download", "-o", str(SUBS_DIR / f"{aid:02d}_{slug}"),
                    "--no-playlist"], check=True, capture_output=True, text=True)
                found = list(SUBS_DIR.glob(f"{aid:02d}_{slug}*.srt"))
                print(f"  ✅ 字幕: {found[0].name}" if found else "  ⚠️ 未找到 SRT")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️ 字幕失败: {e.stderr[:200]}")

    print(f"\n下载完成! 音频: {AUDIO_DIR}, 字幕: {SUBS_DIR}")

# ====================== 步骤 2: 解析 SRT ======================

def parse_all(
    pause_threshold=2.0,
    smart_segmentation=False,
    restore_punctuation=False,
    target_words=150,
    min_words=70,
    max_words=260,
    min_duration=12,
    max_duration=70,
    soft_pause=0.8,
):
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import pysrt
    except ImportError:
        print("❌ 请先安装: pip install pysrt"); sys.exit(1)

    for aid, info in TALKS.items():
        slug = info["slug"]
        out = PARSED_DIR / f"{aid:02d}_{slug}.json"
        if out.exists():
            print(f"[跳过] id={aid} 已解析"); continue

        srts = list(SUBS_DIR.glob(f"{aid:02d}_{slug}*.srt"))
        if not srts:
            print(f"[跳过] id={aid} 无 SRT"); continue

        # 优先人工字幕
        srt_path = srts[0]
        for f in srts:
            if "auto" not in f.name.lower():
                srt_path = f; break

        print(f"[解析] id={aid} | {srt_path.name}")
        subs = pysrt.open(str(srt_path), encoding="utf-8")

        entries = []
        for sub in subs:
            text = re.sub(r"<[^>]+>", "", sub.text.replace("\n", " ")).strip()
            if not text: continue
            s = sub.start.hours*3600 + sub.start.minutes*60 + sub.start.seconds + sub.start.milliseconds/1000
            e = sub.end.hours*3600 + sub.end.minutes*60 + sub.end.seconds + sub.end.milliseconds/1000
            entries.append({"text": text, "start": round(s,2), "end": round(e,2)})

        if not entries:
            print(f"  ⚠️ SRT 为空"); continue

        paragraphs = merge_to_paragraphs(
            entries,
            pause_threshold,
            smart_segmentation,
            restore_punctuation=restore_punctuation,
            target_words=target_words,
            min_words=min_words,
            max_words=max_words,
            min_duration=min_duration,
            max_duration=max_duration,
            soft_pause=soft_pause,
        )
        json.dump({"article_id": aid, "slug": slug, "srt_file": srt_path.name,
                    "paragraphs": paragraphs}, open(out,"w",encoding="utf-8"), indent=2, ensure_ascii=False)

        wc = sum(len(p["text"].split()) for p in paragraphs)
        print(f"  ✅ {len(paragraphs)} 段落, {wc} 词, 时长 {paragraphs[-1]['end_time']}s")

    print(f"\n解析完成! 结果: {PARSED_DIR}")


def merge_to_paragraphs(
    entries,
    pause_threshold=2.0,
    smart_segmentation=False,
    restore_punctuation=False,
    target_words=150,
    min_words=70,
    max_words=260,
    min_duration=12,
    max_duration=70,
    soft_pause=0.8,
):
    if not entries:
        return []
    groups = split_by_pause(entries, pause_threshold)
    if smart_segmentation:
        groups = rebalance_groups(
            groups,
            restore_punctuation=restore_punctuation,
            target_words=target_words,
            min_words=min_words,
            hard_max_words=max_words,
            min_duration=min_duration,
            max_duration=max_duration,
            soft_pause=soft_pause,
        )
    paragraphs = []
    for g in groups:
        text = " ".join(x["text"] for x in g).strip()
        if not text:
            continue
        paragraphs.append({
            "text": text,
            "start_time": int(round(g[0]["start"])),
            "end_time": int(round(g[-1]["end"])),
        })
    return paragraphs


def split_by_pause(entries, pause_threshold):
    groups, cur = [], [entries[0]]
    prev_end = entries[0]["end"]
    for e in entries[1:]:
        # Keep sentence integrity: only break on pause when current chunk ends a sentence.
        if e["start"] - prev_end > pause_threshold and cur and ends_sentence(cur[-1]["text"]):
            groups.append(cur)
            cur = []
        cur.append(e)
        prev_end = e["end"]
    if cur:
        groups.append(cur)
    return groups


def ends_sentence(text):
    if not text:
        return False
    t = text.strip()
    if not t:
        return False
    t = t.rstrip('"\'”’)]} ')
    return bool(t) and t[-1] in ".!?。！？"


def group_words(g):
    return sum(len(x["text"].split()) for x in g)


def group_duration(g):
    return g[-1]["end"] - g[0]["start"]


def find_split_point(g, target_words=150, soft_pause=0.8):
    if len(g) < 2:
        return None
    total = group_words(g)
    left_words = 0
    best_idx, best_score = None, float("inf")
    for i in range(1, len(g)):
        left_words += len(g[i - 1]["text"].split())
        right_words = total - left_words
        if left_words < 35 or right_words < 35:
            continue
        # Never split in the middle of a sentence.
        if not ends_sentence(g[i - 1]["text"]):
            continue
        gap = g[i]["start"] - g[i - 1]["end"]
        pause_bonus = 0 if gap >= soft_pause else 80
        balance = abs(left_words - target_words) + abs(right_words - target_words)
        score = balance + pause_bonus
        if score < best_score:
            best_score = score
            best_idx = i
    return best_idx


def split_group_by_sentence_text(g, target_words=150, hard_max_words=260, max_duration=70):
    """Fallback splitter: split oversized groups by sentence text with estimated timing."""
    if len(g) <= 1:
        return [g]

    full_text = " ".join(x["text"] for x in g).strip()
    if not full_text:
        return [g]

    # Split on sentence-ending punctuation while keeping sentence integrity.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?。！？])\s+", full_text) if s.strip()]
    if len(sentences) <= 1:
        return [g]

    start = g[0]["start"]
    end = g[-1]["end"]
    total_duration = max(end - start, 0.1)
    total_chars = max(sum(len(s) for s in sentences), 1)

    sentence_entries = []
    cursor = start
    for i, s in enumerate(sentences):
        if i == len(sentences) - 1:
            seg_end = end
        else:
            seg_dur = total_duration * (len(s) / total_chars)
            seg_end = min(end, cursor + seg_dur)
        sentence_entries.append({"text": s, "start": cursor, "end": seg_end})
        cursor = seg_end

    groups, cur = [], []
    cur_words = 0
    for e in sentence_entries:
        w = len(e["text"].split())
        cur_duration = (e["end"] - cur[0]["start"]) if cur else 0
        if cur and ((cur_words + w > hard_max_words) or (cur_duration > max_duration and cur_words >= target_words)):
            groups.append(cur)
            cur = []
            cur_words = 0
        cur.append(e)
        cur_words += w
    if cur:
        groups.append(cur)
    return groups if groups else [g]


def split_group_by_restored_punctuation(g, target_words=150, hard_max_words=260, max_duration=70, sentence_pause=0.9, min_sentence_words=10):
    """Fallback for ASR text without punctuation: infer sentence boundaries via pauses and length."""
    if len(g) <= 1:
        return [g]

    sentence_chunks = []
    cur = [g[0]]
    cur_words = len(g[0]["text"].split())
    for i in range(1, len(g)):
        prev = g[i - 1]
        now = g[i]
        gap = now["start"] - prev["end"]
        should_break = gap >= sentence_pause and cur_words >= min_sentence_words
        if should_break:
            sentence_chunks.append(cur)
            cur = [now]
            cur_words = len(now["text"].split())
        else:
            cur.append(now)
            cur_words += len(now["text"].split())
    if cur:
        sentence_chunks.append(cur)

    if len(sentence_chunks) <= 1:
        return [g]

    sentence_entries = []
    for chunk in sentence_chunks:
        t = " ".join(x["text"] for x in chunk).strip()
        if not t:
            continue
        if not ends_sentence(t):
            t = t.rstrip() + "."
        sentence_entries.append({"text": t, "start": chunk[0]["start"], "end": chunk[-1]["end"]})

    if len(sentence_entries) <= 1:
        return [g]

    groups, cur = [], []
    cur_words = 0
    for e in sentence_entries:
        w = len(e["text"].split())
        cur_duration = (e["end"] - cur[0]["start"]) if cur else 0
        if cur and ((cur_words + w > hard_max_words) or (cur_duration > max_duration and cur_words >= target_words)):
            groups.append(cur)
            cur = []
            cur_words = 0
        cur.append(e)
        cur_words += w
    if cur:
        groups.append(cur)
    return groups if groups else [g]


def split_large_group(g, hard_max_words=260, max_duration=70, target_words=150, soft_pause=0.8, restore_punctuation=False):
    if group_words(g) <= hard_max_words and group_duration(g) <= max_duration:
        return [g]
    idx = find_split_point(g, target_words=target_words, soft_pause=soft_pause)
    if idx is None:
        by_punctuation = split_group_by_sentence_text(
            g,
            target_words=target_words,
            hard_max_words=hard_max_words,
            max_duration=max_duration,
        )
        if by_punctuation != [g] or not restore_punctuation:
            return by_punctuation
        return split_group_by_restored_punctuation(
            g,
            target_words=target_words,
            hard_max_words=hard_max_words,
            max_duration=max_duration,
        )
    left = split_large_group(
        g[:idx],
        hard_max_words=hard_max_words,
        max_duration=max_duration,
        target_words=target_words,
        soft_pause=soft_pause,
    )
    right = split_large_group(
        g[idx:],
        hard_max_words=hard_max_words,
        max_duration=max_duration,
        target_words=target_words,
        soft_pause=soft_pause,
    )
    return left + right


def rebalance_groups(
    groups,
    restore_punctuation=False,
    target_words=150,
    min_words=70,
    hard_max_words=260,
    min_duration=12,
    max_duration=70,
    soft_pause=0.8,
):
    expanded = []
    for g in groups:
        expanded.extend(
            split_large_group(
                g,
                restore_punctuation=restore_punctuation,
                hard_max_words=hard_max_words,
                max_duration=max_duration,
                target_words=target_words,
                soft_pause=soft_pause,
            )
        )
    if not expanded:
        return expanded

    merged = []
    i = 0
    while i < len(expanded):
        cur = expanded[i]
        while i < len(expanded) - 1 and (group_words(cur) < min_words or group_duration(cur) < min_duration):
            i += 1
            cur = cur + expanded[i]
        merged.append(cur)
        i += 1

    if len(merged) >= 2 and (group_words(merged[-1]) < min_words or group_duration(merged[-1]) < min_duration):
        merged[-2] = merged[-2] + merged[-1]
        merged.pop()
    return merged

# ====================== 步骤 3: 补全 SQL ======================

def generate_sql():
    if not SEED_SQL_PATH.exists():
        print(f"❌ 找不到 seed_data.sql，请确保与 pipeline.py 同目录"); sys.exit(1)

    sql = open(SEED_SQL_PATH, "r", encoding="utf-8").read()

    if "6. ARTICLE_SEGMENTS" in sql:
        print("⚠️ seed_data.sql 已包含 article_segments，如需重跑请先恢复原文件"); sys.exit(1)

    updated, sid = 0, 1
    lines = ["\n\n-- ============================================================",
             "-- 6. ARTICLE_SEGMENTS（由 pipeline.py 从 SRT 字幕自动生成）",
             "-- ============================================================\n"]

    for aid, info in TALKS.items():
        slug = info["slug"]
        pp = PARSED_DIR / f"{aid:02d}_{slug}.json"
        ap = AUDIO_DIR / f"{aid:02d}_{slug}.mp3"
        if not pp.exists(): print(f"[跳过] id={aid}"); continue

        data = json.load(open(pp, encoding="utf-8"))
        paras = data.get("paragraphs", [])
        if not paras: continue

        full = " ".join(p["text"] for p in paras)
        wc = len(full.split())
        dur = paras[-1]["end_time"]
        if ap.exists():
            d = get_duration(ap)
            if d > 0: dur = d

        # 回填 word_count / total_duration
        m = re.search(rf"\({aid},\s*'[^']*?',\s*\n\s*'[^']*?',\s*\n\s*'[^']*?',\s*\n\s*'[^']*?',\s*\n\s*'[^']*?',\s*'[^']*?',\s*'[^']*?',\s*'[^']*?',\s*(\d+),\s*'audio',\s*(\d+)\)", sql)
        if m:
            sql = sql.replace(m.group(0), m.group(0).replace(
                f"{m.group(1)}, 'audio', {m.group(2)}", f"{dur}, 'audio', {wc}"))
            updated += 1

        lines.append(f"-- article_id={aid}: {slug}")
        lines.append("INSERT INTO `article_segments` (`segment_id`, `article_id`, `paragraph_index`, "
                      "`sentence_index`, `content_en`, `content_cn`, `start_time`, `end_time`) VALUES")
        vals = []
        for i, p in enumerate(paras):
            t = p["text"].replace("\\","\\\\").replace("'","\\'")
            vals.append(f"({sid}, {aid}, {i+1}, 0, '{t}', NULL, {p['start_time']}, {p['end_time']})")
            sid += 1
        lines.append(",\n".join(vals) + ";\n")
        print(f"  ✅ id={aid}: {len(paras)} 段落, wc={wc}, dur={dur}s")

    open(SEED_SQL_PATH, "w", encoding="utf-8").write(sql.rstrip() + "\n" + "\n".join(lines))
    print(f"\n{'='*60}\nseed_data.sql 已补全! articles 更新 {updated} 条, segments {sid-1} 条\n{'='*60}")

def get_duration(fp):
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1",str(fp)], capture_output=True, text=True, check=True)
        return int(float(r.stdout.strip()))
    except: return 0

# ====================== 主入口 ======================

def main():
    p = argparse.ArgumentParser(description="TED 数据处理流水线（SRT 方案，无需 GPU）")
    p.add_argument("--mode", choices=["download","parse","sql","all"], required=True,
        help="download-下载 | parse-解析SRT | sql-补全SQL | all-全部")
    p.add_argument("--pause-threshold", type=float, default=2.0, help="段落分界阈值（秒）")
    p.add_argument("--smart-segmentation", action="store_true", help="智能分段：基于段长二次切分与合并")
    p.add_argument("--restore-punctuation", action="store_true", help="标点恢复：为无标点 ASR 文本推断句末")
    p.add_argument("--target-words", type=int, default=150, help="智能分段目标词数")
    p.add_argument("--min-words", type=int, default=70, help="智能分段最小词数")
    p.add_argument("--max-words", type=int, default=260, help="智能分段最大词数")
    p.add_argument("--min-duration", type=float, default=12.0, help="智能分段最小时长（秒）")
    p.add_argument("--max-duration", type=float, default=70.0, help="智能分段最大时长（秒）")
    p.add_argument("--soft-pause", type=float, default=0.8, help="智能分段优先切分的软停顿阈值（秒）")
    a = p.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if a.mode in ("download","all"): download_all()
    if a.mode in ("parse","all"):
        parse_all(
            a.pause_threshold,
            a.smart_segmentation,
            restore_punctuation=a.restore_punctuation,
            target_words=a.target_words,
            min_words=a.min_words,
            max_words=a.max_words,
            min_duration=a.min_duration,
            max_duration=a.max_duration,
            soft_pause=a.soft_pause,
        )
    if a.mode in ("sql","all"): generate_sql()

if __name__ == "__main__": main()
