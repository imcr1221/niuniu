牛牛 交通工具（二） — GitHub Pages + GitHub Actions 自动生成语音

1. 把本压缩包内 niuniu_transport2 文件夹中的 index.html、images 文件夹、generate_audio.py 上传到仓库的 niuniu/transport2/ 目录。
2. 把本包 .github/workflows/generate-tts.yml 放在【仓库根目录】的 .github/workflows/ 下面，不能放在 niuniu/transport2/ 内。
3. 在 GitHub 仓库 Settings > Actions > General > Workflow permissions，选择 Read and write permissions 并保存。
4. 在 Actions 页面打开 Generate Chinese TTS audio，点击 Run workflow（main 分支）。
5. 等工作流成功，GitHub 会把 MP3 和 tts-manifest.js 自动提交到 niuniu/transport2/audio/。等待 Pages 更新后刷新网页。
6. 以后修改 index.html 里的朗读文本并推送到 main，会自动运行生成。已生成且未修改的语音不会重复生成。

注意：若仓库默认分支不是 main，需将工作流的 branches: [main] 改为实际分支名；若网站路径不是 niuniu/transport2，请相应修改工作流中三处路径。
工作流在 GitHub 服务器运行，不需要本地安装 Python。
