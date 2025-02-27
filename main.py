from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import requests
import json
import time
import threading
import random
import sys

app = Flask(__name__)
socketio = SocketIO(app)

class BrainAgent:
    def __init__(self, name, role, api_url, model):
        self.name = name
        self.role = role
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
        
        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=300
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out"
        except Exception as e:
            return f"Error: {str(e)}"

class RouterAgent:
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model
        
    def determine_relevant_regions(self, user_input, all_regions):
        prompt = f"""
You are a router in a human brain simulation. Your job is to determine which brain regions should be activated to process the following input:

"{user_input}"

Here are all the available brain regions with their roles:
{all_regions}

For each region, decide if it should be activated (1) or not (0) for this input.
Respond with only a JSON object of region names and 0/1 values, nothing else.
Example: {{"Prefrontal Cortex": 1, "Amygdala": 0, ...}}

Always include the Prefrontal Cortex (value 1) as it's the supervisor.
Be selective - only activate regions truly relevant to the input (typically 4-7 regions + Prefrontal Cortex).
"""
        
        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                response_text = response.json().get('response', '').strip()
                # Extract JSON object from response
                try:
                    # Find the first { and last } to extract JSON
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        return json.loads(json_str)
                    else:
                        # Fallback to activating all regions
                        return {region: 1 for region in all_regions.keys()}
                except json.JSONDecodeError:
                    # Fallback to activating all regions
                    return {region: 1 for region in all_regions.keys()}
            else:
                # Fallback to activating all regions
                return {region: 1 for region in all_regions.keys()}
        except:
            # Fallback to activating all regions
            return {region: 1 for region in all_regions.keys()}

class BrainSystem:
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model
        self.agents = self.initialize_agents()
        self.conversation_history = []
        regions_info = {name: agent.role for name, agent in self.agents.items()}
        self.router = RouterAgent(api_url, model)
        
    def initialize_agents(self):
        agents = {
            "Prefrontal Cortex": BrainAgent(
                "Prefrontal Cortex", 
                "Executive function, decision-making, planning, working memory, impulse control, and coordination of other brain regions. As the supervisor agent, you integrate information from all regions and make final decisions.",
                self.api_url,
                self.model
            ),
            "Amygdala": BrainAgent(
                "Amygdala", 
                "Emotional processing, especially fear, anxiety, happiness, and threat detection. You evaluate emotional significance and generate emotional responses. Critical for survival responses and emotional memory.",
                self.api_url,
                self.model
            ),
            "Hippocampus": BrainAgent(
                "Hippocampus", 
                "Memory formation, storage, and retrieval. You connect current input with past experiences and knowledge. You create new memories and retrieve relevant ones.",
                self.api_url,
                self.model
            ),
            "Temporal Lobe": BrainAgent(
                "Temporal Lobe", 
                "Processing of auditory information, language comprehension, and semantic memory. You help understand meaning, recognize objects, faces, and sounds.",
                self.api_url,
                self.model
            ),
            "Parietal Lobe": BrainAgent(
                "Parietal Lobe", 
                "Spatial awareness, sensory integration, and attention. You help understand relationships between objects and concepts, interpret sensory information, and maintain body awareness.",
                self.api_url,
                self.model
            ),
            "Occipital Lobe": BrainAgent(
                "Occipital Lobe", 
                "Visual processing and interpretation. You analyze visual information, imagery, colors, motion, and help form visual memories.",
                self.api_url,
                self.model
            ),
            "Cerebellum": BrainAgent(
                "Cerebellum", 
                "Motor coordination, precision, timing, and some cognitive functions. You ensure smooth processing, sequence learning, and contribute to emotional regulation.",
                self.api_url,
                self.model
            ),
            "Broca's Area": BrainAgent(
                "Broca's Area", 
                "Speech production and language processing. You help formulate grammatically correct responses, coordinate muscle movements for speech, and assist with language comprehension.",
                self.api_url,
                self.model
            ),
            "Wernicke's Area": BrainAgent(
                "Wernicke's Area", 
                "Language comprehension, connecting words with meaning. You help understand the semantic content of input, interpret language, and support language-based reasoning.",
                self.api_url,
                self.model
            ),
            "Anterior Cingulate Cortex": BrainAgent(
                "Anterior Cingulate Cortex", 
                "Error detection, conflict monitoring, and attention regulation. You highlight inconsistencies and uncertainties, help with decision-making, and regulate emotional responses.",
                self.api_url,
                self.model
            ),
            "Thalamus": BrainAgent(
                "Thalamus", 
                "Sensory relay, filtering, and attention regulation. You decide what information reaches consciousness, relay sensory signals, and help regulate sleep/wake cycles.",
                self.api_url,
                self.model
            ),
            "Hypothalamus": BrainAgent(
                "Hypothalamus", 
                "Regulation of basic drives, emotional states, and homeostasis. You signal basic motivations like hunger, thirst, temperature regulation, and influence hormone release.",
                self.api_url,
                self.model
            ),
            "Basal Ganglia": BrainAgent(
                "Basal Ganglia", 
                "Action selection, habit formation, and procedural learning. You help choose appropriate behaviors and responses, facilitate movement initiation, and support reward-based learning.",
                self.api_url,
                self.model
            ),
            "Brainstem": BrainAgent(
                "Brainstem", 
                "Basic life functions, arousal, and alertness. You regulate breathing, heart rate, sleep cycles, and consciousness levels, forming the most primitive part of the brain.",
                self.api_url,
                self.model
            ),
            "Insula": BrainAgent(
                "Insula", 
                "Interoception, awareness of bodily states, and social emotions. You sense internal feelings, contribute to empathy, emotional awareness, and help process disgust and pain.",
                self.api_url,
                self.model
            )
        }
        return agents
    
    def process_input(self, user_input, verbose=False):
        # Get a dictionary of brain regions and their roles
        regions_info = {name: agent.role for name, agent in self.agents.items()}
        
        # Determine which brain regions to activate
        socketio.emit('processing_update', {'message': 'Routing input to relevant brain regions...'})
        active_regions = self.router.determine_relevant_regions(user_input, regions_info)
        
        # Force Prefrontal Cortex to always be active
        active_regions["Prefrontal Cortex"] = 1
        
        # Log which regions are active
        active_region_names = [name for name, value in active_regions.items() if value == 1]
        socketio.emit('processing_update', {
            'message': f'Activating regions: {", ".join(active_region_names)}',
            'active_regions': active_region_names
        })
        
        # Store thoughts from each region
        thoughts = {}
        processed_count = 0
        total_active = sum(active_regions.values())
        
        # First round: Initial responses from all active regions except Prefrontal Cortex
        for name, agent in self.agents.items():
            if name != "Prefrontal Cortex" and active_regions.get(name, 0) == 1:
                processed_count += 1
                if verbose:
                    socketio.emit('processing_update', {'message': f'Processing in {name}...'})
                else:
                    socketio.emit('processing_update', {
                        'message': f'Thinking... ({processed_count}/{total_active})',
                        'active_region': name
                    })
                
                thought = agent.think("Initial processing", user_input)
                thoughts[name] = thought
                
                if verbose:
                    socketio.emit('brain_thought', {
                        'region': name,
                        'thought': thought,
                        'active_regions': active_region_names
                    })
                
                # Simulate processing time
                time.sleep(0.5)
        
        # Compile all thoughts for the Prefrontal Cortex
        context = "\n".join([f"{name}: {thought}" for name, thought in thoughts.items()])
        
        # Prefrontal Cortex integrates all inputs
        if verbose:
            socketio.emit('processing_update', {'message': f'Integrating in Prefrontal Cortex...'})
        else:
            socketio.emit('processing_update', {
                'message': f'Thinking... ({total_active}/{total_active})',
                'active_region': 'Prefrontal Cortex'
            })
        
        prefrontal_thought = self.agents["Prefrontal Cortex"].think(context, user_input)
        thoughts["Prefrontal Cortex"] = prefrontal_thought
        
        if verbose:
            socketio.emit('brain_thought', {
                'region': 'Prefrontal Cortex',
                'thought': prefrontal_thought,
                'active_regions': active_region_names
            })
        
        # Second round: Regions respond to Prefrontal's initial integration
        updated_thoughts = {}
        if verbose:
            socketio.emit('processing_update', {'message': 'Second round of processing with prefrontal feedback'})
        
        processed_count = 0
        for name, agent in self.agents.items():
            if name != "Prefrontal Cortex" and active_regions.get(name, 0) == 1:
                processed_count += 1
                if verbose:
                    socketio.emit('processing_update', {'message': f'Refining in {name}...'})
                else:
                    socketio.emit('processing_update', {
                        'message': f'Refining thought... ({processed_count}/{total_active-1})',
                        'active_region': name
                    })
                
                updated_context = f"Prefrontal Cortex's integration: {prefrontal_thought}\nYour previous thought: {thoughts.get(name, '')}"
                updated_thought = agent.think(updated_context, user_input)
                updated_thoughts[name] = updated_thought
                
                if verbose:
                    socketio.emit('brain_thought', {
                        'region': name,
                        'thought': updated_thought,
                        'active_regions': active_region_names
                    })
                
                # Simulate processing time
                time.sleep(0.5)
        
        # Final integration by Prefrontal Cortex
        if verbose:
            socketio.emit('processing_update', {'message': 'Final integration by Prefrontal Cortex'})
        else:
            socketio.emit('processing_update', {
                'message': 'Finalizing response...',
                'active_region': 'Prefrontal Cortex'
            })
        
        final_context = "\n".join([f"{name}: {thought}" for name, thought in updated_thoughts.items()])
        final_thought = self.agents["Prefrontal Cortex"].think(
            f"Your previous integration: {prefrontal_thought}\nUpdated context from brain regions:\n{final_context}", 
            user_input
        )
        
        if verbose:
            socketio.emit('brain_thought', {
                'region': 'Prefrontal Cortex',
                'thought': final_thought,
                'active_regions': active_region_names
            })
        
        # Generate final response using all context
        if verbose:
            socketio.emit('processing_update', {'message': 'Generating final response'})
        else:
            socketio.emit('processing_update', {
                'message': 'Generating response...',
                'active_region': 'Prefrontal Cortex'
            })
        
        response = self.generate_response(user_input, thoughts, updated_thoughts, final_thought, active_region_names)
        
        # Add to conversation history
        self.conversation_history.append({"user": user_input, "response": response})
        
        # Signal completion
        socketio.emit('processing_complete', {
            'response': response,
            'active_regions': []  # Clear active regions
        })
        
        return response
    
    def generate_response(self, user_input, thoughts, updated_thoughts, final_integration, active_regions):
        # Compile all context - only include active regions
        active_thoughts = {name: thought for name, thought in thoughts.items() if name in active_regions or name == "Prefrontal Cortex"}
        active_updated_thoughts = {name: thought for name, thought in updated_thoughts.items() if name in active_regions or name == "Prefrontal Cortex"}
        
        context = (
            f"User input: {user_input}\n\n"
            f"Initial brain processing:\n" + 
            "\n".join([f"{name}: {thought}" for name, thought in active_thoughts.items()]) +
            f"\n\nUpdated brain processing:\n" + 
            "\n".join([f"{name}: {thought}" for name, thought in active_updated_thoughts.items()]) +
            f"\n\nFinal integration by Prefrontal Cortex: {final_integration}"
        )
        
        # Add conversation history for context if available
        history_context = ""
        if self.conversation_history:
            history_context = "Previous conversation:\n" + "\n".join([
                f"User: {exchange['user']}\nSystem: {exchange['response']}" 
                for exchange in self.conversation_history[-3:] # Include last 3 exchanges
            ])
            
        prompt = f"""
Based on the internal processing of all brain regions, generate a final response to the user.
The response should be coherent, balanced, and reflect the integrated processing of all regions.

{history_context}

{context}

Final response to user:
"""
        
        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                final_response = response.json().get('response', '').strip()
                return final_response
            else:
                return f"Error generating response: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "I'm sorry, but it's taking longer than expected to process your request. Could you please try again?"
        except Exception as e:
            return f"I apologize, but something went wrong while processing your request: {str(e)}"

# Initialize the brain system
api_url = "http://192.168.1.4:3080"
model = "deepseek-r1:latest"
brain = BrainSystem(api_url, model)

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    verbose = data.get('verbose', False)
    
    # Process in a separate thread to allow for real-time updates
    def process_message():
        brain.process_input(user_input, verbose)
    
    thread = threading.Thread(target=process_message)
    thread.start()
    
    return jsonify({'status': 'processing'})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')