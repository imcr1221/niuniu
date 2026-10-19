import asyncio, hashlib, json, os
import edge_tts

VOICE = "zh-CN-XiaoyiNeural"   # 活泼女声
RATE  = "-5%"
PITCH = "+8Hz"
OUT   = "audio"

os.makedirs(OUT, exist_ok=True)

with open("tts-texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

manifest = {}

async def main():
    for text in texts:
        name = hashlib.md5(text.encode("utf-8")).hexdigest()[:12] + ".mp3"
        path = os.path.join(OUT, name)
        manifest[text] = f"{OUT}/{name}"
        if os.path.exists(path):
            continue
        try:
            c = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
            await c.save(path)
            print("生成:", text, "->", path)
        except Exception as e:
            print("失败:", text, e)

    with open(os.path.join(OUT, "tts-manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.TTS_AUDIO=" + json.dumps(manifest, ensure_ascii=False) + ";\n")
    print("manifest 已写入 audio/tts-manifest.js")

asyncio.run(main())