import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class MemoryModule:
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading memory: {e}")
                return self._create_default_memory()
        else:
            return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict[str, Any]:
        return {
            "test_patterns": {},
            "function_contexts": {},
            "diff_patterns": {},
            "coverage_gaps": {},
            "prompt_effectiveness": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_memory(self):
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving memory: {e}")
    
    def store_test_pattern(self, function_name: str, function_signature: str, 
                          test_code: str, coverage_score: float = None, 
                          mutation_score: float = None):
        pattern_key = f"{function_name}_{hash(function_signature) % 10000}"
        
        self.memory["test_patterns"][pattern_key] = {
            "function_name": function_name,
            "function_signature": function_signature,
            "test_code": test_code,
            "coverage_score": coverage_score,
            "mutation_score": mutation_score,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        self._save_memory()
    
    def get_similar_test_patterns(self, function_signature: str, limit: int = 3) -> List[Dict[str, Any]]:
        similar_patterns = []
        
        for pattern_key, pattern in self.memory["test_patterns"].items():
            if self._calculate_signature_similarity(function_signature, pattern["function_signature"]) > 0.5:
                similar_patterns.append(pattern)
        
        similar_patterns.sort(key=lambda x: (x.get("usage_count", 0), x.get("coverage_score", 0)), reverse=True)
        
        return similar_patterns[:limit]
    
    def _calculate_signature_similarity(self, sig1: str, sig2: str) -> float:
        params1 = self._extract_parameter_types(sig1)
        params2 = self._extract_parameter_types(sig2)
        
        if not params1 or not params2:
            return 0.0
        
        common_params = set(params1) & set(params2)
        total_params = set(params1) | set(params2)
        
        return len(common_params) / len(total_params) if total_params else 0.0
    
    def _extract_parameter_types(self, signature: str) -> List[str]:
        try:
            if '(' in signature and ')' in signature:
                params_str = signature.split('(')[1].split(')')[0]
                return [p.strip().split(':')[1].strip() if ':' in p else 'any' for p in params_str.split(',') if p.strip()]
        except:
            pass
        return []
    
    def store_function_context(self, function_name: str, file_path: str, 
                              diff_context: str, module_context: str = ""):
        self.memory["function_contexts"][function_name] = {
            "file_path": file_path,
            "diff_context": diff_context,
            "module_context": module_context,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        self._save_memory()
    
    def get_function_context(self, function_name: str) -> Optional[Dict[str, Any]]:
        return self.memory["function_contexts"].get(function_name)
    
    def store_diff_pattern(self, diff_hash: str, diff_content: str, 
                          affected_functions: List[str], test_quality_score: float = None):
        self.memory["diff_patterns"][diff_hash] = {
            "diff_content": diff_content,
            "affected_functions": affected_functions,
            "test_quality_score": test_quality_score,
            "created_at": datetime.now().isoformat()
        }
        self._save_memory()
    
    def get_similar_diff_patterns(self, diff_content: str, limit: int = 2) -> List[Dict[str, Any]]:
        similar_patterns = []
        
        for diff_hash, pattern in self.memory["diff_patterns"].items():
            similarity = self._calculate_diff_similarity(diff_content, pattern["diff_content"])
            if similarity > 0.3:
                similar_patterns.append({**pattern, "similarity": similarity})
        
        similar_patterns.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_patterns[:limit]
    
    def _calculate_diff_similarity(self, diff1: str, diff2: str) -> float:
        lines1 = set(diff1.split('\n'))
        lines2 = set(diff2.split('\n'))
        
        common_lines = lines1 & lines2
        total_lines = lines1 | lines2
        
        return len(common_lines) / len(total_lines) if total_lines else 0.0
    
    def _extract_function_names_from_diff(self, diff_content: str) -> List[str]:
        import re
        function_pattern = r'def\s+(\w+)\s*\('
        return re.findall(function_pattern, diff_content)
    
    def store_coverage_gap(self, function_name: str, missing_coverage: List[str], 
                          test_suggestions: List[str]):
        self.memory["coverage_gaps"][function_name] = {
            "missing_coverage": missing_coverage,
            "test_suggestions": test_suggestions,
            "created_at": datetime.now().isoformat(),
            "resolved": False
        }
        self._save_memory()
    
    def get_coverage_gaps(self, function_name: str) -> Optional[Dict[str, Any]]:
        return self.memory["coverage_gaps"].get(function_name)
    
    def store_prompt_effectiveness(self, prompt_strategy: str, function_type: str, 
                                  quality_score: float, coverage_score: float):
        key = f"{prompt_strategy}_{function_type}"
        
        if key not in self.memory["prompt_effectiveness"]:
            self.memory["prompt_effectiveness"][key] = {
                "quality_scores": [],
                "coverage_scores": [],
                "usage_count": 0
            }
        
        self.memory["prompt_effectiveness"][key]["quality_scores"].append(quality_score)
        self.memory["prompt_effectiveness"][key]["coverage_scores"].append(coverage_score)
        self.memory["prompt_effectiveness"][key]["usage_count"] += 1
        
        self._save_memory()
    
    def get_best_prompt_strategy(self, function_type: str) -> str:
        best_strategy = "diff-aware"
        best_score = 0.0
        
        for key, data in self.memory["prompt_effectiveness"].items():
            if key.endswith(f"_{function_type}") and data["quality_scores"]:
                avg_quality = sum(data["quality_scores"]) / len(data["quality_scores"])
                if avg_quality > best_score:
                    best_score = avg_quality
                    best_strategy = key.split("_")[0]
        
        return best_strategy
    
    def get_insights(self) -> Dict[str, Any]:
        summary = self.get_memory_summary()
        
        insights = {
            "summary": summary,
            "best_strategies": {},
            "common_patterns": []
        }
        
        for key, data in self.memory["prompt_effectiveness"].items():
            if data["quality_scores"] and data["coverage_scores"]:
                avg_quality = sum(data["quality_scores"]) / len(data["quality_scores"])
                avg_coverage = sum(data["coverage_scores"]) / len(data["coverage_scores"])
                
                strategy, function_type = key.split("_", 1)
                if function_type not in insights["best_strategies"]:
                    insights["best_strategies"][function_type] = {}
                
                insights["best_strategies"][function_type][strategy] = {
                    "avg_quality": avg_quality,
                    "avg_coverage": avg_coverage,
                    "usage_count": data["usage_count"]
                }
        
        return insights
    
    def get_memory_summary(self) -> Dict[str, Any]:
        return {
            "total_test_patterns": len(self.memory["test_patterns"]),
            "total_function_contexts": len(self.memory["function_contexts"]),
            "total_diff_patterns": len(self.memory["diff_patterns"]),
            "total_coverage_gaps": len(self.memory["coverage_gaps"]),
            "total_prompt_strategies": len(self.memory["prompt_effectiveness"]),
            "last_updated": self.memory["last_updated"]
        }
    
    def clear(self):
        self.memory = self._create_default_memory()
        self._save_memory()
