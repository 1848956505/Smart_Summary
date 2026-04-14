import json
import random
import time
import os
import sys
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from openai import OpenAI
import configv8_0 as config

# 设置随机种子确保可复现性
random.seed(config.RANDOM_SEED)

# --- 初始化客户端（每个进程独立初始化）---
def init_client():
    return OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

# --- 配置与常量 ---
STYLE_MAP = {
    "Feishu": config.FEISHU_EXPERT_PROMPT,
    "DingTalk": config.DINGTALK_EXPERT_PROMPT,
    "QiWei": config.QIWEI_EXPERT_PROMPT
}

# --- 加载种子库 ---
with open(config.SEED_FILE, "r", encoding="utf-8") as f:
    TASK_SEEDS_DB = json.load(f)
FLAT_ROLES = list(TASK_SEEDS_DB.keys())

# def inject_noise(input_text):
#     """注入各种噪声增强数据真实性"""
#     # 1. 拼写错误噪声
#     if random.random() < config.TYPO_NOISE_PROB:
#         for correct, typos in config.TYPO_MAPPINGS.items():
#             if correct in input_text and random.random() < 0.3:
#                 typo = random.choice(typos)
#                 input_text = input_text.replace(correct, typo)
    
#     # 2. 情感噪声
#     if random.random() < config.EMOTION_NOISE_PROB:
#         emotion_word = random.choice(config.EMOTION_WORDS)
#         # 随机插入到文本开头、中间或结尾
#         insert_pos = random.choice(['start', 'middle', 'end'])
#         if insert_pos == 'start':
#             input_text = f"{emotion_word}，{input_text}"
#         elif insert_pos == 'middle':
#             words = input_text.split('，')
#             if len(words) > 1:
#                 insert_idx = random.randint(1, len(words)-1)
#                 words.insert(insert_idx, emotion_word)
#                 input_text = '，'.join(words)
#         else:
#             input_text = f"{input_text} {emotion_word}"
    
#     # 3. 信息不完整
#     if random.random() < config.INCOMPLETE_INFO_PROB:
#         # 随机删除部分句子
#         sentences = [s.strip() for s in input_text.split('。') if s.strip()]
#         if len(sentences) > 2:
#             remove_idx = random.randint(0, len(sentences)-1)
#             sentences.pop(remove_idx)
#             input_text = '。'.join(sentences) + '。'
    
#     # 4. 名称提及
#     if random.random() < config.NAME_MENTION_PROB:
#         name_mention = random.choice(config.NAME_MENTION_POOL)
#         input_text = f"{name_mention}：{input_text}"
    
#     return input_text

def generate_single_sample(style_name, prompt_template, sample_idx):
    """单条数据生成逻辑（独立函数便于多进程）"""
    client = init_client()  # 每个进程有自己的客户端
    
    for attempt in range(config.MAX_RETRIES):
        try:
            role = random.choice(FLAT_ROLES)
            scenario = random.choice(config.SCENARIO_POOL)
            temporal_pattern = random.choice(config.TEMPORAL_PATTERNS)
            instruction = random.choice(config.INSTRUCTION_POOL)
            
            # 使用配置中的种子数范围
            num_seeds = random.randint(config.SEEDS_PER_SAMPLE_MIN, config.SEEDS_PER_SAMPLE_MAX)
            seeds = random.sample(TASK_SEEDS_DB[role], min(num_seeds, len(TASK_SEEDS_DB[role])))
            task_seeds_str = "\n".join([f"- {s}" for s in seeds])
            
            # 常规任务注入
            routine_task = random.choice(config.ROUTINE_TASKS) if random.random() < config.ROUTINE_TASK_PROB else "无额外琐事"
            
            # 长度风格
            length_rng = random.random()
            if length_rng < 0.2:
                length_desc = "极其简短，控制在50字以内，只说核心点，口语化严重。"
            elif length_rng < 0.8:
                length_desc = "中等长度，300-500字左右，包含适量的口语碎碎念和背景描述。"
            else:
                length_desc = "非常冗长啰嗦，500字以上，包含大量细节、工作事项、吐槽和无关琐事，考验提取能力。"
            
            # 在这里注入提示词
            formatted_prompt = prompt_template.format(
                role=role,
                scenario=scenario,
                task_seeds=task_seeds_str,
                routine_task=routine_task,
                temporal_pattern=temporal_pattern,
                instruction=instruction,
                style_name=style_name,
                length_requirement=length_desc
                name_mention_prob = name_mention_prob,
                typo_noise_prob = typo_noise_prob,
                emotion_noise_prob = emotion_noise_prob,
                incomplete_info_prob = incomplete_info_prob
            )
            
            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": "请按照JSON格式要求输出合成数据。"}
                ],
                response_format={"type": "json_object"},
                temperature=config.TEMPERATURE,
                top_p=config.TOP_P,
                seed=config.RANDOM_SEED + sample_idx  # 确保每个样本有可复现的种子
            )
            
            res_json = json.loads(response.choices[0].message.content)
            
            # # 注入噪声
            # noisy_input = inject_noise(res_json["input"])
            # res_json["input"] = noisy_input
            
            return {
                "instruction": f"{instruction} (风格要求：{style_name})",
                "input": res_json["input"],
                "output": res_json["output"],
                "meta": {
                    "style": style_name,
                    "role": role,
                    "seeds": seeds,
                    "scenario": scenario[:15],
                    "sample_idx": sample_idx
                }
            }
            
        except Exception as e:
            print(f"\n⚠️ 出错 [{style_name}] 样本 {sample_idx} 尝试 {attempt+1}: {e}")
            time.sleep(2)
    
    return None

def generate_style_samples(style_name, prompt_template, total_samples):
    """生成指定风格的所有样本（多进程版本）"""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
    
    output_file = os.path.join(config.OUTPUT_DIR, config.OUTPUT_FILE_PATTERN.format(style=style_name.lower()))
    print(f"\n📂 正在生成 {style_name} 风格数据 -> {output_file}")
    print(f"   🔄 使用 {config.NUM_WORKERS} 个进程并行处理...")
    
    success_count = 0
    pbar = tqdm(total=total_samples, desc=f"{style_name}")
    
    # 使用追加模式，防止程序崩溃后数据丢失
    with open(output_file, "a", encoding="utf-8") as f:
        # 创建进程池
        with ProcessPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
            # 提交所有任务
            future_to_idx = {
                executor.submit(generate_single_sample, style_name, prompt_template, idx): idx 
                for idx in range(total_samples)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    sample = future.result()
                    if sample:
                        f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                        f.flush()
                        success_count += 1
                        pbar.update(1)
                    else:
                        print(f"\n❌ 样本 {idx} 生成失败，重试中...")
                        # 重试失败的样本
                        retry_sample = generate_single_sample(style_name, prompt_template, idx)
                        if retry_sample:
                            f.write(json.dumps(retry_sample, ensure_ascii=False) + "\n")
                            f.flush()
                            success_count += 1
                            pbar.update(1)
                except Exception as e:
                    print(f"\n🔥 进程处理样本 {idx} 时出错: {e}")
    
    pbar.close()
    return success_count

def main():
    print(f"🚀 开始全量数据合成任务 | 目标：{len(STYLE_MAP)}种风格 x {config.SAMPLES_PER_STYLE}条")
    print(f"   ⚙️  配置: 温度={config.TEMPERATURE}, Top-p={config.TOP_P}, 随机种子={config.RANDOM_SEED}")
    print(f"   🏃  并行度: {config.NUM_WORKERS} 个进程")
    
    # 为每种风格创建独立的进程池
    for style_name, prompt_template in STYLE_MAP.items():
        success_count = generate_style_samples(style_name, prompt_template, config.SAMPLES_PER_STYLE)
        print(f"✅ {style_name} 风格完成: {success_count}/{config.SAMPLES_PER_STYLE} 条")
    
    print(f"\n✨ 所有数据合成完毕！请在 {config.OUTPUT_DIR} 文件夹中查看结果。")

if __name__ == "__main__":
    main()