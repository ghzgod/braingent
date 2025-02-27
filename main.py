import requests
import json
import time
from colorama import init, Fore, Style, Back

# Initialize colorama
init(autoreset=True)

class BrainAgent:
    def __init__(self, name, role, color, api_url, model):
        self.name = name
        self.role = role
        self.color = color
        self.api_url = api_url
        self.model = model
        
    def think(self, context, prompt):
        full_prompt = f"""
You are the {self.name} part of a human brain.
Your role: {self.role}

Focus only on how the {self.name} would process and respond to this input.
Context from other brain regions: {context}

Input: {prompt}

Give a brief response (2-5 sentences) from the perspective of the {self.name}.
"""
        
        response = requests.post(
            f"{self.api_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    def display_thought(self, thought):
        print(f"{self.color}[{self.name}]: {thought}{Style.RESET_ALL}")
        return thought

class BrainSystem:
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model
        self.agents = self.initialize_agents()
        self.conversation_history = []
        
    def initialize_agents(self):
        agents = {
            "Prefrontal Cortex": BrainAgent(
                "Prefrontal Cortex", 
                "Executive function, decision-making, planning, working memory, impulse control, and coordination of other brain regions. You are the supervisor agent.",
                Fore.CYAN + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Amygdala": BrainAgent(
                "Amygdala", 
                "Emotional processing, especially fear, anxiety, and threat detection. You evaluate emotional significance of inputs.",
                Fore.RED + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Hippocampus": BrainAgent(
                "Hippocampus", 
                "Memory formation, storage, and retrieval. You connect current input with past experiences and knowledge.",
                Fore.GREEN + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Temporal Lobe": BrainAgent(
                "Temporal Lobe", 
                "Processing of auditory information, language comprehension, and semantic memory. You help understand meaning.",
                Fore.YELLOW + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Parietal Lobe": BrainAgent(
                "Parietal Lobe", 
                "Spatial awareness, sensory integration, and attention. You help understand relationships between objects and concepts.",
                Fore.MAGENTA + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Occipital Lobe": BrainAgent(
                "Occipital Lobe", 
                "Visual processing and interpretation. You analyze visual information and imagery.",
                Fore.BLUE + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Cerebellum": BrainAgent(
                "Cerebellum", 
                "Motor coordination, precision, timing, and some cognitive functions. You ensure smooth processing.",
                Fore.WHITE + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Broca's Area": BrainAgent(
                "Broca's Area", 
                "Speech production and language processing. You help formulate grammatically correct responses.",
                Fore.LIGHTCYAN_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Wernicke's Area": BrainAgent(
                "Wernicke's Area", 
                "Language comprehension, connecting words with meaning. You help understand the semantic content of input.",
                Fore.LIGHTRED_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Anterior Cingulate Cortex": BrainAgent(
                "Anterior Cingulate Cortex", 
                "Error detection, conflict monitoring, and attention regulation. You highlight inconsistencies and uncertainties.",
                Fore.LIGHTGREEN_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Thalamus": BrainAgent(
                "Thalamus", 
                "Sensory relay, filtering, and attention regulation. You decide what information reaches consciousness.",
                Fore.LIGHTYELLOW_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Hypothalamus": BrainAgent(
                "Hypothalamus", 
                "Regulation of basic drives, emotional states, and homeostasis. You signal basic motivations and needs.",
                Fore.LIGHTMAGENTA_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Basal Ganglia": BrainAgent(
                "Basal Ganglia", 
                "Action selection, habit formation, and procedural learning. You help choose appropriate behaviors and responses.",
                Fore.LIGHTBLUE_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Brainstem": BrainAgent(
                "Brainstem", 
                "Basic life functions, arousal, and alertness. You regulate the overall activation level of the system.",
                Fore.LIGHTWHITE_EX + Back.BLACK,
                self.api_url,
                self.model
            ),
            "Insula": BrainAgent(
                "Insula", 
                "Interoception, awareness of bodily states, and social emotions. You sense internal feelings and empathy.",
                Fore.LIGHTBLACK_EX + Back.WHITE,
                self.api_url,
                self.model
            )
        }
        return agents
    
    def process_input(self, user_input):
        print("\n" + "="*80)
        print(Fore.CYAN + Style.BRIGHT + "INTERNAL BRAIN PROCESSING BEGINS" + Style.RESET_ALL)
        print("="*80 + "\n")
        
        # Store thoughts from each region
        thoughts = {}
        
        # First round: Initial responses from all regions except Prefrontal Cortex
        for name, agent in self.agents.items():
            if name != "Prefrontal Cortex":
                thought = agent.think("Initial processing", user_input)
                thoughts[name] = agent.display_thought(thought)
        
        # Compile all thoughts for the Prefrontal Cortex
        context = "\n".join([f"{name}: {thought}" for name, thought in thoughts.items()])
        
        # Prefrontal Cortex integrates all inputs
        prefrontal_thought = self.agents["Prefrontal Cortex"].think(context, user_input)
        thoughts["Prefrontal Cortex"] = self.agents["Prefrontal Cortex"].display_thought(prefrontal_thought)
        
        # Second round: Regions respond to Prefrontal's initial integration
        updated_thoughts = {}
        for name, agent in self.agents.items():
            if name != "Prefrontal Cortex":
                updated_context = f"Prefrontal Cortex's integration: {prefrontal_thought}\nYour previous thought: {thoughts[name]}"
                updated_thought = agent.think(updated_context, user_input)
                updated_thoughts[name] = agent.display_thought(updated_thought)
        
        # Final integration by Prefrontal Cortex
        final_context = "\n".join([f"{name}: {thought}" for name, thought in updated_thoughts.items()])
        final_thought = self.agents["Prefrontal Cortex"].think(
            f"Your previous integration: {prefrontal_thought}\nUpdated context from brain regions:\n{final_context}", 
            user_input
        )
        self.agents["Prefrontal Cortex"].display_thought(final_thought)
        
        # Generate final response using all context
        response = self.generate_response(user_input, thoughts, updated_thoughts, final_thought)
        
        # Add to conversation history
        self.conversation_history.append({"user": user_input, "response": response})
        
        print("\n" + "="*80)
        print(Fore.CYAN + Style.BRIGHT + "BRAIN PROCESSING COMPLETE" + Style.RESET_ALL)
        print("="*80 + "\n")
        
        return response
    
    def generate_response(self, user_input, thoughts, updated_thoughts, final_integration):
        # Compile all context
        context = (
            f"User input: {user_input}\n\n"
            f"Initial brain processing:\n" + 
            "\n".join([f"{name}: {thought}" for name, thought in thoughts.items()]) +
            f"\n\nUpdated brain processing:\n" + 
            "\n".join([f"{name}: {thought}" for name, thought in updated_thoughts.items()]) +
            f"\n\nFinal integration by Prefrontal Cortex: {final_integration}"
        )
        
        prompt = f"""
Based on the internal processing of all brain regions, generate a final response to the user.
The response should be coherent, balanced, and reflect the integrated processing of all regions.

{context}

Final response to user:
"""
        
        response = requests.post(
            f"{self.api_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            final_response = response.json()['response'].strip()
            print(f"{Fore.WHITE + Back.BLUE + Style.BRIGHT}[FINAL RESPONSE]: {final_response}{Style.RESET_ALL}")
            return final_response
        else:
            error_msg = f"Error generating response: {response.status_code} - {response.text}"
            print(f"{Fore.WHITE + Back.RED + Style.BRIGHT}[ERROR]: {error_msg}{Style.RESET_ALL}")
            return error_msg

def main():
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════════════════════════╗
    ║                 Neural Network Brain Chat                 ║
    ║ A simulation of brain regions collaborating to think      ║
    ╚══════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    api_url = "http://192.168.1.4:3080"
    model = "deepseek-r1:latest"
    
    # Test connection before proceeding
    try:
        response = requests.get(f"{api_url}/api/version")
        if response.status_code != 200:
            print(f"{Fore.RED}Failed to connect to Ollama API at {api_url}. Status code: {response.status_code}{Style.RESET_ALL}")
            return
        print(f"{Fore.GREEN}Successfully connected to Ollama API. Version: {response.json().get('version', 'unknown')}{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error connecting to Ollama API at {api_url}: {e}{Style.RESET_ALL}")
        return
    
    brain = BrainSystem(api_url, model)
    
    print(f"{Fore.YELLOW}Initializing brain regions...{Style.RESET_ALL}")
    for name in brain.agents.keys():
        print(f"{Fore.GREEN}✓ {name} online{Style.RESET_ALL}")
        time.sleep(0.1)  # For visual effect
    
    print(f"\n{Fore.CYAN}The neural network brain is ready for conversation!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Type 'exit' or 'quit' to end the session.{Style.RESET_ALL}\n")
    
    while True:
        user_input = input(f"{Fore.WHITE + Style.BRIGHT}You: {Style.RESET_ALL}")
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print(f"{Fore.YELLOW}Neural Network Brain shutting down. Goodbye!{Style.RESET_ALL}")
            break
        
        response = brain.process_input(user_input)
        print(f"{Fore.WHITE + Back.BLUE + Style.BRIGHT}Agent: {response}{Style.RESET_ALL}")
        print(f"{Fore.WHITE + Style.BRIGHT}You: {Style.RESET_ALL}", end="")

if __name__ == "__main__":
    main()