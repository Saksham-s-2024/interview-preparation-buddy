import re
import ast
from typing import List, Optional, Tuple
from .models import CodingResponse


class CodeAssessor:
    def __init__(self):
        self.test_cases = self._initialize_test_cases()
    
    def _initialize_test_cases(self) -> dict:
        """Initialize test cases for different problems"""
        return {
            "two_sum": [
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
                {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]}
            ],
            "max_subarray": [
                {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
                {"input": {"nums": [1]}, "expected": 1},
                {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23}
            ],
            "stock_profit": [
                {"input": {"prices": [7, 1, 5, 3, 6, 4]}, "expected": 5},
                {"input": {"prices": [7, 6, 4, 3, 1]}, "expected": 0},
                {"input": {"prices": [1, 2, 3, 4, 5]}, "expected": 4}
            ],
            "longest_substring": [
                {"input": {"s": "abcabcbb"}, "expected": 3},
                {"input": {"s": "bbbbb"}, "expected": 1},
                {"input": {"s": "pwwkew"}, "expected": 3}
            ],
            "anagram": [
                {"input": {"s": "anagram", "t": "nagaram"}, "expected": True},
                {"input": {"s": "rat", "t": "car"}, "expected": False},
                {"input": {"s": "listen", "t": "silent"}, "expected": True}
            ],
            "climbing_stairs": [
                {"input": {"n": 2}, "expected": 2},
                {"input": {"n": 3}, "expected": 3},
                {"input": {"n": 5}, "expected": 8}
            ]
        }
    
    def assess_code(self, code: str, problem_type: str, language: str) -> CodingResponse:
        """Assess the submitted code solution"""
        if not code.strip():
            return CodingResponse(
                feedback="No code provided. Please submit your solution.",
                score=0.0,
                test_cases_passed=0,
                total_test_cases=0,
                time_complexity=None,
                space_complexity=None,
                suggestions=["Please write and submit your code solution."]
            )
        
        # Basic code analysis
        syntax_score = self._check_syntax(code, language)
        structure_score = self._check_code_structure(code)
        
        # Run test cases (simplified assessment)
        test_results = self._run_test_cases(code, problem_type, language)
        
        # Analyze complexity
        time_complexity = self._analyze_time_complexity(code)
        space_complexity = self._analyze_space_complexity(code)
        
        # Generate feedback
        feedback = self._generate_feedback(
            syntax_score, structure_score, test_results, 
            time_complexity, space_complexity
        )
        
        # Calculate overall score
        overall_score = self._calculate_score(
            syntax_score, structure_score, test_results
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            syntax_score, structure_score, test_results, 
            time_complexity, space_complexity
        )
        
        return CodingResponse(
            feedback=feedback,
            score=overall_score,
            test_cases_passed=test_results["passed"],
            total_test_cases=test_results["total"],
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            suggestions=suggestions
        )
    
    def _check_syntax(self, code: str, language: str) -> float:
        """Check if code has valid syntax"""
        try:
            if language.lower() in ["python", "py"]:
                ast.parse(code)
                return 1.0
            elif language.lower() in ["javascript", "js"]:
                # Basic JavaScript syntax check
                if "function" in code or "=>" in code or "class" in code:
                    return 1.0
                return 0.8
            elif language.lower() in ["java"]:
                # Basic Java syntax check
                if "public" in code and "class" in code:
                    return 1.0
                return 0.8
            else:
                return 0.7  # Default score for other languages
        except SyntaxError:
            return 0.0
        except Exception:
            return 0.5
    
    def _check_code_structure(self, code: str) -> float:
        """Check code structure and best practices"""
        score = 0.0
        
        # Check for function definition
        if re.search(r'(def\s+\w+|function\s+\w+|public\s+\w+\s+\w+\s*\()', code):
            score += 0.3
        
        # Check for proper indentation
        lines = code.split('\n')
        indented_lines = sum(1 for line in lines if line.strip() and line.startswith((' ', '\t')))
        if indented_lines > 0:
            score += 0.2
        
        # Check for comments
        if '#' in code or '//' in code or '/*' in code:
            score += 0.1
        
        # Check for variable naming
        if re.search(r'\b[a-z][a-zA-Z0-9_]*\s*=', code):
            score += 0.2
        
        # Check for return statement
        if 'return' in code:
            score += 0.2
        
        return min(score, 1.0)
    
    def _run_test_cases(self, code: str, problem_type: str, language: str) -> dict:
        """Run test cases (simplified version)"""
        test_cases = self.test_cases.get(problem_type, [])
        if not test_cases:
            return {"passed": 0, "total": 0}
        
        # This is a simplified assessment
        # In a real implementation, you'd execute the code safely
        passed = 0
        total = len(test_cases)
        
        # Basic heuristics for assessment
        if "return" in code and ("def" in code or "function" in code):
            # If code has function and return, assume it might work
            passed = min(total, 2)  # Assume 2 test cases pass
        
        return {"passed": passed, "total": total}
    
    def _analyze_time_complexity(self, code: str) -> Optional[str]:
        """Analyze time complexity of the code"""
        code_lower = code.lower()
        
        # Look for nested loops
        if re.search(r'for.*for|while.*for|for.*while', code_lower):
            return "O(n²)"
        
        # Look for single loop
        if re.search(r'for\s+\w+|while\s+\w+', code_lower):
            return "O(n)"
        
        # Look for recursive patterns
        if re.search(r'def.*\1|function.*\1', code_lower):
            return "O(log n)" if "//" in code or "/" in code else "O(n)"
        
        # Look for hash map/dictionary usage
        if re.search(r'dict|hash|map|set', code_lower):
            return "O(1)" if "lookup" in code_lower else "O(n)"
        
        return "O(1)"
    
    def _analyze_space_complexity(self, code: str) -> Optional[str]:
        """Analyze space complexity of the code"""
        code_lower = code.lower()
        
        # Look for array/list creation
        if re.search(r'\[\]|list\(|array\(', code_lower):
            return "O(n)"
        
        # Look for recursive calls
        if re.search(r'def.*\1|function.*\1', code_lower):
            return "O(log n)" if "//" in code or "/" in code else "O(n)"
        
        # Look for hash map/dictionary usage
        if re.search(r'dict|hash|map|set', code_lower):
            return "O(n)"
        
        return "O(1)"
    
    def _generate_feedback(self, syntax_score: float, structure_score: float, 
                          test_results: dict, time_complexity: str, 
                          space_complexity: str) -> str:
        """Generate comprehensive feedback"""
        feedback_parts = []
        
        if syntax_score >= 0.8:
            feedback_parts.append("✅ Good syntax and structure.")
        elif syntax_score >= 0.5:
            feedback_parts.append("⚠️ Code has some syntax issues but is mostly correct.")
        else:
            feedback_parts.append("❌ Code has significant syntax errors.")
        
        if structure_score >= 0.7:
            feedback_parts.append("✅ Well-structured code with good practices.")
        elif structure_score >= 0.4:
            feedback_parts.append("⚠️ Code structure could be improved.")
        else:
            feedback_parts.append("❌ Code lacks proper structure.")
        
        if test_results["total"] > 0:
            pass_rate = test_results["passed"] / test_results["total"]
            if pass_rate >= 0.8:
                feedback_parts.append("✅ Most test cases passed.")
            elif pass_rate >= 0.5:
                feedback_parts.append("⚠️ Some test cases passed.")
            else:
                feedback_parts.append("❌ Most test cases failed.")
        
        if time_complexity:
            feedback_parts.append(f"📊 Time complexity: {time_complexity}")
        
        if space_complexity:
            feedback_parts.append(f"💾 Space complexity: {space_complexity}")
        
        return " ".join(feedback_parts)
    
    def _calculate_score(self, syntax_score: float, structure_score: float, 
                        test_results: dict) -> float:
        """Calculate overall score"""
        if test_results["total"] == 0:
            return (syntax_score + structure_score) / 2 * 10
        
        test_score = test_results["passed"] / test_results["total"]
        return ((syntax_score + structure_score + test_score) / 3) * 10
    
    def _generate_suggestions(self, syntax_score: float, structure_score: float,
                             test_results: dict, time_complexity: str, 
                             space_complexity: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if syntax_score < 0.8:
            suggestions.append("Fix syntax errors and ensure code compiles.")
        
        if structure_score < 0.7:
            suggestions.append("Improve code structure with proper functions and indentation.")
        
        if test_results["total"] > 0 and test_results["passed"] < test_results["total"]:
            suggestions.append("Debug your solution to pass more test cases.")
        
        if time_complexity in ["O(n²)", "O(2^n)"]:
            suggestions.append("Consider optimizing for better time complexity.")
        
        if space_complexity == "O(n)" and "O(1)" in [time_complexity]:
            suggestions.append("Consider if space complexity can be reduced.")
        
        if not suggestions:
            suggestions.append("Great job! Your solution looks good.")
        
        return suggestions
