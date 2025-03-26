import aiml
import os

class ChatBot:
    def __init__(self):
        self.kernel = aiml.Kernel()
        # Define the AIML files directory
        aiml_path = os.path.join(os.path.dirname(__file__), "aiml_files")
        print("AIML path:", aiml_path)
        
        # Check if the folder exists
        if not os.path.exists(aiml_path):
            print(f"⚠️ AIML folder not found at {aiml_path}! Creating it...")
            os.makedirs(aiml_path)
        
        # Get list of AIML files in the directory
        aiml_files = [f for f in os.listdir(aiml_path) if f.endswith(".aiml")]
        print("Found AIML files:", aiml_files)
        
        if not aiml_files:
            print("⚠️ No AIML files found in the directory. Please add your AIML files.")
        else:
            # Directly load each AIML file
            for filename in aiml_files:
                filepath = os.path.join(aiml_path, filename)
                print(f"Loading {filepath}...")
                try:
                    self.kernel.learn(filepath)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
    def get_response(self, message):
        return self.kernel.respond(message)

# Create a chatbot instance
chatbot_instance = ChatBot()

if __name__ == "__main__":
    # Optionally, test a response immediately
    print("Test response for 'HELLO':", chatbot_instance.get_response("HELLO"))
    
    print("Chatbot is ready! Type your message and press Enter. Type 'exit' to quit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        # For case-insensitive matching, you can optionally convert input to uppercase:
        # response = chatbot_instance.get_response(user_input.upper())
        response = chatbot_instance.get_response(user_input)
        print("Bot:", response)
