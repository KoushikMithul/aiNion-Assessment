"""
Nion Orchestration Engine
Main entry point for the orchestration system
"""
import json
import sys
from src.models import InputMessage
from src.orchestration_engine import OrchestrationEngine
from src.output_formatter import OutputFormatter


def main():
    """Main function to run the orchestration engine"""
    
    # Check if input file is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_json_file>")
        print("Example: python main.py test_cases/test_case_1.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
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
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
