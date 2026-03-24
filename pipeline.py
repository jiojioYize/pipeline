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
    8:{"search":"TED-Ed Where do math symbols come from John David Walters","slug":"math-symbols"},
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
    26:{"search":"TED Taylor Sparks how to discover materials of the future","slug":"materials-future"},
    27:{"search":"TED-Ed How do self-driving cars see Sajan Saini","slug":"self-driving-see"},
    28:{"search":"TED-Ed ethical dilemma of self-driving cars Patrick Lin","slug":"self-driving-ethics"},
    29:{"search":"TED Wanis Kabbaj driverless world","slug":"driverless-world-transport"},
    30:{"search":"TED Aicha Evans your self-driving robotaxi is almost here","slug":"robotaxi"},
    31:{"search":"TED Nico Larco how will autonomous vehicles transform our cities","slug":"av-transform-cities"},
    32:{"search":"TED David Silver how self-driving cars work","slug":"self-driving-how"},
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

def parse_all(pause_threshold=2.0):
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

        paragraphs = merge_to_paragraphs(entries, pause_threshold)
        json.dump({"article_id": aid, "slug": slug, "srt_file": srt_path.name,
                    "paragraphs": paragraphs}, open(out,"w",encoding="utf-8"), indent=2, ensure_ascii=False)

        wc = sum(len(p["text"].split()) for p in paragraphs)
        print(f"  ✅ {len(paragraphs)} 段落, {wc} 词, 时长 {paragraphs[-1]['end_time']}s")

    print(f"\n解析完成! 结果: {PARSED_DIR}")


def merge_to_paragraphs(entries, pause_threshold=2.0):
    if not entries: return []
    paragraphs, texts, start, prev_end = [], [], entries[0]["start"], entries[0]["end"]

    for e in entries:
        if e["start"] - prev_end > pause_threshold and texts:
            paragraphs.append({"text": " ".join(texts).strip(),
                "start_time": int(round(start)), "end_time": int(round(prev_end))})
            texts, start = [], e["start"]
        texts.append(e["text"])
        prev_end = e["end"]

    if texts:
        paragraphs.append({"text": " ".join(texts).strip(),
            "start_time": int(round(start)), "end_time": int(round(prev_end))})
    return [p for p in paragraphs if p["text"].strip()]

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
    a = p.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if a.mode in ("download","all"): download_all()
    if a.mode in ("parse","all"): parse_all(a.pause_threshold)
    if a.mode in ("sql","all"): generate_sql()

if __name__ == "__main__": main()
