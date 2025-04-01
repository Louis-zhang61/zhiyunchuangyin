import os
from zhipuai import ZhipuAI
import requests
import streamlit as st
import re
import time
import random
import base64
from pychorus import find_and_output_chorus
from pydub import AudioSegment  # 新增导入

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


# 根据歌名生成歌词函数
def generate_lyrics_by_title(song_title):
    messages = [
        {"role": "user", "content": "作为一名华语作词专家，请为我写一首歌曲"},
        {"role": "assistant", "content": "当然，要创作歌词，请告诉我一些你的想法"},
        {"role": "user", "content": f"请根据歌名 {song_title} 创作一首歌词，"
                                    f"当用户选择根据主题生成歌词时，增加青海景点相关的主题预设。"
                                    f"例如，“青海湖的浪漫”“茶卡盐湖的梦幻”“祁连山的壮美” 等。当用户选择这些主题时，系统自动为智谱 AI 提供相关景点的特色描述信息，引导其生成与景点氛围相契合的歌词。如对于 “青海湖的浪漫” 主题，歌词中可能会出现 “湛蓝湖水映着霞光，候鸟飞翔诉说情长” 等内容。"
                                    f"请注意押韵是最重要的！"
                                    f"这首歌的歌词的目的是为了迎合青海文旅的要求。 "
                                    f""
                                    f'''示例输出格式：
                         （歌名）
                         [主歌1]
                         （歌词内容...）
                         [副歌]
                         （歌词内容...）
                         ...」

                         实际案例（可直接使用）
                         流行情歌：
                         「生成一首流行情歌，主题是“异地恋”，情感 bittersweet（甜蜜又苦涩）。结构为主歌×2 + 副歌×2 + 桥段，押韵格式ABAB，关键词包括“时差”、“屏幕”、“未完成的拥抱”。语言直白但有画面感，副歌重复一句英文词如“I miss you more”。」

                         说唱歌词：
                         「写一段硬核说唱，主题是“街头奋斗”，情感愤怒而坚定。韵脚密集，每两句押韵，加入比喻如“像困兽撕破铁笼”。关键词：霓虹、血迹、钞票、谎言。最后一句要爆点如“这游戏老子才是规则”。」
                         「请生成一首适合青海旅游宣传的歌词，要求如下：

                         核心主题：

                         展现青海的 自然风光（如青海湖、茶卡盐湖、祁连山、门源油菜花等）。

                         体现 民族文化（藏族、回族、蒙古族等多元文化，或赛马会、花儿会等民俗活动）。

                         传递 “纯净、自由、治愈、探险” 的青海旅行体验。

                         风格与情感：

                         风格：[民谣/流行/世界音乐/古风/电子（可选）]

                         情感：空灵/壮美/温暖/神圣/自由（任选或结合）

                         必备元素（至少包含3项）：

                         自然意象：雪山、盐湖、经幡、候鸟、戈壁、星空、青稞等。

                         文化符号：转经筒、酥油茶、马背民歌、唐卡、塔尔寺等。

                         旅行场景：公路自驾、湖畔骑行、星空露营、牧民家访等。

                         语言要求：

                         有 画面感（如“落日把茶卡染成一面银镜”）。

                         可加入 少量藏语/蒙古语词汇（如“扎西德勒”意为吉祥，“可可西里”意为美丽的青山）。

                         避免口号化，用诗意或故事性表达（如不要直接写“欢迎来青海”）。

                         结构建议：

                         主歌1：描写青海的 自然景观（如青海湖的四季）。

                         主歌2：融入 人文或旅行者视角（如牧民的故事或旅人的感动）。

                         副歌：升华 情感共鸣（如“这里比远方更远，比自由更自由”）。

                         桥段：可加入 呼唤式句子（如“随风去吧，去云朵生根的地方”）。

                         示例输出格式：
                         （歌名：《青海青》/《与神湖对话》/《盐与光的边疆》等）
                         [主歌1]
                         （例：候鸟掠过冰封的湖心，
                         经幡在风里写六字真言…）
                         [副歌]
                         （例：青海青啊，谁把天空揉成一面镜子，
                         照见牦牛，照见格桑，照见流浪的孩子…）
                         ...」
                         古风歌词：
                         「创作一首古风歌词，主题“江湖离别”，情感苍凉。结构自由，押韵AABB，意象包括“长枪”、“残酒”、“孤雁”。语言文言化，避免现代词汇，参考风格如《赤伶》。」'''
                                    f"最终的输出，只需要有歌词就可以。 "},

    ],
    return generate_lyrics(messages)


# 根据要求生成歌词函数
def generate_lyrics_with_requires(theme, lyrics_requires):
    messages = [
        {"role": "user", "content": "作为一名华语作词专家，请为我写一首歌曲"},
        {"role": "assistant", "content": "当然，要创作歌词，请告诉我一些你的想法"},
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
        url = BASE_URL + "/_open/luno/music/generate"  # 假设Luno模型的接口路径
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
    st.title("智韵创音")

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
        st.write("如有更多疑问，可访问我们的[帮助页面](https://example.com/help )获取详细指南。")

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
                "lyrics_requires_placeholder": "请输入歌词要求，如歌曲结构、押韵、具体歌词片段等",
                "generate_lyrics_button": "生成歌词",
                "music_generation": "音乐生成",
                "lyrics_placeholder": "请输入歌词",
                "instrumental_requirements": "生成纯音乐要求",
                "title_placeholder": "请输入歌曲名称",
                "create_music_button": "创作音乐",
                "ringtone_creation": "铃声制作",
                "upload_file": "请选择音乐文件上传",
                "highlight_duration": "铃声部分时长（秒）",
                "extract_button": "点击制作铃声",
                "golden_sentence": "金句推荐",
                "generate_golden_sentence_button": "生成金句",
                "footer": "© 2024 最终版权刘昱樟所有 “智韵创音”音乐生成器",
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
                "success_extract_music_highlight": "成功提取音乐高潮部分，文件保存在: {}",
                "failure_extract_music_highlight": "提取音乐高潮部分失败。",
                "luno_unavailable": "目前 a 10.5s 模型使用人数过多，请选择 f 12 模型。"
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
                "luno_unavailable": "Currently, the luno model is unavailable. Please select the suno model."
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
            "suno": "f 12.5（高质量）",
            "luno": "a 10.5s（快！）"
        }
        model_choice_display = st.selectbox("选择模型", list(model_display_mapping.values()))
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
            if model_choice == "luno":
                st.warning(get_text("luno_unavailable"))
            else:
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
                            # 使用大模型随机生成与青海有关的故事短句
                            qinghai_story_prompt = "随机生成一个与青海有关的故事短句，要求文字优美、富有画面感，长度不超过30字，与青海的自然风光或民族文化相关"
                            qinghai_story = generate_text(qinghai_story_prompt)
                            if qinghai_story:
                                st.write(qinghai_story)
                            else:
                                st.write("青海湖的湛蓝湖水映着霞光，候鸟飞翔诉说情长。")
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
            golden_sentence = generate_text("生成一句富有哲理或情感的金句，和青海文旅对题。要求简洁优美，具有启发性。")
            if golden_sentence:
                st.write(golden_sentence)
            else:
                st.warning("生成金句失败，请稍后再试。")

    # 底部版权
    st.markdown(f"<footer>{get_text('footer')}</footer>", unsafe_allow_html=True)


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

# 添加一些CSS样式优化界面平衡
st.markdown("""
<style>
    body {
        background: linear-gradient(to bottom right, #e0e0e0, #f5f5f5); 
        background-size: cover;
        font-family: 'Roboto', sans-serif; 
    }

   .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 15px 32px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        cursor: pointer;
        transition: background-color 0.3s;
    }

   .stButton > button:hover {
        background-color: #388E3C;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
    }

    h1 {
        font-size: 32px;
        color: #388E3C;
        text-align: center;
        margin-bottom: 20px;
    }

   .card {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 30px;
        margin: 15px 0;
    }

   .stTextInput,.stTextArea {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 10px;
    }

   .stTextInput input:focus,.stTextArea textarea:focus {
        border-color: #4CAF50;
        outline: none;
    }

    footer {
        text-align: center;
        color: gray;
        margin-top: 30px;
        padding: 10px;
        border-top: 2px solid #e6e6e6;
    }

   .music-play-button {
        background-color: #FFC107; 
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        border-radius: 5px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); 
        transition: background-color 0.3s;
    }

   .music-play-button:hover {
        background-color: #FFA000; 
    }

   .music-list-item {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

   .music-song-name {
        font-family: 'Arial', sans-serif;
        color: #333;
        font-size: 16px;
    }

   .music-action-button {
        background-color: #607D8B;
        color: white;
        border: none;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 12px;
        border-radius: 3px;
        cursor: pointer;
        margin-left: 10px;
        transition: background-color 0.3s;
    }

   .music-action-button:hover {
        background-color: #455A64; 
    }

   .card-header {
        font-size: 1.5em;
        color: #388E3C;
    }

   .music-player-container {
        margin-top: 10px;
        text-align: center;
    }

   .stButton > button:disabled {
        background-color: #BDBDBD;
        cursor: not-allowed;
    }

</style>
""", unsafe_allow_html=True)