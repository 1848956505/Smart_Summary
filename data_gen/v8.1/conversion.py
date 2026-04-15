import json
import random
import os

def merge_and_shuffle_datasets(input_dir, output_file):
    combined_data = []
    
    # 1. 扫描文件夹下所有的 jsonl 文件
    if not os.path.exists(input_dir):
        print(f"❌ 错误：找不到文件夹 {input_dir}")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    
    if not files:
        print(f"⚠️ 警告：在 {input_dir} 文件夹下没有找到任何 .jsonl 文件")
        return

    print(f"🔍 找到以下文件：{files}")

    # 2. 读取所有文件内容
    for file_name in files:
        file_path = os.path.join(input_dir, file_name)
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            combined_data.append(json.loads(line))
                            count += 1
                        except json.JSONDecodeError:
                            print(f"跳过无效行：{file_name}")
            print(f"✅ 已加载 {file_name}：{count} 条数据")
        except Exception as e:
            print(f"❌ 读取 {file_name} 时出错: {e}")

    # 3. 核心步骤：打乱顺序
    # 使用 random.shuffle 直接原地打乱列表
    print("🎲 正在打乱数据顺序...")
    random.shuffle(combined_data)

    # 4. 导出为单个 JSON 文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"\n✨ 转换成功！")
        print(f"📊 总计处理数据：{len(combined_data)} 条")
        print(f"💾 输出文件路径：{output_file}")
    except Exception as e:
        print(f"❌ 写入文件时出错: {e}")

if __name__ == "__main__":
    # 配置路径
    INPUT_FOLDER = 'generated_data_v8'      # 你的生成的 jsonl 文件夹
    OUTPUT_JSON = 'train_data_v8.json'  # 最终合并后的文件名
    
    merge_and_shuffle_datasets(INPUT_FOLDER, OUTPUT_JSON)