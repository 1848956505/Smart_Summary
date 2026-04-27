# =====【革命性升级】种子生成提示词（学术级严谨）=====
SEED_PROMPT_TEMPLATE = """
你是一名拥有10年经验的互联网行业专家。请为【{role}】岗位生成20个高保真日常工作事件（Task Seeds）。

# 核心要求（违反任一将导致数据无效）
## 1. 资历梯度（强制分布）
- 初级事件(3个)：含"在导师指导下"、"学习配置"、"首次接触"等表述
- 中级事件(10个)：独立负责模块，含技术细节与量化结果
- 资深事件(7个)：含"主导方案设计"、"决策技术选型"、"带3人小组"等

## 2. 事件类型多样性
- 技术攻坚(70%)：含具体技术栈（如JVM调优/React Hooks）
- 软技能(20%)：跨团队协调、需求评审、知识分享
- 工具链演进(10%)：技术迁移（Selenium→Playwright）、流程优化

## 3. 数据伦理规范（学术红线！）
✅ 保留：技术指标（响应时间0.5s、错误率2%、mAP 0.85）
❌ 脱敏：业务金额→[金额]、用户数→[用户规模]、公司名→[某公司]、人名→[相关人员]

## 4. 真实性增强
- 20%事件含模糊表述（"性能有所提升"、"部分用户反馈"）
- ≥3个失败案例（"AB测试p>0.05"、"方案被驳回"）
- 包含具体冲突（"需求临时变更"、"线上P0故障"）

## 5. 格式规范
- 字数：30-60中文字符（含标点）
- 禁止出现："示例"、"具体数字"、"假设"等占位表述
- 每个事件必须是完整句子

# 输出格式（严格JSON，无额外说明）
{{ "seeds": ["事件1", "事件2", ...] }}
"""

import json
import time
import re
from tqdm import tqdm
from openai import OpenAI
import config_v6 as config

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

# =====【新增】敏感词脱敏库（学术伦理必备）=====
SENSITIVE_PATTERNS = [
    (r"(腾讯|阿里|字节|百度|京东|美团|拼多多|华为|小米|微软|谷歌)", "[某公司]"),
    (r"(\d{4,}万|百万|千万|亿元)", "[金额]"),  # 业务金额脱敏
    (r"(\d{5,}用户|万级用户)", "[用户规模]"),
    (r"(张三|李四|王五|赵六|领导|老板)", "[相关人员]"),
    (r"(北京|上海|深圳|杭州)总部", "[某地]总部")
]

def sanitize_seed(seed: str) -> str:
    """学术伦理脱敏：自动替换敏感信息，保留技术指标"""
    for pattern, repl in SENSITIVE_PATTERNS:
        seed = re.sub(pattern, repl, seed)
    # 保留技术指标（响应时间/错误率等关键数字）
    seed = re.sub(r"([0-9.]+)s", r"\1秒", seed)  # 统一单位表述
    return seed.strip()

def validate_seed(seed: str) -> tuple[bool, str]:
    """种子质量三重校验"""
    if len(seed) < 25 or len(seed) > 65:  # 容忍±5字浮动
        return False, "LENGTH"
    if "具体数字" in seed or "示例" in seed.lower():  # 防模型偷懒
        return False, "PLACEHOLDER"
    if seed.count("，") + seed.count("。") < 1:  # 至少1个标点
        return False, "PUNCTUATION"
    return True, "VALID"

def generate_seeds_for_role(role_name: str, max_retries=config.MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            # =====【关键升级】动态注入资历梯度提示=====
            seniority_hint = "（请混合生成：3个初级事件含'在导师指导下/学习中'，10个中级事件，7个资深事件含'主导/决策/带团队'）"
            prompt = SEED_PROMPT_TEMPLATE.format(role=role_name) + seniority_hint
            
            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "请严格按JSON格式输出，仅包含20个事件。"}
                ],
                temperature=0.85,  # 降低随机性提升稳定性
                max_tokens=1200,
                response_format={"type": "json_object"}
            )
            
            # =====【核心】解析+脱敏+验证流水线=====
            data = json.loads(response.choices[0].message.content)
            raw_seeds = data.get("seeds", [])
            
            # 脱敏处理（学术伦理红线）
            sanitized = [sanitize_seed(s) for s in raw_seeds if isinstance(s, str)]
            
            # 质量过滤（保留有效种子）
            valid_seeds, invalid_count = [], 0
            for seed in sanitized:
                is_valid, reason = validate_seed(seed)
                if is_valid:
                    valid_seeds.append(seed)
                else:
                    invalid_count += 1
            
            # 重试决策逻辑
            if len(valid_seeds) >= 15:  # 接受15-20个有效种子
                if invalid_count > 0:
                    print(f"  ⚠️ {role_name}: 过滤{invalid_count}条无效种子（长度/占位符问题）")
                return valid_seeds[:20]  # 严格截断至20
            
            print(f"  🔄 {role_name}: 有效种子不足({len(valid_seeds)}/15)，第{attempt+1}次重试...")
            time.sleep(config.SLEEP_TIME * (attempt + 1))
            
        except Exception as e:
            print(f"❌ {role_name} 生成失败 (尝试 {attempt+1}/{max_retries}): {type(e).__name__}")
            if "rate_limit" in str(e).lower():
                time.sleep(5)  # 速率限制特殊处理
            if attempt == max_retries - 1:
                return []
    
    return []

if __name__ == "__main__":
    print("🚀 阶段一启动：生成带资历梯度+伦理脱敏的高保真种子库...")
    print(f"📌 覆盖 {len(config.DETAILED_ROLES)} 大类 | {sum(len(v) for v in config.DETAILED_ROLES.values())} 细分岗位")
    
    all_seeds_db, stats = {}, {"total_roles": 0, "total_seeds": 0, "filtered": 0}
    flat_roles = [r for roles in config.DETAILED_ROLES.values() for r in roles]
    
    for role in tqdm(flat_roles, desc="生成中"):
        seeds = generate_seeds_for_role(role)
        if seeds:
            all_seeds_db[role] = seeds
            stats["total_roles"] += 1
            stats["total_seeds"] += len(seeds)
        time.sleep(config.SLEEP_TIME)
    
    # =====【新增】生成质量报告=====
    with open(config.SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(all_seeds_db, f, ensure_ascii=False, indent=2)
    
    # 保存元数据（答辩关键证据）
    meta = {
        "generation_config": {
            "model": config.MODEL_NAME,
            "total_roles": stats["total_roles"],
            "avg_seeds_per_role": round(stats["total_seeds"]/stats["total_roles"], 1),
            "sanitization_rules": [p[1] for p in SENSITIVE_PATTERNS],
            "validation_rules": ["25-65字符", "无占位符", "含标点"]
        },
        "sample_seeds": {
            "junior": [s for s in all_seeds_db.get(list(all_seeds_db.keys())[0], []) if "导师" in s or "学习" in s][:1],
            "senior": [s for s in all_seeds_db.get(list(all_seeds_db.keys())[0], []) if "主导" in s or "决策" in s][:1]
        }
    }
    with open(config.SEED_FILE.replace(".json", "_META.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ 阶段一完成！")
    print(f"✅ 有效岗位: {stats['total_roles']}/{len(flat_roles)}")
    print(f"✅ 生成种子: {stats['total_seeds']} 条 (平均 {meta['generation_config']['avg_seeds_per_role']}/岗)")
    print(f"✅ 脱敏规则: 业务金额/公司名/人名 → [占位符] | 技术指标保留")
    print(f"✅ 元数据报告: {config.SEED_FILE.replace('.json', '_META.json')}")
    print(f"\n💡 答辩提示：打开_META.json查看资历梯度样例与脱敏证据！")