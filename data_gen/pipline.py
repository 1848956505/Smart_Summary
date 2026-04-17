import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from tqdm import tqdm

import configv8_2 as config


random.seed(config.RANDOM_SEED)


PROMPT_MAP = {
    'from': config.FROM_PROMPT,
    'list': config.LIST_PROMPT,
}

STYLE_LABEL_MAP = {
    'from': '表格风格',
    'list': '列表风格',
}


def get_enabled_styles():
    enabled_styles = getattr(config, 'ENABLED_STYLES', list(PROMPT_MAP.keys()))
    invalid_styles = [style for style in enabled_styles if style not in PROMPT_MAP]
    if invalid_styles:
        raise ValueError(f'Unsupported style keys in ENABLED_STYLES: {invalid_styles}')
    return enabled_styles


class SafeFormatDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def init_client():
    return OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


with open(config.SEED_FILE, 'r', encoding='utf-8') as f:
    TASK_SEEDS_DB = json.load(f)

FLAT_ROLES = list(TASK_SEEDS_DB.keys())


def build_prompt(prompt_template, role, scenario, task_seeds, routine_task, temporal_pattern, instruction):
    return prompt_template.format_map(
        SafeFormatDict(
            role=role,
            scenario=scenario,
            task_seeds=task_seeds,
            routine_task=routine_task,
            temporal_pattern=temporal_pattern,
            instruction=instruction,
            name_mention_prob=config.NAME_MENTION_PROB,
            typo_noise_prob=config.TYPO_NOISE_PROB,
            emotion_noise_prob=config.EMOTION_NOISE_PROB,
            incomplete_info_prob=config.INCOMPLETE_INFO_PROB,
        )
    )


def generate_single_sample(style_name, prompt_template, sample_idx):
    rng = random.Random(config.RANDOM_SEED + sample_idx)
    client = init_client()
    style_label = STYLE_LABEL_MAP.get(style_name, style_name)

    for attempt in range(config.MAX_RETRIES):
        try:
            role = rng.choice(FLAT_ROLES)
            scenario = rng.choice(config.SCENARIO_POOL)
            temporal_pattern = rng.choice(config.TEMPORAL_PATTERNS)
            instruction_base = rng.choice(config.INSTRUCTION_POOL)
            instruction = f'{instruction_base}（当前周报风格：{style_label}）'

            num_seeds = rng.randint(config.SEEDS_PER_SAMPLE_MIN, config.SEEDS_PER_SAMPLE_MAX)
            seeds = rng.sample(TASK_SEEDS_DB[role], min(num_seeds, len(TASK_SEEDS_DB[role])))
            task_seeds_str = '\n'.join(f'- {seed}' for seed in seeds)

            routine_task = rng.choice(config.ROUTINE_TASKS) if rng.random() < config.ROUTINE_TASK_PROB else ''

            formatted_prompt = build_prompt(
                prompt_template,
                role,
                scenario,
                task_seeds_str,
                routine_task,
                temporal_pattern,
                instruction,
            )

            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {'role': 'system', 'content': formatted_prompt},
                    {'role': 'user', 'content': '请按 JSON 格式输出。'},
                ],
                response_format={'type': 'json_object'},
                temperature=config.TEMPERATURE,
                top_p=config.TOP_P,
                seed=config.RANDOM_SEED + sample_idx,
            )

            res_json = json.loads(response.choices[0].message.content)
            return {
                'instruction': instruction,
                'input': res_json['input'],
                'output': res_json['output'],
                'meta': {
                    'style': style_name,
                    'role': role,
                    'seeds': seeds,
                    'scenario': scenario[:15],
                    'sample_idx': sample_idx,
                },
            }

        except Exception as exc:
            print(f'\n出错 [{style_name}] 样本 {sample_idx} 尝试 {attempt + 1}: {exc}')
            time.sleep(config.SLEEP_TIME)

    return None


def generate_style_samples(style_name, prompt_template, total_samples):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(
        config.OUTPUT_DIR,
        config.OUTPUT_FILE_PATTERN.format(style=style_name),
    )

    print(f'\n正在生成 {style_name} 风格数据 -> {output_file}')
    print(f'   使用 {config.NUM_WORKERS} 个线程并行处理...')

    success_count = 0
    pbar = tqdm(total=total_samples, desc=style_name)

    with open(output_file, 'a', encoding='utf-8') as f:
        with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
            future_to_idx = {
                executor.submit(generate_single_sample, style_name, prompt_template, idx): idx
                for idx in range(total_samples)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    sample = future.result()
                    if sample is None:
                        print(f'\n样本 {idx} 生成失败，重试一次...')
                        sample = generate_single_sample(style_name, prompt_template, idx)

                    if sample is None:
                        print(f'\n样本 {idx} 仍然失败。')
                        continue

                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
                    f.flush()
                    success_count += 1
                    pbar.update(1)
                except Exception as exc:
                    print(f'\n处理样本 {idx} 时出错: {exc}')

    pbar.close()
    return success_count


def main():
    enabled_styles = get_enabled_styles()
    enabled_prompt_map = {style: PROMPT_MAP[style] for style in enabled_styles}

    print(f'开始全量数据合成任务 | 目标：{len(enabled_prompt_map)} 种风格 x {config.SAMPLES_PER_STYLE} 条')
    print(f'   启用风格：{", ".join(enabled_styles)}')
    print(f'   配置: 温度={config.TEMPERATURE}, Top-p={config.TOP_P}, 随机种子={config.RANDOM_SEED}')
    print(f'   并行度: {config.NUM_WORKERS} 个线程')

    for style_name, prompt_template in enabled_prompt_map.items():
        success_count = generate_style_samples(style_name, prompt_template, config.SAMPLES_PER_STYLE)
        print(f'{style_name} 风格完成: {success_count}/{config.SAMPLES_PER_STYLE} 条')

    print(f'\n所有数据合成完毕！请在 {config.OUTPUT_DIR} 文件夹中查看结果。')


if __name__ == '__main__':
    main()
