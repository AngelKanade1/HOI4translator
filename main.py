import os
import re
import json
import requests
from tkinter import filedialog, messagebox, Tk, Label, Entry, Button, IntVar
from tkinter import ttk
from urllib import request
from urllib import parse
import json
import hashlib


# 彩云ai调用
def tran(text, url, token):
    headers = {
        'content-type': "application/json",
        'x-authorization': "token " + token,
    }
    special_char_pattern = r'(\§.*?§|£[\S\s]*|\\n|\[.*?\]|\(.*?\))'
    parts = re.split(special_char_pattern, text)
    translated_parts = []
    for part in parts:
        if not re.match(special_char_pattern, part):
            if now_api == 0:
                tranType = "en2zh"
                if toEnglish:
                    tranType = "zh2en"
                payload = {
                    "source": part,
                    "trans_type": tranType,
                    "request_id": "demo",
                }
                response = requests.request(
                    "POST", url, data=json.dumps(payload), headers=headers)
                if response.status_code == 200:
                    resp = json.loads(response.text)['target']
                    translated_parts.append(resp)
                else:
                    translated_parts.append(part)
            else:
                try:
                    if text:
                        translated_parts.append(translate_Word(text))
                except Exception as e:
                    print(e)
                    error_log = str(e)
                    with open(f"{output_folder_entry.get()}/error_log.txt", "a") as f:
                        f.write(error_log+"\n")
                        print("错误日志已保存在文件夹中")
        else:
            translated_parts.append(part)
    translated_text = ''.join(translated_parts)
    return translated_text

#百度api调用
def translate_Word(en_str):
    lang = "zh"
    if toEnglish:
        lang = "en"
    URL='http://api.fanyi.baidu.com/api/trans/vip/translate'
    From_Data={}
    From_Data['from']='auto'
    From_Data['to']=lang
    From_Data['q']=en_str
    From_Data['appid']=appid_entry.get()
    From_Data['salt']='1435660288'
    Key=key_entry.get()
    m=From_Data['appid']+en_str+From_Data['salt']+Key
    m_MD5=hashlib.md5(m.encode('utf8'))
    From_Data['sign']=m_MD5.hexdigest()

    data=parse.urlencode(From_Data).encode('utf-8')
                                        
    response=request.urlopen(URL,data)  
    html=response.read().decode('utf-8')
    translate_results=json.loads(html)  
    translate_results=translate_results['trans_result'][0]['dst']

    return translate_results


def translate_file(source_file_path, target_file_path, url, token, progress_bar, current_value):
    try:
        with open(source_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if "l_english" in line:
                    line = line.replace("l_english","l_simp_chinese")
                    file.write(line)
                    continue
                if "l_simp_chinese" in line:
                    line = line.replace("l_simp_chinese","l_english")
                    file.write(line)
                    continue
                if '"' in line:
                    parts = line.split('"')
                    for i in range(1, len(parts), 2):
                        parts[i] = tran(parts[i], url, token)
                    line = '"'.join(parts)
                file.write(line)
                root.update()
    except Exception as e:
        messagebox.showerror(
            "Error", f"Could not process file {source_file_path}: {e}")

    current_value.set(current_value.get() + 1)
    progress_bar['value'] = current_value.get()
    print("finish a file")
    root.update()


def translate_directory(source_directory, target_directory, url, token, progress_bar, current_value):
    count = 0
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.yml'):
                count += 1
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(
                    source_file_path, source_directory)
                target_file_path = os.path.join(
                    target_directory, relative_path)
                translate_file(source_file_path, target_file_path,
                               url, token, progress_bar, current_value)
    messagebox.showinfo("Completed", "Translation completed successfully!")
    if not toEnglish:
        rename_files_in_folder(target_directory, "english", "simp_chinese")
    else:
        rename_files_in_folder(target_directory, "simp_chinese", "english")


def rename_files_in_folder(folder_path, old_str, new_str):
    for subdir, dirs, files in os.walk(folder_path):
        for file_name in files:
            if old_str in file_name:
                old_path = os.path.join(subdir, file_name)
                new_file_name = file_name.replace(old_str, new_str)
                new_path = os.path.join(subdir, new_file_name)
                os.rename(old_path, new_path)


def get_total_file_count(directory, file_extension):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                count += 1
    return count


def start_translation():
    source_path = source_folder_entry.get()
    output_path = output_folder_entry.get()
    if not (source_path and output_path):
        messagebox.showwarning("Warning", "Please fill all the fields!")
    else:
        total_files = get_total_file_count(source_path, '.yml')
        progress_bar['maximum'] = total_files
        current_value.set(0)
        tran_button.destroy()
        root.update()
        translate_directory(source_path, output_path, url, token, progress_bar, current_value)
        
        
def switch_api():
    global now_api
    if now_api == 0:
        api_label.grid_remove()
        token_entry.grid_remove()
        appid_label.grid(row=0, column=0, padx=0,sticky='w')
        appid_entry.grid(row=0, column=1, padx=0, pady=5, sticky='w')
        baidu_key.grid(row=0, column=2, padx=0,sticky='w')
        key_entry.grid(row=0, column=3, padx=0, pady=5, sticky='w')
        now_api = 1
        switch_api_button.config(text = "切换为彩云ai")
    else:
        appid_label.grid_remove()
        appid_entry.grid_remove()
        baidu_key.grid_remove()
        key_entry.grid_remove()
        api_label.grid(row=0, column=0, sticky='w')
        token_entry.grid(row=0, column=1, padx=5, pady=5)
        now_api = 0
        switch_api_button.config(text = "切换为百度api")
        
def switch_lang():
    global toEnglish
    if not toEnglish:
        toEnglish = True
        which_button.config(text = "中译英")
    else:
        toEnglish = False
        which_button.config(text = "英译中")

url = "http://api.interpreter.caiyunai.com/v1/translator"
token = ""

# 创建主窗口
root = Tk()
root.title("Translation Tool")
now_api = 0
toEnglish = False

# UI区
api_label = Label(root, text="彩云API Token:")
api_label.grid(row=0, column=0, sticky='w')
token_entry = Entry(root, width=50)
token_entry.grid(row=0, column=1, padx=5, pady=5)

Label(root, text="选择目标文件夹:").grid(row=1, column=0, sticky='w')
source_folder_entry = Entry(root, width=50)
source_folder_entry.grid(row=1, column=1, padx=5, pady=5)
Button(root, text="浏览...", command=lambda: source_folder_entry.insert(
    0, filedialog.askdirectory())).grid(row=1, column=2, padx=5, pady=5)

Label(root, text="选择输出文件夹:").grid(row=2, column=0, sticky='w')
output_folder_entry = Entry(root, width=50)
output_folder_entry.grid(row=2, column=1, padx=5, pady=5)
Button(root, text="浏览...", command=lambda: output_folder_entry.insert(
    0, filedialog.askdirectory())).grid(row=2, column=2, padx=5, pady=5)

which_button = Button(root, text="英译中", command=switch_lang)
which_button.grid(row=3, column=0, pady=10)

tran_button = Button(root, text="开始翻译", command=start_translation)
tran_button.grid(row=3, column=1, pady=10)

switch_api_button = Button(root, text="切换为百度api", command=switch_api)
switch_api_button.grid(row=3, column=2, pady=10)

appid_label = Label(root, text="百度appid:")
appid_entry = Entry(root, width=40)
baidu_key = Label(root, text="百度key:")
key_entry = Entry(root, width=40)

# Create progress bar
current_value = IntVar(value=0)
progress_bar = ttk.Progressbar(root, variable=current_value, maximum=100)
progress_bar.grid(row=4, column=0, columnspan=3, pady=10,
                  padx=5, sticky="ew")

# Run the main loop
root.mainloop()
