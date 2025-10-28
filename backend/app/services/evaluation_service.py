"""评估服务 - 测试结果评估和工具调用匹配"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class EvaluationService:
    """测试结果评估服务"""
    
    @staticmethod
    def evaluate_result(
        output: str,
        expected_output: Optional[str],
        tool_calls: Optional[List[Dict[str, Any]]],
        expected_tool_calls: Optional[List[Dict[str, Any]]],
        evaluation_criteria: Optional[Dict[str, Any]] = None,
        evaluation_weights: Optional[Dict[str, int]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估测试结果
        
        Args:
            output: 模型输出
            expected_output: 期望输出
            tool_calls: 模型的工具调用
            expected_tool_calls: 期望的工具调用
            evaluation_criteria: 评估标准
            evaluation_weights: 评分权重配置 {tool_calls: 70, text_similarity: 20, custom_criteria: 10}
        
        Returns:
            (score, details) - 分数和详细信息
        """
        scores = {}
        details = {}
        
        # 使用默认权重或用户自定义权重
        if not evaluation_weights:
            evaluation_weights = {
                'tool_calls': 70,
                'text_similarity': 20,
                'custom_criteria': 10
            }
        
        # 1. 评估工具调用（如果有）
        if expected_tool_calls:
            tool_score, tool_details = EvaluationService._evaluate_tool_calls(
                tool_calls, expected_tool_calls
            )
            scores['tool_call'] = tool_score
            details['tool_calls'] = tool_details  # 注意：这里改为 tool_calls（复数）以匹配前端
            logger.info(f"📊 工具调用评分: {tool_score:.2f}")
        
        # 2. 评估文本输出（如果有期望输出）
        if expected_output:
            text_score = EvaluationService._evaluate_text_similarity(
                output, expected_output
            )
            scores['text_similarity'] = text_score
            details['text_similarity'] = {
                'score': text_score,
                'output_length': len(output),
                'expected_length': len(expected_output)
            }
            logger.info(f"📊 文本相似度: {text_score:.2f}")
        
        # 3. 应用自定义评估标准
        if evaluation_criteria:
            custom_score = EvaluationService._apply_custom_criteria(
                output, tool_calls, evaluation_criteria
            )
            scores['custom'] = custom_score
            details['custom_criteria'] = evaluation_criteria
            logger.info(f"📊 自定义评估: {custom_score:.2f}")
        
        # 计算总分（使用自定义权重或智能调整）
        if scores:
            # 根据实际评估的维度智能调整权重
            weights = {}
            total_weight = 0
            
            if 'tool_call' in scores:
                weights['tool_call'] = evaluation_weights.get('tool_calls', 70) / 100.0
                total_weight += evaluation_weights.get('tool_calls', 70)
            
            if 'text_similarity' in scores:
                weights['text_similarity'] = evaluation_weights.get('text_similarity', 20) / 100.0
                total_weight += evaluation_weights.get('text_similarity', 20)
            
            if 'custom' in scores:
                weights['custom'] = evaluation_weights.get('custom_criteria', 10) / 100.0
                total_weight += evaluation_weights.get('custom_criteria', 10)
            
            # 如果总权重不是100%（某些维度缺失），则归一化权重
            if total_weight > 0 and total_weight != 100:
                normalization_factor = 100.0 / total_weight
                weights = {k: v * normalization_factor for k, v in weights.items()}
                logger.info(f"⚖️  权重归一化: 实际总权重 {total_weight}% -> 归一化为 100%")
            
            total_score = sum(
                scores.get(key, 0) * weight 
                for key, weight in weights.items()
            )
            
            # 保存实际使用的权重到details
            details['weights_used'] = {k: round(v * 100, 2) for k, v in weights.items()}
        else:
            total_score = 0.0
        
        details['scores'] = scores
        details['total_score'] = total_score
        
        logger.info(f"✅ 总评分: {total_score:.2f}")
        
        return total_score, details
    
    @staticmethod
    def _evaluate_tool_calls(
        actual_calls: Optional[List[Dict[str, Any]]],
        expected_calls: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估工具调用的准确性
        
        评分维度：
        1. 名称匹配 (20分)
        2. 数量匹配 (20分)
        3. 参数名称匹配 (30分)
        4. 参数值匹配 (30分)
        """
        # 标准化工具调用格式为 {name, arguments}
        def normalize_tool_call(call):
            """将工具调用标准化为统一格式"""
            name = call.get('function', {}).get('name') or call.get('name')
            args = call.get('function', {}).get('arguments') or call.get('arguments', {})
            
            # 如果arguments是字符串，尝试解析
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except:
                    args = {}
            
            return {
                'name': name,
                'arguments': args
            }
        
        # 初始化详情，包含标准化后的期望和实际的工具调用
        normalized_expected = [normalize_tool_call(call) for call in (expected_calls or [])]
        normalized_actual = [normalize_tool_call(call) for call in (actual_calls or [])]
        
        details = {
            'expected': normalized_expected,
            'actual': normalized_actual,
            'name_match': 0.0,
            'count_match': 0.0,
            'params_match': 0.0,
            'values_match': 0.0
        }
        
        # 如果没有期望的工具调用，返回满分
        if not expected_calls:
            details['name_match'] = 20.0
            details['count_match'] = 20.0
            details['params_match'] = 30.0
            details['values_match'] = 30.0
            return 1.0, details
        
        # 如果没有实际调用工具
        if not actual_calls:
            return 0.0, details
        
        # 1. 名称匹配 (20分)
        expected_names = set(call['name'] for call in normalized_expected if call['name'])
        actual_names = set(call['name'] for call in normalized_actual if call['name'])
        
        if expected_names:
            name_match_ratio = len(expected_names & actual_names) / len(expected_names)
            details['name_match'] = name_match_ratio * 20.0
        else:
            details['name_match'] = 20.0
        
        # 2. 数量匹配 (20分)
        expected_count = len(normalized_expected)
        actual_count = len(normalized_actual)
        count_match_ratio = min(actual_count, expected_count) / expected_count if expected_count > 0 else 1.0
        details['count_match'] = count_match_ratio * 20.0
        
        # 3. 参数名称和值匹配 (60分)
        param_name_scores = []
        param_value_scores = []
        
        for expected in normalized_expected:
            expected_name = expected['name']
            expected_args = expected['arguments']
            
            # 查找匹配的实际调用
            best_param_name_score = 0.0
            best_param_value_score = 0.0
            
            for actual in normalized_actual:
                actual_name = actual['name']
                actual_args = actual['arguments']
                
                # 只比较同名工具
                if actual_name != expected_name:
                    continue
                
                # 参数名称匹配度
                if isinstance(expected_args, dict) and isinstance(actual_args, dict):
                    if expected_args:
                        # 检查所有期望的参数名称是否都存在
                        matching_keys = sum(1 for key in expected_args.keys() if key in actual_args)
                        param_name_score = matching_keys / len(expected_args)
                    else:
                        param_name_score = 1.0
                    
                    # 参数值匹配度
                    param_value_score = EvaluationService._compare_parameters(
                        actual_args, expected_args
                    )
                    
                    if param_name_score > best_param_name_score:
                        best_param_name_score = param_name_score
                    if param_value_score > best_param_value_score:
                        best_param_value_score = param_value_score
            
            param_name_scores.append(best_param_name_score)
            param_value_scores.append(best_param_value_score)
        
        # 计算平均参数匹配分数
        if param_name_scores:
            details['params_match'] = (sum(param_name_scores) / len(param_name_scores)) * 30.0
        else:
            details['params_match'] = 0.0
        
        if param_value_scores:
            details['values_match'] = (sum(param_value_scores) / len(param_value_scores)) * 30.0
        else:
            details['values_match'] = 0.0
        
        # 计算总分 (0-1)
        total_score = (
            details['name_match'] +
            details['count_match'] +
            details['params_match'] +
            details['values_match']
        ) / 100.0
        
        return total_score, details
    
    @staticmethod
    def _compare_parameters(
        actual_params: Dict[str, Any],
        expected_params: Dict[str, Any]
    ) -> float:
        """
        比较参数的相似度
        
        Returns:
            0.0-1.0的相似度分数
        """
        if not expected_params:
            return 1.0
        
        total_keys = len(expected_params)
        matched_keys = 0
        partial_matches = 0.0
        
        for key, expected_value in expected_params.items():
            if key not in actual_params:
                continue
            
            actual_value = actual_params[key]
            
            # 精确匹配
            if actual_value == expected_value:
                matched_keys += 1
            # 类型匹配但值不同
            elif type(actual_value) == type(expected_value):
                if isinstance(expected_value, str):
                    # 字符串相似度
                    similarity = SequenceMatcher(None, str(actual_value), str(expected_value)).ratio()
                    partial_matches += similarity * 0.5
                elif isinstance(expected_value, (int, float)):
                    # 数值相似度
                    if expected_value != 0:
                        diff_ratio = abs(actual_value - expected_value) / abs(expected_value)
                        similarity = max(0, 1 - diff_ratio)
                        partial_matches += similarity * 0.5
        
        score = (matched_keys + partial_matches) / total_keys if total_keys > 0 else 0.0
        return min(1.0, score)
    
    @staticmethod
    def _evaluate_text_similarity(output: str, expected: str) -> float:
        """
        评估文本相似度
        
        使用SequenceMatcher计算相似度
        """
        if not expected:
            return 1.0
        
        if not output:
            return 0.0
        
        similarity = SequenceMatcher(None, output.lower(), expected.lower()).ratio()
        return similarity
    
    @staticmethod
    def _apply_custom_criteria(
        output: str,
        tool_calls: Optional[List[Dict[str, Any]]],
        criteria: Dict[str, Any]
    ) -> float:
        """
        应用自定义评估标准
        
        支持的标准：
        - min_length: 最小输出长度
        - max_length: 最大输出长度
        - must_contain: 必须包含的关键词
        - must_not_contain: 不能包含的关键词
        - tool_must_call: 必须调用的工具名称列表
        """
        score = 1.0
        penalties = []
        
        # 长度检查
        if 'min_length' in criteria:
            min_len = criteria['min_length']
            if len(output) < min_len:
                penalty = 0.2
                score -= penalty
                penalties.append(f"输出长度不足 (最小:{min_len}, 实际:{len(output)})")
        
        if 'max_length' in criteria:
            max_len = criteria['max_length']
            if len(output) > max_len:
                penalty = 0.1
                score -= penalty
                penalties.append(f"输出长度超出 (最大:{max_len}, 实际:{len(output)})")
        
        # 关键词检查
        if 'must_contain' in criteria:
            keywords = criteria['must_contain']
            if isinstance(keywords, str):
                keywords = [keywords]
            for keyword in keywords:
                if keyword not in output:
                    penalty = 0.2 / len(keywords)
                    score -= penalty
                    penalties.append(f"缺少关键词: {keyword}")
        
        if 'must_not_contain' in criteria:
            keywords = criteria['must_not_contain']
            if isinstance(keywords, str):
                keywords = [keywords]
            for keyword in keywords:
                if keyword in output:
                    penalty = 0.2 / len(keywords)
                    score -= penalty
                    penalties.append(f"包含禁止关键词: {keyword}")
        
        # 工具调用检查
        if 'tool_must_call' in criteria:
            required_tools = criteria['tool_must_call']
            if isinstance(required_tools, str):
                required_tools = [required_tools]
            
            called_tools = []
            if tool_calls:
                called_tools = [
                    call.get('function', {}).get('name') or call.get('name')
                    for call in tool_calls
                ]
            
            for tool_name in required_tools:
                if tool_name not in called_tools:
                    penalty = 0.3 / len(required_tools)
                    score -= penalty
                    penalties.append(f"未调用必需工具: {tool_name}")
        
        if penalties:
            logger.warning(f"自定义标准检查失败: {', '.join(penalties)}")
        
        return max(0.0, score)
