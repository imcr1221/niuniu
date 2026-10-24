import asyncio, hashlib, json, os
import edge_tts

VOICE = "zh-CN-XiaoyiNeural"
RATE  = "-25%"
PITCH = "+8Hz"
OUT   = "audio"                     # ← 保持原样，workflow 只认这个

os.makedirs(OUT, exist_ok=True)

with open("tts-texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

manifest = {}

async def synth(text, path, retries=3):
    for i in range(retries):
        try:
            c = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
            await c.save(path)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return True
        except Exception as e:
            print(f"失败({i+1}/{retries}): {text} -> {e}")
        await asyncio.sleep(2 * (i + 1))
    return False

async def main():
    failed = []
    for text in texts:
        # 文字、声音、语速或音调变化时使用新的文件名，避免复用旧音频。
        cache_key = json.dumps(
            {"text": text, "voice": VOICE, "rate": RATE, "pitch": PITCH},
            ensure_ascii=False, sort_keys=True,
        )
        name = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:16] + ".mp3"
        path = os.path.join(OUT, name)
        rel  = f"{OUT}/{name}"

        if os.path.exists(path) and os.path.getsize(path) > 0:
            manifest[text] = rel
            continue

        ok = await synth(text, path)
        if ok:
            manifest[text] = rel      # 只有成功才写
        else:
            failed.append(text)
            print("未生成:", text)

    with open(os.path.join(OUT, "tts-manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.TTS_AUDIO=" + json.dumps(manifest, ensure_ascii=False) + ";\n")
    print(f"manifest 已写入，{len(manifest)} 条，失败 {len(failed)} 条")
    if failed:
        print("失败列表:", failed)

asyncio.run(main())