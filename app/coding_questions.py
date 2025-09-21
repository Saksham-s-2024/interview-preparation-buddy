from typing import List, Dict, Optional
from .models import CodingQuestion
import random
                 
class CodingQuestionBank:
    def __init__(self):
        self.questions = self._initialize_questions()
    
    def _initialize_questions(self) -> Dict[str, List[CodingQuestion]]:
        """Initialize coding questions by category"""
        return {
            "arrays": [
                CodingQuestion(
                    problem_statement="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                    examples=[
                        "Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].",
                        "Input: nums = [3,2,4], target = 6\nOutput: [1,2]"
                    ],
                    constraints=[
                        "2 <= nums.length <= 10^4",
                        "-10^9 <= nums[i] <= 10^9",
                        "-10^9 <= target <= 10^9"
                    ],
                    difficulty="easy",
                    category="arrays"
                ),
                CodingQuestion(
                    problem_statement="Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
                    examples=[
                        "Input: nums = [-2,1,-3,4,-1,2,1,-5,4]\nOutput: 6\nExplanation: [4,-1,2,1] has the largest sum = 6.",
                        "Input: nums = [1]\nOutput: 1"
                    ],
                    constraints=[
                        "1 <= nums.length <= 10^5",
                        "-10^4 <= nums[i] <= 10^4"
                    ],
                    difficulty="medium",
                    category="arrays"
                ),
                CodingQuestion(
                    problem_statement="You are given an array prices where prices[i] is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock. Return the maximum profit you can achieve from this transaction.",
                    examples=[
                        "Input: prices = [7,1,5,3,6,4]\nOutput: 5\nExplanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.",
                        "Input: prices = [7,6,4,3,1]\nOutput: 0\nExplanation: In this case, no transactions are done and the max profit = 0."
                    ],
                    constraints=[
                        "1 <= prices.length <= 10^5",
                        "0 <= prices[i] <= 10^4"
                    ],
                    difficulty="easy",
                    category="arrays"
                )
            ],
            "strings": [
                CodingQuestion(
                    problem_statement="Given a string s, find the length of the longest substring without repeating characters.",
                    examples=[
                        "Input: s = 'abcabcbb'\nOutput: 3\nExplanation: The answer is 'abc', with the length of 3.",
                        "Input: s = 'bbbbb'\nOutput: 1\nExplanation: The answer is 'b', with the length of 1."
                    ],
                    constraints=[
                        "0 <= s.length <= 5 * 10^4",
                        "s consists of English letters, digits, symbols and spaces."
                    ],
                    difficulty="medium",
                    category="strings"
                ),
                CodingQuestion(
                    problem_statement="Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
                    examples=[
                        "Input: s = 'anagram', t = 'nagaram'\nOutput: true",
                        "Input: s = 'rat', t = 'car'\nOutput: false"
                    ],
                    constraints=[
                        "1 <= s.length, t.length <= 5 * 10^4",
                        "s and t consist of lowercase English letters."
                    ],
                    difficulty="easy",
                    category="strings"
                )
            ],
            "trees": [
                CodingQuestion(
                    problem_statement="Given the root of a binary tree, return its maximum depth. A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
                    examples=[
                        "Input: root = [3,9,20,null,null,15,7]\nOutput: 3",
                        "Input: root = [1,null,2]\nOutput: 2"
                    ],
                    constraints=[
                        "The number of nodes in the tree is in the range [0, 10^4].",
                        "-100 <= Node.val <= 100"
                    ],
                    difficulty="easy",
                    category="trees"
                ),
                CodingQuestion(
                    problem_statement="Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).",
                    examples=[
                        "Input: root = [3,9,20,null,null,15,7]\nOutput: [[3],[9,20],[15,7]]",
                        "Input: root = [1]\nOutput: [[1]]"
                    ],
                    constraints=[
                        "The number of nodes in the tree is in the range [0, 2000].",
                        "-1000 <= Node.val <= 1000"
                    ],
                    difficulty="medium",
                    category="trees"
                )
            ],
            "dynamic_programming": [
                CodingQuestion(
                    problem_statement="You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
                    examples=[
                        "Input: n = 2\nOutput: 2\nExplanation: There are two ways to climb to the top.\n1. 1 step + 1 step\n2. 2 steps",
                        "Input: n = 3\nOutput: 3\nExplanation: There are three ways to climb to the top.\n1. 1 step + 1 step + 1 step\n2. 1 step + 2 steps\n3. 2 steps + 1 step"
                    ],
                    constraints=[
                        "1 <= n <= 45"
                    ],
                    difficulty="easy",
                    category="dynamic_programming"
                ),
                CodingQuestion(
                    problem_statement="Given a string s, return the longest palindromic substring in s.",
                    examples=[
                        "Input: s = 'babad'\nOutput: 'bab'\nExplanation: 'aba' is also a valid answer.",
                        "Input: s = 'cbbd'\nOutput: 'bb'"
                    ],
                    constraints=[
                        "1 <= s.length <= 1000",
                        "s consist of only digits and English letters."
                    ],
                    difficulty="medium",
                    category="dynamic_programming"
                )
            ],
            "linked_lists": [
                CodingQuestion(
                    problem_statement="Given the head of a linked list, remove the nth node from the end of the list and return its head.",
                    examples=[
                        "Input: head = [1,2,3,4,5], n = 2\nOutput: [1,2,3,5]",
                        "Input: head = [1], n = 1\nOutput: []"
                    ],
                    constraints=[
                        "The number of nodes in the list is sz.",
                        "1 <= sz <= 30",
                        "0 <= Node.val <= 100",
                        "1 <= n <= sz"
                    ],
                    difficulty="medium",
                    category="linked_lists"
                )
            ]
        }
    
    def get_question_for_role(self, role: str, seniority: str, language: str) -> Optional[CodingQuestion]:
        """Get appropriate coding question based on role and seniority"""
        role_lower = role.lower()
        
        # Determine if role involves coding
        coding_roles = [
            "backend", "frontend", "fullstack", "software", "developer", "engineer", 
            "programmer", "data scientist", "machine learning", "devops", "sre"
        ]
        
        if not any(keyword in role_lower for keyword in coding_roles):
            return None
        
        # Select appropriate difficulty based on seniority
        if seniority.lower() in ["junior", "entry", "intern"]:
            difficulty_preference = ["easy"]
        elif seniority.lower() in ["mid", "middle", "intermediate"]:
            difficulty_preference = ["easy", "medium"]
        else:  # senior, lead, principal
            difficulty_preference = ["medium", "hard"]
        
        # Get all questions matching difficulty
        available_questions = []
        for category, questions in self.questions.items():
            for question in questions:
                if question.difficulty in difficulty_preference:
                    available_questions.append(question)
        
        if not available_questions:
            return None
        
        # Return random question
        return random.choice(available_questions)
    
    def get_all_categories(self) -> List[str]:
        """Get all available question categories"""
        return list(self.questions.keys())
    
    def get_questions_by_category(self, category: str) -> List[CodingQuestion]:
        """Get all questions in a specific category"""
        return self.questions.get(category, [])
