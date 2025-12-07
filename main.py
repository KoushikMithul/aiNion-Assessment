"""
Nion Orchestration Engine
Main entry point for the orchestration system
"""
import json
import sys
import os
import glob
from pathlib import Path
from datetime import datetime
from src.models import InputMessage
from src.orchestration_engine import OrchestrationEngine
from src.output_formatter import OutputFormatter


def save_output_to_file(input_file: str, output: str):
    """Save orchestration output to a file in the outputs directory"""
    # Create outputs directory if it doesn't exist
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # Extract test case name from input file path
    # e.g., "test_cases/test_case_1.json" -> "test_case_1"
    input_path = Path(input_file)
    test_case_name = input_path.stem  # Gets filename without extension
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_filename = f"{test_case_name}_result.txt"
    output_path = outputs_dir / output_filename
    
    # Write output to file
    with open(output_path, 'w') as f:
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Input: {input_file}\n")
        f.write("=" * 70 + "\n\n")
        f.write(output)
    
    print(f"\n✅ Output saved to: {output_path}")


def process_single_test(input_file: str):
    """Process a single test case file"""
    try:
        # Read input message
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        # Parse input message
        message = InputMessage(**input_data)
        
        # Initialize orchestration engine
        engine = OrchestrationEngine()
        
        # Process message
        result = engine.process_message(message)
        
        # Format and print output
        formatter = OutputFormatter()
        output = formatter.format(result)
        print(output)
        
        # Save output to file
        save_output_to_file(input_file, output)
        return True
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return False
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the orchestration engine"""
    
    # Check if input is provided
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <input_json_file>           # Run single test case")
        print("  python main.py --all                       # Run all test cases")
        print("  python main.py test_case_1 test_case_2     # Run specific test cases")
        print("\nExamples:")
        print("  python main.py test_cases/test_case_1.json")
        print("  python main.py --all")
        print("  python main.py test_case_1 test_case_3")
        sys.exit(1)
    
    # Handle --all flag
    if sys.argv[1] == "--all":
        print("Running all test cases...\n")
        test_files = sorted(glob.glob("test_cases/test_case_*.json"))
        
        if not test_files:
            print("Error: No test case files found in test_cases/ directory")
            sys.exit(1)
        
        success_count = 0
        total_count = len(test_files)
        
        for test_file in test_files:
            print(f"\n{'='*70}")
            print(f"Processing: {test_file}")
            print('='*70)
            if process_single_test(test_file):
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f"Summary: {success_count}/{total_count} test cases completed successfully")
        print('='*70)
        
        if success_count < total_count:
            sys.exit(1)
        return
    
    # Handle multiple specific test case names (without paths/extensions)
    if not sys.argv[1].endswith('.json'):
        print("Running specified test cases...\n")
        success_count = 0
        total_count = len(sys.argv) - 1
        
        for arg in sys.argv[1:]:
            # Convert test case name to file path
            if arg.startswith("test_cases/"):
                test_file = arg if arg.endswith('.json') else f"{arg}.json"
            else:
                test_file = f"test_cases/{arg}.json" if arg.endswith('.json') else f"test_cases/{arg}.json"
            
            print(f"\n{'='*70}")
            print(f"Processing: {test_file}")
            print('='*70)
            if process_single_test(test_file):
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f"Summary: {success_count}/{total_count} test cases completed successfully")
        print('='*70)
        
        if success_count < total_count:
            sys.exit(1)
        return
    
    # Handle single test case file
    input_file = sys.argv[1]
    if not process_single_test(input_file):
        sys.exit(1)


if __name__ == "__main__":
    main()
