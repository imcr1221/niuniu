牛牛 · 第10次课 交通工具（二）

目录结构：index.html、generate_audio.py、images/、audio/（运行后生成）

1. 安装依赖：pip install edge-tts
2. 在本目录运行：python generate_audio.py
3. 脚本读取 index.html 中 id="tts-texts" 的 JSON 数组，生成 audio/*.mp3、audio/tts-manifest.js、tts-tests.json。
4. 把整个目录上传到 GitHub Pages 对应目录（建议 niuniu/transport2/）。
5. 语音须在有网络的电脑上运行脚本生成；仅打开 HTML 不会自动联网生成音频。

声音：zh-CN-XiaoyiNeural；RATE=-25%；PITCH=+8Hz。
