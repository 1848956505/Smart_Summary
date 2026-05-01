import json
import os
import random
from pathlib import Path


def project_record(record, fields_to_keep=None):
    if fields_to_keep is None:
        return record

    return {field: record.get(field) for field in fields_to_keep if field in record}


def merge_and_shuffle_datasets(input_dir, output_file, fields_to_keep=None):
    combined_data = []

    if not os.path.exists(input_dir):
        print(f'错误：找不到文件夹 {input_dir}')
        return

    files = [f for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    if not files:
        print(f'警告：在 {input_dir} 文件夹下没有找到任何 .jsonl 文件')
        return

    print(f'找到以下文件：{files}')

    for file_name in files:
        file_path = os.path.join(input_dir, file_name)
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        combined_data.append(project_record(record, fields_to_keep))
                        count += 1
                    except json.JSONDecodeError:
                        print(f'跳过无效行：{file_name}')
            print(f'✅ 已加载 {file_name}，共 {count} 条数据')
        except Exception as e:
            print(f'读取 {file_name} 时出错：{e}')

    print('🎉 正在打乱数据顺序...')
    random.shuffle(combined_data)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print('\n✅ 转换成功！')
        print(f'📊 总计处理数据：{len(combined_data)} 条')
        print(f'📑 输出文件路径：{output_file}')
    except Exception as e:
        print(f'写入文件时出错：{e}')


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent
    INPUT_FOLDER = str(BASE_DIR / 'generated_data_v8_3')
    OUTPUT_JSON = str(BASE_DIR / 'train_data_v8.3.json')

    # 设为 ['instruction', 'input', 'output'] 可只导出这三个字段；
    # 设为 None 可保留全部字段。
    FIELDS_TO_KEEP = ['instruction', 'input', 'output']

    merge_and_shuffle_datasets(INPUT_FOLDER, OUTPUT_JSON, FIELDS_TO_KEEP)
