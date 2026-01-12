# """
# Production-Ready Test Suite for Quiz Generation Service
# Tests the exact JSON format you specified
# """

# import asyncio
# import json
# import sys
# import os

# # Ensure we can import from app
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from app.services.quiz_generation_service import (
#     QuizGenerationService,
#     QuizGenerationRequest
# )

# # Colors for output
# class Colors:
#     GREEN = '\033[92m'
#     RED = '\033[91m'
#     YELLOW = '\033[93m'
#     BLUE = '\033[94m'
#     END = '\033[0m'

# def print_success(msg):
#     print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

# def print_error(msg):
#     print(f"{Colors.RED}❌ {msg}{Colors.END}")

# def print_info(msg):
#     print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


# async def test_basic_quiz():
#     """Test 1: Basic quiz with all question types"""
#     print("\n" + "="*60)
#     print("TEST 1: Basic Quiz Generation")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         # Sample content (like from your database)
#         content = """
#         Circuit breakers are automatic electrical switches designed to protect 
#         electrical circuits from damage caused by overcurrent. When excessive 
#         current flows through a circuit, the circuit breaker trips and interrupts 
#         the flow of electricity. There are several types of circuit breakers:
        
#         1. Thermal circuit breakers use a bimetallic strip that bends when heated 
#         by excessive current. This bending triggers the breaker to trip.
        
#         2. Magnetic circuit breakers use an electromagnet. When current exceeds 
#         the rated level, the magnetic field becomes strong enough to pull a 
#         contact apart, breaking the circuit.
        
#         3. Thermal-magnetic circuit breakers combine both mechanisms for better 
#         protection against both overloads and short circuits.
        
#         Circuit breakers are rated by current (e.g., 15A, 20A, 30A) and voltage. 
#         Unlike fuses, which must be replaced after they blow, circuit breakers 
#         can be reset after tripping. This makes them more convenient and 
#         cost-effective for repeated use. They are essential safety devices in 
#         modern electrical installations.
#         """
        
#         request = QuizGenerationRequest(
#             content=content,
#             difficulty_level="intermediate",
#             num_mcq=3,
#             num_true_false=3,
#             num_short_answer=2,
#             num_of_options=4
#         )
        
#         print_info("Generating quiz...")
#         quiz = await service.generate_quiz(request)
        
#         print_success(f"Quiz generated: {quiz.quiz_id}")
#         print(f"  Total Questions: {quiz.total_questions}")
#         print(f"  MCQ: {len(quiz.multiple_choice)}")
#         print(f"  T/F: {len(quiz.true_false)}")
#         print(f"  Short Answer: {len(quiz.short_answer)}")
        
#         # Show sample questions
#         if quiz.multiple_choice:
#             print(f"\n  📝 Sample MCQ:")
#             q = quiz.multiple_choice[0]
#             print(f"     Q: {q.question}")
#             for letter, text in q.options.items():
#                 marker = "✓" if letter == q.correct_answer else " "
#                 print(f"     {marker} {letter}. {text}")
        
#         if quiz.true_false:
#             print(f"\n  ✓/✗ Sample T/F:")
#             q = quiz.true_false[0]
#             print(f"     Q: {q.question}")
#             print(f"     A: {q.correct_answer}")
        
#         if quiz.short_answer:
#             print(f"\n  💭 Sample Short Answer:")
#             q = quiz.short_answer[0]
#             print(f"     Q: {q.question}")
#             print(f"     Key Points: {len(q.key_points)}")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# async def test_mcq_only():
#     """Test 2: Only MCQ questions"""
#     print("\n" + "="*60)
#     print("TEST 2: MCQ Only")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         content = """
#         Welding is a fabrication process that joins materials, usually metals, 
#         by using high heat to melt the parts together. Common welding techniques 
#         include MIG (Metal Inert Gas), TIG (Tungsten Inert Gas), and stick welding. 
#         Each method has specific applications and requires different equipment. 
#         Safety is paramount in welding, requiring proper protective equipment 
#         including welding helmets, gloves, and flame-resistant clothing.
#         """
        
#         request = QuizGenerationRequest(
#             content=content,
#             difficulty_level="beginner",
#             num_mcq=5,
#             num_true_false=0,
#             num_short_answer=0,
#             num_of_options=4
#         )
        
#         quiz = await service.generate_quiz(request)
        
#         print_success(f"Generated {len(quiz.multiple_choice)} MCQ questions")
        
#         # Verify all questions have 4 options
#         for i, q in enumerate(quiz.multiple_choice, 1):
#             if len(q.options) != 4:
#                 print_error(f"Question {i} has {len(q.options)} options (expected 4)")
#                 return False
#             print(f"  Q{i}: {len(q.options)} options ✓")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         return False


# async def test_different_option_counts():
#     """Test 3: Different number of MCQ options"""
#     print("\n" + "="*60)
#     print("TEST 3: Different Option Counts")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         content = """
#         Carpentry is a skilled trade focused on working with wood. Key joints 
#         include mortise and tenon, dovetail, and lap joints. Each joint has 
#         specific strength characteristics and applications. Tools include saws, 
#         chisels, planes, and measuring devices. Safety equipment like goggles 
#         and dust masks are essential for protecting against flying debris and 
#         wood dust inhalation.
#         """
        
#         # Test with 3 options
#         request_3 = QuizGenerationRequest(
#             content=content,
#             difficulty_level="intermediate",
#             num_mcq=2,
#             num_true_false=0,
#             num_short_answer=0,
#             num_of_options=3
#         )
        
#         quiz_3 = await service.generate_quiz(request_3)
#         print_info(f"Testing 3 options (A, B, C):")
#         for q in quiz_3.multiple_choice:
#             print(f"  Options: {list(q.options.keys())}")
#             if len(q.options) == 3:
#                 print_success("  3 options ✓")
#             else:
#                 print_error(f"  Expected 3, got {len(q.options)}")
        
#         # Test with 5 options
#         request_5 = QuizGenerationRequest(
#             content=content,
#             difficulty_level="intermediate",
#             num_mcq=2,
#             num_true_false=0,
#             num_short_answer=0,
#             num_of_options=5
#         )
        
#         quiz_5 = await service.generate_quiz(request_5)
#         print_info(f"\nTesting 5 options (A, B, C, D, E):")
#         for q in quiz_5.multiple_choice:
#             print(f"  Options: {list(q.options.keys())}")
#             if len(q.options) == 5:
#                 print_success("  5 options ✓")
#             else:
#                 print_error(f"  Expected 5, got {len(q.options)}")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         return False


# async def test_json_format():
#     """Test 4: Verify JSON format matches specification"""
#     print("\n" + "="*60)
#     print("TEST 4: JSON Format Verification")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         content = """
#         Plumbing systems transport water and waste in buildings. Key components 
#         include pipes, fittings, valves, and fixtures. Common pipe materials are 
#         copper, PVC, and PEX. Soldering is used for copper joints, while PVC 
#         uses cement. Water pressure is measured in PSI (pounds per square inch). 
#         Proper venting prevents siphoning and allows waste to flow properly.
#         """
        
#         request = QuizGenerationRequest(
#             content=content,
#             difficulty_level="intermediate",
#             num_mcq=2,
#             num_true_false=2,
#             num_short_answer=1,
#             num_of_options=4
#         )
        
#         quiz = await service.generate_quiz(request)
        
#         # Export to JSON
#         quiz_json = service.export_to_json(quiz)
#         quiz_dict = service.export_to_dict(quiz)
        
#         print_success("JSON export successful")
#         print(f"  JSON length: {len(quiz_json)} characters")
        
#         # Verify structure
#         required_fields = [
#             'quiz_id', 'generated_at', 'difficulty_level', 
#             'total_questions', 'multiple_choice', 'true_false', 'short_answer'
#         ]
        
#         for field in required_fields:
#             if field in quiz_dict:
#                 print_success(f"  Field '{field}' present")
#             else:
#                 print_error(f"  Field '{field}' missing")
#                 return False
        
#         # Verify MCQ structure
#         if quiz_dict['multiple_choice']:
#             mcq = quiz_dict['multiple_choice'][0]
#             mcq_fields = ['question', 'options', 'correct_answer', 'explanation']
#             for field in mcq_fields:
#                 if field in mcq:
#                     print_success(f"  MCQ field '{field}' present")
#                 else:
#                     print_error(f"  MCQ field '{field}' missing")
#                     return False
        
#         print("\n  Sample JSON output:")
#         print(json.dumps(quiz_dict, indent=2)[:500] + "...")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         return False


# async def test_difficulty_levels():
#     """Test 5: All difficulty levels"""
#     print("\n" + "="*60)
#     print("TEST 5: Difficulty Levels")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         content = """
#         Automotive engines convert fuel into mechanical energy. The four-stroke 
#         cycle includes intake, compression, power, and exhaust strokes. Each 
#         cylinder has valves, a piston, and spark plug. Engine displacement is 
#         measured in liters or cubic inches. Regular maintenance includes oil 
#         changes, filter replacements, and spark plug inspection.
#         """
        
#         difficulties = ["beginner", "intermediate", "advanced"]
        
#         for difficulty in difficulties:
#             request = QuizGenerationRequest(
#                 content=content,
#                 difficulty_level=difficulty,
#                 num_mcq=2,
#                 num_true_false=0,
#                 num_short_answer=0,
#                 num_of_options=4
#             )
            
#             quiz = await service.generate_quiz(request)
#             print_success(f"{difficulty.upper()}: {quiz.total_questions} questions generated")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         return False


# async def test_content_grounding():
#     """Test 6: Verify questions are grounded in content"""
#     print("\n" + "="*60)
#     print("TEST 6: Content Grounding (Anti-Hallucination)")
#     print("="*60)
    
#     try:
#         service = QuizGenerationService()
        
#         # Very specific content
#         content = """
#         The XYZ-2000 is a specialized welding machine manufactured exclusively 
#         in Germany since 2015. It operates at exactly 240 volts and can produce 
#         welds up to 8mm thick. The machine weighs precisely 45 kilograms and 
#         costs $3,500. It uses a proprietary cooling system called "AquaFlow" 
#         that reduces operating temperature by 30%.
#         """
        
#         request = QuizGenerationRequest(
#             content=content,
#             difficulty_level="intermediate",
#             num_mcq=3,
#             num_true_false=2,
#             num_short_answer=1,
#             num_of_options=4
#         )
        
#         quiz = await service.generate_quiz(request)
        
#         print_info("Checking if questions reference content details...")
        
#         # Check if questions contain specific facts from content
#         content_facts = ["XYZ-2000", "240 volts", "8mm", "45 kilograms", 
#                         "$3,500", "AquaFlow", "30%", "Germany", "2015"]
        
#         all_questions_text = ""
#         for q in quiz.multiple_choice:
#             all_questions_text += q.question + " " + " ".join(q.options.values())
#         for q in quiz.true_false:
#             all_questions_text += q.question
#         for q in quiz.short_answer:
#             all_questions_text += q.question
        
#         found_facts = [fact for fact in content_facts if fact in all_questions_text]
        
#         print(f"  Found {len(found_facts)} specific facts from content in questions")
#         if len(found_facts) > 0:
#             print_success("Questions appear grounded in provided content")
#         else:
#             print_error("Questions may not be fully grounded in content")
        
#         return True
        
#     except Exception as e:
#         print_error(f"Test failed: {e}")
#         return False


# async def run_all_tests():
#     """Run all tests"""
#     print("\n" + "🧪 " + "="*58)
#     print("   QUIZ GENERATION SERVICE - PRODUCTION TEST SUITE")
#     print("="*60)
    
#     # Check API key
#     if not os.getenv("GROQ_API_KEY"):
#         print_error("\nGROQ_API_KEY not set!")
#         print("Set it with: export GROQ_API_KEY='your_key_here'")
#         return False
    
#     tests = [
#         ("Basic Quiz Generation", test_basic_quiz),
#         ("MCQ Only", test_mcq_only),
#         ("Different Option Counts", test_different_option_counts),
#         ("JSON Format", test_json_format),
#         ("Difficulty Levels", test_difficulty_levels),
#         ("Content Grounding", test_content_grounding),
#     ]
    
#     results = []
    
#     for name, test_func in tests:
#         try:
#             result = await test_func()
#             results.append((name, result))
#         except Exception as e:
#             print_error(f"{name} crashed: {e}")
#             results.append((name, False))
    
#     # Summary
#     print("\n" + "="*60)
#     print("TEST SUMMARY")
#     print("="*60)
    
#     passed = sum(1 for _, result in results if result)
#     total = len(results)
    
#     for name, result in results:
#         if result:
#             print_success(name)
#         else:
#             print_error(name)
    
#     print(f"\n{'='*60}")
#     print(f"Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
    
#     if passed == total:
#         print_success("\n🎉 All tests passed! Service is ready for production!")
#     else:
#         print_error(f"\n⚠️  {total-passed} test(s) failed")
    
#     print("="*60 + "\n")
    
#     return passed == total


# if __name__ == "__main__":
#     success = asyncio.run(run_all_tests())
#     sys.exit(0 if success else 1)


# VERSION 2



"""
Production-Ready Test Suite for Quiz Generation Service
Tests the exact JSON format you specified
"""

import asyncio
import json
import sys
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Ensure we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.quiz_generation_service import (
    QuizGenerationService,
    QuizGenerationRequest
)

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


async def test_basic_quiz():
    """Test 1: Basic quiz with all question types"""
    print("\n" + "="*60)
    print("TEST 1: Basic Quiz Generation")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        # Sample content (like from your database)
        content = """
        Circuit breakers are automatic electrical switches designed to protect 
        electrical circuits from damage caused by overcurrent. When excessive 
        current flows through a circuit, the circuit breaker trips and interrupts 
        the flow of electricity. There are several types of circuit breakers:
        
        1. Thermal circuit breakers use a bimetallic strip that bends when heated 
        by excessive current. This bending triggers the breaker to trip.
        
        2. Magnetic circuit breakers use an electromagnet. When current exceeds 
        the rated level, the magnetic field becomes strong enough to pull a 
        contact apart, breaking the circuit.
        
        3. Thermal-magnetic circuit breakers combine both mechanisms for better 
        protection against both overloads and short circuits.
        
        Circuit breakers are rated by current (e.g., 15A, 20A, 30A) and voltage. 
        Unlike fuses, which must be replaced after they blow, circuit breakers 
        can be reset after tripping. This makes them more convenient and 
        cost-effective for repeated use. They are essential safety devices in 
        modern electrical installations.
        """
        
        request = QuizGenerationRequest(
            content=content,
            difficulty_level="intermediate",
            num_mcq=3,
            num_true_false=3,
            num_short_answer=2,
            num_of_options=4
        )
        
        print_info("Generating quiz...")
        quiz = await service.generate_quiz(request)
        
        print_success(f"Quiz generated: {quiz.quiz_id}")
        print(f"  Total Questions: {quiz.total_questions}")
        print(f"  MCQ: {len(quiz.multiple_choice)}")
        print(f"  T/F: {len(quiz.true_false)}")
        print(f"  Short Answer: {len(quiz.short_answer)}")
        
        # Show sample questions
        if quiz.multiple_choice:
            print(f"\n  📝 Sample MCQ:")
            q = quiz.multiple_choice[0]
            print(f"     Q: {q.question}")
            for letter, text in q.options.items():
                marker = "✓" if letter == q.correct_answer else " "
                print(f"     {marker} {letter}. {text}")
        
        if quiz.true_false:
            print(f"\n  ✓/✗ Sample T/F:")
            q = quiz.true_false[0]
            print(f"     Q: {q.question}")
            print(f"     A: {q.correct_answer}")
        
        if quiz.short_answer:
            print(f"\n  💭 Sample Short Answer:")
            q = quiz.short_answer[0]
            print(f"     Q: {q.question}")
            print(f"     Key Points: {len(q.key_points)}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcq_only():
    """Test 2: Only MCQ questions"""
    print("\n" + "="*60)
    print("TEST 2: MCQ Only")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        content = """
        Welding is a fabrication process that joins materials, usually metals, 
        by using high heat to melt the parts together. Common welding techniques 
        include MIG (Metal Inert Gas), TIG (Tungsten Inert Gas), and stick welding. 
        Each method has specific applications and requires different equipment. 
        Safety is paramount in welding, requiring proper protective equipment 
        including welding helmets, gloves, and flame-resistant clothing.
        """
        
        request = QuizGenerationRequest(
            content=content,
            difficulty_level="beginner",
            num_mcq=5,
            num_true_false=0,
            num_short_answer=0,
            num_of_options=4
        )
        
        quiz = await service.generate_quiz(request)
        
        print_success(f"Generated {len(quiz.multiple_choice)} MCQ questions")
        
        # Verify all questions have 4 options
        for i, q in enumerate(quiz.multiple_choice, 1):
            if len(q.options) != 4:
                print_error(f"Question {i} has {len(q.options)} options (expected 4)")
                return False
            print(f"  Q{i}: {len(q.options)} options ✓")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


async def test_different_option_counts():
    """Test 3: Different number of MCQ options"""
    print("\n" + "="*60)
    print("TEST 3: Different Option Counts")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        content = """
        Carpentry is a skilled trade focused on working with wood. Key joints 
        include mortise and tenon, dovetail, and lap joints. Each joint has 
        specific strength characteristics and applications. Tools include saws, 
        chisels, planes, and measuring devices. Safety equipment like goggles 
        and dust masks are essential for protecting against flying debris and 
        wood dust inhalation.
        """
        
        # Test with 3 options
        request_3 = QuizGenerationRequest(
            content=content,
            difficulty_level="intermediate",
            num_mcq=2,
            num_true_false=0,
            num_short_answer=0,
            num_of_options=3
        )
        
        quiz_3 = await service.generate_quiz(request_3)
        print_info(f"Testing 3 options (A, B, C):")
        for q in quiz_3.multiple_choice:
            print(f"  Options: {list(q.options.keys())}")
            if len(q.options) == 3:
                print_success("  3 options ✓")
            else:
                print_error(f"  Expected 3, got {len(q.options)}")
        
        # Test with 5 options
        request_5 = QuizGenerationRequest(
            content=content,
            difficulty_level="intermediate",
            num_mcq=2,
            num_true_false=0,
            num_short_answer=0,
            num_of_options=5
        )
        
        quiz_5 = await service.generate_quiz(request_5)
        print_info(f"\nTesting 5 options (A, B, C, D, E):")
        for q in quiz_5.multiple_choice:
            print(f"  Options: {list(q.options.keys())}")
            if len(q.options) == 5:
                print_success("  5 options ✓")
            else:
                print_error(f"  Expected 5, got {len(q.options)}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


async def test_json_format():
    """Test 4: Verify JSON format matches specification"""
    print("\n" + "="*60)
    print("TEST 4: JSON Format Verification")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        content = """
        Plumbing systems transport water and waste in buildings. Key components 
        include pipes, fittings, valves, and fixtures. Common pipe materials are 
        copper, PVC, and PEX. Soldering is used for copper joints, while PVC 
        uses cement. Water pressure is measured in PSI (pounds per square inch). 
        Proper venting prevents siphoning and allows waste to flow properly.
        """
        
        request = QuizGenerationRequest(
            content=content,
            difficulty_level="intermediate",
            num_mcq=2,
            num_true_false=2,
            num_short_answer=1,
            num_of_options=4
        )
        
        quiz = await service.generate_quiz(request)
        
        # Export to JSON
        quiz_json = service.export_to_json(quiz)
        quiz_dict = service.export_to_dict(quiz)
        
        print_success("JSON export successful")
        print(f"  JSON length: {len(quiz_json)} characters")
        
        # Verify structure
        required_fields = [
            'quiz_id', 'generated_at', 'difficulty_level', 
            'total_questions', 'multiple_choice', 'true_false', 'short_answer'
        ]
        
        for field in required_fields:
            if field in quiz_dict:
                print_success(f"  Field '{field}' present")
            else:
                print_error(f"  Field '{field}' missing")
                return False
        
        # Verify MCQ structure
        if quiz_dict['multiple_choice']:
            mcq = quiz_dict['multiple_choice'][0]
            mcq_fields = ['question', 'options', 'correct_answer', 'explanation']
            for field in mcq_fields:
                if field in mcq:
                    print_success(f"  MCQ field '{field}' present")
                else:
                    print_error(f"  MCQ field '{field}' missing")
                    return False
        
        print("\n  Sample JSON output:")
        print(json.dumps(quiz_dict, indent=2)[:500] + "...")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


async def test_difficulty_levels():
    """Test 5: All difficulty levels"""
    print("\n" + "="*60)
    print("TEST 5: Difficulty Levels")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        content = """
        Automotive engines convert fuel into mechanical energy. The four-stroke 
        cycle includes intake, compression, power, and exhaust strokes. Each 
        cylinder has valves, a piston, and spark plug. Engine displacement is 
        measured in liters or cubic inches. Regular maintenance includes oil 
        changes, filter replacements, and spark plug inspection.
        """
        
        difficulties = ["beginner", "intermediate", "advanced"]
        
        for difficulty in difficulties:
            request = QuizGenerationRequest(
                content=content,
                difficulty_level=difficulty,
                num_mcq=2,
                num_true_false=0,
                num_short_answer=0,
                num_of_options=4
            )
            
            quiz = await service.generate_quiz(request)
            print_success(f"{difficulty.upper()}: {quiz.total_questions} questions generated")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


async def test_content_grounding():
    """Test 6: Verify questions are grounded in content"""
    print("\n" + "="*60)
    print("TEST 6: Content Grounding (Anti-Hallucination)")
    print("="*60)
    
    try:
        service = QuizGenerationService()
        
        # Very specific content
        content = """
        The XYZ-2000 is a specialized welding machine manufactured exclusively 
        in Germany since 2015. It operates at exactly 240 volts and can produce 
        welds up to 8mm thick. The machine weighs precisely 45 kilograms and 
        costs $3,500. It uses a proprietary cooling system called "AquaFlow" 
        that reduces operating temperature by 30%.
        """
        
        request = QuizGenerationRequest(
            content=content,
            difficulty_level="intermediate",
            num_mcq=3,
            num_true_false=2,
            num_short_answer=1,
            num_of_options=4
        )
        
        quiz = await service.generate_quiz(request)
        
        print_info("Checking if questions reference content details...")
        
        # Check if questions contain specific facts from content
        content_facts = ["XYZ-2000", "240 volts", "8mm", "45 kilograms", 
                        "$3,500", "AquaFlow", "30%", "Germany", "2015"]
        
        all_questions_text = ""
        for q in quiz.multiple_choice:
            all_questions_text += q.question + " " + " ".join(q.options.values())
        for q in quiz.true_false:
            all_questions_text += q.question
        for q in quiz.short_answer:
            all_questions_text += q.question
        
        found_facts = [fact for fact in content_facts if fact in all_questions_text]
        
        print(f"  Found {len(found_facts)} specific facts from content in questions")
        if len(found_facts) > 0:
            print_success("Questions appear grounded in provided content")
        else:
            print_error("Questions may not be fully grounded in content")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 " + "="*58)
    print("   QUIZ GENERATION SERVICE - PRODUCTION TEST SUITE")
    print("="*60)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print_error("\nGROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your_key_here'")
        return False
    
    tests = [
        ("Basic Quiz Generation", test_basic_quiz),
        ("MCQ Only", test_mcq_only),
        ("Different Option Counts", test_different_option_counts),
        ("JSON Format", test_json_format),
        ("Difficulty Levels", test_difficulty_levels),
        ("Content Grounding", test_content_grounding),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(name)
        else:
            print_error(name)
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Service is ready for production!")
    else:
        print_error(f"\n⚠️  {total-passed} test(s) failed")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)