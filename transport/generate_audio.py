"""Read every sibling HTML file and build the shared audio/ directory."""
import asyncio
import hashlib
import html
import json
import os
import re
import ssl
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'audio'
VOICE = 'zh-CN-XiaoyiNeural'
RATE = '-25%'
PITCH = '+8Hz'
FORCE_REGENERATE = os.getenv('FORCE_REGENERATE', '0') == '1'
COURSE_ID = os.getenv('TTS_COURSE_ID', ROOT.name)
# Optional trusted CA bundle for managed environments. Certificate verification stays enabled.
if os.getenv('EDGE_TTS_CA_BUNDLE'):
    import edge_tts.communicate
    edge_tts.communicate._SSL_CTX = ssl.create_default_context(cafile=os.environ['EDGE_TTS_CA_BUNDLE'])

def collect_texts():
    result = []
    for page in sorted(ROOT.glob('*.html')):
        source = page.read_text(encoding='utf-8')
        batch = [html.unescape(t) for t in re.findall(r'data-tts-text="([^"]+)"', source)]
        for match in re.finditer(r'<script\b(?=[^>]*\bid=[\"\x27]tts-texts[\"\x27])[^>]*>(.*?)</script>', source, re.S):
            values = json.loads(match.group(1))
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                raise ValueError(f'{page.name}: tts-texts must be a JSON array of strings')
            batch.extend(values)
        for text in batch:
            text = text.strip()
            if text and text not in result:
                result.append(text)
    if not result:
        raise ValueError('No declared TTS texts found in sibling HTML files')
    return result

async def main():
    texts = collect_texts()
    OUT.mkdir(exist_ok=True)
    (ROOT / 'tts-texts.json').write_text(json.dumps(texts, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest, failed = {}, []
    semaphore = asyncio.Semaphore(4)
    async def synth(text):
        name = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]+'.mp3'
        target = OUT / name
        async with semaphore:
            if not FORCE_REGENERATE and target.is_file() and target.stat().st_size > 100:
                manifest[text] = 'audio/'+name
                return
            temp = target.with_suffix('.tmp.mp3')
            for attempt in range(3):
                try:
                    temp.unlink(missing_ok=True)
                    await asyncio.wait_for(edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH, connect_timeout=10, receive_timeout=30).save(str(temp)), 45)
                    if temp.stat().st_size <= 100:
                        raise ValueError('Empty audio response')
                    os.replace(temp, target)
                    manifest[text] = 'audio/'+name
                    print('Generated:', text, flush=True)
                    return
                except Exception as error:
                    print(f'Retry {attempt+1}/3: {text}: {error}', flush=True)
                    temp.unlink(missing_ok=True)
                    if attempt < 2:
                        await asyncio.sleep(attempt+1)
            failed.append(text)
    await asyncio.gather(*(synth(t) for t in texts))
    ordered = {t:manifest[t] for t in texts if t in manifest}
    (OUT/'tts-manifest.js').write_text('window.TTS_AUDIO='+json.dumps(ordered, ensure_ascii=False, indent=2)+';\n', encoding='utf-8')
    tests = [{'id':f'{COURSE_ID}-{i+1}', 'text':t, 'audio':ordered[t]} for i,t in enumerate(texts) if t in ordered]
    (ROOT/'tts-tests.json').write_text(json.dumps(tests, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Audio ready: {len(ordered)}/{len(texts)}', flush=True)
    if failed:
        raise SystemExit('Failed audio: '+', '.join(failed))

if __name__ == '__main__':
    asyncio.run(main())
