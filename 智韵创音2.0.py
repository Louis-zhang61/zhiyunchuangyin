import os
from zhipuai import ZhipuAI
import requests
import streamlit as st
import re
import time
import random
import base64
from pychorus import find_and_output_chorus
from pydub import AudioSegment

# 从环境变量中获取配置信息
ZhipuAI_API_KEY = os.environ.get("ZHIPUAI_API_KEY", "d6415b0b9a8f5d2a18463afc7b617b05.L0aTMIsPzFAsQL3k")
BASE_URL = os.environ.get("BASE_URL", "https://dzwlai.com/apiuser")
API_KEY = os.environ.get("API_KEY", "2jhskfdgjldfgjldf-9639-kiuwoiruk")
X_TOKEN = os.environ.get("X_TOKEN", "sk-0e591b28bd9c46378c654e33cd927a83")
X_USERID = os.environ.get("X_USERID", "abc001")

# 初始化智谱AI客户端
client = ZhipuAI(api_key=ZhipuAI_API_KEY)


# 通用的文本生成函数
def generate_text(prompt):
    try:
        response = client.chat.completions.create(
            model="GLM-4-Plus",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"生成文本失败：{str(e)}")
        return None


# 通用的歌词生成函数
def generate_lyrics(messages):
    try:
        response = client.chat.completions.create(
            model="GLM-4-Plus",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"生成歌词失败：{str(e)}")
        return None


# 根据歌名生成歌词函数（优化版）
def generate_lyrics_by_title(song_title):
    # 构建更明确的提示，确保生成符合要求的歌词
    prompt = f"""
    作为一名华语作词专家，请根据以下要求为我创作一首歌词：

    歌名：{song_title}

    明确主题和情感
    歌词创作应以真挚的情感为基础，避免“假、大、空”的口号式表达。例如，通过具体的小事来反映深刻的主题，使歌词更具感染力。

    注重语言简洁与押韵
    歌词的语言要简洁、口语化，同时注重押韵和节奏感。避免过于复杂的句式，确保歌词易记、易唱。

    注重细节与画面感
    用生动的语言描绘画面，让听众通过歌词感受到具体的情感和场景。例如，通过“一只蝴蝶飞进我的窗口”来传递思念之情。

    寻找灵感与创意
    多尝试不同的写作方法，如限制性写作、合作创作等。同时，研究喜欢的艺术家，从中汲取灵感。

歌词创作的核心要素：
        （1）主题明确，情感真挚
        歌词创作的基础是明确主题，无论是爱情、励志、哲理还是社会话题，都需要围绕一个核心展开。
        情感真挚是歌词打动人心的关键，通过细腻的描写和真挚的表达，让听众产生共鸣。
        （2）语言简洁，易于传唱
        歌词语言要简洁明了，避免冗长和复杂，确保歌词朗朗上口、易于记忆。
        例如，《水手》的副歌“至少我们还有梦”，用简单直白的语言传递了希望和坚韧。
        （3）韵律和谐，节奏鲜明
        歌词的韵脚和节奏是音乐性的体现，朗朗上口的歌词更容易被听众记住。
        例如，《我》的副歌“我就是我”，通过押韵和重复，增强了记忆点。

    经典结构：主歌（Verse）+ 副歌（Chorus）
        （1）主歌（Verse）
        主歌是歌曲的主体部分，通常用于叙述故事或表达情感。其特点是节奏较平稳，歌词内容多为细腻的描述或情感的铺垫。主歌通常包含两到三段，每段歌词长度和节奏相似，但内容上可能略有变化，起到推进故事或情感的作用。

        （2）副歌（Chorus）
        副歌是歌曲的高潮部分，旋律和歌词重复性强，是歌曲中最容易被记忆的部分。副歌通常用来强化主题或情感，歌词内容简短有力，往往直接点明歌曲的中心思想。

        我们也来看一个例子：周杰伦《七里香》。这首歌在前奏与第一遍副歌之前放了两段主歌（AB），而且每段主歌唱了两遍（A1A2B1B2），另外两段主歌在每一遍的结尾部分也是承接部分都在旋律上做了不同的处理，整首歌在主副歌的排列方式上也十分独特，简短多变的设计都非常精巧。注意我们的标记方式为【A1，A2，B1，B2，C1，C2，C1，B3，B4，C1，C2】。

    示例输出格式：
    （歌名）
    [主歌1]
    （歌词内容...）
    [副歌]
    （歌词内容...）
    ...
    """
    messages = [
        {"role": "user", "content": prompt}
    ]
    return generate_lyrics(messages)


# 根据要求生成歌词函数
def generate_lyrics_with_requires(theme, lyrics_requires):
    messages = [
        {"role": "user",
         "content": f"请根据以下要求生成歌词：主题：{theme}，要求：{lyrics_requires} 请注意押韵是最重要的！！！"}
    ]
    return generate_lyrics(messages)


# 音乐创作（自定义模式）
def create_music_custom(prompt, model="suno", tags="", title="", continueClipId="", continueAt="", mvVersion="chirp-v4",
                        make_instrumental=False):
    if model == "suno":
        url = BASE_URL + "/_open/suno/music/generate"
    elif model == "luno":
        url = BASE_URL + "/_open/suno/music/generate"  # luno模型的接口路径与suno相同
    headers = {
        "key": API_KEY,
        "x-token": X_TOKEN,
        "x-userId": X_USERID
    }
    data = {
        "inputType": "20",
        "makeInstrumental": "true" if make_instrumental else "false",
        "prompt": prompt,
        "tags": tags,
        "title": title,
        "continueClipId": continueClipId,
        "continueAt": continueAt,
        "mvVersion": mvVersion
    }
    if model == "luno":
        data["expectAiModel"] = "luno"
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"音乐创作请求失败，状态码：{response.status_code}，错误信息：{response.text}")
        return None


# 获取音乐生成状态并提取音频地址
def get_music_state(taskBatchId):
    url = BASE_URL + f"/_open/suno/music/getState?taskBatchId={taskBatchId}"
    headers = {
        "x-token": X_TOKEN,
        "x-userId": X_USERID
    }
    mp3_urls = []

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()

            # 检查响应格式是否正确
            if 'data' not in result or 'items' not in result.get('data', {}):
                st.error("获取音乐状态响应格式错误：未找到'data.items'字段。")
                break

            for item in result['data']['items']:
                if item['status'] == 30:  # 状态30表示成功完成
                    mp3_urls.append(item.get('cld2AudioUrl'))
            # 检查所有任务是否完成
            if all(item['status'] == 30 for item in result['data']['items']):
                st.success("所有音乐生成任务已成功完成。")
                break
            elif any(item['status'] == 40 for item in result['data']['items']):
                st.error("部分音乐生成任务失败。")
                break
            time.sleep(10)
        else:
            st.error(f"获取音乐状态出错，状态码：{response.status_code}，错误信息：{response.text}")
            break
    if not mp3_urls:
        st.warning("没有生成的音频。")
    return mp3_urls


# Streamlit应用
def main():
    # 设置页面标题和样式
    st.markdown("""
    <style>
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
            position: relative;
        }
        .main-title {
            font-size: 36px;
            font-weight: bold;
            margin: 0;
            animation: jump 2s infinite;
        }
        .subtitle {
            font-size: 14px;
            margin: 5px 0 0 0;
            color: #555;
            position: absolute;
            bottom: -20px;
            right: 0;
        }
        .arrow-link {
            margin-left: 20px;
            display: flex;
            align-items: center;
        }
        .arrow {
            width: 20px;
            height: 20px;
            margin-right: 8px;
            animation: arrow-move 3s infinite;
        }
        .link-text {
            font-size: 16px;
            color: #4CAF50;
            font-weight: bold;
            text-decoration: underline;
            cursor: pointer;
        }
        @keyframes jump {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        @keyframes arrow-move {
            0% { transform: translateX(0); }
            50% { transform: translateX(-10px); }
            100% { transform: translateX(0); }
        }

        /* 新增问卷调查区域样式 */
        .survey-container {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .survey-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            text-align: center;
        }

        .survey-question {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }

        .survey-question-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #4CAF50;
        }

        /* 问卷按钮样式 */
        .survey-button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin: 5px;
        }

        .survey-button:hover {
            background-color: #388E3C;
        }

        /* 问卷按钮选中样式 */
        .survey-button.selected {
            background-color: #388E3C;
            box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
        }

        .survey-textarea {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
        }

        .survey-submit-button {
            background-color: #2196F3;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-top: 10px;
        }

        .survey-submit-button:hover {
            background-color: #0b7dda;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .title-container {
                font-size: 14px;
            }
            .main-title {
                font-size: 24px;
            }
            .survey-title {
                font-size: 20px;
            }
            .survey-textarea {
                font-size: 14px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="title-container">
        <h1 class="main-title">智韵创音_内测</h1>
        <p class="subtitle">武音人自己的音乐生成器。
        <br>
        只生成符合中国人胃口的歌曲。</p>
        <div class="arrow-link">
            <svg class="arrow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
            <a href="http://zychuangyin.xzin.top/" target="_blank" class="link-text">听听生成的歌曲/纯音乐（电脑端体验感更好哦！）</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 设置和语言选择（侧边栏）
    with st.sidebar:
        st.header("⚙️ 设置")
        languages = ["中文", "English"]
        language = st.selectbox("选择语言", languages)
        st.markdown("---")

        # 使用说明（展开形式）
        st.write("欢迎使用智韵创音！以下是一些简单的操作指南：")
        st.markdown(
            "- **音乐生成**：在右侧音乐生成区域，你可以输入歌词或描述、歌曲名称，并选择是否生成纯音乐（无歌词）。点击“创作音乐”按钮后，系统将生成相应的音乐，并提供音频播放。")
        st.markdown(
            "- **歌词生成**：在左侧歌词生成区域，你可以通过输入歌名、主题和歌词要求来生成歌词。系统将根据这些信息生成符合要求的歌词。")
        st.markdown("- **金句推荐**：在金句推荐区域，点击“生成金句”按钮，系统将随机为你推荐一句优美的金句。")
        st.markdown(
            "- **铃声制作**：在铃声制作区域，上传音乐文件并设置铃声部分时长后，点击“点击制作铃声”按钮，系统将提取音乐高潮部分并生成铃声文件。")
        st.markdown("- **留言板**：在该区域，你可以写下对「智韵创音」的留言，留言会展示在留言板上。")

        st.write("**关于作者与软件**")
        st.markdown(
            '''我是武汉音乐学院作曲系研究生，作为 AI 爱好者，始终关注其发展，一直思考如何将 AI 与音乐创作深度融合。这一探索之路充满挑战，任重而道远，但我满怀热忱，将持续深耕。
''')
    # 根据语言选择显示不同的文本
    def get_text(key):
        if language == "中文":
            texts = {
                "title": "智韵创音",
                "lyrics_generation": "歌词生成",
                "generate_by_title_checkbox": "根据歌名生成歌词",
                "song_title_placeholder": "请输入歌名",
                "generate_lyrics_by_title_button": "根据歌名生成歌词",
                "theme_placeholder": "请输入主题，如爱情、梦想等",
                "lyrics_requires_placeholder": "请输入歌词要求，如歌曲结构、押韵、具体歌词片段等（支持再编辑）",
                "generate_lyrics_button": "生成歌词",
                "music_generation": "音乐生成",
                "lyrics_placeholder": "请输入歌词",
                "instrumental_requirements": "生成纯音乐要求",
                "title_placeholder": "请输入歌曲名称",
                "create_music_button": "创作音乐",
                "ringtone_creation": "铃声制作（只有精品生成的音乐可以）",
                "upload_file": "请选择音乐文件上传（暂时只支持精品生成的音乐文件）",
                "highlight_duration": "铃声部分时长（秒）",
                "extract_button": "制作铃声",
                "golden_sentence": "金句推荐",
                "generate_golden_sentence_button": "生成金句",
                "footer": "© 2024  “智韵创音”音乐生成器",
                "make_instrumental": "生成纯音乐（无歌词）",
                "generating_lyrics_by_title": "根据歌名生成歌词...",
                "failed_generate_lyrics_by_title": "未能根据歌名生成歌词，请稍后再试。",
                "generating_lyrics": "生成歌词...",
                "failed_generate_lyrics": "未能生成歌词，请稍后再试。",
                "music_generation_in_progress": "正在进行音乐生成，请稍等...",
                "play_mp3": "播放MP3音频：",
                "no_mp3_generated": "没有生成的音频。",
                "task_batch_id_not_found": "在响应中未找到任务批次ID。",
                "music_creation_failed": "音乐创作请求失败，请检查输入或联系管理员。",
                "music_commercial_use": "作品一旦付费，版权属于用户。 ",
                "success_extract_music_highlight": "成功提取音乐高潮部分，文件保存在: {}",
                "failure_extract_music_highlight": "提取音乐高潮部分失败。",
                "message_board_title": "音海留言板",
                "message_board_description": "在这里写下你对「智韵创音」的想法、建议或故事，与大家分享吧！",
                "message_placeholder": "请输入你的留言",
                "submit_message_button": "提交留言",
                "message_submitted": "留言已提交！",
                "no_messages": "暂无留言。",
                "survey_title": "用户调研问卷",
                "platform_question": "1. 你认为是在网页上好还是在微信小程序上好？",
                "community_question": "2. 我们在此基础上成立一个武音社区你认为可以吗？（比如，你对学校某事的吐槽/表白墙）",
                "suggestion_question": "3. 你还有什么意见或建议可以写在这。（你的看法对我们很重要！）",
                "submit_survey": "提交问卷",
                "survey_thank_you": "问卷提交成功！感谢您的反馈！",
                "contact_us": "联系我们",
                "email": "1281974050@qq.com"  # 新增邮箱信息
            }
        else:
            texts = {
                "title": "Music Creator",
                "lyrics_generation": "Lyrics Generation",
                "generate_by_title_checkbox": "Generate lyrics by song title",
                "song_title_placeholder": "Enter the song title",
                "generate_lyrics_by_title_button": "Generate lyrics based on song title",
                "theme_placeholder": "Enter a theme, such as love, dreams, etc.",
                "lyrics_requires_placeholder": "Enter lyrics requirements, such as song structure, rhyme, specific lyric fragments, etc.",
                "generate_lyrics_button": "Generate Lyrics",
                "music_generation": "Music Generation",
                "lyrics_placeholder": "Enter lyrics",
                "instrumental_requirements": "Instrumental music requirements",
                "title_placeholder": "Enter song title",
                "create_music_button": "Create Music",
                "ringtone_creation": "Ringtone Creation",
                "upload_file": "Please upload a music file",
                "highlight_duration": "Highlight duration (seconds)",
                "extract_button": "Extract Highlight",
                "golden_sentence": "Golden Sentence",
                "generate_golden_sentence_button": "Generate Golden Sentence",
                "footer": "© 2024 All rights reserved by Liu Yuzhang. 'Music Creator'",
                "make_instrumental": "Generate Instrumental Music (No Lyrics)",
                "generating_lyrics_by_title": "Generating lyrics by song title...",
                "failed_generate_lyrics_by_title": "Failed to generate lyrics by song title, please try again later.",
                "generating_lyrics": "Generating lyrics...",
                "failed_generate_lyrics": "Failed to generate lyrics, please try again later.",
                "music_generation_in_progress": "Music generation is in progress, please wait...",
                "play_mp3": "Play MP3 audio:",
                "no_mp3_generated": "No audio generated.",
                "task_batch_id_not_found": "Task batch ID not found in response.",
                "music_creation_failed": "Music creation request failed, please check input or contact administrator.",
                "success_extract_music_highlight": "Successfully extracted music highlight, file saved at: {}",
                "failure_extract_music_highlight": "Failed to extract music highlight.",
                "message_board_title": "Soundwaves Message Board",
                "message_board_description": "Share your thoughts, suggestions, or stories about 'MelodyGenie' here!",
                "message_placeholder": "Enter your message",
                "submit_message_button": "Submit Message",
                "message_submitted": "Message submitted!",
                "no_messages": "No messages yet.",
                "music_commercial_use": "Works can be commercialized without copyright issues",
                "survey_title": "User Survey",
                "platform_question": "1. Do you think it's better to use on a web page or WeChat mini program?",
                "community_question": "2. Do you think it's a good idea to build a music community based on this?",
                "suggestion_question": "3. Do you have any other opinions or suggestions? (Your feedback is important to us!)",
                "submit_survey": "Submit Survey",
                "survey_thank_you": "Survey submitted successfully! Thank you for your feedback!",
                "contact_us": "Contact Us",
                "email": "1281974050@qq.com"  # 新增邮箱信息
            }
        return texts.get(key, "")

    # 创建左右两列，调整比例使得音乐生成部分略大
    col1, col2 = st.columns([2, 3])

    # 歌词生成部分（左列）
    with col1:
        st.header(get_text("lyrics_generation"))
        # 新增根据歌名生成歌词的选项
        generate_by_title = st.checkbox(get_text("generate_by_title_checkbox"))
        if generate_by_title:
            song_title = st.text_input(get_text("song_title_placeholder"),
                                       placeholder=get_text("song_title_placeholder"))
            if song_title:
                generate_title_button = st.button(get_text("generate_lyrics_by_title_button"))
                if generate_title_button:
                    with st.spinner(get_text("generating_lyrics_by_title")):
                        lyrics = generate_lyrics_by_title(song_title)
                        if lyrics:
                            st.text_area(get_text("lyrics_generation"), value=lyrics, height=300)
                        else:
                            st.warning(get_text("failed_generate_lyrics_by_title"))
        else:
            theme = st.text_input(get_text("theme_placeholder"), placeholder=get_text("theme_placeholder"))
            lyrics_requires = st.text_area(get_text("lyrics_requires_placeholder"),
                                           placeholder=get_text("lyrics_requires_placeholder"), height=100)

            # 按钮禁用逻辑
            if theme and lyrics_requires:
                generate_button = st.button(get_text("generate_lyrics_button"))
            else:
                generate_button = st.button(get_text("generate_lyrics_button"), disabled=True)

            st.markdown('<hr>', unsafe_allow_html=True)
            if generate_button:
                with st.spinner(get_text("generating_lyrics")):
                    # 使用歌词生成函数
                    lyrics = generate_lyrics_with_requires(theme, lyrics_requires)
                    if lyrics:
                        st.text_area(get_text("lyrics_generation"), value=lyrics, height=300)
                    else:
                        st.warning(get_text("failed_generate_lyrics"))

    # 音乐生成部分（右列）
    with col2:
        st.header(get_text("music_generation"))
        prompt = st.text_area(
            get_text("lyrics_placeholder"),
            placeholder=get_text("lyrics_placeholder"),
            height=300
        )
        title = st.text_input(
            get_text("title_placeholder"),
            placeholder=get_text("title_placeholder")
        )
        music_style = st.selectbox("选择音乐风格", ["流行", "摇滚", "古典", "民谣", "电子", "爵士"])  # 示例音乐风格选项
        is_instrumental = st.checkbox(
            get_text("make_instrumental"),
            value=False
        )
        model_display_mapping = {
            "suno": "精品生成（8元/首 5分钟左右生成） ",
            "luno": "快速生成（1.5元/首 1分钟左右生成）"
        }
        model_choice_display = st.selectbox("生成方式", list(model_display_mapping.values()))
        model_choice = {v: k for k, v in model_display_mapping.items()}[model_choice_display]

        # 如果用户选择生成纯音乐且未输入描述，自动填充默认描述并显示在输入框中
        if is_instrumental and not prompt:
            prompt = "一段无歌词的纯音乐，让人感受到宁静与美好。"
            st.text_area(
                get_text("instrumental_requirements"),  # 修改输入框名称为“生成纯音乐要求”
                value=prompt,  # 显示默认描述
                height=300
            )

        # 按钮禁用逻辑
        if (prompt or is_instrumental) and title:
            music_button = st.button(get_text("create_music_button"))
        else:
            music_button = st.button(
                get_text("create_music_button"),
                disabled=True
            )

        if music_button:
            # 如果用户未输入描述且选择生成纯音乐，使用默认描述
            if not prompt and is_instrumental:
                prompt = "一段无歌词的纯音乐，让人感受到宁静与美好。"

            # 定义 music_description
            music_description = "默认歌曲描述"  # 你可以根据需要修改这个值

            # 调用音乐生成函数，根据是否纯音乐设置参数
            make_instrumental = is_instrumental  # 是否为纯音乐
            model = model_choice
            creation_result = create_music_custom(
                prompt,
                model=model,
                title=title,
                make_instrumental=make_instrumental,
                tags=music_style,  # 添加音乐风格
                mvVersion=music_description  # 添加歌曲描述
            )
            if creation_result:
                task_batch_id = creation_result['data'].get('taskBatchId')
                if task_batch_id:
                    st.write(get_text("music_generation_in_progress"))

                    # 动态文字展示
                    with st.spinner(get_text("music_generation_in_progress")):
                        # 使用大模型随机生成故事短句
                        qinghai_story_prompt = "随机生成一个故事短句，要求文字优美、富有画面感，长度不超过30字，自然风光或民族文化相关"
                        qinghai_story = generate_text(qinghai_story_prompt)
                        if qinghai_story:
                            st.write(qinghai_story)
                        else:
                            st.write("湛蓝湖水映着霞光，候鸟飞翔诉说情长。")
                        time.sleep(1)  # 每隔1秒展示一句

                    # 获取音乐生成状态并获取音频地址
                    mp3_urls = get_music_state(task_batch_id)
                    if mp3_urls:
                        st.write(get_text("play_mp3"))
                        for url in mp3_urls:
                            st.audio(url)
                    else:
                        st.warning(get_text("no_mp3_generated"))
                else:
                    st.error(get_text("task_batch_id_not_found"))
            else:
                st.error(get_text("music_creation_failed"))
    # 添加作品可商用说明
    st.markdown(f"<p>{get_text('music_commercial_use')}</p>", unsafe_allow_html=True)

    # 高潮提取模块
    st.header(get_text("ringtone_creation"))
    uploaded_file = st.file_uploader(get_text("upload_file"), type=['mp3', 'wav', 'm4a'])
    highlight_duration = st.number_input(get_text("highlight_duration"), min_value=1, value=15)

    if st.button(get_text("extract_button")):
        # 使用相对路径
        output_folder = "music_highlights"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        extracted_file_path = extract_music_highlights(uploaded_file, output_folder, highlight_duration)

        if extracted_file_path:
            st.success(get_text("success_extract_music_highlight").format(extracted_file_path))
            # 在线播放提取的音频
            st.audio(extracted_file_path)
        else:
            st.error(get_text("failure_extract_music_highlight"))

    # 金句框架部分
    st.header(get_text("golden_sentence"))
    if st.button(get_text("generate_golden_sentence_button")):
        with st.spinner("生成金句中..."):
            golden_sentence = generate_text("生成一句富有哲理或情感的金句。要求简洁优美，具有启发性。")
            if golden_sentence:
                st.write(golden_sentence)
            else:
                st.warning("生成金句失败，请稍后再试。")

    # 留言板模块
    st.header(get_text("message_board_title"))
    st.write(get_text("message_board_description"))
    user_message = st.text_area(get_text("message_placeholder"), placeholder=get_text("message_placeholder"))
    if st.button(get_text("submit_message_button")):
        if user_message.strip():
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append(user_message)
            st.success(get_text("message_submitted"))
        else:
            st.warning("请输入留言内容。")

    if 'messages' in st.session_state and st.session_state.messages:
        st.subheader("留言列表")
        for message in st.session_state.messages:
            st.write(message)
    else:
        st.info(get_text("no_messages"))


    # 问卷调查区域
    st.header(get_text("survey_title"))
    with st.container():
        survey_data = {}

        # 第一个问题
        st.markdown(f"**{get_text('platform_question')}**")
        platform_options = ["网页更好", "小程序更好"] if language == "中文" else ["Web better", "Mini Program better"]
        selected_platform = st.radio("", platform_options)

        # 第二个问题
        st.markdown(f"**{get_text('community_question')}**")
        community_options = ["可以", "不可以"] if language == "中文" else ["Yes", "No"]
        selected_community = st.radio("", community_options)

        # 第三个问题
        st.markdown(f"**{get_text('suggestion_question')}**")
        suggestion = st.text_area("", placeholder=get_text("suggestion_question"), height=100)

        # 提交问卷
        if st.button(get_text("submit_survey")):
            survey_data = {
                "platform": selected_platform,
                "community": selected_community,
                "suggestion": suggestion
            }
            # 这里可以添加代码将调查数据发送到服务器或保存到文件
            st.success(get_text("survey_thank_you"))
            # 显示用户提交的数据（实际应用中可以将其发送到服务器）
            st.write("您提交的数据:")
            st.write(survey_data)

    # 联系我们部分
    st.header(get_text("contact_us"))
    st.markdown(f"""
    如果您在使用过程中遇到任何问题，或者有其他建议和需求，欢迎通过以下方式联系我们：
    - 邮箱：{get_text("email")}
    """, unsafe_allow_html=True)

    # 关于作者部分
    st.markdown("<h3 style='text-align: center;'>悄悄告诉你</h3>", unsafe_allow_html=True)
    st.markdown('''
    <div style="background-color: rgba(255, 255, 255, 0.8); border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); text-align: center;">
        <p style="text-align: center; line-height: 1.6;">
            
            该软件最大的特色是生成的歌曲伴奏，能够很好地契合大众的口味。
            并且在我们这里，所谓的“AI幻觉”出现的概率非常低，仅为1.7%。
        
    </div>
    ''', unsafe_allow_html=True)

    # 底部版权
    st.markdown(f"<footer>{get_text('footer')}</footer>", unsafe_allow_html=True)

    # 添加毛玻璃效果和视差滚动留言列表
    st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom right, #e0e0e0, #f5f5f5); /* 更改渐变色 */
            background-size: cover;
            font-family: 'Roboto', sans-serif; 
        }

        /* 毛玻璃效果 */
        .stApp {
            background-color: rgba(255, 255, 255, 0.85); /* 背景色 */
            backdrop-filter: blur(10px); /* 毛玻璃效果 */
            -webkit-backdrop-filter: blur(10px); /* Webkit浏览器兼容 */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 添加阴影 */
        }

        /* 呼吸灯效果应用于按钮 */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 15px 32px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: all 0.3s ease; /* 添加过渡效果 */
            font-size: 16px;
            animation: breathe 2s infinite; /* 呼吸灯动画 */
            transform: scale(1); /* 初始缩放 */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影 */
        }

        .stButton > button:hover {
            background-color: #388E3C;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            transform: scale(1.05); /* 悬停时的放大效果 */
        }

        @keyframes breathe {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }

        /* 顶部小箭头指示器和文字 */
        .top-indicator {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            cursor: pointer;
            animation: bounce 2s infinite;
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .top-indicator::after {
            content: "↑";
            font-size: 24px;
            animation: bounce 2s infinite;
            color: #4CAF50;
        }

        .top-text {
            margin-top: 10px;
            font-size: 16px;
            color: #333;
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }

        /* 文字轻微缩放和阴影 */
        h1, h2, h3 {
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        }

        h1 {
            animation: scaleText 5s infinite alternate;
        }

        @keyframes scaleText {
            from { transform: scale(1); }
            to { transform: scale(1.05); }
        }

        /* 视差滚动留言列表 */
        .parallax-container {
            height: 300px; /* 容器高度 */
            overflow-y: auto; /* 添加垂直滚动条 */
            padding: 20px;
            background-attachment: fixed; /* 固定背景 */
            background-position: center; /* 背景居中 */
            background-repeat: no-repeat; /* 背景不重复 */
            background-size: cover; /* 背景覆盖 */
        }

        .parallax-item {
            padding: 15px;
            margin-bottom: 15px;
            background-color: rgba(255, 250, 255, 0.9);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transform: translateY(0);
            transition: transform 0.3s ease;
        }

        .parallax-container:hover .parallax-item {
            transform: translateY(5px);
        }

        /* 卡片样式 */
        .card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin: 15px 0;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        /* 输入框样式 */
        .stTextInput,.stTextArea {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 15px;
            font-size: 16px;
            transition: box-shadow 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stTextInput input:focus,.stTextArea textarea:focus {
            border-color: #388E3C;
            outline: none;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* 播放按钮样式 */
        .music-play-button {
            background-color: #FFC107; 
            color: white;
            border: none;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); 
            transition: background-color 0.3s;
        }

        .music-play-button:hover {
            background-color: #FFA000; 
        }

        /* 避免禁用按钮动画 */
        .stButton > button:disabled {
            background-color: #BDBDBD;
            cursor: not-allowed;
            animation: none; /* 禁用动画 */
        }

        /* 侧边栏样式 */
        .sidebar-content {
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* 背景图预留位置 */
        body {
            background-image: url('groundback.png'); /* 请替换为您的背景图链接 */
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        /* 标题样式 */
        .stTitle {
            text-align: center;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 高潮提取函数（支持MP3、WAV、M4A）
    def extract_music_highlights(input_file, output_folder, highlight_duration):
        if input_file is not None:
            file_name = input_file.name
            output_file_name = os.path.splitext(file_name)[0] + '_high.wav'
            output_file_path = os.path.join(output_folder, output_file_name)

            try:
                # 检查文件格式
                if file_name.lower().endswith(('.mp3', '.wav', '.m4a')):
                    # 创建临时文件
                    temp_file_path = os.path.join(output_folder, "temp." + file_name.split('.')[-1])
                    with open(temp_file_path, 'wb') as f:
                        f.write(input_file.read())

                    # 对于 M4A 文件，先转换为 WAV 格式
                    if file_name.lower().endswith('.m4a'):
                        # 读取 M4A 文件
                        audio = AudioSegment.from_file(temp_file_path, format="m4a")
                        # 导出为 WAV 文件
                        wav_file_path = os.path.join(output_folder, "temp.wav")
                        audio.export(wav_file_path, format="wav")
                        # 使用 pychorus 处理 WAV 文件
                        find_and_output_chorus(wav_file_path, output_file_path, highlight_duration)
                    else:
                        # 直接处理 MP3 或 WAV 文件
                        find_and_output_chorus(temp_file_path, output_file_path, highlight_duration)

                    if os.path.exists(output_file_path):
                        return output_file_path
                    else:
                        return None
                else:
                    st.error("不支持的文件格式，请上传MP3、WAV或M4A文件")
                    return None
            except Exception as e:
                st.error(f"提取音乐高潮部分出错：{str(e)}")
                return None
        else:
            return None


if __name__ == "__main__":
    main()
