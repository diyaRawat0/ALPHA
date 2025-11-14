try:
    from commands.command_registry import executable_functions
except ImportError:
    print("Error: Could not import executable_functions from commands.command_registry.")
    print("Please ensure commands/command_registry.py exists and contains 'executable_functions'.")

    executable_functions = {}

def route_function_call(function_call):
    func_name = function_call.name

    args = function_call.args
    #print(f"Attempting to route and execute function: {func_name} with args: {args}")

    if func_name in executable_functions:
        try:
            func_to_run = executable_functions[func_name]

            result = func_to_run(**args)
            #print(f"Function '{func_name}' executed successfully.")
            return result

        except TypeError as e:

            print(f"Error: Argument mismatch for function '{func_name}': {e}")
            return f"❌ Error: Incorrect arguments provided for function '{func_name}'. Details: {e}"
        except Exception as e:
            # Catch any other exceptions that occur during the function's execution
            print(f"❌ An error occurred during execution of '{func_name}': {e}")
            return f"❌ Error during execution of function '{func_name}': {e}"
    else:
        print(f"❌ Error: Model requested unknown function: {func_name}")
        return f"❌ Error: Unknown function requested by model: {func_name}"